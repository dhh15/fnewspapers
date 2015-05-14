# -*- coding: utf-8 -*-
import nltk
import codecs
import re
import numpy as np
import cPickle as pickle
import datetime as dt
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
import time

DATA_DIR = "../data/"
DATA_DIR2 = "/srv/data/fnewspapers/"

n_words = 0
CONTEXT = 5

SOCIALIST_ISSNS = ["fk14802", "fk10276", "fk10276", "1458-0926", "fk14794",
                   "fk14940", "fk10173", "fk10459", "fk14854", "fk10105",
                   "fk10445", "fk25048", "fk14799", "fk14860", "fk10401",
                   "fk10206", "fk10180", "fk10397"]

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

def word_freq(filenames, word_prefixes):
    word_prefixes = [word_prefix.lower() for word_prefix in word_prefixes]
    char_count = 0
    wcounts = np.zeros(len(word_prefixes), dtype=float)
    for fn in filenames:
        f = codecs.open(DATA_DIR2 + "nlf_rawtext_fin/" + fn, 'r', 'utf8')
        text = f.read()
        text = text.lower()
        #text = re.sub(u'[^a-zåäö ]', '', text)
        #text = re.sub(u'\s\s+', ' ', text)
        f.close()
        char_count += len(text)
        for i in range(len(word_prefixes)):
            word_prefix = word_prefixes[i]
            wcounts[i] += text.count(word_prefix)
    return wcounts / max(1,char_count)

def context_words(filenames, word_prefix):
    word_prefix = word_prefix.lower()
    for fn in filenames:
        f = codecs.open(DATA_DIR2 + "nlf_rawtext_fin/" + fn, 'r', 'utf8')
        text = f.read()
        text = text.lower()
        text = re.sub(u'[^a-zåäö ]', '', text)
        f.close()
        #tokens = nltk.tokenize.word_tokenize(text)
        tokens = text.split()
        n_words += len(tokens)
        for i, token in enumerate(tokens):
            if token.startswith(word_prefix):
                context = tokens[i-CONTEXT:i] + tokens[i+1:i+CONTEXT]
                yield context

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

def get_filenames(wanted_issns=None, get_others=False, max_n=100000, return_dates=False):
    print "Reading newspaper files..."
    fname = DATA_DIR2 + 'nlf_newspapers_fin.csv'
    names = []
    if get_others:
        other_names = []
    if wanted_issns is not None:
        wanted_issns = set(wanted_issns)
    min_date = dt.datetime(1895,1,1)
    max_date = dt.datetime(1910,12,31)
    with open(fname, 'r') as f:
        i = 0
        for line in f:
            if i == 0:
                i += 1
                continue
            parts = line.split(',')
            name = parts[0]
            issn = parts[1]
            date = dt.datetime.strptime(parts[2], "%Y-%m-%d")
            if date < min_date or date > max_date:
                continue
            if return_dates:
                item = (name, date)
            else:
                item = name

            if wanted_issns is not None:
                if issn in wanted_issns:
                    names.append(item)
                elif get_others:
                    other_names.append(item)
            else:
                names.append(item)
            i += 1
    if not get_others:
        print "%d matching files in total." % len(names)
    else:
        print "(%d, %d) matching files in total." % (len(names), len(other_names))
    print "Read."
    if len(names) > max_n:
        import random
        random.shuffle(names)
        if get_others:
            return names[:max_n], other_names[:max_n]
        else:
            return names[:max_n]
    else:
        if get_others:
            return names, other_names
        else:
            return names

def identify_keywords(freqs):
    print "Loading baseline frequencies..."
    #(bl_freqs, bl_total) = pickle.load(open("/srv/work/unigrams3utf8.pckl", "rb"))
    (bl_fracs, bl_total) = pickle.load(open("/srv/work/unigrams_1900.pckl", "rb"))
    print "Loaded."
    res = []
    for (word, count) in freqs:
        frac = float(count) / n_words
        if word not in bl_fracs:
            continue
        #bl_frac = float(bl_freqs[word]) / bl_total
        bl_frac = float(bl_fracs[word])
        #diff = frac - bl_frac
        # Smoothing
        dummy_count = 0.0000001
        bl_frac += dummy_count
        frac += dummy_count
        if bl_frac > 0.0000001:
            diff = frac / bl_frac
        else:
            print "We shouldn't get here:", bl_frac
            diff = 1
        res.append((diff, word, frac, bl_frac))
    res = sorted(res, key=lambda tup: tup[0])[::-1]
    return res

