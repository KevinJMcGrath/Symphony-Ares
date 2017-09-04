import codecs
import json
import os
import requests
import traceback
import unicodedata

import modules.plugins.JIRA.logging as log

_configPath = os.path.abspath('modules/plugins/JIRA/config.json')

with codecs.open(_configPath, 'r', 'utf-8-sig') as json_file:
    _config = json.load(json_file)

jiraAPIendpoint = _config['jiraHost'] + "/rest/api/2"
jiraIssueURL = _config['jiraHost'] + "/browse/"

jiraUsername = _config['jiraUsername']
jiraPassword = _config['jiraPassword']

ValidSubmissionProjectKeys = _config['validProjects']
UnnamedParameterOrder = _config['paramOrder']

jiraSession = requests.Session()
jiraSession.auth = (jiraUsername, jiraPassword)
jiraSession.headers.update({"Content-Type": "application/json"})

# TODO: Figure out how to obfuscate user/pass
# TODO: Load createmeta for each JIRA type to determine required fields


def FindJIRAUserByEmail(emailAddress):
    ep = jiraAPIendpoint + '/user/search?username=' + emailAddress + '&includeActive=true'
    response = JIRA_REST('GET', ep, None)

    return response.JSON[0]['key'] if response.IsSuccess else 'kevin.mcgrath'


def CreateIssue(jiraIssue):
    log.LogJIRAMessage('Sending JIRA Issue JSON: ' + json.dumps(jiraIssue))

    ep = jiraAPIendpoint + '/issue/bulk'
    return JIRA_REST('POST', ep, jiraIssue)


def JIRA_REST(method, endpoint, body):
    errorStr = ''
    response = None

    try:
        if method == 'GET':
            response = jiraSession.get(endpoint)
        elif method == 'POST':
            response = jiraSession.post(endpoint, json=body)
        else:
            raise MethodNotImplementedException(method + ' is not yet implemented.')

        if response.status_code // 100 != 2:
            response.raise_for_status()

    except requests.exceptions.HTTPError as httpex:
        errorStr = "JIRA REST Exception (http): " + str(httpex)
        stackTrace = 'Stack Trace: ' + ''.join(traceback.format_stack())
        log.LogJIRAError(errorStr)
        log.LogJIRAError(stackTrace)

    except requests.exceptions.RequestException as connex:
        errorStr = "JIRA REST Exception (connection): " + str(connex)
        stackTrace = 'Stack Trace: ' + ''.join(traceback.format_stack())
        log.LogJIRAError(errorStr)
        log.LogJIRAError(stackTrace)

    except Exception as ex:
        errorStr = "JIRA REST Exception (system): " + str(ex)
        stackTrace = 'Stack Trace: ' + ''.join(traceback.format_stack())
        log.LogJIRAError(errorStr)
        log.LogJIRAError(stackTrace)

    resp = JIRAResponse(response)
    resp.Error = errorStr

    return resp


def GetRequiredFields(projectKey):
    ep = jiraAPIendpoint + "/issue/createmeta?projectKeys=" + projectKey + \
         "&expand=projects.issuetypes.fields"

    response = jiraSession.get(ep).json()

    project = response[0]
    issueTypes = project['issueTypes']

    reqFields = {}

    for iType in issueTypes:
        name = iType['name']
        fieldKeys = iType['fields'].keys()

        reqNames = []
        for fname in fieldKeys:
            if iType['fields'][fname]['required']:
                reqNames.append(fname)

        reqFields[name] = reqNames

    return reqFields


def EscapeText(inputStr: str):
    inputStr = inputStr.replace("\n", "_br_").replace("<br/>", "_br_")

    inputStr = "".join(ch for ch in inputStr if unicodedata.category(ch)[0] != "C")

    return inputStr.replace("_br_", "\n")


class MethodNotImplementedException(Exception):
    pass


class JIRAResponse:
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

