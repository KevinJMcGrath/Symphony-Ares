import datetime
import requests

import modules.botlog as botlog
import modules.botconfig as botconfig
import modules.crypto as crypto
import modules.symphony.messaging as messaging
import modules.symphony.messagereader as symreader
import modules.utility_date_time as utdt


def SendSymphonyEcho(messageDetail):
    msg = messageDetail.Command.MessageText
    messaging.SendSymphonyMessage(messageDetail.StreamId, msg)


def SendSymphonyEchoV2(messageDetail):
    msg = messageDetail.Command.MessageText
    messaging.SendSymphonyMessageV2(messageDetail.StreamId, msg)


def LogSymphonyMessageDebug(messageDetail):
    botlog.LogSymphonyInfo('Message for Debugging: ' + repr(messageDetail.MessageRaw))
    messageDetail.ReplyToChat('Thank you for helping improve my code!')


def GetGoogleTranslation(messageDetail):
    transText = messageDetail.Command.MessageText

    if transText:

        botlog.LogSymphonyInfo('Attempting to translate: ' + transText)

        payload = {"client": "gtx", "sl": "auto", "tl": "en", "dt": "t", "q": transText}
        transEP = "https://translate.googleapis.com/translate_a/single"

        response = requests.get(transEP, params=payload).json()
        translation = response[0][0][0]
        lang = response[2]

        msg = 'I think you said: ' + translation + ' (' + lang + ')'
    else:
        msg = 'Please include a word or sentence to be translated.'

    messaging.SendSymphonyMessage(messageDetail.StreamId, msg)


# https://www.alphavantage.co/documentation/
def GetAlphaVantageStockQuote(messageDetail):

    quoteText = messageDetail.Command.MessageText

    try:
        avAPIKey = botconfig.GetCommandSetting('alphavantage')['apikey']

        quoteSymbol = quoteText.split()[0]

        payload = {"function": "TIME_SERIES_DAILY", "apikey": avAPIKey, "symbol": quoteSymbol}
        avEP = 'https://www.alphavantage.co/query'
        response = requests.get(avEP, params=payload).json()

        tsDate = sorted(list(response['Time Series (Daily)'].keys()), reverse=True)[0]
        tsOpen = response['Time Series (Daily)'][tsDate]['1. open']
        tsClose = response['Time Series (Daily)'][tsDate]['4. close']

        msg = 'Quote for: ' + quoteText + '<br/>Date: ' + tsDate + '<br/>Open: ' + tsOpen
        msg += '<br/>Close: ' + tsClose + ''

        messaging.SendSymphonyMessage(messageDetail.StreamId, msg)

    except Exception as ex:
        errorStr = "Symphony REST Exception (system): {}".format(ex)
        botlog.LogSystemError(errorStr)
        msg = "Sorry, I could not return a quote."
        messaging.SendSymphonyMessage(messageDetail.StreamId, msg)


def GetGiphyImage(messageDetail):
    try:
        giphyAPIKey = botconfig.GetCommandSetting('giphy')['apikey']

        giphyText = messageDetail.Command.MessageText

        paramList = giphyText.split()

        isRandom = len(paramList) == 0 or paramList[0] == 'random'

        if isRandom:
            ep = "http://api.giphy.com/v1/gifs/random"
            payload = {"apikey": giphyAPIKey}
        else:
            ep = "http://api.giphy.com/v1/gifs/translate"
            payload = {"apikey": giphyAPIKey, "s": giphyText}

        response = requests.get(ep, params=payload).json()

        if isRandom:
            msg = "<a href='" + response['data']['image_original_url'] + "'/>"
        else:
            msg = "<a href='" + response['data']['images']['original']['url'] + "'/>"

        messaging.SendSymphonyMessage(messageDetail.StreamId, msg)

    except Exception as ex:
        errorStr = "Symphony REST Exception (system): {}".format(ex)
        botlog.LogSystemError(errorStr)
        msg = "Sorry, I could not return a GIF right now."
        messaging.SendSymphonyMessage(messageDetail.StreamId, msg)