def frequency_over_time(words):
    start_date = dt.datetime(1895,1,1)
    ts = [start_date+relativedelta(years=i) for i in range(16)]

    t0 = time.time()
    soc_files, other_files = get_filenames(wanted_issns=SOCIALIST_ISSNS, get_others=True, max_n=100000, return_dates=True)
    print "Read filenames in %.2f seconds." % (time.time()-t0)
    soc_freqs = np.zeros((len(ts)-1, len(words)))
    other_freqs = np.zeros((len(ts)-1, len(words)))
    for i in range(len(ts)-1):
        socs = [file_tuple[0] for file_tuple in soc_files if file_tuple[1] >= ts[i] and file_tuple[1] < ts[i+1]]
        soc_freqs[i,:] = word_freq(socs, words)
        others = [file_tuple[0] for file_tuple in other_files if file_tuple[1] >= ts[i] and file_tuple[1] < ts[i+1]]
        other_freqs[i,:] = word_freq(others, words)
    return ts, soc_freqs, other_freqs

def temporal_analysis():
    words = ["sorto", u"ryssä", "nais", "torppar", u"työttömy", "nykyi", "histor", "jumala", "kirkko", "jeesus", u"marx", u"sosialis", u"porwari", u"työ", u"työttömyy", u"työläi", u"työvä", u"kapitalis", u"taantu", u"taistel", u"toveri", u"vallankumou", "torppari", "agitaattori", u"köyhälistö", u"kärsi", "orja", "sort", "sosialidemokraatti", "lakko", "vapau", "voitto"]
    ts, soc_freqs, other_freqs = frequency_over_time(words)
    print 100000 * soc_freqs
    print 100000 * other_freqs
    from matplotlib import rcParams
    rcParams.update({'figure.autolayout': True})
    for i, word in enumerate(words):
        plt.figure(1)
        plt.clf()
        plt.plot(ts[:-1], soc_freqs[:,i], '-x')
        plt.plot(ts[:-1], other_freqs[:,i], '-o')
        max_y = max(np.max(soc_freqs[:,i]), np.max(other_freqs[:,i]))
        plt.ylim((0, max_y*1.05))
        plt.xlabel('Year')
        plt.ylabel('Frequency')
        plt.title(word)
        plt.legend(['Socialist', 'Others'], loc='best')
        plt.savefig('../plots/%s.png' % word)
        date_str = re.sub(" ", "T", str(dt.datetime.now()))[:-7]
        date_str = re.sub(":", "", date_str)
    pickle.dump((ts,soc_freqs,other_freqs,word), open('../plot_data/%s.pckl' % date_str, 'wb'))
    save_csv2(words, soc_freqs, "socialist")
    save_csv2(words, other_freqs, "others")

def save_csv(labels, X, title):
    with codecs.open('../data/timeseries_%s.csv' % title, 'w', 'utf8') as f:
        f.write(",".join(labels) + "\n")
        for i in range(X.shape[0]):
            vals = [str(val) for val in X[i,:]]
            f.write(",".join(vals) + "\n")

def save_csv2(labels, X, ts, title):
    with codecs.open('../data/timeseries2_%s.csv' % title, 'w', 'utf8') as f:
        f.write(",".join(labels) + "\n")
        for i in range(X.shape[0]):
            for j in range(X.shape[1]):
                freq = X[i,j]
                year = ts[i].year
                word = labes[j]
                f.write("%d,%s,%f\n" % (year, word, freq))

def keyword_analysis():
    #print socialist_issns()
    #files = get_filenames(wanted_issn="fk14802")
    files = get_filenames(wanted_issns=SOCIALIST_ISSNS, max_n=50000)
    print files[:5]
    freqs = get_common_words(files)
    kws = identify_keywords(freqs)
    date_str = re.sub(" ", "T", str(dt.datetime.now()))[:-7]
    date_str = re.sub(":", "", date_str)
    
    fout = codecs.open('../results/keywords_%s.csv' % date_str, 'w', 'utf-8')
    fout.write("Word,RelativeFreq,SocialistFreq,CorpusFreq\n")
    N = 3000
    for res in kws[:N]:
        fout.write(("%s,%f,%f,%f\n" % (res[1], res[0], 1000*res[2], 1000*res[3])))#.encode('utf-8'))
    fout.close()

    fout2 = codecs.open('../results/negative_keywords_%s.csv' % date_str, 'w', 'utf-8')
    fout2.write("Word,RelativeFreq,SocialistFreq,CorpusFreq\n")
    for i in range(1,min(N,len(kws))):
        res = kws[-i]
        fout2.write(("%s,%f,%f,%f\n" % (res[1], res[0], 1000*res[2], 1000*res[3])))#.encode('utf-8'))
    fout2.close()
    #for (i,fr) in enumerate(freqs):
    #    print (u"%d\t%d\t%s" % (i+1, fr[1], fr[0])).encode('utf-8')

if __name__ == "__main__":
    #keyword_analysis()
    temporal_analysis()
