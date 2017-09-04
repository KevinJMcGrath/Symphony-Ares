import codecs
import json
import os
import traceback

import modules.botconfig as botconfig
import modules.botlog as botlog
from modules.symphony.tokenizer import CommandTypes

PluginCommands = None
DefaultCommands = None
HashCommands = None


class CommandDefinition:
    def __init__(self):
        self.IsImmediate = False
        self.Trigger = ''
        self.ModuleName = ''
        self.Description = ''
        self.HelpText = ''
        self.Function = ''
        self.CommandDictionary = {}


def LoadAllCommands():
    LoadDefaultCommands()
    LoadPluginCommands()


def LoadDefaultCommands():
    global DefaultCommands
    global HashCommands

    defPath = botconfig.DefaultCommandDefinitionPath

    DefaultCommands = {cmd.Trigger: cmd for cmd in GetCommandDefinitions(defPath, 'default', CommandTypes.Slash)}

    HashCommands = [cmd for cmd in GetCommandDefinitions(defPath, 'default', CommandTypes.Hash)]


def LoadPluginCommands():
    global PluginCommands

    PluginCommands = {}
    pluginPath = botconfig.PluginPath

    # os.walk() produces this: [['__pycache__', 'Salesforce', 'JIRA'], [], [], []]
    # List Comprehension syntax = [item for item in itemCollection]
    pluginDirectoryList = [x[1] for x in os.walk(pluginPath)][0]

    for pluginName in pluginDirectoryList:
        configPath = os.path.abspath(pluginPath + '/' + pluginName + '/config.json')

        # Only load plugins from folders with a config.json specified
        if os.path.isfile(configPath):
            pluginCmdList = GetCommandDefinitions(configPath, pluginName, CommandTypes.Slash)

            for cmd in pluginCmdList:
                if cmd.Trigger not in PluginCommands:
                    PluginCommands[cmd.Trigger] = cmd
                else:
                    botlog.LogSystemWarn('Plugin trigger ' + cmd.Trigger + ' already exists. Command from ' +
                                         pluginName + ' was not registered.')


def GetCommandDefinitions(definitionPath, pluginName, cType: CommandTypes):

    cmdDefs = []

    try:

        with codecs.open(definitionPath, 'r', 'utf-8-sig') as json_file:
            defJSON = json.load(json_file)

        if cType == CommandTypes.Hash:
            defCol = defJSON['hashcommands']
        else:
            defCol = defJSON['commands']

        for cmdDef in defCol:
            if cType == CommandTypes.Hash:
                cDef = CommandDefinition()
                cDef.ModuleName = pluginName
                cDef.Trigger = cmdDef['triggers']
                cDef.Function = cmdDef['function']

                if pluginName != 'default':
                    cDef.Module = 'modules.plugins.' + pluginName + '.commands'
                else:
                    cDef.Module = 'modules.command.defaultcommands'

                cmdDefs.append(cDef)

            else:
                for trigger in cmdDef['triggers']:
                    cDef = CommandDefinition()
                    cDef.ModuleName = pluginName

                    if pluginName != 'default':
                        cDef.Module = 'modules.plugins.' + pluginName + '.commands'
                    else:
                        cDef.Module = 'modules.command.defaultcommands'

                    cDef.Trigger = trigger
                    cDef.Description = cmdDef['description']
                    cDef.HelpText = cmdDef['helptext']
                    cDef.Function = cmdDef['function']

                    cDef.IsImmediate = cmdDef['immediate'] if 'immediate' in cmdDef else False

                    cmdDefs.append(cDef)

    except Exception as ex:
        errorStr = "Failed to load plugin: " + pluginName + ' - Error: ' + str(ex)
        stackTrace = 'Stack Trace: ' + ''.join(traceback.format_stack())
        botlog.LogSystemError(errorStr)
        botlog.LogSystemError(stackTrace)

    return cmdDefs
