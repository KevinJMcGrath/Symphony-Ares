import traceback

import modules.botconfig as config
import modules.botlog as botlog
import modules.symphony.callout as callout
import modules.symphony.messagedetail as msg
import modules.symphony.stream as stream
import modules.symphony.user as user


def CreateDataFeed():
    datafeedEP = config.SymphonyBaseURL + '/agent/v1/datafeed/create'

    return callout.SymphonyPOST(datafeedEP, None).ResponseData.id


def PollDataFeed(datafeedId):
    datafeedEP = config.SymphonyBaseURL + '/agent/v2/datafeed/' + datafeedId + '/read'

    response = callout.SymphonyGET(datafeedEP)

    # Messages coming from the API are formatted as an array of JSON objects
    # Thus, I need to break up the array, parse the individual objects, and pass
    # the list of python objects back to the engine
    messageItems = []
    if response.Success:
        for respItem in response.ResponseData:
            # Hopefully this will
            try:
                detail = msg.MessageDetail(respItem)
                detail.Sender = user.GetSymphonyUserDetail(detail.FromUserId)
                detail.ChatRoom = stream.GetStreamInfo(respItem.streamId)
                botlog.LogSymphonyInfo(detail.GetConsoleLogLine())

                if detail.Sender and detail.Sender.IsValidSender:
                    detail.InitiateCommandParsing()

                messageItems.append(detail)

            except SystemExit:
                botlog.LogConsoleInfo('Exiting Ares.')
            except Exception as ex:
                errorStr = "Symphony REST Exception (system): " + str(ex)
                stackTrace = 'Stack Trace: ' + ''.join(traceback.format_stack())
                botlog.LogSystemError(errorStr)
                botlog.LogSystemError(stackTrace)
    else:
        # if the response is not successful, return None. This way, I can tell the datafeed call was bad
        # and attempt to reconnect to the server.
        return None

    return messageItems



