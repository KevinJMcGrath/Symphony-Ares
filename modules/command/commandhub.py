import importlib

import modules.plugins.commandloader as cmdloader
import modules.command.commandqueue as queue
from modules.symphony.tokenizer import CommandTypes

# import modules.botlog as botlog

cmdloader.LoadAllCommands()


def ProcessCommand(messageDetail):
    if messageDetail.Command.IsCommand:
        if messageDetail.Command.CommandType == CommandTypes.Slash:
            RunSlashCommand(messageDetail)
        elif messageDetail.Command.CommandType == CommandTypes.Hash:
            RunHashCommand(messageDetail)


def SendReply(messageDetail, reply):
    messageDetail.ReplyToChat(reply)


def SendHelp(messageDetail, helpMsg, desc):
    msg = 'Instructions for ' + messageDetail.Command.CommandName + ':<br/><br/>'
    msg += helpMsg + '<br/><br/>'
    msg += 'Description: ' + desc

    SendReply(messageDetail, msg)


def RunSlashCommand(messageDetail):
    # Check to see if it's a default command
    command = None

    if messageDetail.Command.CommandName in cmdloader.DefaultCommands:
        command = cmdloader.DefaultCommands[messageDetail.Command.CommandName]
    elif messageDetail.Command.CommandName in cmdloader.PluginCommands:
        command = cmdloader.PluginCommands[messageDetail.Command.CommandName]

    if command is not None:
        if messageDetail.Command.IsHelp:
            SendHelp(messageDetail, command.HelpText, command.Description)
        else:
            mod = importlib.import_module(command.Module)

            if hasattr(mod, command.Function):
                func = getattr(mod, command.Function)

                # Allow for some commands to be processed immediately
                if command.IsImmediate:
                    func(messageDetail)
                else:
                    queue.AsyncCommand(func, messageDetail)
            else:
                SendReply(messageDetail, "Apologies - I found a definition for that command, "
                                         "but the developer forgot to build the function.")
    else:
        SendReply(messageDetail, "I am sorry - I do not understand that command.")


def RunHashCommand(messageDetail):
    for command in cmdloader.HashCommands:
        # Set intersection is a clever way to compare the two lists of hashtags
        intersection = set(messageDetail.Command.Hashtags).intersection(command.Trigger)

        if len(intersection) > 0:
            mod = importlib.import_module(command.Module)

            if hasattr(mod, command.Function):
                func = getattr(mod, command.Function)
                func(messageDetail)
            else:
                SendReply(messageDetail, "Sadly, I found triggers for those hashtags, "
                                         "but the related function is incomplete or missing.")
            break
