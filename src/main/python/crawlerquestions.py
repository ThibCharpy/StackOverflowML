import re
import urllib.request
import json
from html.parser import HTMLParser
from time import sleep

data = {}


def write_json(question_id, title, tags, text, code):
    global data
    data['data'][question_id] = {}
    data['data'][question_id]['title'] = title
    data['data'][question_id]['tags'] = tags
    data['data'][question_id]['text'] = text
    data['data'][question_id]['code'] = code

    with open('resources/data.json', 'w') as json_da:
        json.dump(data, json_da)
        json_da.close()


def get_data(question_id):
    url = "http://stackoverflow.com/questions/" + str(question_id)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = str(urllib.request.urlopen(req).read())

    regex_title = 'stion-header">[^><]+?<h1 itemprop="name"><a href="[^><]+?" class="question-hyperlink">(.*?)</a></h1>'
    regex_question = '<div class="post-text" itemprop="text">(.*?)</div>'
    regex_tags = '<div class="post-taglist">(.*?)</div>'
    regex_tag = 'rel="tag">(.*?)</a>'
    regex_codes = '<code>(.*?)</code>'

    match_title = re.search(regex_title, html)
    match_question = re.search(regex_question, html)
    match_tags = re.search(regex_tags, html)

    title = ""
    tags = ""
    text = ""
    code = ""

    if match_title:
        title = match_title.group(1)
    else:
        print("no title for ", question_id)

    if match_question:
        html_question = match_question.group(1)
        if html_question:
            match_code = re.findall(regex_codes, html_question)

            if match_code:
                for i in match_code:
                    i = re.sub(r"\\.", " ", i)
                    code += " " + i
            # else:
            #     print("no code for ", question_id)

            # remove code parts
            text = re.sub(r"<code>.*?</code>", " ", html_question)
            # remove html tags
            text = strip_tags(text)
            # remove \n \r
            text = re.sub(r"\\.", " ", text)
        else:
            print("no text for ", question_id)

    else:
        print("no question for ", question_id)

    if match_tags:
        tagslist = re.findall(regex_tag, match_tags.group(1))
        for tag in tagslist:
            tags += tag + " "
    else:
        print("no tags for ", question_id)

    write_json(question_id, title, tags, text, code)


class MLStripper(HTMLParser):
    def error(self, message):
        print("ERROR IN STRIPPER, very panicked.")

    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def mainfunction():
    counter = 0
    with open('resources/data.json', 'r') as json_data:
        global data
        data = json.load(json_data)
        json_data.close()

    with open('resources/left.txt', 'r') as idsfile:
        ids = idsfile.readlines()
        idsfile.close()
        ids = [x.strip() for x in ids]

        for question_id in ids:
            print("Parsing question " + question_id + ', request n°' + str(counter + 1))
            counter += 1
            try:
                get_data(question_id)
            except urllib.error.HTTPError:
                print("DAMN !!!!! 429 catched")
                counter = 0
                with open('resources/left.txt', 'r+') as file:
                    identifiants = file.readlines()
                    file.close()
                    identifiants = [x.strip() for x in identifiants]
                    for qid in range(len(identifiants)):
                        if qid == question_id:
                            newlist = ids[qid:]
                            for elem in newlist:
                                file.write(elem + '\n')
                            break
                    file.close()
                sleep(60)
            sleep(3)


mainfunction()
