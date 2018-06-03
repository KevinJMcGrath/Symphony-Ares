import codecs
import json
import os
from string import Template
from enum import Enum


class MessageMLVersion(Enum):
    v1 = 1
    v2 = 2


_configPath = os.path.abspath('./config.json')

with codecs.open(_configPath, 'r', 'utf-8-sig') as json_file:
    _config = json.load(json_file)

# Symphony Endpoints
# SessionAuthEP = _config['symphonyinfo']['sessionTokenHost'] + ':' + _config['symphonyinfo'][
#     'sessionTokenPort'] + '/sessionauth/v1/authenticate'
# KeyManagerEP = _config['symphonyinfo']['authenticationHost'] + ':' + \
#                _config['symphonyinfo']['authenticationPort'] + '/keyauth/v1/authenticate'

SymphonyBaseURL = _config['symphonyinfo']['apiHost'] + ':' + _config['symphonyinfo']['apiPort']

_symSessionHost = _config['symphonyinfo']['sessionTokenHost']
_symSessionPort = _config['symphonyinfo']['sessionTokenPort']
_symSessionEP = Template(_config['symphonyinfo']['sessionEndpoint'])

SessionAuthEP = _symSessionEP.substitute(host=_symSessionHost, port=_symSessionPort)

_symKMHost = _config['symphonyinfo']['sessionTokenHost']
_symKMPort = _config['symphonyinfo']['sessionTokenPort']
_symKMEP = Template(_config['symphonyinfo']['keyManagerEndpoint'])

KeyManagerEP = _symKMEP.substitute(host=_symKMHost, port=_symKMPort)

_symAPIHost = _config['symphonyinfo']['apiHost']
_symAPIPort = _config['symphonyinfo']['apiPort']

_createIM = Template(_config['symphonyEndpoints']['createIM'])
_sendMessage = Template(_config['symphonyEndpoints']['sendMessage'])

CreateIMEndpoint = _createIM.substitute(host=_symAPIHost, port=_symAPIPort)


def GetSendMessageEndpoint(streamId, messageMLVersion: MessageMLVersion):
    if messageMLVersion == MessageMLVersion.v2:
        return _sendMessage.substitute(host=_symAPIHost, port=_symAPIPort, ver='v4', streamId=streamId)
    else:
        return _sendMessage.substitute(host=_symAPIHost, port=_symAPIPort, ver='v2', streamId=streamId)


# Certificate Stuff
_certFilePath = os.path.abspath(_config['botinfo']['certificatePath'] + '/' + _config['botinfo']['certificateFilePath'])
_certKeyfilePath = os.path.abspath(_config['botinfo']['certificatePath'] + '/' +
                                   _config['botinfo']['certificateKeyfilePath'])

BotCertificate = (_certFilePath, _certKeyfilePath)

# Misc details
BotEmailAddress = _config['botinfo']['botEmail']

BaseLoggingPath = os.path.abspath(_config['loggingPath'])
LogToFile = _config['logToFile']

Blacklist = _config['blacklist']

PluginPath = os.path.abspath(_config['pluginPath'])

DefaultCommandDefinitionPath = os.path.abspath(_config['defaultCommandDefinitionPath'])

UseRedisQueues = _config['redis']['active']
RedisHost = _config['redis']['host']
RedisPort = _config['redis']['port']
RedisPassword = _config['redis']['password']


def GetCommandSetting(name):
    _settings = _config['defaultCommandSettings']

    for setting in _settings:
        if setting['name'] == name:
            return setting

    return None
