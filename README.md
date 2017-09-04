# Symphony-Ares
A multi-function bot for use with the Symphony communications platform

Ares is an example of a multi-function command and chat bot for the Symphony communications platform. It was written using Python 3.5. The original intention of the bot was proof-of-concept for utilizing Symphony's Agent APIs. It has since evolved to include functionality used in the Business Operations team, as well as some added functionality for other teams. 

The bot utilizes a local Redis server and the RQ python library for queueing requests - ensuring the processing of long running tasks does not bog down reading and processing of new messages. This is, in general, a future proofing effort since the Datafeed API stores unread messages until they are retreived. 

## Requirements

The bot was built using Pycharm on Ubuntu 17.04 and runs against Python 3.5, though it likely will run against Python 2.7 with minor modifications. 

* Python 3.5 

    * lxml - http://lxml.de/
    * PyCrypto - https://www.dlitz.net/software/pycrypto/
    * RQ - http://python-rq.org/

* Redis 2.6.0 or better

    * https://redis.io/
    * Sample Docker config: https://github.com/sameersbn/docker-redis

* A Symphony bot account with client certificate files

    * Client certificates are generally provided as .p12 files. The code asks for .pem files in /certificates
    * You will need the certificate password to extract the .pem files
    * crt.pem: openssl pkcs12 -in path.p12 -out bot.crt.pem -clcerts -nokeys
    * key.pem: openssl pkcs12 -in path.p12 -out bot.key.pem -nocerts -nodes

* Access to your POD's REST endpoints

## Installation

Installation of the bot is somewhat manual today. 

1. Clone the repo to your local environment 

    * `git clone https://github.com/KevinJMcGrath/Symphony-Ares`

2. Install and configure your Redis server. 
3. Create new config files by copying the *.sample.json to *.json (e.g. config.sample.json -> config.json)
4. Modify the various config files:

    * ./Ares/config.json - Contains general config details, including information about your Symphony configuration
    * ./Ares/modules/command/default.json - Contains a listing of the default commands - may not need modification
    * ./Ares/modules/plugins/JIRA/config.json - Contains information about your JIRA configuration and the commands the JIRA plugin will accept
    * ./Ares/modules/plugins/Salesforce/config.json - Similar to JIRA's config, only for Salesforce

## Starting the Bot

1. Ensure your Redis server is running
2. Start the Redis worker process

    * Open a new terminal session
    * Change to the bot folder, e.g. `cd /bots/symphony/Ares/`
    * Run the worker script: `python3 startWorker.py`

3. Start the bot

    * Open a new terminal session
    * Change to the bot folder
    * Run the bot script: `python3 startBot.py`

## Logging

Ares does not log messages, but will log other activity, including commands that are issued. Various logs can be found in ./Ares/logging

## Usage

Several functions are included by default with the bot. 

**Note**: The bot user _must_ be in the room in which a command is issued. Symphony does not support global commands at this time. 

### Google Translate:

Autodetects and translates the provided sentence into English

* Command: /translate "Hola. Como estas?"
* Reply: I think you said "Hello how are you?" (es)
* The two-letter language code for the auto-identified source language is included at the end of the reply

### Stock Quotes (AlphaVantage)

Pulls the most recent Open and Close prices for the given ticker symbol

* Command: /quote AAPL
* Reply: 

    Quote for: AAPL
    Date: 2017-09-04
    Open: 164.7600
    Close: 164.0400

* Note: An AlphaVantage API token is required. This can be obtained for free: https://www.alphavantage.co/documentation/

### Giphy

Searches for and returns a gif

* Command: /gif Search Text
* Reply: [link to gif]
* Note 1: /gif with no parameters produces a random gif
* Note 2: Requires an API token for Giphy: https://developers.giphy.com/

### Echo

A simple test to verify the bot is working and Symphony's APIs are responding

* Command: /echo [echo text]
* Reply: [echo text]

## Plugins

This initial python distribution includes a nascent framework for creating plugins for the bot. A plugin must contain several files:

* config.json - this fill must be valid json and must contain a `"commands": []` array that will tell the plugin parser what commands you have provided for the users

    Each command must have the following attributes:

    * "triggers": [] -> An array of strings - each string will act as a command alias for this command

        E.g. "triggers": ["quote", "$", "qt"] => the /quote command will also trigger with /qt or /$

    * "function": FunctionName -> The method name in your commands.py that the triggers wll execute
    * "description": [text] -> Description of your command. Returned with /[command] help
    * "helptext": [text] -> Help info for your command. Returned with /[command] help

* commands.py - Contains the method definitions specified in config.json
* __init__.py -> A blank file that python uses to correctly identify packages

Any additional files required for processing your command are ignored by the plugin parser



##TODO

* Provide documentation on how to process the incoming message and send a response
* Add Redis config info to root config.json
* Add additional functionality to JIRA and Salesforce plugins
* Add monitoring/alerting tool for keeping tabs on the bot state
* Add default command to report status of jobs in Redis queues
* Add setup scripts for installing and configuring the bot more easily