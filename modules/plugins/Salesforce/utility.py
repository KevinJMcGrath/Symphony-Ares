import codecs
import json
import os
import requests
import traceback
import unicodedata

import modules.plugins.Salesforce.logging as log
import modules.botlog as botlog

_configPath = os.path.abspath('modules/plugins/Salesforce/config.json')

with codecs.open(_configPath, 'r', 'utf-8-sig') as json_file:
    _config = json.load(json_file)

sfdcBaseURL = _config['sfdcHost']
sfdcUsername = _config['sfdcUsername']
sfdcPassword = _config['sfdcPassword'] + _config['sfdcUserAuthToken']
sfdcClientId = _config['client_id']
sfdcClientSecret = _config['client_secret']

sfdcSession = None
SFDCReady = False


def AuthenticateSalesforce():
    global sfdcSession
    global SFDCReady

    sfdcSession = requests.Session()

    authEp = sfdcBaseURL + '/services/oauth2/token'
    authReq = {"grant_type": "password", "client_id": sfdcClientId, "client_secret": sfdcClientSecret,
               "username": sfdcUsername, "password": sfdcPassword}

    # This is required. For some reason, if you don't tell them what you're sending, it FREAKS OUT
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = sfdcSession.post(authEp, data=authReq, headers=headers)

    if response.status_code // 100 == 2:
        sfdcSession.headers.update({"Authorization": "Bearer " + response.json()['access_token'],
                                    "Content-Type": "application/json"})
        SFDCReady = True
    else:
        SFDCReady = False
        response.raise_for_status()


def SFDC_REST(method, endpoint, body):
    errorStr = ''
    response = None

    try:
        # if sfdcSession is None:
        # I don't want to authenticate every time, but it seems to be failingtoo much
        AuthenticateSalesforce()

        if SFDCReady:
            if method == 'GET':
                response = sfdcSession.get(endpoint)
            elif method == 'POST' or method == 'AUTH':
                response = sfdcSession.post(endpoint, json=body)
            else:
                raise MethodNotImplementedException(method + ' is not yet implemented.')

            if response.status_code // 100 == 2:
                pass
            # HTTP 401 - session Id or OAuth token has expired or is invalid
            elif response.status_code == 401:
                AuthenticateSalesforce()
                SFDC_REST(method, endpoint, body)
            else:
                response.raise_for_status()

        else:
            errorStr = 'Salesforce is not responding correctly at this time. Contact BizOps'

    except requests.exceptions.HTTPError as httpex:
        errorStr = "SFDC REST Exception (http): " + str(httpex)
        stackTrace = 'Stack Trace: ' + ''.join(traceback.format_stack())
        log.LogSFDCError(errorStr)
        log.LogSFDCError(stackTrace)

    except requests.exceptions.RequestException as connex:
        errorStr = "SFDC REST Exception (connection): " + str(connex) + ' Code: '
        errorStr += str(response.status_code) if response and response.status_code else 'Unknown'
        stackTrace = 'Stack Trace: ' + ''.join(traceback.format_stack())
        log.LogSFDCError(errorStr)
        log.LogSFDCError(stackTrace)

    except Exception as ex:
        errorStr = "SFDC REST Exception (system): " + str(ex)
        stackTrace = 'Stack Trace: ' + ''.join(traceback.format_stack())
        log.LogSFDCError(errorStr)
        log.LogSFDCError(stackTrace)

    resp = SFDCResponse(response)
    resp.Error = errorStr

    return resp


def EscapeText(inputStr: str):
    inputStr = inputStr.replace("\n", "_br_").replace("<br/>", "_br_")

    inputStr = "".join(ch for ch in inputStr if unicodedata.category(ch)[0] != "C")

    return inputStr.replace("_br_", "\n")


class MethodNotImplementedException(Exception):
    pass


class SFDCResponse:
    def __init__(self, response):
        self.IsSuccess = False
        self.StatusCode = 0
        self.JSON = None
        self.Raw = None
        self.Error = 'Response was empty!'

        if response is not None:
            self.ParseRespose(response)

    def ParseRespose(self, response):
        self.IsSuccess = response.status_code // 100 == 2
        self.StatusCode = response.status_code
        self.JSON = response.json()
        self.Raw = response.text
