import json
import re

import modules.botconfig as config
import modules.symphony.callout as callout
import modules.botlog as botlog


def SendUserIM(userIds, message):
    createEP = config.SymphonyBaseURL + '/pod/v1/im/create'
    body = [int(uid) for uid in userIds]

    response = callout.SymphonyPOST(createEP, json.dumps(body))

    streamId = response.ResponseData.id

    SendSymphonyMessage(streamId, message)


def SendSymphonyMessage(streamId, message: str):
    if not message.startswith('<messageML>'):
        message = FormatSymphonyMessage(message)

    messageEP = config.SymphonyBaseURL + '/agent/v2/stream/' + streamId + '/message/create'

    bodyJSON = {"message": message, "format": "MESSAGEML"}

    botlog.LogSymphonyInfo('Sending Symphony Message | StreamId: ' + streamId + ' | Message: ' + message)
    return callout.SymphonyPOST(messageEP, json.dumps(bodyJSON))


def FormatSymphonyMessage(message: str):
    return "<messageML>" + message + "</messageML>"


def FormatSymphonyLink(url: str):
    return '<a href="' + url + '"/>'


def FormatSymphonyId(streamId: str):
    return re.sub("==$", "", streamId.replace("/", "_"))

