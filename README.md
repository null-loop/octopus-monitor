# Octopus Monitor
Python monitoring app outputting status to IR LED Lamp

## Overview
Monitors the state of an Octopus deployment project and outputs the state via IR to an LED Lamp.

## Usage
`monitor.py -key [Octopus API Key] -url [Base Octopus URL] -project [ID of target to monitor] -environment [ID of environment to monitor] -frequency [polling interval in seconds]`