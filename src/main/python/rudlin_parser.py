import urllib.request
import re
from scrapy.selector import Selector


def get_data_from_page(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = str(urllib.request.urlopen(req).read())

    # print(html)

    regex_title = '<div id="question-header">.+?<h1 itemprop="name"><a href="[^><]+?" class="question-hyperlink">(.*?)</a></h1>'
    # regex_question = '<div class="post-text" itemprop="text">(.?*)</div>'
    # regex_tags = '<div class="post-taglist">(.*?)</div>'

    match_title = re.search(regex_title, html)
    # print(match_title)
    # match_question = re.search(regex_question, html)
    # match_tags = re.search(regex_tags, html)

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


print("Le titre est : ", get_data_from_page("https://stackoverflow.com/questions/4"))
