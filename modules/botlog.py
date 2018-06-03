import logging
import logging.handlers
import sys

import modules.botconfig as config


# Setup various logging facilities
_consolelog = logging.getLogger('ares')
_errlog = logging.getLogger('ares.error')

_symlog = logging.getLogger('ares.symphony')
_symErrorLog = logging.getLogger('ares.symphony.error')

_pluginLog = logging.getLogger('ares.plugins')
_pluginErrorLog = logging.getLogger('ares.plugins.error')

_consolelog.setLevel(logging.DEBUG)
_errlog.setLevel(logging.DEBUG)
_symlog.setLevel(logging.DEBUG)
_symErrorLog.setLevel(logging.DEBUG)
_pluginLog.setLevel(logging.DEBUG)
_pluginErrorLog.setLevel(logging.DEBUG)


_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')

if config.LogToFile:
    _errorLogPath = config.BaseLoggingPath + '/error.log'

    _symLogPath = config.BaseLoggingPath + '/symphony.log'
    _symErrorLogPath = config.BaseLoggingPath + '/symphony_error.log'

    _pluginLogPath = config.BaseLoggingPath + '/plugins.log'
    _pluginErrorLogPath = config.BaseLoggingPath + '/plugins_error.log'

    # Create stream handler to display console output
    # stdout doesn't print to the Pycharm console, apparently
    _consoleStreamHandler = logging.StreamHandler()

    # Create rotating file handlers that backup 5 times at 2MB
    _symLogHandler = logging.handlers.RotatingFileHandler(_symLogPath, maxBytes=2000000, backupCount=5)
    _symErrorLogHandler = logging.handlers.RotatingFileHandler(_symLogPath, maxBytes=2000000, backupCount=5)
    _pluginLogHandler = logging.handlers.RotatingFileHandler(_symLogPath, maxBytes=2000000, backupCount=5)
    _pluginErrorLogHandler = logging.handlers.RotatingFileHandler(_symLogPath, maxBytes=2000000, backupCount=5)
    _errLogHandler = logging.handlers.RotatingFileHandler(_errorLogPath, maxBytes=2000000, backupCount=5)
else:
    _consoleStreamHandler = logging.StreamHandler(sys.stdout)
    _errLogHandler = logging.StreamHandler(sys.stderr)
    _symLogHandler = logging.StreamHandler(sys.stdout)
    _symErrorLogHandler = logging.StreamHandler(sys.stderr)
    _pluginLogHandler = logging.StreamHandler(sys.stdout)
    _pluginErrorLogHandler = logging.StreamHandler(sys.stderr)


_consoleStreamHandler.setLevel(logging.DEBUG)
_consoleStreamHandler.setFormatter(_formatter)

_errLogHandler.setLevel(logging.DEBUG)
_errLogHandler.setFormatter(_formatter)

_symLogHandler.setLevel(logging.DEBUG)
_symLogHandler.setFormatter(_formatter)

_symErrorLogHandler.setLevel(logging.ERROR)
_symErrorLogHandler.setFormatter(_formatter)

_pluginLogHandler.setLevel(logging.DEBUG)
_pluginLogHandler.setFormatter(_formatter)

_pluginErrorLogHandler.setLevel(logging.ERROR)
_pluginErrorLogHandler.setFormatter(_formatter)

_consolelog.addHandler(_consoleStreamHandler)
_errlog.addHandler(_errLogHandler)

_symlog.addHandler(_symLogHandler)
_symErrorLog.addHandler(_symErrorLogHandler)

_pluginLog.addHandler(_pluginLogHandler)
_pluginErrorLog.addHandler(_pluginErrorLogHandler)


def LogConsoleInfo(message):
    _consolelog.info(message)


def LogConsoleError(message):
    _errlog.error(message)


def LogSymphonyInfo(message):
    _symlog.info(message)


def LogSymphonyError(message):
    _symErrorLog.error(message)


def LogSystemInfo(message):
    _consolelog.info(message)


def LogSystemWarn(message):
    _consolelog.warning(message)


def LogSystemError(message):
    _errlog.error(message)
