import logging.handlers
import os

_jiralog = logging.getLogger('jira')

_jiralog.setLevel(logging.DEBUG)

_logPath = os.path.abspath("./logging/jira.log")

_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')

_consoleStreamHandler = logging.StreamHandler()
_consoleStreamHandler.setLevel(logging.DEBUG)
_consoleStreamHandler.setFormatter(_formatter)

_symLogRotFileHandler = logging.handlers.RotatingFileHandler(_logPath, maxBytes=2000000, backupCount=5)
_symLogRotFileHandler.setLevel(logging.DEBUG)
_symLogRotFileHandler.setFormatter(_formatter)

_jiralog.addHandler(_consoleStreamHandler)
_jiralog.addHandler(_symLogRotFileHandler)


def LogJIRAMessage(message):
    _jiralog.info(message)


def LogJIRAError(message):
    _jiralog.error(message)
