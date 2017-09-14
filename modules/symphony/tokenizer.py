import binascii
import re
from lxml import etree


class CommandParser:
    def __init__(self, messageRaw, parseCommand):
        self.IsCommand = False
        self.IsHelp = False
        self.CommandType = ''
        self.CommandRaw = ''
        self.CommandName = ''
        self.Hashtags = []
        self.Mentions = []
        self.UnnamedParams = []
        self.NamedParams = {}
        self.MessageXML = None
        self.MessageText = ''
        self.MessageFlattened = ''

        if parseCommand:
            self.MessageXML = etree.fromstring(messageRaw)
            self.MessageFlattened = ConvertAllText(self.MessageXML)

            self.GetCommand()

            if self.IsCommand:
                if self.CommandType == CommandTypes.Slash:
                    self.ParseSlashCommandParameters()
                elif self.CommandType == CommandTypes.Hash:
                    pass

    def GetCommand(self):
        # Get the first token and determine if it's a slash command
        if self.MessageXML is not None and self.MessageXML.text:
            self.CommandRaw = self.MessageXML.text.split()[0]

        if self.CommandRaw and self.CommandRaw.startswith('/'):
            self.CommandName = self.CommandRaw.replace('/', '')
            self.IsCommand = True
            self.CommandType = CommandTypes.Slash
            self.MessageText = self.MessageXML.text.replace(self.CommandRaw, '')

        else:
            for node in self.MessageXML:
                if node.tag == 'hash':
                    self.Hashtags.append(node.attrib['tag'])  # get the name of the hashtag for processing
                elif node.tag == 'mention':
                    self.Mentions.append(node.attrib['uid'])

            if len(self.Hashtags) > 0:
                self.CommandRaw = '_hashtag_'
                self.CommandName = '_hashtag_'
                self.IsCommand = True
                self.CommandType = CommandTypes.Hash

    def ParseSlashCommandParameters(self):

        # First, get the command text and remove the command.
        workingText = self.MessageXML.text.replace(self.CommandRaw, '').strip()

        # If the first parameter of a command is 'help', we can stop parsing.
        # We'll use the IsHelp flag to tell the command processer to simply return the
        # help text on the command
        if workingText.lower().startswith('help'):
            self.IsHelp = True
            return

        # Next, we need to isolate any parameters that are enclosed with quotes.
        # Any text within quotes is considered a single parameter.
        workingText = EncodeQuotedStrings(workingText)

        # Next, I'll look for any equal signs, and remove spaces around them. This will transform
        # named parameters from param1 = bob to param1=bob
        workingText = TrimEquals(workingText)

        # Now we split the remaining text on whitespace. Any parameter that has an equal sign
        # in it is parsed as a key:value. The rest are considered unnamed arguments and are stuffed in the list.
        argList = workingText.split()

        # Note: a parameter of the form: =value is invalid. It shouldn't happen because I trim the spaces
        # above, but if someone puts it as the first parameter, it could show up.
        # Theoretically, key= is a valid parameter, though I will murder someone if they do it.
        for arg in argList:
            if not arg.startswith('='):
                if '=' in arg:
                    cmdpair = arg.split('=')
                    self.NamedParams[cmdpair[0]] = cmdpair[1] if len(cmdpair) > 1 else ''
                else:
                    self.UnnamedParams.append(arg)


# Use this method to convert all the xml into text values for whatever reason that might be useful
def ConvertAllText(messageTree):

    retVal = []
    treant = etree.iterwalk(messageTree, events=("start", ))

    # Parse the rest of the nodes in the xml
    for action, node in treant:
        if node.tag == 'messageML':
            retVal.append(node.text.strip() if node.text else '')
        elif node.tag == 'hash':
            retVal.append('#' + node.attrib['tag'])
        elif node.tag == 'mention':
            retVal.append('_u_' + str(node.attrib['uid']))
        elif node.tag == 'cash':
            retVal.append('$' + node.attrib['tag'])
        elif node.tag == 'chime':
            retVal.append('*chime*')
        elif node.tag == 'br':
            retVal.append('\\n')
        elif node.tag == 'a':
            retVal.append(node.attrib['href'])
        elif node.tag == 'ul':
            retVal.append('\\n')
        elif node.tag == 'li':
            if node.text:
                retVal.append('* ' + node.text.strip() + '\\n')
        else:
            if node.text:
                st = node.text.strip()
                if st:
                    retVal.append(st)

        if node.tail:
            tail = node.tail.strip()
            if tail:
                retVal.append(tail)

    return " ".join(retVal).replace('"', r'\"')


def TrimEquals(inputStr):
    regexEqual = r"\s*=\s*"

    patternEqual = re.compile(regexEqual)
    matchListEqual = patternEqual.finditer(inputStr)

    for m in matchListEqual:
        mtext = m.group(0)
        replaceText = '='
        inputStr = inputStr.replace(mtext, replaceText)

    return inputStr


def EncodeQuotedStrings(inputStr):
    # Need a little bit of a hacky solution to represent this regex
    regexQuote = "([\"" + r"'])(?:(?=(\\?))\2.)*?\1"

    patternQuote = re.compile(regexQuote)
    # Obtain a list of Match Objects
    matchListQuote = patternQuote.finditer(inputStr)

    for m in matchListQuote:
        mtext = m.group(0)
        replaceText = '__hex__' + ConvertToHexString(mtext)
        inputStr = inputStr.replace(mtext, replaceText)

    return inputStr


def ConvertToHexString(inputStr):
    byteStr = inputStr.encode('utf-8')
    hexStr = binascii.hexlify(byteStr)
    return hexStr.decode('utf-8')


class CommandTypes:
    Slash, Hash, Responder, TBD = range(4)
