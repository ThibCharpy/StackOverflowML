import json
import urllib.request
import re
import csv
from html.parser import HTMLParser
from time import sleep

data = {}


def write_json(question_id, title, tags, text, code):
    data[question_id] = {}
    data[question_id]['title'] = title
    data[question_id]['tags'] = tags
    data[question_id]['text'] = text
    data[question_id]['code'] = code


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
            else:
                print("no code for ", question_id)

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


# Return the ids must be use in the crawler
def parse_csv(filename):
    with open(filename, 'r') as f:
        counter = 0
        reader = csv.reader(f)
        # Id, CreationDate, DeletionDate, ScoreOwnerUserId, AnswerCount
        reader = filter(lambda row: row[3] == 'NA', reader)
        id_list = []
        for row in reader:
            counter += 1
            print(counter)
            sleep(1)
            print("Collecting data for id = ", row[0])
            id_list.append(row[0])
            get_data(row[0])
        f.close()
        return id_list


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



ids = parse_csv("resources/questions.csv")
