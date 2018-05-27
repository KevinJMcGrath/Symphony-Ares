import re
import traceback

import modules.plugins.JIRA.utility as util
import modules.plugins.JIRA.feedback.matching as fbmatch
import modules.symphony.user as user
import modules.botlog as log


def SubmitFeedbackJIRAv2(messageDetail):
    try:
        issueFieldsDict = {}
        watcherList = []
        labelSet = set(messageDetail.Command.Hashtags)

        reporter_field = {
            "name": util.FindJIRAUserByEmailV2(messageDetail.Sender.Email)
        }

        issueFieldsDict['reporter'] = reporter_field

        project = 'SFDC'
        type_name = 'Unknown'
        bodyDetail: str = messageDetail.Command.MessageFlattened

        # Conduct Epic Search
        epic_item = fbmatch.MatchEpic(bodyDetail)

        if epic_item is not None:
            issueFieldsDict['assignee'] = {"name": epic_item['assignTo']}

            if epic_item['epic'] != "":
                issueFieldsDict['customfield_10200'] = epic_item['epic']

            # Union (|=) the epic specific labels with the hashtag labels
            labelSet |= set(epic_item['labels'])
        else:
            log.LogConsoleInfo('No epic match was returned!')

        # convert label set to list for JSON serialization
        issueFieldsDict['labels'] = list(labelSet)

        # Determine what type the feedback is
        type_dict = {
            "bug": "Bug",
            'bugs': 'Bug',
            'defect': 'Bug',
            'defects': 'Bug',
            'problem': 'Bug',
            'problems': 'Bug',
            'feature': 'New Feature',
            'features': 'New Feature',
            'featurerequest': 'New Feature',
            'missing': 'New Feature',
            'needed': 'New Feature',
            'required': 'New Feature',
            'newfeature': 'New Feature',
            'newfeaturerequest': 'New Feature',
            'usability': 'Usability Issue',
            'useability': 'Usability Issue',
            'performance': 'Usability Issue',
            'unstable': 'Usability Issue',
            'awkward': 'Usability Issue'
        }

        for tag in messageDetail.Command.Hashtags:
            if tag.lower() in type_dict:
                type_name = type_dict[tag.lower()]
                break

        # Regex to identify hash tags.
        regexHashtags = r"(\#[a-zA-Z]+\b)"
        summary = re.sub(regexHashtags, '', messageDetail.Command.MessageFlattened)

        # Regex to replace extra spaces with single space
        regexSpace = "\s\s+"
        summary = re.sub(regexSpace, ' ', summary)[:100]

        if messageDetail.Command.CommandRaw is not None:
            summary = summary.replace(messageDetail.Command.CommandRaw, '')
            summary = summary.strip()

        # Build dict of UID/Users
        for uid in messageDetail.Command.Mentions:
            try:
                userStr = '_u_' + uid
                userObj = user.GetSymphonyUserDetail(uid)

                if userObj.Id != '-1':
                    bodyReplace = userObj.FullName + '(' + userObj.Email + ')'
                    bodyDetail = bodyDetail.replace(userStr, bodyReplace)

                    # no need to include the mentioned users in the Summary
                    summary = summary.replace(userStr, '')

                    jiraUser = util.FindJIRAUserByEmailV2(userObj.Email)

                    if jiraUser is not None:
                        watcherList.append(jiraUser)

            except Exception as ex:
                log.LogSystemError(str(ex))

        nosubmit = False
        debug = False
        for tag in messageDetail.Command.Hashtags:
            if tag.lower() == 'nosubmit':
                nosubmit = True
            elif tag.lower() == 'debug':
                debug = True

        if not nosubmit:
            new_issue = util.CreateIssueV2(projectKey=project, summary=summary, desc=bodyDetail,
                                           issueTypeName=type_name, jiraFields=issueFieldsDict)

            # add watchers
            util.AddWatchersV2(new_issue, watcherList)

            msg = 'JIRA created successfully.<br/>Key: ' + new_issue.key + "<br/>JIRA Link: <a href='" + \
                  new_issue.permalink() + "'/>"

            messageDetail.ReplyToSenderv2(msg)
        else:
            msg = 'Feedback received but #nosubmit was included. Issue not sent to JIRA.'
            messageDetail.ReplyToSenderv2(msg)

        if debug:
            issueFieldsDict['project'] = project
            issueFieldsDict['summary'] = summary
            issueFieldsDict['description'] = bodyDetail
            issueFieldsDict['issueType'] = type_name

            from modules.symphony.messaging import FormatDicttoMML2 as json_format
            json_str = json_format(issueFieldsDict)

            messageDetail.ReplyToSenderv2(json_str)

    except Exception as ex:
        errStr = 'Unable to submit JIRA. Error: ' + str(ex)
        messageDetail.ReplyToSenderv2(errStr)
        stackTrace = 'Stack Trace: ' + ''.join(traceback.format_exc())
        log.LogSymphonyError(errStr)
        log.LogSymphonyError(stackTrace)


