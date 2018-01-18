import modules.botconfig as config
import modules.symphony.callout as callout


def IsValidSendingUser(emailAddress):
    return emailAddress not in config.Blacklist


def GetBotUserId():
    botEmail = config.BotEmailAddress

    return GetSymphonyUserId(botEmail)


def GetSymphonyUserId(emailAddress):
    userEP = config.SymphonyBaseURL + '/pod/v1/user?email=' + emailAddress

    response = callout.SymphonyGET(userEP)

    return response.ResponseData.id


def GetSymphonyUserDetail(userId):
    userQueryEP = config.SymphonyBaseURL + '/pod/v2/user?uid=' + str(userId) + '&local=true'

    response = callout.SymphonyGET(userQueryEP)

    if response.Success:
        userObj = response.ResponseData

        return SymphonyUser(user=userObj)
    else:
        return SymphonyUser(user=None)


class SymphonyUser:
    def __init__(self, user=None):  # userId: str, fname: str, lname: str, email: str, company: str):
        if user is None:
            self.Id = '-1'
            self.FirstName = 'Susan'
            self.LastName = 'Waters-Nobody'
            self.Email = 'swn@symphony.com'
            self.Name = 'Susan Walters-Nobody'
            self.IsValidSender = False
        else:
            self.Id = str(user.id)  # userId
            self.FirstName = user.firstName if hasattr(user, 'firstName') else 'Unknown'  # fname
            self.LastName = user.lastName if hasattr(user, 'lastName') else 'Unknown'  # lname
            self.Email = user.emailAddress  # email
            self.Name = user.displayName  # fname + ' ' + lname
            self.Company = user.company  # company
            self.IsValidSender = IsValidSendingUser(self.Email)
