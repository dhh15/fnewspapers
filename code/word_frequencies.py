# -*- coding: utf-8 -*-
import nltk
import codecs
import re
import numpy as np
import pandas as pd

DATA_DIR = "../../data/"
DATA_DIR2 = "../../data/nlf_rawtext_fin_2015/nlf_rawtext_fin/"

def get_tokens(filenames):
    for fn in filenames:
        f = codecs.open(DATA_DIR2 + fn, 'r', 'utf8')
        text = f.read()
        text = text.lower()
        text = re.sub(u'[^a-zåäö ]', '', text)
        f.close()
        tokens = nltk.tokenize.word_tokenize(text)
        for token in tokens:
            if len(token) > 2:
                yield token

def get_common_words(filenames, n=300):
    """
    Get n most frequent words from given files and their occurrences.
    """
    tokens = get_tokens(filenames)
    fdist = nltk.FreqDist(tokens)
    return fdist.most_common(n)

def socialist_issns():
    sis = []
    f = open(DATA_DIR + "socialist_papers.csv", 'r')
    for line in f:
        parts = line.split(';')
        sis.append(parts[2])
    return sis

def get_filenames():
    print "Reading newspaper files..."
    fname = DATA_DIR + 'nlf_newspapers_fin.csv'
    data = pd.read_csv(fname, delimiter=',', header=0)
    print "Read."
    return data['Filename'][:3000]

if __name__ == "__main__":
    print socialist_issns()
    files = get_filenames()
    print files
    freqs = get_common_words(files)
    for (i,fr) in enumerate(freqs):
        print "%d\t%d\t%s" % (i+1, fr[1], fr[0])
