import gzip
import cPickle as pickle

x = {}

#f = gzip.open('../data/klk_fi_1grams_189x.gz')
filename = '/srv/work/klk_fi_1grams_190x.gz'
f = gzip.open(filename)
i = 0
total = 0
for line in f:
    if i % 1000000 == 0:
        print i
    parts = line.split()
    val = int(parts[0])
    total += val
    i += 1
f.close()
print "Total words: %d" % total

f = gzip.open(filename)
i = 0
for line in f:
    if i % 1000000 == 0:
        print i
    parts = line.split()
    key = parts[1].strip().decode('utf-8').lower()
    val = int(parts[0])
    frac = float(val) / total
    if len(key) >= 4 and frac >= 0.00000001:
        x[key] = x.get(key,0) + frac
    i += 1
f.close()
print "%d rows, %d elements in dict, %d words in total" % (i, len(x), total)

print "Starting to save..."
with open('/srv/work/unigrams_1900.pckl','wb') as fout:
    pickle.dump((x,total), fout)
print "Saved."
