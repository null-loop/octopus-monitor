# Octopus Monitor
Python monitoring app outputting status to IR LED Lamp

## Overview
Monitors the state of an Octopus deployment project and outputs the state via IR to an LED Lamp.

##Setup

Install and configure LIRC as per [this gist](https://gist.github.com/prasanthj/c15a5298eb682bde34961c322c95378b)


## Usage
`monitor.py -key [Octopus API Key] -url [Base Octopus URL] -project [ID of target to monitor] -environment [ID of environment to monitor] -frequency [polling interval in seconds]`