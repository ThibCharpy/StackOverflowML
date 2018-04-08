import json
import regex
import re


def correct():
    regex_data = "'[0-9]{8}': {'title':.+?}, '[0-9]{8}'"
    regex_onedata = "'([0-9]+?)': {('title':.+?)}, '[0-9]"
    with open('resources/data.json', 'r') as json_data:
        data = json.load(json_data)
        json_data.close()

    match = regex.findall(regex_data, str(data), overlapped=True)

    with open('resources/newdata.json', 'w') as target:
        for i in match:
            match_one = re.search(regex_onedata, i)
            idq = match_one.group(1)
            rest = match_one.group(2)
            try:
                target.write("{ 'id' : '" + idq + "', " + rest + "}\n")
            except UnicodeEncodeError:
                print(rest)


correct()
