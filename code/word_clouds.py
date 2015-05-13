from os import path
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import codecs
import sys

def get_frequencies(filename):
    f = codecs.open(filename, 'r', 'utf-8')
    x = []
    for i, line in enumerate(f):
        if i == 0:
            continue
        parts = line.split(',')
        word = parts[0]
        freq = float(parts[1])
        x.append((word,freq))
    return x

def draw_cloud(freqs, picture_filename, n_words=100):
    wordcloud = WordCloud().generate_from_frequencies(freqs[:n_words])
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.show()
    plt.savefig(picture_filename)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = '../results/keywords_2015-05-13T121302.csv'
    if len(sys.argv) > 2:
        picture_filename = sys.argv[2]
    else:
        picture_filename = '../pics/wordcloud.png'
    freqs = get_frequencies(filename)
    draw_cloud(freqs, picture_filename)
