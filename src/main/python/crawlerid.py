import re
import urllib.request
from time import sleep

tags_wanted = ['python', 'java', 'c', 'html']


def crawl():
    with open('resources/ids.txt', 'w+') as f:
        for i in range(116, 300):
            for tag in tags_wanted:
                print(tag + ' page ' + str(i))
                url = 'https://stackoverflow.com/questions/tagged/' + tag + '?page=' + str(
                    i) + '&sort=newest&pagesize=50'
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                html = str(urllib.request.urlopen(req).read())

                regex_id = '<div class="question-summary" id="question-summary-([0-9]+?)">'

                match_id = re.findall(regex_id, html)
                if not match_id:
                    break
                for ids in match_id:
                    question_id = ids
                    f.write(question_id + '\n')
            sleep(2)
    f.close()
    print('DONE')


crawl()