def CreateBizOpsJIRAIssueV2(messageDetail):
    reporter = util.FindJIRAUserByEmail(messageDetail.Sender.Email)

    # jiraDict = {}

    # jiraDict['summary'] = messageDetail.Command.MessageFlattened.strip()
    # jiraDict


def CreateBizOpsJIRAIssue(messageDetail):

    reporter = util.FindJIRAUserByEmail(messageDetail.Sender.Email)

    # replaced .Command.MessageText with .Command.MessageFlattened - 1/16/2018
    summary = messageDetail.Command.MessageFlattened.strip()[:50]
    desc = messageDetail.Command.MessageFlattened + \
        '\n\nThis issue was submitted by Ares; may we never know the tip of his sword ' \
        'or the heel of his boot.'

    desc = desc.replace('/bizops', '').strip()
    summary = summary.replace('/bizops', '').replace(r'\n', '').replace('\n', '').strip()

    issue = {"project": "BIZOPS", "issuetype": "Task", "priority": "Minor",
             "summary": summary, "description": desc, "reporter": reporter}

    msg = CreateNewJIRA([], issue)

    messageDetail.ReplyToSender(msg)


def CreateNewJIRA(unnamedArgList, namedArgDict):

    jiraIssue = {}

    # Add all named parameters to the jiraIssue dictionary
    if namedArgDict is not None and len(namedArgDict) > 0:
        jiraIssue = namedArgDict

    # Cycle through all the parameters in the order list. Check to see
    # if they were filled in by kwargs. If we find one missing,
    # take each parameter from args and insert it to the jiraIssue dictionary
    if unnamedArgList is not None and len(unnamedArgList) > 0:
        for index in range(0, len(util.UnnamedParameterOrder)):
            paramName = util.UnnamedParameterOrder[index]

            if paramName not in jiraIssue and len(unnamedArgList) > 0:
                jiraIssue[paramName] = unnamedArgList[0]
                del unnamedArgList[0]

    # TODO: Need a lookup for Ids for certain fields
    # TODO: Lookup for jira ID by email

    # For any remaining values in args, join and add as summary or,
    # if summary was in kwargs, add as description
    remainder = util.EscapeText(" ".join(unnamedArgList))

    if 'summary' not in jiraIssue:
        jiraIssue['summary'] = remainder
    # else:
    #   jiraIssue['description'] = remainder

    jiraIssue['summary'] = 'Ares Submission: ' + jiraIssue['summary'] if 'summary' in jiraIssue else 'TBD'

    if 'project' not in jiraIssue or jiraIssue['project'] not in util.ValidSubmissionProjectKeys:
        return "Could not send JIRA Issue - missing or invalid project key"

    # TODO: Make jira object building generic based on schema. Might be overkill

    jiraForSubmit = {'issueUpdates': [{'update': {}, 'fields': {}}]}
    jiraForSubmit['issueUpdates'][0]['fields']['project'] = {"key": jiraIssue['project']}
    jiraForSubmit['issueUpdates'][0]['fields']['issuetype'] = {"name": jiraIssue['issuetype']}
    jiraForSubmit['issueUpdates'][0]['fields']['summary'] = jiraIssue['summary']

    if 'priority' in jiraIssue:
        jiraForSubmit['issueUpdates'][0]['fields']['priority'] = {"name": jiraIssue['priority']}

    if 'reporter' in jiraIssue:
        jiraForSubmit['issueUpdates'][0]['fields']['reporter'] = {"name": jiraIssue['reporter']}

    if 'description' in jiraIssue:
        jiraForSubmit['issueUpdates'][0]['fields']['description'] = jiraIssue['description']

    response = util.CreateIssue(jiraForSubmit)

    if response.IsSuccess:
        key = response.JSON['issues'][0]['key']

        return 'New Issue: <a href="' + util.jiraIssueURL + key + '"/>'
    else:
        return 'Unable to create JIRA issue. Error: ' + response.Error

