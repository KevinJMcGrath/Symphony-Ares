import codecs
import json
import os


JIRAFields = None


class JIRAFieldDefinition:
    def __init__(self):
        Name: str = ""
        Type: str = ""
        APIName: str = ""


def LoadJIRAFields():
    global JIRAFields

    JIRAFields = {}

    _configPath = os.path.abspath('modules/plugins/JIRA/config.json')

    with codecs.open(_configPath, 'r', 'utf-8-sig') as json_file:
        _config = json.load(json_file)

    fields = _config['fields']

    for field in fields:
        fieldtype = field['type']
        apiname = field['apiname']

        jfd = JIRAFieldDefinition()
        jfd.Name = field['apiname']
        jfd.Type = fieldtype
        jfd.APIName = apiname

        JIRAFields[jfd.Name] = jfd

        for alias in field['aliases']:

            if alias not in JIRAFields:
                jfdAlias = JIRAFieldDefinition()
                jfdAlias.Name = alias
                jfdAlias.Type = fieldtype
                jfdAlias.APIName = apiname

                JIRAFields[jfdAlias.Name] = jfdAlias
