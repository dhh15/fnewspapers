import gzip
import cPickle as pickle

x = {}
f = gzip.open('../data/klk_fi_1grams_189x.gz')

i = 0
total = 0
for line in f:
    if i % 1000000 == 0:
        print i
    parts = line.split()
    key = parts[1].strip().decode('utf-8').lower()
    val = int(parts[0])
    total += val
    if len(key) >= 3:
        x[key] = x.get(key,0) + val
    i += 1
print "%d rows, %d elements in dict, %d words in total" % (i, len(x), total)

print "Starting to save..."
with open('/srv/work/unigrams3utf8.pckl','wb') as fout:
    pickle.dump((x,total), fout)
print "Saved."