def SendUserFeedbackHelp(messageDetail):
    msg = "Client Feedback Submission Help <br/><br/>"
    msg += "Syntax: <br/>"
    msg += "<ul><li>1. Activate the bot with either <hash tag='usability'/> or <hash tag='newfeature'/></li>"
    msg += "<li>2. Write a succinct title of the issue (50 characters).</li>"
    msg += "<li>3. Add additional detail of the issue - context of the user's usage and what problem " \
           "needs to be solved.</li>"
    msg += "<li>4. @mention users - they will be included as Watchers in JIRA.</li>"
    msg += "<li>5. Add screenshots which will also be forwarded to JIRA</li>"
    msg += "<li>6. End with <hash tag='clients'/> and then a comma separated list of client names.</li> </ul><br/><br/>"
    msg += "<hash tag='usability'/> = 'It is very difficult for the user to use an existing functionality.'<br/>"
    msg += "<hash tag='newfeature'/> = 'This would make the user's life easier if this feature was added.'<br/>"
    msg += "<br/>For <b>more information</b>, go to Confluence: <a href='http://bit.ly/2sezQN9'/>"

    messaging.SendSymphonyMessage(messageDetail.StreamId, msg)


def SubmitUserFeedback(messageDetail):
    import modules.plugins.Salesforce.commands as sfdc

    sfdc.SubmitUserFeedback(messageDetail)


def ReparseRoomFeedback(messageDetail):

    streamId = messageDetail.StreamId

    if len(messageDetail.Command.UnnamedParams) > 0:
        timeStr = ''.join(messageDetail.Command.UnnamedParams)

        offsetSeconds = utdt.ConvertShorthandToSeconds(timeStr)

        if offsetSeconds <= 0:
            offsetSeconds = 15*60
    else:
        # Default to 15 mins if no valid time string is provided
        offsetSeconds = 15*60

    dtReparse = datetime.datetime.now() + datetime.timedelta(seconds=-1*offsetSeconds)

    messageList = symreader.GetSymphonyMessagesSinceDateTime(streamId, dtReparse)

    from modules.plugins.Salesforce.commands import SubmitUserFeedbackCollection

    SubmitUserFeedbackCollection(messageList)
    

def RemoteShutdown(messageDetail):
    if messageDetail.Command.UnnamedParams and len(messageDetail.Command.UnnamedParams):
        pwd = messageDetail.Command.UnnamedParams[0]

        pwdHash = '14811b20d51133c29fd0f19e3f7d7ef3b48ccae559e3c22b65542ba144c1750f'

        if crypto.CompareHashDigest(pwd, pwdHash):
            messageDetail.ReplyToSender("Shutting down Ares now.")
            botlog.LogSystemInfo("Shutdown command received from " + messageDetail.Sender.Email)
            exit(0)
        else:
            messageDetail.ReplyToSender("Incorrect password, baka.")
    else:
        messageDetail.ReplyToSender("You must specify a password.")


def SendStatusCheck(messageDetail):
    import random

    replies = ["I'm up! I'm up!", "Five by Five.", "Ready to serve.", "Where do you want to go today?", "Listening...",
               "<a href='https://www.youtube.com/watch?v=hUw13iIrKN0&amp;t=10s'/>", "Who's asking?",
               "Can I <i>help</i> you?", "Who disturbs my slumber?!", "Eat your heart out, Siri.",
               "I hear Alexa was written in... <i>QBasic</i>",
               "I didn't really care for the new <i>Wonder Woman</i> movie.", "More work?", "Ready for action.",
               "The flows of magic are whimsical today."]

    randReply = True

    if len(messageDetail.Command.UnnamedParams) > 0:
        index = messageDetail.Command.UnnamedParams[0]

        if index.isnumeric():
            indexNum = int(index)

            if indexNum < len(replies):
                messageDetail.ReplyToChat(replies[indexNum])
                randReply = False

    if randReply:
        messageDetail.ReplyToChat(random.choice(replies))

