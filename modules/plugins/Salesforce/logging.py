import logging.handlers
import os

_sfdclog = logging.getLogger('sfdc')

_sfdclog.setLevel(logging.DEBUG)

_logPath = os.path.abspath("./logging/sfdc.log")

_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')

_consoleStreamHandler = logging.StreamHandler()
_consoleStreamHandler.setLevel(logging.DEBUG)
_consoleStreamHandler.setFormatter(_formatter)

_symLogRotFileHandler = logging.handlers.RotatingFileHandler(_logPath, maxBytes=2000000, backupCount=5)
_symLogRotFileHandler.setLevel(logging.DEBUG)
_symLogRotFileHandler.setFormatter(_formatter)

_sfdclog.addHandler(_consoleStreamHandler)
_sfdclog.addHandler(_symLogRotFileHandler)


def LogSFDCMessage(message):
    _sfdclog.info(message)


def LogSFDCError(message):
    _sfdclog.error(message)
