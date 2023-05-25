import sys

import unicodedata
from nltk.tokenize import sent_tokenize
from nltk.stem import LancasterStemmer




def start_tokenization(text,tokenizedList,lock,stopWords):
    tbl = dict.fromkeys(i for i in range(sys.maxunicode) if unicodedata.category(chr(i)).startswith('P'))
    text = text.translate(tbl)
    text=text.lower()

    # tknzr = TweetTokenizer(reduce_len=True)
    word = sent_tokenize(text=text,language="english")
    ss = LancasterStemmer()
    stem_list=[]
    for w in word:
        stem_list.append(ss.stem(w))
    
    tokens_without_sw = [word for word in stem_list if word not in stopWords]
    
    with lock:
        tokenizedList.append(' '.join(tokens_without_sw))

