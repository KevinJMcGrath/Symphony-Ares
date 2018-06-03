import re

from modules.symphony.messagedetail import MessageDetail


def ParseQuerk(messageDetail: MessageDetail):
    msg_text = messageDetail.Command.MessageFlattened

    # replace multiple whitespace with a single whitespace
    regexStr = "\s\s+"
    msg_text = re.sub(regexStr, ' ', msg_text).strip()

    msg_text_nospace = msg_text.replace(' ', '')
    msg_text_dash = msg_text.replace(' ', '-')
    msg_text_underscore = msg_text.replace(' ', '_')
