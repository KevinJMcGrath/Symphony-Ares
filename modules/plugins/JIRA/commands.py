import modules.plugins.JIRA.utility as util
import modules.botlog as log


def CreateBizOpsJIRAIssue(messageDetail):

    reporter = util.FindJIRAUserByEmail(messageDetail.Sender.Email)

    # replaced .Command.MessageText with .Command.MessageFlattened - 1/16/2018
    summary = messageDetail.Command.MessageFlattened.strip()[:50]
    desc = messageDetail.Command.MessageFlattened + \
        '\n\nThis issue was submitted by Ares; may we never know the tip of his sword ' \
        'or the heel of his boot.'

    desc = desc.replace('/bizops', '').strip()
    summary = summary.replace('/bizops', '').replace(r'\n', '').strip()

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

