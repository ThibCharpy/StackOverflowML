# coding: utf-8

# In[1]:


import urllib.request
import re


# In[2]:


def get_questions_from_page(url):
    """
    Extracts blocks of HTML which correspond to questions on the page.
    
    Args: 
        url (str): url of a page
    
    Returns: 
        (list of str): list of html contents of each question
    """

    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    # print("trying to open", url)
    with urllib.request.urlopen(req) as response:
        html = str(response.read())

    print("parsing", url)
    regex_mainbar = "<div id=\"mainbar\">(.*?)<div id=\"sidebar\">"
    match_mainbar = re.search(regex_mainbar, html)
    if match_mainbar:
        html_mainbar = match_mainbar.group(0)
    else:
        print("mainbar not found")

    # Each question is inside a <div> with a class "summary"
    # Splitting the text by div title, we get N+1 elements:
    # 0:  html before the first question
    # 1..N:  html of all the N questions
    regex_question = "<div class=\"summary\">"
    list_html_questions = re.split(regex_question, html_mainbar)[1:]
    # print(len(list_html_questions), "questions found")
    return list_html_questions


# In[3]:


def get_tags_from_question(html_question):
    """
    Extracts the list of tags from a question HTML.
    
    Args:
        html_question (str): HTML code of a question
    Returns:
        (list of str): list of tags as strings
    """
    regex_tags = "\/questions\/tagged\/(.*?)\""
    tags = re.findall(regex_tags, html_question)
    return [decode_url(tag) for tag in tags]


# In[4]:


def decode_url(url):
    decode_url = {}
    decode_url["%23"] = "#"
    decode_url["%2b"] = "+"
    for key in decode_url:
        if key in url:
            url = url.replace(key, decode_url[key])
    return url


# In[5]:


def extract_cooccurrences(cooccur_dict):
    """
    Args:
        cooccur_dict (dict of {tag_id (str): nb_of_cooccur (int)} dicts)
    Returns:
        tuples (tag1_idx, tag2_idx, nb_of_cooccurrences)
    """
    cooccur_tuples = []
    for tag1_idx in cooccur_dict:
        for tag2_idx in cooccur_dict[tag1_idx]:
            # De-duplicating
            if tag1_idx < tag2_idx:
                smaller_idx = tag1_idx
                bigger_idx = tag2_idx
            else:
                smaller_idx = tag2_idx
                bigger_idx = tag1_idx
            t = (smaller_idx, bigger_idx, cooccur_dict[tag1_idx][tag2_idx])
            if t not in cooccur_tuples:
                cooccur_tuples.append(t)
    return cooccur_tuples


# In[7]:


def serialize(obj, path):
    with open(path, 'w') as out_file:
        out_file.write(str(obj))
    print('File', path, 'written.')


# In[8]:


def calculate_pairs(all_tags, cooccur_dict):
    cooccur_tuples = extract_cooccurrences(cooccur_dict)
    # Sort tuples by number of cooccurences
    cooccur_tuples.sort(key=lambda tup: tup[2], reverse=True)
    pairs = []
    for tup in cooccur_tuples[:100]:
        tag1 = all_tags[int(tup[0])]
        tag2 = all_tags[int(tup[1])]
        pairs.append((tag1, tag2, tup[2]))
    return pairs


# In[9]:


# List of all tag names
all_tags = []

# Dictionary that counts total occurences of each tag
# Example {"3": 16, "17": 8}, 
#         where "3" is the code of "java", "17" is the code of "python"
tags_counts = {}

# Each tag has a co-occurrence dictionary in the form {index_of_related_tag: number_of_cooccurrences, ...}
# Meta-dictionary of a form {tag: coappearance_dictionary}
# Example: {"3": {"5": 1, "17": 4},    "5": {"3": 1, "4": 33, "9": 15}, ... } ,
#     where "3" - the code of "java", "5" - "javascript",  "17" - "python".
cooccur_dict = {}

MAX_PAGE_INDEX = 10000  # 669683   #201030 for 50 questions per page
SERIALIZE_EVERY_N_PAGES = 1000

for page_index in range(1, MAX_PAGE_INDEX + 1):
    # url = "http://stackoverflow.com/questions?page=" + str(page_index) + "&sort=newest"
    url = "http://stackoverflow.com/questions?pagesize=50&page=" + str(page_index) + "&sort=newest"
    questions = get_questions_from_page(url)
    for html_question in questions:
        tags = get_tags_from_question(html_question)
        # print(tags)

        # 1. Looping through each tag, adding new tags to list, adding 1 to tag's occurence count
        for tag in tags:
            if tag not in all_tags:
                all_tags.append(tag)
            tag_index = str(all_tags.index(tag))
            if tag_index in tags_counts:
                tags_counts[tag_index] += 1
            else:
                tags_counts[tag_index] = 1

        # 2. Looping through all PAIRS of tags in question, calculating co-occurrence    
        for tag1_idx_in_question in range(len(tags)):
            tag1_text = tags[tag1_idx_in_question]
            tag1_index = str(all_tags.index(tag1_text))
            if tag1_index not in cooccur_dict:
                cooccur_dict[tag1_index] = {}

            for tag2_idx_in_question in range(len(tags)):
                if tag2_idx_in_question == tag1_idx_in_question:
                    continue
                tag2_text = tags[tag2_idx_in_question]
                tag2_index = str(all_tags.index(tag2_text))
                # If there already was a coappearances between these 2 tags yet, increment count by 1.
                # Otherwise, create this coappearance with count 1.
                if tag2_index in cooccur_dict[tag1_index]:
                    cooccur_dict[tag1_index][tag2_index] += 1
                else:
                    cooccur_dict[tag1_index][tag2_index] = 1

    # Serializing results
    if page_index > 0 and page_index % SERIALIZE_EVERY_N_PAGES == 0:
        pairs = calculate_pairs(all_tags, cooccur_dict)
        # serialize(all_tags, 'results/{0}_all_tags.txt'.format(page_index))
        # serialize(tags_counts, 'results/{0}_tags_counts.txt'.format(page_index))
        # serialize(cooccur_dict, 'results/{0}_cooccur_dict.txt'.format(page_index))
        serialize(pairs, 'results/{0}_pairs.txt'.format(page_index))

