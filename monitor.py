from sys import argv
import time
import requests
import lirc

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
        solid('Green')
        time.sleep(1)
        solid('Red')
        time.sleep(1)
        solid('Blue')
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


def solid(colour):
    send_colour(colour)


def send_colour(colour):
    print('Sending colour ' + colour)


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
        solid('LightBlue')
    elif state == 'Acquiring':
        solid('PaleBlue')
    elif state == 'Deploying':
        solid('Blue')
    elif state == 'Testing':
        solid('Pink')
    elif state == 'WaitFailed':
        solid('Yellow')
    elif state == 'AcquireFailed':
        solid('Orange')
    elif state == 'DeployFailed':
        solid('DarkOrange')
    elif state == 'TestFailed':
        solid('Red')
    elif state == 'PollFailed':
        solid('DarkPurple')
    else:
        solid('Green')

if __name__ == '__main__':
    main()
