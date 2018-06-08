import json
import re

import modules.symphony.callout as callout
import modules.botconfig as config
import modules.botlog as botlog


def SendUserIM(userIds, message, endpointVersion='v1', data=None):
    # createEP = config.SymphonyBaseURL + '/pod/v1/im/create'
    # createEP = endpointIM.substitute(host=config.SymphonyBaseURL, imVersion=endpointVersion)

    createEP = config.CreateIMEndpoint

    body = [int(uid) for uid in userIds]

    response = callout.SymphonyPOST(createEP, json.dumps(body))

    streamId = response.ResponseData.id

    if endpointVersion == 'v1':
        SendSymphonyMessage(streamId, message)
    else:
        SendSymphonyMessageV2(streamId, message, data)


def SendUserIMv2(userIds, message, data=None):
    SendUserIM(userIds, message, endpointVersion='v2', data=data)


def SendSymphonyMessage(streamId, message: str):
    if not message.startswith('<messageML>'):
        message = FormatSymphonyMessage(message)

    # messageEP = config.SymphonyBaseURL + '/agent/v2/stream/' + streamId + '/message/create'
    # messageEP = endpointRoom.substitute(host=config.SymphonyBaseURL, roomVersion='v2', streamId=streamId)
    messageEP = config.GetSendMessageEndpoint(streamId, config.MessageMLVersion.v1)

    bodyJSON = {"message": message, "format": "MESSAGEML"}

    botlog.LogSymphonyInfo('Sending Symphony Message | StreamId: ' + streamId + ' | Message: ' + message)
    return callout.SymphonyPOST(messageEP, json.dumps(bodyJSON))


def SendSymphonyMessageV2(streamId, message: str, data=None):
    if not message.startswith('<messageML>'):
        message = FormatSymphonyMessage(message)

    # messageEP = endpointRoom.substitute(host=config.SymphonyBaseURL, roomVersion='v4', streamId=streamId)
    messageEP = config.GetSendMessageEndpoint(streamId, config.MessageMLVersion.v2)

    # The data payload has to be converted to a JSON string - the MultipartEncoder won't
    # convert a dict automatically
    if data is not None:
        data = json.dumps(data)

    bodyObj = {"message": message, "data": data}

    botlog.LogSymphonyInfo('Sending Symphony Message V4 | StreamId: ' + streamId)
    return callout.SymphonyPOSTV2(messageEP, bodyObj)


def FormatSymphonyMessage(message: str):
    return "<messageML>" + message + "</messageML>"


def FormatSymphonyLink(url: str):
    return '<a href="' + url + '"/>'


def FormatSymphonyId(streamId: str):
    return re.sub("==$", "", streamId.replace("/", "_"))


def FormatDicttoMML2(jsonObj: dict) -> str:
    json_str = json.dumps(jsonObj, indent=4, separators=(',', ': ')).replace('"', '&quot;').replace('\'', '&apos;')

    # apparently you need to include a newline character before the closing code tag. Why? ¯\_(-_-)_/¯
    json_str = "<code>" + json_str + "\n</code>"

    return json_str



