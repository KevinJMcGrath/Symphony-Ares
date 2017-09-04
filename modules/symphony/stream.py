import modules.botconfig as config
import modules.symphony.callout as agent


def GetStreamInfo(streamId):
    chatRoom = SymphonyChatRoom(streamId)

    streamEP = config.SymphonyBaseURL + '/pod/v1/streams/' + streamId + '/info'

    symresponse = agent.SymphonyGET(streamEP)

    if symresponse.Success:
        chatRoom.Active = symresponse.ResponseData.active
        chatRoom.CrossPod = symresponse.ResponseData.crossPod
        chatRoom.Type = symresponse.ResponseData.streamType.type

        if chatRoom.Type == 'ROOM':
            chatRoom.Name = symresponse.ResponseData.roomAttributes.name
        else:
            chatRoom.Name = 'Non-room'

    return chatRoom


class SymphonyChatRoom:
    def __init__(self, streamId: str):
        self.StreamId = streamId
        self.Name = ''
        self.Type = ''
        self.CrossPod = False
        self.Active = True
