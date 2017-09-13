import json
import requests
import traceback
import types

import modules.botconfig as config
import modules.botlog as botlog


agentSession = requests.Session()
agentSession.cert = config.BotCertificate


def GetSessionToken():
    return GetSymphonyAuthToken(config.SessionAuthEP)


def GetKeyManagerToken():
    return GetSymphonyAuthToken(config.KeyManagerEP)


def GetSymphonyAuthToken(authEndpoint):
    response = SymphonyREST('AUTH', authEndpoint, None)
    return response.ResponseData.token


def SymphonyReAuth():
    global agentSession

    sessionToken = GetSessionToken()
    keyAuthToken = GetKeyManagerToken()

    RESTHeaders = {"sessionToken": sessionToken, "keyManagerToken": keyAuthToken,
                   "Content-Type": "application/json"}

    # Attempting to use requests.Session
    agentSession.headers.update(RESTHeaders)


def SymphonyGET(endpoint):
    return SymphonyREST('GET', endpoint, None)


def SymphonyPOST(endpoint, body):
    return SymphonyREST('POST', endpoint, body)


def SymphonyREST(method, endpoint, body):
    retVal = SymphonyAgentResponse()

    # Allowing for reauth from the async process
    if method != 'AUTH' and 'sessionToken' not in agentSession.headers:
        SymphonyReAuth()

    try:
        if method == 'GET':
            response = agentSession.get(endpoint)
        elif method == 'POST':
            response = agentSession.post(endpoint, data=body)
        elif method == 'AUTH':
            response = agentSession.post(endpoint)
        else:
            raise MethodNotImplementedException(method + ' is not yet implemented.')

        retVal.ResponseText = response.text
        retVal.ResponseCode = response.status_code

        if response.status_code == 200:
            retVal.Success = True
            retVal.ParseResponseJSON()
        elif response.status_code // 100 == 2:  # Any other 200 code, not success but don't throw exception
            retVal.Success = True
        else:
            response.raise_for_status()

    except requests.exceptions.HTTPError as httpex:
        errorStr = "Symphony REST Exception (http): " + str(httpex)
        retVal.ErrorMessage = errorStr
        stackTrace = 'Stack Trace: ' + ''.join(traceback.format_stack())
        botlog.LogSymphonyError(errorStr)
        botlog.LogSymphonyError(stackTrace)

    except requests.exceptions.RequestException as connex:
        errorStr = "Symphony REST Exception (connection): " + str(connex)
        retVal.ErrorMessage = errorStr
        stackTrace = 'Stack Trace: ' + ''.join(traceback.format_stack())
        botlog.LogSymphonyError(errorStr)
        botlog.LogSymphonyError(stackTrace)

    except Exception as ex:
        errorStr = "Symphony REST Exception (system): " + str(ex)
        retVal.ErrorMessage = errorStr
        stackTrace = 'Stack Trace: ' + ''.join(traceback.format_stack())
        botlog.LogSystemError(errorStr)
        botlog.LogSystemError(stackTrace)

    finally:
        return retVal


class SymphonyAgentResponse:
    def __init__(self):
        self.Success = False
        self.ResponseText = ''
        self.ResponseCode = 0
        self.ErrorMessage = ''
        self.ResponseData = {}

    def ParseResponseJSON(self):
        self.ResponseData = json.loads(self.ResponseText, object_hook=lambda d: types.SimpleNamespace(**d))


class JSONData:
    def __init__(self, jsonStr):
        self.__dict__ = json.loads(jsonStr)


class MethodNotImplementedException(Exception):
    pass
