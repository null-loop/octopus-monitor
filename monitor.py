from sys import argv
from enum import Enum
import time
import requests
import os

DETAILED_DEPLOYING = True


def main():
    options = get_options(argv)
    if '-colour-test' in options:
        test_colours()
    elif not valid_options(options):
        display_options_help()
    else:
        execute_monitor_loop(options)


def test_colours():
    while True:
        ir_send(LampCommand.GREEN)
        time.sleep(1)
        ir_send(LampCommand.RED)
        time.sleep(1)
        ir_send(LampCommand.BLUE)
        time.sleep(1)


def display_options(options):
    for option in options:
        print(option + " = " + options[option])


def display_options_help():
    print("Mandatory options:")
    print("-key         : API key to use for Octopus")
    print("-url         : Base URL of the Octopus install")
    print("-project     : ID of the project to monitor")
    print("-environment : ID of the environment to monitor")
    print()
    print("Optional options:")
    print("-frequency   : Frequency of polling in seconds (defaults to 5 seconds)")


def valid_options(options):
    if '-key' not in options:
        return False
    if '-url' not in options:
        return False
    if '-project' not in options:
        return False
    if '-environment' not in options:
        return False
    return True


def get_options(arguments):
    working_arguments = arguments
    opts = {}  # Empty dictionary to store key-value pairs.
    while working_arguments:  # While there are arguments left to parse...
        if working_arguments[0][0] == '-':  # Found a "-name value" pair.
            opts[working_arguments[0]] = working_arguments[1]  # Add key and value to the dictionary.
        working_arguments = working_arguments[1:]  # Reduce the argument list by copying it starting from index 1.
    return opts


def get_deploying_state(state, task_details):
    if state == 'Success':
        return 'Success'
    if DETAILED_DEPLOYING:
        # examine the ActivityLogs to determine detailed deployment status...
        deploy_logs = task_details.get('ActivityLogs')[0]

        wait_status = deploy_logs.get('Children')[0].get('Status')
        if wait_status == 'Running':
            return 'Waiting'
        if wait_status == 'Failed':
            return 'WaitFailed'

        acquire_package_status = deploy_logs.get('Children')[1].get('Status')
        if acquire_package_status == 'Running':
            return 'Acquiring'
        if acquire_package_status == 'Failed':
            return 'AcquireFailed'

        deploying_status = deploy_logs.get('Children')[2].get('Status')
        if deploying_status == 'Running':
            return 'Deploying'
        if deploying_status == 'Failed':
            return 'DeployFailed'

        testing_status = deploy_logs.get('Children')[3].get('Status')
        if testing_status == 'Running':
            return 'Testing'
        if testing_status == 'Failed':
            return 'TestFailed'
    return state


def get_octopus_state(options):
    base_url = options['-url']
    key = options['-key']
    project = options['-project']
    environment = options['-environment']
    headers = {'x-Octopus-ApiKey': key}

    deployments_url = base_url + 'api/deployments?projects=' + project + '&environments=' + environment
    r = requests.get(deployments_url, headers=headers)
    deployments = r.json()
    task_id = deployments.get('Items')[0].get('TaskId')

    server_tasks_url = base_url + 'api/tasks/' + task_id + '/details'

    r = requests.get(server_tasks_url, headers=headers)
    task_details = r.json()
    state = task_details.get('Task').get('State')

    return get_deploying_state(state, task_details)


def execute_monitor_loop(options):
    frequency = 5
    if '-frequency' in options:
        frequency = int(options['-frequency'])
    display_options(options)
    current_state = ""
    while True:
        try:
            state = get_octopus_state(options)
        except Exception as ex:
            state = "PollFailed"
        if state != current_state:
            change_state(state, options)
            current_state = state
        time.sleep(frequency)


def ir_send(colour):
    print('Sending command ' + colour.name)
    os.system('irsend SEND_ONCE LED_24_KEY ' + colour.name)


def change_state(state, options):
    print("Changing state to " + state)
    # Possible value are :
    # "Waiting", "WaitFailed",
    # "Acquiring", "AcquireFailed",
    # "Deploying", "DeployFailed",
    # "Testing", "TestFailed",
    # "Success"
    # "PollFailed

    if state == 'Waiting':
        ir_send(LampCommand.LIGHT_BLUE)
    elif state == 'Acquiring':
        ir_send(LampCommand.SKY_BLUE)
    elif state == 'Deploying':
        ir_send(LampCommand.BLUE)
    elif state == 'Testing':
        ir_send(LampCommand.DARK_BLUE)
    elif state == 'WaitFailed':
        ir_send(LampCommand.YELLOW)
    elif state == 'AcquireFailed':
        ir_send(LampCommand.DARK_YELLOW)
    elif state == 'DeployFailed':
        ir_send(LampCommand.ORANGE)
    elif state == 'TestFailed':
        ir_send(LampCommand.RED)
    elif state == 'PollFailed':
        ir_send(LampCommand.PURPLE)
    else:
        ir_send(LampCommand.GREEN)


class LampCommand(Enum):
    BRIGHT_DOWN = 1
    BRIGHT_UP = 2
    OFF = 3
    ON = 4
    RED = 5
    GREEN = 6
    BLUE = 7
    WHITE = 8
    ORANGE = 9
    PEA_GREEN = 10
    DARK_BLUE = 11
    JUMP_7 = 12
    DARK_YELLOW = 13
    CYAN = 14
    BROWN = 15
    FADE_ALL = 16
    YELLOW = 17
    LIGHT_BLUE = 18
    PINK = 19
    FADE_7 = 20
    STRAW_YELLOW = 21
    SKY_BLUE = 22
    PURPLE = 23
    JUMP_3 = 24


if __name__ == '__main__':
    main()
