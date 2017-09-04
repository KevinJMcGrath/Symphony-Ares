import botbuilder
import modules.botlog as botlog
import modules.command.commandhub as hub
import modules.symphony.datafeed as datafeed
import modules.plugins.commandloader as cmdloader

botlog.LogSymphonyInfo('Starting Ares session...')
botSession = botbuilder.SymSession()

# Bot Loop Begins here
botSession.StartBot()

# Pre-load the command definitions
cmdloader.LoadAllCommands()

loopControl = True

while loopControl:
    if not botSession.IsValidSession():
        botSession.StartBot()
    else:
        messages = datafeed.PollDataFeed(botSession.DataFeedId)

        for msg in messages:
            if msg.IsValid and msg.Sender.IsValidSender:
                hub.ProcessCommand(msg)

'''
    botlog.LogConsoleInfo('Current Queue Size: ' + str(len(cq.jobQueue)))

    for job in cq.jobQueue:
        jid = job.id
        res = job.result if job.result is not None else 'None'
        botlog.LogConsoleInfo('Job Id: ' + jid + ' - result: ' + res)
'''