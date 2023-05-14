from nltk import pos_tag

import re
from math import log10




def calculate_score(text):
    splited_list = split_self(text)
    entry = splited_list[0]
    all = ""
    i = 1
    while i < len(splited_list):
        all += splited_list[i] + ' '
        i += 1
    idf_text = all
    all = split_pronounce(all)
    sentence_score_list = []
    tf_idf_list = []
    for word in all:
        tf_idf_list.append(tf_Idf(word, idf_text))

    keywords = find_keyword(tf_idf_list, int(len(idf_text.split(" ")) / 10))

    for word in all:
        noun = find_noun(word)
        numeric = find_numeric_char(word)
        entry_similarity = title_similarity(word.lower(), entry.lower())
        theme_similar = theme_similarity(word, keywords)
        word=re.split(" ",word)
        if word[0]== '':
            word.remove('')
        sentence_length = len(word)
        sentence_score_list.append([noun / sentence_length, numeric / sentence_length, entry_similarity / sentence_length, theme_similar / sentence_length])

    return sentence_score_list


def find_noun(text):
    tagged_sent = pos_tag(text.split())
    propernouns = [word for word, pos in tagged_sent if pos == 'NNP']
    return len(propernouns)


def find_numeric_char(text):
    result = re.findall('[0-9]+', text)
    return len(result)


def title_similarity(text, entry):
    text1 = entry.split()
    text = text.split()
    counter = 0
    for w in text1:
        for w2 in text:
            if w2.find(w) != -1:
                counter += 1
    return counter


def theme_similarity(text, keywords):
    text = text.split(" ")
    counter = 0
    i = 0
    while i < len(text):
        j = 0
        while j < len(keywords):
            if text[i] == keywords[j][1]:
                counter += 1
                break
            j += 1
        i += 1
    return counter


def tf_Idf(text, all_text):
    text = text.lower()
    split_text = text.split(" ")
    all_text = all_text.lower()
    split_all_text = all_text.split(" ")
    i = 0
    deleted_count = 0

    tf_idf_list = []

    while i < len(split_text):
        if split_text[i] != '':
            key = split_text[i]
        else:
            deleted_count += 1
            i += 1
            continue
        tf = split_text.count(key) / (len(split_text) - 1)
        if split_all_text.count(key) == 0:
            key = key + '.'
        df = len(split_all_text) / split_all_text.count(key)
        idf = log10(df)
        total = idf * tf
        tf_idf_list.append([total, key])
        i += 1
    return tf_idf_list


def find_keyword(keyword_list, max):
    sort_list = []
    for l in keyword_list:
        for li in l:
            sort_list.append(li)
    sort_list.sort(reverse=True)
    new_list = [sort_list[0]]
    i = 0
    while i < len(sort_list):
        j = 0
        controller = 0
        while j < len(new_list):
            if sort_list[i][1] == new_list[j][1]:
                controller = 1
                break
            j += 1
        if (controller != 1):
            new_list.append(sort_list[i])
        i += 1
    i = 0
    return_list = []
    while i < max:
        return_list.append(new_list[i])
        i += 1
    return return_list


def split_pronounce(lines):
    x = re.split("\.", lines)
    i = 0
    sentence = []
    while (i < len(x)):
        if len(x[i]) > 2:
            sentence.append(x[i])
        i += 1
    return sentence


def split_self(lines):
    x = re.split("\n", lines)
    i = 0
    y = []
    while i < len(x):
        if len(x[i]) > 2:
            y.append(x[i])
        i += 1
    return y