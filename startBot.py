import botbuilder
import modules.botlog as botlog
import modules.command.commandhub as hub
import modules.symphony.datafeed as datafeed
import modules.plugins.commandloader as cmdloader

botlog.LogSymphonyInfo('Starting Ares session...')
botSession = botbuilder.SymSession()

# Bot Loop Begins here
loopControl = botSession.StartBot()

# Pre-load the command definitions
cmdloader.LoadAllCommands()

while loopControl:

    messages = datafeed.PollDataFeed(botSession.DataFeedId)

    if messages is not None:
        for msg in messages:
            if msg.IsValid and msg.Sender.IsValidSender:
                hub.ProcessCommand(msg)

    else:
        botSession.InvalidateSession()
        loopControl = False

        loopControl = botSession.StartBot()
