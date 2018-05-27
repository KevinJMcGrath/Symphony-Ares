import modules.plugins.Salesforce.utility as util

import modules.botlog as log


def SFDCVersion(messageDetail):
    ep = util.sfdcBaseURL + '/services/data/'

    response = util.SFDC_REST('GET', ep, {})
    ver = response.JSON[0]['label']
    messageDetail.ReplyToSender(ver)


def AccountSearch(messageDetail):
    ep = util.sfdcBaseURL + '/services/data/'
    pass


def SubmitUserFeedback(messageDetail):
    response = SubmitSFDCFeedbackRequest(messageDetail)

    if response.IsSuccess:
        msg = "User feedback submitted successfully"
    else:
        msg = "Failed to send feedback. Contact Biz Ops"

    messageDetail.ReplyToSender(msg)


def SubmitUserFeedbackCollection(messageDetailList):
    from modules.symphony.tokenizer import CommandTypes

    submitCount = 0
    successCount = 0
    if len(messageDetailList) > 0:
        for messageDetail in messageDetailList:
            if messageDetail.IsValid and messageDetail.Sender.IsValidSender:
                if messageDetail.Command.IsCommand and messageDetail.Command.CommandType == CommandTypes.Hash:

                    submitCount += 1
                    response = SubmitSFDCFeedbackRequest(messageDetail)

                    if response.IsSuccess:
                        successCount += 1
                    else:
                        log.LogSystemError('Failed to send SFDC message: ' + messageDetail.MessageRaw)

    if submitCount > 0:
        messageDetailList[0].ReplyToChat('Resubmitted ' + str(submitCount) + ' messages; '
                                         + str(successCount) + ' succeeded.')
    else:
        messageDetailList[0].ReplyToChat('No feedback-messages were found.')


def SubmitSFDCFeedbackRequest(messageDetail):
    ep = util.sfdcBaseURL + '/services/apexrest/symphony/feedback'

    # etree.findall()
    hashtags = messageDetail.Command.MessageXML.findall('.//hash')

    clients = []
    for ele in hashtags:
        if 'client' in ele.attrib['tag'] and ele.tail:
            clients = [x.strip() for x in ele.tail.split(',')]

    sfdcBody = {
        "messageid": messageDetail.MessageId,
        "streamid": messageDetail.StreamId,
        "submitteremail": messageDetail.Sender.Email,
        "hashtags": messageDetail.Command.Hashtags,
        "mentionedusers": messageDetail.Command.Mentions,
        "summary": messageDetail.Command.MessageFlattened[:50].replace('"', '\''),
        "comments": messageDetail.Command.MessageFlattened.replace(r'\"', '\'').replace('"', '\''),
        "companylist": clients
    }

    if messageDetail.Attachments:
        sfdcBody['attachments'] = messageDetail.Attachments

    log.LogSymphonyInfo(messageDetail.MessageRaw)

    return util.SFDC_REST('POST', ep, sfdcBody)