# a) 15 questions per page:  37 sec for 100 p./1500 quest.
#       ====> about 10,000 p./150,000 quest. per hour 
#       =====> about 66 hours to parse all of 10M questions (669683 pages)
# b) 50 questions per page:  55 seconds for 100 p./5000 quest.
#       ====> approximately 6,000 pages/300,000 questions per hour  
#        =====> about 33 hours to parse 10M questions (201030 pages)


# In[10]:


all_tags

# In[14]:


# Display sorted dict
for key in sorted(tags_counts, key=tags_counts.get, reverse=True):
    print("tag #{0} - {1} - {2}".format(key, all_tags[int(key)], tags_counts[key]))

# In[15]:


len(all_tags)

# In[16]:


cooccur_dict

# In[37]:


pairs = calculate_pairs(all_tags, cooccur_dict)
for pair in pairs:
    print(pair[0], pair[1], pair[2])

# In[29]:


serialize(all_tags, 'results/10_all_tags.txt')
serialize(tags_counts, 'results/10_tags_counts.txt')
serialize(cooccur_dict, 'results/10_cooccur_dict.txt')
serialize(pairs, 'results/10_pairs.txt')

# In[32]:


p = [('javascript', 'jquery', 17), ('html', 'css', 13), ('javascript', 'html', 12), ('php', 'mysql', 11),
     ('html', 'jquery', 9), ('ios', 'swift', 8), ('mysql', 'sql', 7), ('css', 'jquery', 7), ('swift', 'parse.com', 6),
     ('javascript', 'node.js', 6), ('javascript', 'css', 6), ('ios', 'objective-c', 6), ('wordpress', 'php', 5),
     ('javascript', 'php', 5), ('php', 'arrays', 5), ('html', 'php', 5), ('c#', 'asp.net', 5),
     ('android', 'android-activity', 5), ('ios', 'xcode', 5), ('wpf', 'c#', 4), ('android', 'java', 4),
     ('table', 'php', 4), ('ios', 'parse.com', 4), ('swift', 'xcode', 4), ('android', 'android-fragments', 4),
     ('.net', 'c#', 4), ('javascript', 'arrays', 4), ('algorithm', 'java', 3), ('ajax', 'php', 3), ('php', 'jquery', 3),
     ('xcode', 'parse.com', 3), ('node.js', 'mongodb', 3), ('pointers', 'c++', 3), ('python-2.7', 'python', 3),
     ('linux', 'python', 3), ('ios', 'cocoa-touch', 3), ('javascript', 'google-spreadsheet', 3),
     ('python-3.x', 'python', 3), ('django', 'python', 3), ('javascript', 'html5', 3), ('wpf', 'devexpress', 2),
     ('sql', 'sqlite', 2), ('java', 'eclipse', 2), ('java', 'multithreading', 2), ('swing', 'java', 2),
     ('java', 'maven', 2), ('java', 'keytool', 2), ('logging', 'java', 2), ('javascript', 'sorting', 2),
     ('sorting', 'php', 2), ('sorting', 'arrays', 2), ('database', 'sql', 2), ('sql', 'join', 2), ('mysqli', 'php', 2),
     ('javascript', 'css3', 2), ('css3', 'jquery', 2), ('cordova', 'ionic-framework', 2), ('ios8', 'ios', 2),
     ('android', 'android-intent', 2), ('android-intent', 'android-activity', 2), ('wordpress', 'woocommerce', 2),
     ('wordpress', 'braintree', 2), ('codeigniter', 'php', 2), ('php', 'directory', 2), ('database', 'php', 2),
     ('curl', 'php', 2), ('php', 'laravel-5.1', 2), ('php', 'braintree', 2), ('woocommerce', 'php', 2),
     ('datetime', 'php', 2), ('ios', 'phasset', 2), ('database', 'mysql', 2), ('ruby-on-rails', 'nested-forms', 2),
     ('swift', 'sprite-kit', 2), ('ios', 'ipad', 2), ('mongodb', 'mongodb-query', 2), ('css', 'responsive-design', 2),
     ('ios', 'uiwebview', 2), ('node.js', 'mongoose', 2), ('node.js', 'express', 2), ('ruby-on-rails', 'ruby', 2),
     ('pointers', 'arrays', 2), ('session', 'cookies', 2), ('android', 'android-manifest', 2), ('ios', 'iphone', 2),
     ('html', 'table', 2), ('ruby-on-rails', 'twitter-bootstrap', 2), ('c', 'c++', 2), ('qt', 'c++', 2),
     ('c++', 'arrays', 2), ('c++11', 'c++', 2), ('html5', 'html5-video', 2), ('devexpress', 'c#', 2),
     ('c#', 'drop-down-menu', 2), ('asp.net', 'drop-down-menu', 2), ('angularjs', 'ionic', 2), ('javascript', 'c#', 2),
     ('entity-framework', 'c#', 2), ('c#-4.0', 'c#', 2), ('sql-server', 'c#', 2)]
