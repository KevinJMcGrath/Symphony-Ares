import logging.handlers
import os

_pabotlog = logging.getLogger('PABot')

_pabotlog.setLevel(logging.DEBUG)

_logPath = os.path.abspath("./logging/pabot.log")

_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')

_consoleStreamHandler = logging.StreamHandler()
_consoleStreamHandler.setLevel(logging.DEBUG)
_consoleStreamHandler.setFormatter(_formatter)

_symLogRotFileHandler = logging.handlers.RotatingFileHandler(_logPath, maxBytes=2000000, backupCount=5)
_symLogRotFileHandler.setLevel(logging.DEBUG)
_symLogRotFileHandler.setFormatter(_formatter)

_pabotlog.addHandler(_consoleStreamHandler)
_pabotlog.addHandler(_symLogRotFileHandler)


def LogPABotMessage(message):
    _pabotlog.info(message)


def LogPABotError(message):
    _pabotlog.error(message)
