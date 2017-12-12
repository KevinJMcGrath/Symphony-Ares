import datetime
import re
from dateutil.parser import parse


def ConvertDateTimeToMilliseconds(inputDT: datetime.datetime):
    return int(inputDT.timestamp()*1000)


def ConvertDTStringToMilliseconds(inputStr):
    dt = parse(inputStr)

    return ConvertDateTimeToMilliseconds(dt)


def ConvertShorthandToSeconds(shorthandStr):
    # Identifies groups that match this patter: ##[d,h,m,s]
    # Ex. 1d2h3m15s
    regex = '\d+[d,h,m,s]'

    patternEqual = re.compile(regex)
    matchListEqual = patternEqual.finditer(shorthandStr)

    offsetVal = 0
    for m in matchListEqual:
        subG = m.group(0)

        # For each match group, extract the integer component.
        # \b = "word boundary" => start of sentence, or after a space, comma or period
        # \d+ = "match all integers, one or more times"
        valueList = re.findall(r'\b\d+', subG)

        # If an integer is found, let's attempt to translate that into a corresponding number of seconds
        if len(valueList) > 0:

            valStr = valueList[0]
            unitStr = subG.replace(valStr, '')

            val = int(valStr)

            if unitStr == 's':
                offsetVal += val
            elif unitStr == 'm':
                offsetVal += val * 60
            elif unitStr == 'h':
                offsetVal += val * 60 * 60
            elif unitStr == 'd':
                offsetVal += val * 24 * 60 * 60

    return offsetVal
