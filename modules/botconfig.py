import codecs
import json
import os

_configPath = os.path.abspath('./config.json')

with codecs.open(_configPath, 'r', 'utf-8-sig') as json_file:
    _config = json.load(json_file)

SessionAuthEP = _config['symphonyinfo']['authenticationHost'] + ':' + _config['symphonyinfo'][
    'authenticationPort'] + '/sessionauth/v1/authenticate'
KeyManagerEP = _config['symphonyinfo']['authenticationHost'] + ':' + \
               _config['symphonyinfo']['authenticationPort'] + '/keyauth/v1/authenticate'

SymphonyBaseURL = _config['symphonyinfo']['apiHost'] + ':' + _config['symphonyinfo']['apiPort']

_certFilePath = os.path.abspath(_config['botinfo']['certificatePath'] + '/' + _config['botinfo']['certificateFilePath'])
_certKeyfilePath = os.path.abspath(_config['botinfo']['certificatePath'] + '/' +
                                   _config['botinfo']['certificateKeyfilePath'])

BotCertificate = (_certFilePath, _certKeyfilePath)

BotEmailAddress = _config['botinfo']['botEmail']

BaseLoggingPath = os.path.abspath(_config['loggingPath'])

Blacklist = _config['blacklist']

PluginPath = os.path.abspath(_config['pluginPath'])

DefaultCommandDefinitionPath = os.path.abspath(_config['defaultCommandDefinitionPath'])


def GetCommandSetting(name):
    _settings = _config['defaultCommandSettings']

    for setting in _settings:
        if setting['name'] == name:
            return setting

    return None
