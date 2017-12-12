import codecs
import json
import os
import re
from dateutil.parser import parse
import modules.plugins.PABot.database as db

_configPath = os.path.abspath('modules/plugins/PABot/config.json')

with codecs.open(_configPath, 'r', 'utf-8-sig') as json_file:
    _config = json.load(json_file)

# Checks to see if the todoItems table exists and creates it otherwise
db.InitDB()


def AddToDoItem(summary, dueDate, reminderStart, reminderFreq):

    if dueDate is not None:
        dDate = parse(dueDate).isoformat()
    else:
        dDate = 'NULL'





