# -*- coding: utf-8 -*-
import nltk
import codecs
import re
import numpy as np
import cPickle as pickle
import datetime as dt

DATA_DIR = "../data/"
DATA_DIR2 = "/srv/data/fnewspapers/"

n_words = 0

def get_tokens(filenames):
    global n_words
    for fn in filenames:
        f = codecs.open(DATA_DIR2 + "nlf_rawtext_fin/" + fn, 'r', 'utf8')
        text = f.read()
        text = text.lower()
        text = re.sub(u'[^a-zåäö ]', '', text)
        f.close()
        #tokens = nltk.tokenize.word_tokenize(text)
        tokens = text.split()
        n_words += len(tokens)
        for token in tokens:
            if len(token) > 2:
                yield token

def get_common_words(filenames, n=10000):
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

def get_filenames(wanted_issns=None, max_n=100000):
    print "Reading newspaper files..."
    fname = DATA_DIR2 + 'nlf_newspapers_fin.csv'
    names = []
    wanted_issns = set(wanted_issns)
    with open(fname, 'r') as f:
        i = 0
        for line in f:
            if i == 0:
                i += 1
                continue
            parts = line.split(',')
            name = parts[0]
            issn = parts[1]
            if wanted_issns is None or issn in wanted_issns:
                names.append(name)
            i += 1
    print "%d matching files in total." % len(names)
    print "Read."
    if len(names) > max_n:
        import random
        random.shuffle(names)
        return names[:max_n]
    else:
        return names

def identify_keywords(freqs):
    print "Loading baseline frequencies..."
    (bl_freqs, bl_total) = pickle.load(open("/srv/work/unigrams3utf8.pckl", "rb"))
    print "Loaded."
    res = []
    for (word, count) in freqs:
        frac = float(count) / n_words
        if word not in bl_freqs:
            continue
        bl_frac = float(bl_freqs[word]) / bl_total
        #diff = frac - bl_frac
        if bl_frac > 0.0000001:
            diff = frac / bl_frac
        else:
            diff = 1
        res.append((diff, word, frac, bl_frac))
    res = sorted(res, key=lambda tup: tup[0])[::-1]
    return res

if __name__ == "__main__":
    #print socialist_issns()
    #files = get_filenames(wanted_issn="fk14802")
    all_issns = ["fk14802", "fk10276", "fk10276", "1458-0926", "fk14794", "fk14940", "fk10173", "fk10459", "fk14854", "fk10105", "fk10445", "fk25048", "fk14799", "fk14860", "fk10401", "fk10206", "fk10180", "fk10397"]
    files = get_filenames(wanted_issns=all_issns, max_n=50000)
    print files[:5]
    freqs = get_common_words(files)
    kws = identify_keywords(freqs)
    date_str = re.sub(" ", "T", str(dt.datetime.now()))[:-7]
    date_str = re.sub(":", "", date_str)
    
    fout = codecs.open('../results/keywords_%s.csv' % date_str, 'w', 'utf-8')
    fout.write("Word,RelativeFreq,SocialistFreq,CorpusFreq\n")
    N = 1000
    for res in kws[:N]:
        fout.write(("%s,%f,%f,%f\n" % (res[1], 1000*res[0], 1000*res[2], 1000*res[3])))#.encode('utf-8'))
    fout.close()

    fout2 = codecs.open('../results/negative_keywords_%s.csv' % date_str, 'w', 'utf-8')
    fout2.write("Word,RelativeFreq,SocialistFreq,CorpusFreq\n")
    for i in range(1,min(N,len(kws))):
        res = kws[-i]
        fout2.write(("%s,%f,%f,%f\n" % (res[1], 1000*res[0], 1000*res[2], 1000*res[3])))#.encode('utf-8'))
    fout2.close()
    #for (i,fr) in enumerate(freqs):
    #    print (u"%d\t%d\t%s" % (i+1, fr[1], fr[0])).encode('utf-8')
