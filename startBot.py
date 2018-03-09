import time

import botbuilder
import modules.botlog as botlog
import modules.command.commandhub as hub
import modules.symphony.datafeed as datafeed
import modules.plugins.commandloader as cmdloader

loopCount = 0


def Main():
    global loopCount

    botlog.LogSymphonyInfo('Starting Ares session...')
    botSession = botbuilder.SymSession()

    # Bot Loop Begins here
    loopControl = botSession.StartBot()
    loopCount = 0

    # Pre-load the command definitions
    cmdloader.LoadAllCommands()

    while loopControl:

        messages = datafeed.PollDataFeed(botSession.DataFeedId)

        if messages is not None:

            if len(messages) == 0:
                # botlog.LogConsoleInfo('204 - No Content')
                pass

            for msg in messages:
                if msg.IsValid and msg.Sender.IsValidSender:
                    hub.ProcessCommand(msg)

        else:
            botlog.LogSymphonyInfo('Error detected reading datafeed. Invalidating session...')
            botSession.InvalidateSession()
            loopControl = False

            loopControl = botSession.StartBot()


while loopCount < 10:
    try:
        Main()
    except SystemExit:
        loopCount = 99
        pass
    except Exception as ex:
        botlog.LogSystemError('Error: ' + str(ex))
        botlog.LogSymphonyError('Unhandled error, probably network difficulties at the Agent. Retrying in 30s.')

        time.sleep(30)
        loopCount += 1
