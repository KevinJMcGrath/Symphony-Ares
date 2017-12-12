import codecs
import json
import os
import sqlite3

_configPath = os.path.abspath('modules/plugins/PABot/config.json')

with codecs.open(_configPath, 'r', 'utf-8-sig') as json_file:
    _config = json.load(json_file)

sqliteDBPath = os.path.abspath('modules/plugins/PABot/' + _config['databasePath'])


def InitDB():
    sql = "SELECT name FROM sqlite_master WHERE type='table' AND name='todoItems'"

    conn = sqlite3.connect(sqliteDBPath)

    if not conn.execute(sql).fetchone():
        CreateNewDatabase()


def CreateNewDatabase():
    table_name = "todoItems"
    fields = [
        {"name": "summary", "type": "TEXT"},
        {"name": "due_date", "type": "INTEGER"},
        {"name": "reminder_start", "type": "INTEGER"},
        {"name": "reminder_frequency", "type": "INTEGER"},
        {"name": "active", "type": "INTEGER"}
    ]

    conn = sqlite3.connect(sqliteDBPath)
    c = conn.cursor()

    # Create table
    createSQL = 'CREATE TABLE ' + table_name + ' (item_id INTEGER PRIMARY KEY,'

    fieldStrList = []
    for field in fields:
        fieldStrList.append(field["name"] + ' ' + field["type"])

    createSQL += ','.join(fieldStrList) + ')'

    c.execute(createSQL)
    conn.commit()
    conn.close()
