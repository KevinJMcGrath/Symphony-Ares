from typing import List

import modules.symphony.messaging as msg
import modules.symphony.tokenizer as tokenizer

import modules.botlog as log


class ResponseType:
    IM, MIM, ROOM = range(3)


class MessageDetail:
    def __init__(self, respItem):
        self.MessageId = msg.FormatSymphonyId(respItem.id) if hasattr(respItem, 'id') else '-1'
        # I REALLY don't like the idea of EAFP. Sometimes it's just better to check things first
        # instead of just throwing an exception like a big 'ol tantrum.
        self.FromUserId = str(respItem.fromUserId) if hasattr(respItem, 'fromUserId') else '-1'
        self.StreamId = msg.FormatSymphonyId(respItem.streamId) if hasattr(respItem, 'streamId') else '-1'
        # Some of the message types (like room additions) have no message
        self.MessageRaw = respItem.message if hasattr(respItem, 'message') else None
        self.Type = respItem.v2messageType if hasattr(respItem, 'v2messageType') else ''

        self.Attachments = self.ParseAttachments(respItem)
        # respItem.attachments if hasattr(respItem, 'attachments') else []

        self.IsValid = self.Type == 'V2Message'
        self.Sender = None
        self.ChatRoom = None
        self.Command = None

        if len(self.Attachments) > 0:
            log.LogConsoleInfo(respItem)

    def ParseAttachments(self, respItem):
        attachList = []

        if hasattr(respItem, 'attachments'):
            for att in respItem.attachments:
                attJ = {"id": att.id, "name": att.name, "size": att.size}
                attachList.append(attJ)

        return attachList

    def InitiateCommandParsing(self):
        if self.MessageRaw is not None:
            if self.MessageRaw.startswith('<message'):
                self.Command = tokenizer.CommandParser(self.MessageRaw, True)
            else:
                log.LogSymphonyError('Invalid MessageML: ' + self.MessageRaw)

    def GetConsoleLogLine(self):
        # Python's ternary conditional is a stupid order just to be diffrent
        lineout = 'User: ' + self.Sender.Name if self.Sender is not None else 'Unknown'
        lineout += ' (' + self.FromUserId + ') - '

        if self.ChatRoom is not None:
            lineout += '<' + self.ChatRoom.Type + '> ' + self.ChatRoom.Name + ' (' + self.ChatRoom.StreamId + ')'
        else:
            lineout += '<Unknown Room> (' + self.StreamId + ')'

        return lineout

    def ReplyToChat(self, message: str):
        msg.SendSymphonyMessage(self.StreamId, message)

    def ReplyToSender(self, message: str):
        msg.SendUserIM([self.FromUserId], message)

    def NewIM(self, message: str, users: List[int]):
        msg.SendUserIM(users, message)

    def NewChat(self, message: str, streamId):
        msg.SendSymphonyMessage(streamId, message)
