import logging
import logging.handlers

import modules.botconfig as config


# Setup various logging facilities
_consolelog = logging.getLogger('ares')
_symlog = logging.getLogger('ares.symphony')
_errlog = logging.getLogger('ares.error')

_consolelog.setLevel(logging.DEBUG)
_symlog.setLevel(logging.DEBUG)
_errlog.setLevel(logging.DEBUG)

_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')

# Create stream handler to display console output
_consoleStreamHandler = logging.StreamHandler()
_consoleStreamHandler.setLevel(logging.DEBUG)
_consoleStreamHandler.setFormatter(_formatter)

_consolelog.addHandler(_consoleStreamHandler)

_symLogPath = config.BaseLoggingPath + '/symphony.log'
_errorLogPath = config.BaseLoggingPath + '/error.log'

# Create rotating file handlers that backup 5 times at 2MB
_symLogRotFileHandler = logging.handlers.RotatingFileHandler(_symLogPath, maxBytes=2000000, backupCount=5)
_symLogRotFileHandler.setLevel(logging.DEBUG)
_symLogRotFileHandler.setFormatter(_formatter)

_errLogRotFileHandler = logging.handlers.RotatingFileHandler(_errorLogPath, maxBytes=2000000, backupCount=5)
_errLogRotFileHandler.setLevel(logging.DEBUG)
_errLogRotFileHandler.setFormatter(_formatter)

_symlog.addHandler(_symLogRotFileHandler)
_errlog.addHandler(_errLogRotFileHandler)


def LogConsoleInfo(message):
    _consolelog.info(message)


def LogConsoleError(message):
    _consolelog.error(message)


def LogSymphonyInfo(message):
    _symlog.info(message)


def LogSymphonyError(message):
    _symlog.error(message)


def LogSystemInfo(message):
    _errlog.info(message)


def LogSystemWarn(message):
    _errlog.warning(message)


def LogSystemError(message):
    _errlog.error(message)
