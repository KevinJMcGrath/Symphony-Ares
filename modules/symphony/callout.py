import json
import requests
from requests_toolbelt import MultipartEncoder
import traceback
import types

import modules.botconfig as config
import modules.botlog as botlog

agentSession = requests.Session()
agentSession.cert = config.BotCertificate

agentV2Session = requests.Session()
agentV2Session.cert = config.BotCertificate


def GetSessionToken():
    botlog.LogConsoleInfo(config.SessionAuthEP)
    return GetSymphonyAuthToken(config.SessionAuthEP)


def GetKeyManagerToken():
    return GetSymphonyAuthToken(config.KeyManagerEP)


def GetSymphonyAuthToken(authEndpoint):
    response = SymphonyREST('AUTH', authEndpoint, None)
    return response.ResponseData.token


def BuildHeaders(sessionToken, keyAuthToken, contentType="application/json"):
    RESTheaders = {
        "sessionToken": sessionToken,
        "keyManagerToken": keyAuthToken,
        "Content-Type": contentType,
        "User-Agent": "AresBot (Kevin McGrath - BizOps - kevin.mcgrath@symphony.com)"
    }

    return RESTheaders


def SymphonyReAuth():
    global agentSession

    sessionToken = GetSessionToken()
    keyAuthToken = GetKeyManagerToken()

    # RESTHeaders = {"sessionToken": sessionToken, "keyManagerToken": keyAuthToken,
    #                "Content-Type": "application/json"}

    RESTHeaders = BuildHeaders(sessionToken, keyAuthToken)

    # Attempting to use requests.Session
    agentSession.headers.update(RESTHeaders)


def SymphonyGET(endpoint):
    return SymphonyREST('GET', endpoint, None)


def SymphonyPOST(endpoint, body):
    return SymphonyREST('POST', endpoint, body)


def SymphonyPOSTV2(endpoint, body):
    return SymphonyREST('POSTV2', endpoint, body)


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
        elif method == 'POSTV2':
            response = PostV2(endpoint, body)
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
        botlog.LogConsoleInfo("Response Code: " + str(response.status_code))
        botlog.LogConsoleInfo("Response Message: " + response.text)
        retVal.ErrorMessage = errorStr
        stackTrace = 'Stack Trace: ' + ''.join(traceback.format_stack())
        botlog.LogSymphonyError(errorStr)
        botlog.LogSymphonyError(stackTrace)

    except requests.exceptions.RequestException as connex:
        errorStr = "Symphony REST Exception (connection - Status Code " + str(response.status_code) + \
                   "): " + str(connex)
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


def PostV2(endpoint, body):
    encoder = MultipartEncoder(fields=body)

    v2SessionToken = GetSessionToken()
    v2KeyAuthToken = GetKeyManagerToken()

    # v2Headers = {"sessionToken": v2SessionToken, "keyManagerToken": v2KeyAuthToken,
    #              "Content-Type": encoder.content_type}

    v2Headers = BuildHeaders(v2SessionToken, v2KeyAuthToken, encoder.content_type)

    agentV2Session.headers.update(v2Headers)

    return agentV2Session.post(endpoint, data=encoder)


# Does not work
# I believe the problem is the Content-Type header, which does not include the boundary
# statement. If I am prepared to build the boundary myself, I might be able to get this
# to work without the requests_toolbelt package
def PostV2_1(endpoint, body):
    import io
    ph = io.StringIO("")

    tempSession = requests.Session()
    tempSession.cert = config.BotCertificate

    tempSessionToken = GetSessionToken()
    tempKeyAuthToken = GetKeyManagerToken()

    tempHeaders = {"sessionToken": tempSessionToken, "keyManagerToken": tempKeyAuthToken,
                   "Content-Type": "multipart/form-data"}

    tempSession.headers.update(tempHeaders)

    return tempSession.post(endpoint, data=body, files=ph)


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
