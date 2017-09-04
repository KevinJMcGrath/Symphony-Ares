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
        self._reauthIndex = 0
        self._reauthMax = 3
        self._errIndex = 0
        self._errMax = 5

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
        self._errIndex = 0
        self._reauthIndex = 0

    def Authenticate(self):

        botlog.LogConsoleInfo('Authenticating...')

        while not self.IsAuthenticated:

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
                    self._reauthIndex = 0

            if not self.IsAuthenticated:
                if self._reauthIndex < self._reauthMax:
                    self._reauthIndex += 1
                    botlog.LogSymphonyError('Authentication failed. Attempting re-authentication in 5s (' +
                                            str(self._reauthIndex) + ' of ' + str(self._reauthMax) + ')')
                    time.sleep(5)
                else:
                    botlog.LogSymphonyError('Authentication failed after max retries. Halting bot.')
                    exit(1)

    def ConnectDatafeed(self):

        while not self.IsDatafeedConnected:
            self.BotUserId = user.GetBotUserId()
            botlog.LogConsoleInfo('Bot User Id: ' + str(self.BotUserId))

            botlog.LogConsoleInfo('Creating Datafeed...')
            self.DataFeedId = datafeed.CreateDataFeed()

            if self.DataFeedId != '':
                botlog.LogConsoleInfo('Datafeed Connected! Id: ' + self.DataFeedId)
                self.IsDatafeedConnected = True
                self._errIndex = 0
            elif self._errIndex < self._errMax:
                self._errIndex += 1
                botlog.LogSymphonyError('Unable to connect to Datafeed. retrying in 5s (' +
                                        str(self._errIndex) + ' of ' + str(self._errMax) + ')')
                time.sleep(5)
            else:
                botlog.LogSymphonyError('Failed to connecto to Datafeed. Invalidating session.')
                self.InvalidateSession()

    def StartBot(self):

        self.Authenticate()
        self.ConnectDatafeed()


