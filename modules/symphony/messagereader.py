import traceback
import sys

import modules.symphony.callout as callout
import modules.symphony.messagedetail as msg
import modules.symphony.stream as stream
import modules.symphony.user as user

import modules.botconfig as config
import modules.botlog as botlog
import modules.utility_date_time as dtutil


def GetSymphonyMessagesSinceDateTime(streamId, startDateTime):
    dtmilli = dtutil.ConvertDateTimeToMilliseconds(startDateTime)
    dtStr = str(dtmilli)
    messageEP = config.SymphonyBaseURL + '/agent/v2/stream/' + streamId + '/message?since=' + dtStr

    return GetSymphonyMessages(messageEP)


def GetSymphonyMessages(endpoint):
    response = callout.SymphonyGET(endpoint)

    # Messages coming from the API are formatted as an array of JSON objects
    # Thus, I need to break up the array, parse the individual objects, and pass
    # the list of python objects back to the engine
    messageItems = []
    if response.Success:
        for respItem in response.ResponseData:
            # Hopefully this will
            try:
                if respItem.v2messageType and respItem.v2messageType == 'V2Message':
                    detail = msg.MessageDetail(respItem)
                    detail.Sender = user.GetSymphonyUserDetail(detail.FromUserId)
                    detail.ChatRoom = stream.GetStreamInfo(respItem.streamId)
                    botlog.LogSymphonyInfo(detail.GetConsoleLogLine())

                    if detail.Sender and detail.Sender.IsValidSender:
                        detail.InitiateCommandParsing()

                    messageItems.append(detail)
                elif respItem.v2messageType != 'V2Message':
                    botlog.LogConsoleInfo('Non-chat Message Type: ' + respItem.v2messageType)
                else:
                    botlog.LogConsoleInfo('Non-chat Message Type: unknown')

            except SystemExit:
                botlog.LogConsoleInfo('Exiting Ares.')
            except Exception as ex:
                errorStr = "Symphony REST Exception (system): " + str(ex)
                # stackTrace = 'Stack Trace: ' + ''.join(traceback.format_stack())
                exInfo = sys.exc_info()
                stackTrace = 'Stack Trace: ' + ''.join(traceback.format_exception(exInfo[0], exInfo[1], exInfo[2]))
                botlog.LogSystemError(errorStr)
                botlog.LogSystemError(stackTrace)
                botlog.LogConsoleInfo(response.ResponseText)

    return messageItems
