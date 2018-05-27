import datetime
import time

import modules.symphony.callout as callout
import modules.symphony.datafeed as datafeed
import modules.symphony.user as user
import modules.botlog as botlog


class SymSession:
    def __init__(self):
        self.IsAuthenticated = False
        self.IsDatafeedConnected = False
        self.SessionToken = ''
        self.KeyAuthToken = ''
        self.DataFeedId = ''
        self.BotUserId = ''
        self.DatafeedErrorCount = 0

        self.SessionExpirationDate = datetime.date.today() - datetime.timedelta(days=1)
        self.RESTHeaders = {}

    def IsValidSession(self):
        return self.IsAuthenticated and self.IsDatafeedConnected and self.SessionExpirationDate >= datetime.date.today()

    def InvalidateSession(self):
        self.IsAuthenticated = False
        self.SessionToken = ''
        self.KeyAuthToken = ''

        if self.DatafeedErrorCount >= 5:
            self.IsDatafeedConnected = False
            self.DataFeedId = ''
            self.DatafeedErrorCount = 0
        else:
            self.DatafeedErrorCount += 1

    def Authenticate(self):

        botlog.LogConsoleInfo('Authenticating...')
        self.SessionToken = callout.GetSessionToken()

        if self.SessionToken != '':
            botlog.LogSymphonyInfo('Success! Session token obtained.')

            self.KeyAuthToken = callout.GetKeyManagerToken()

            if self.KeyAuthToken != '':
                botlog.LogSymphonyInfo('Success! Key Manager token obtained.')

                self.SessionExpirationDate = datetime.date.today() + datetime.timedelta(days=7)
                # self.RESTHeaders = {"sessionToken": self.SessionToken, "keyManagerToken": self.KeyAuthToken,
                #                     "Content-Type": "application/json"}

                self.RESTHeaders = callout.BuildHeaders(self.SessionToken, self.KeyAuthToken)

                # Attempting to use requests.Session
                callout.agentSession.headers.update(self.RESTHeaders)

                botlog.LogSymphonyInfo('Session expires on ' + str(self.SessionExpirationDate))

                self.IsAuthenticated = True
            else:
                botlog.LogSystemError("Failed to obtain KM Token")
        else:
            botlog.LogSystemError("Failed to obtain Session Token")

    def ConnectDatafeed(self):
        self.BotUserId = user.GetBotUserId()
        botlog.LogSymphonyInfo('Bot User Id: ' + str(self.BotUserId))

        if self.DataFeedId == '':
            botlog.LogSymphonyInfo('Creating Datafeed...')
            self.DataFeedId = datafeed.CreateDataFeed()
        else:
            botlog.LogSymphonyInfo('Attempting to Reuse Existing Datafeed in 5 seconds...')
            for sleepIndex in range(0, 5):
                botlog.LogConsoleInfo(str(sleepIndex) + '...')
                time.sleep(1)

            botlog.LogSymphonyInfo('Reconnecting to Datafeed...')

        if self.DataFeedId != '':
            botlog.LogSymphonyInfo('Datafeed Connected! Id: ' + self.DataFeedId)
            self.IsDatafeedConnected = True
        else:
            botlog.LogSymphonyError('Failed to connect to Datafeed.')

    def StartBot(self):

        self.LimitedAuth()
        if self.IsAuthenticated:
            self.LimitedDatafeedConnect()

            if self.IsDatafeedConnected:
                return True

        return False

    def LimitedAuth(self):
        botlog.LogSymphonyInfo('Authenticating...')
        for index in range(0, 5):
            self.Authenticate()

            if self.IsAuthenticated:
                return
            else:
                botlog.LogSymphonyError('Authentication attmept ' + str(index) + 'failed. Trying again in 5 seconds.')
                time.sleep(5)

        botlog.LogSymphonyError('Maximum authentication attempts reached. Halting bot.')
        exit(1)

    def LimitedDatafeedConnect(self):
        botlog.LogSymphonyInfo('Connecting to the Datafeed...')
        for index in range(0, 5):
            self.ConnectDatafeed()

            if self.IsDatafeedConnected:
                return
            else:
                botlog.LogSymphonyError('Datafeed Connect attmpt ' + str(index) + 'failed. Trying again in 5 seconds.')
                time.sleep(5)

        botlog.LogSymphonyError('Maximum datafeed connection attempts reached. Halting bot.')
        exit(1)
