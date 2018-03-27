import urllib.request
import re


def get_data_from_id(id):
    return get_data_from_page("https://stackoverflow.com/questions/" + str(id))


def get_data_from_page(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = str(urllib.request.urlopen(req).read())

    # print(html)

    regex_title = "class=\"question-hyperlink\">([^><]*)"
    regex_filtertitle = "[^><]+>(.*)"
    # regex_question = "<div class=\"post-text\" itemprop=\"text\">(.?*)</div>"
    # regex_tags = "<div class=\"post-taglist\">(.*?)</div>"

    match_title = re.search(regex_title, html)
    test = re.search(regex_filtertitle, match_title.group())
    print(test.group())
    # print(match_title)
    # match_question = re.search(regex_question, html)
    # match_tags = re.search(regex_tags, html)

    print(match_title)

    if match_title:
        html_title = match_title.group(0)
    else:
        print("no title for ", url)

    # if match_question:
    #     html_question = match_question.group(0)
    # else:
    #     print("no question for ", url)
    #
    # if match_tags:
    #     html_tags = match_tags.group(0)
    # else:
    #     print("no tags for ", url)
    return html_title


print("Le titre est : ", get_data_from_id(4))

import csv

# Return the ids must be use in the crawler
def parse_csv (filename):
    with open(filename,'rb') as f:
        reader = csv.reader(f)
        #Id, CreationDate, DeletionDate, ScoreOwnerUserId, AnswerCount
        reader = filter(lambda row: row[2] == 'NA',reader)
        idList = []
        for row in reader:
            idList.append(row[0])
        return idList