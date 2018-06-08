import codecs
import json
import os
import re

import modules.botlog as log

EpicList = {}
DefaultItem = None


def GetConfigPath():
    # http://www.karoltomala.com/blog/?p=622
    path = os.path.abspath(__file__)

    return os.path.join(os.path.dirname(path), "feedback_config.json")


def LoadEpics():
    global EpicList
    global DefaultItem

    if EpicList is None or len(EpicList) == 0:
        config_path = GetConfigPath()

        with codecs.open(config_path, 'r', 'utf-8-sig') as json_file:
            defJSON = json.load(json_file)

        for item in defJSON['epics']:
            EpicList[item['name']] = item

        DefaultItem = defJSON['default']


def MatchEpic(bodytext: str):

    searchtext = bodytext.lower()
    epic_match = {}

    freq_dict = GetFrequencyDict(searchtext)

    for epic_key in EpicList:
        epic = EpicList.get(epic_key)

        for keyword in epic['keywords']:
            count = epic_match.get(epic['name'], 0)

            kw_match_count = 0
            if " " in keyword:
                kw_match_count = searchtext.count(keyword)
            elif keyword in freq_dict:
                kw_match_count = freq_dict[keyword]

            epic_match[epic['name']] = count + kw_match_count

            # log.LogConsoleInfo('Epic: ' + epic_key + ' | KW: ' + keyword + ' | KW Count: ' + str(kw_match_count))

    # returns the epic name with the largest match count
    # If there are multiples with the same max count, returns the first one
    # I need to figure out a way to look at all the max values and pick the one with the
    # higher priority
    if len(epic_match) > 0:
        # log match dict to console
        log.LogConsoleInfo(json.dumps(epic_match))

        epic_name = max(epic_match.keys(), key=(lambda k: epic_match[k]))

        return EpicList.get(epic_name, DefaultItem)
    else:
        return DefaultItem


def GetFrequencyDict(bodytext: str) -> dict:
    # Hashtag: #?\w{3,}
    # Encoded @mention (_u_#######): _u_\d+\b

    frequency = {}

    # find all words three characters or larger, excluding any @mentions
    # https://www.regextester.com/?fam=103621
    # Regex:
    #   (?!_u_\d+\b)\b -> Negative Lookahead: finds the encoded @mention and then **discards** the match
    #       _u_ -> literal expression
    #       \d+ -> any number, repeated 1 or more times
    #       \b -> word boundary
    #   [\w'-]{3,} -> Matches any word, including ' and -, that's 3 or more characters in length
    regex_word_pattern = r"(?!_u_\d+\b)\b[\w'-]{3,}"
    match_pattern = re.findall(regex_word_pattern, bodytext)

    for word in match_pattern:
        # syntax reminder: dict.get(key, default_value)
        count = frequency.get(word, 0)
        frequency[word] = count + 1

    return frequency


# Load config data when the module is loaded for the first time.
LoadEpics()
