import sys

import unicodedata
from nltk.tokenize import TweetTokenizer
from nltk.stem.snowball import *




def start_tokenization(text,tokenizedList,lock,stopWords):
    tbl = dict.fromkeys(i for i in range(sys.maxunicode) if unicodedata.category(chr(i)).startswith('P'))
    text = text.translate(tbl)
    tknzr = TweetTokenizer(reduce_len=True)
    word = tknzr.tokenize(text)
    ss = EnglishStemmer(ignore_stopwords=True)
    stem_list=[]
    for w in word:
        stem_list.append(ss.stem(w))
    
    tokens_without_sw = [word for word in stem_list if not word in stopWords]
    with lock:
        tokenizedList.append(' '.join(tokens_without_sw))

