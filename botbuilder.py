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

        self.SessionExpirationDate = datetime.date.today() - datetime.timedelta(days=1)
        self.RESTHeaders = {}

    def IsValidSession(self):
        return self.IsAuthenticated and self.IsDatafeedConnected and self.SessionExpirationDate >= datetime.date.today()

    def InvalidateSession(self):
        self.IsAuthenticated = False
        self.IsDatafeedConnected = False
        self.SessionToken = ''
        self.KeyAuthToken = ''
        self.DataFeedId = ''

    def Authenticate(self):

        botlog.LogConsoleInfo('Authenticating...')
        self.SessionToken = callout.GetSessionToken()

        if self.SessionToken != '':
            botlog.LogConsoleInfo('Success! Session token obtained.')

            self.KeyAuthToken = callout.GetKeyManagerToken()

            if self.KeyAuthToken != '':
                botlog.LogConsoleInfo('Success! Key Manager token obtained.')

                self.SessionExpirationDate = datetime.date.today() + datetime.timedelta(days=7)
                self.RESTHeaders = {"sessionToken": self.SessionToken, "keyManagerToken": self.KeyAuthToken,
                                    "Content-Type": "application/json"}

                # Attempting to use requests.Session
                callout.agentSession.headers.update(self.RESTHeaders)

                botlog.LogConsoleInfo('Session expires on ' + str(self.SessionExpirationDate))

                self.IsAuthenticated = True
            else:
                botlog.LogSystemError("Failed to obtain KM Token")
        else:
            botlog.LogSystemError("Failed to obtain Session Token")

    def ConnectDatafeed(self):
        self.BotUserId = user.GetBotUserId()
        botlog.LogConsoleInfo('Bot User Id: ' + str(self.BotUserId))

        botlog.LogConsoleInfo('Creating Datafeed...')
        self.DataFeedId = datafeed.CreateDataFeed()

        if self.DataFeedId != '':
            botlog.LogConsoleInfo('Datafeed Connected! Id: ' + self.DataFeedId)
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
        for index in range(0, 5):
            self.ConnectDatafeed()

            if self.IsDatafeedConnected:
                return
            else:
                botlog.LogSymphonyError('Datafeed Connect attmpt ' +  str(index) + 'failed. Trying again in 5 seconds.')
                time.sleep(5)

        botlog.LogSymphonyError('Maximum datafeed connection attempts reached. Halting bot.')
        exit(1)