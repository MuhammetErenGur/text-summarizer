from nltk import pos_tag
import re
from math import log10
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

def calculate_score(text):
    splited_list = split_lines(text)
    entry = splited_list[0]
    all_text = " ".join(splited_list[1:])
    
    idf_text = all_text
    all_sentences = split_sentences(all_text)
    
    sentence_score_list = []
    tf_idf_list = []
    
    for word in all_sentences:
        tf_idf_list.append(tf_idf(word, idf_text))

    keywords = find_keywords(tf_idf_list, int(len(idf_text.split(" ")) / 10))
    
    for word in all_sentences:
        noun_count = find_noun(word)
        numeric_count = find_numeric_chars(word)
        entry_similarity = title_similarity(word.lower(), entry.lower())
        theme_similarity = calculate_theme_similarity(word, keywords)
        word_list = re.split(" ", word)
        
        if word_list[0] == '':
            word_list.remove('')
        
        sentence_length = len(word_list)
        
        sentence_score_list.append([noun_count / sentence_length, numeric_count / sentence_length, entry_similarity / sentence_length, theme_similarity / sentence_length])
    
    return sentence_score_list


def find_noun(text):
    tagged_sent = pos_tag(text.split())
    proper_nouns = [word for word, pos in tagged_sent if pos == 'NNP']
    return len(proper_nouns)


def find_numeric_chars(text):
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


def calculate_theme_similarity(text, keywords):
    text = text.split(" ")
    counter = 0
    
    for word in text:
        for keyword in keywords:
            if word == keyword[1]:
                counter += 1
    
    return counter


def tf_idf(text, all_text):
    text = text.lower()
    split_text = word_tokenize(text)
    
    all_text = all_text.lower()
    split_all_text = word_tokenize(all_text)
    
    stop_words = set(stopwords.words("english"))
    split_text = [word for word in split_text if word not in stop_words]
    split_all_text = [word for word in split_all_text if word not in stop_words]
    
    tf_idf_list = []
    
    for word in split_text:
        if word != '':
            key = word
        else:
            continue
        
        tf = split_text.count(key) / (len(split_text) - 1)
        
        if split_all_text.count(key) == 0:
            key += '.'
        
        df = len(split_all_text) / split_all_text.count(key)
        idf = log10(df)
        total = idf * tf
        
        tf_idf_list.append([total, key])
    
    return tf_idf_list


def find_keywords(keyword_list, max_count):
    sort_list = []
    
    for sublist in keyword_list:
        for item in sublist:
            sort_list.append(item)
    
    sort_list.sort(reverse=True)
    new_list = [sort_list[0]]
    
    for item in sort_list:
        for new_item in new_list:
            if item[1] == new_item[1]:
                break
        else:
            new_list.append(item)
    
    return new_list[:max_count]


def split_sentences(text):
    sentences = re.split("\.", text)
    sentence_list = [sentence for sentence in sentences if len(sentence) > 2]
    return sentence_list


def split_lines(text):
    lines = text.splitlines()
    line_list = [line for line in lines if len(line) > 2]
    return line_list
