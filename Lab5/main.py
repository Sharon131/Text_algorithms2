import time
from sklearn.cluster import DBSCAN
from collections import defaultdict
import numpy as np
import spacy

nlp = spacy.load("pl_core_news_sm")


def delta(x, y):
    if x == y:
        return 1
    else:
        return 0


def delta1(a, b):
    if a == b:
        return 0
    else:
        return 1


def LCS(x, y):
    edit_table = np.zeros((len(x) + 1, len(y) + 1))
    max_num = 0
    max_num_indx = [0, 0]

    for i in range(len(x)+1):
        edit_table[i, 0] = 0
    for i in range(len(y)+1):
        edit_table[0, i] = 0

    for i in range(len(x)):
        k = i + 1
        for j in range(len(y)):
            l = j + 1
            if delta(x[i], y[j]):
                edit_table[k, l] = edit_table[k-1, l-1] + 1
            else:
                edit_table[k, l] = 0
            if edit_table[k, l] > max_num:
                max_num = edit_table[k, l]
                max_num_indx[0] = k
                max_num_indx[1] = l

    return 1 - edit_table[max_num_indx[0], max_num_indx[1]]/max(len(x), len(y))


def n_grams(x, num=2):
    return [x[i:i+num] for i in range(len(x)-num+1)]


def dice(x, y, num=2):
    ngrams_x = set(n_grams(x, num))
    ngrams_y = set(n_grams(y, num))
    comm = []

    for ngram in ngrams_x:
        if ngram in ngrams_y:
            comm.append(ngram)

    return 1 - (2*len(comm))/(len(ngrams_x)+len(ngrams_y))


def vectorLength(v):
    length = 0
    for ngram in v.keys():
        length += v[ngram]**2
    return np.sqrt(length)


def cosineMetric(x, y, num=2):
    ngrams_x = set(n_grams(x, num))
    ngrams_y = set(n_grams(y, num))

    ngrams_x_freq = defaultdict(lambda: 0)
    ngrams_y_freq = defaultdict(lambda: 0)
    for ngram in ngrams_x:
        ngrams_x_freq[ngram] += 1
    for ngram in ngrams_y:
        ngrams_y_freq[ngram] += 1

    scalar = 0

    for ngram in set(ngrams_x_freq.keys()).union(set(ngrams_y_freq.keys())):
        scalar += ngrams_x_freq[ngram] * ngrams_y_freq[ngram]

    return 1 - scalar/(vectorLength(ngrams_x_freq)*vectorLength(ngrams_y_freq))


def editDistance(x, y):
    edit_table = np.zeros((len(x)+1, len(y)+1))
    for i in range(len(x)+1):
        edit_table[i, 0] = i
    for i in range(len(y)+1):
        edit_table[0, i] = i

    for i in range(len(x)):
        k = i + 1
        for j in range(len(y)):
            l = j + 1
            edit_table[k, l] = min([edit_table[k-1, l] + 1,
                                   edit_table[k, l-1] + 1,
                                   edit_table[k-1, l-1] + delta1(x[i], y[j])])

    return edit_table[-1][-1]/max(len(x), len(y))


def getStopListWithMostFrequentTokens(text):
    freqs = defaultdict(lambda: 0)
    stoplist = []

    for token in text:
        freqs[token.text] += 1

    for word in freqs.keys():
        if freqs.get(word)/max(freqs.values()) > 0.15 and freqs.get(word) > 1:
            stoplist.append(word)

    # print(freqs)
    return stoplist


def convertTextToLines(tokens, use_stoplist=False, stoplist=None):
    lines = []
    indx = 0
    new_line = True
    for token in tokens:
        if not use_stoplist or token.text not in stoplist:
            if new_line:
                lines.append('')
                new_line = False
            lines[indx] += token.text

        if '\n' in token.text:
            indx += 1
            new_line = True

    return lines


def getDistanceMatrix(lines, distance_functions):
    distances = [[0 for j in range(len(lines))] for i in range(len(lines))]
    for i in range(len(lines)):
        for j in range(i, len(lines)):
            if i != j:
                distance = distance_functions(lines[i], lines[j])
                distances[i][j] = distance
                distances[j][i] = distance
    return distances


def getClustersValues(lines, clusters):
    prev_cluster = clusters[0]
    text = ''
    for i in range(len(clusters)):
        if prev_cluster != clusters[i]:
            text += "\n######\n\n"
            prev_cluster = clusters[i]
        text += lines[i] + '\n'
    return text


def runClusteringFor(lines_of_text, metric, output_filename, eps=0.5):
    start = time.perf_counter_ns()
    distances = getDistanceMatrix(lines_of_text, metric)
    clustering = DBSCAN(eps=eps, min_samples=1).fit(distances)
    end = time.perf_counter_ns()
    values = getClustersValues(lines_of_text, list(clustering.labels_))
    # print(values)
    print('Time taken: ', (end - start) / 1000000, ' ms')
    file = open(output_filename, mode='w')
    file.write(values)
    file.close()


# test
# print(LCS("abudabi", "aabii"))
# print(n_grams("abudabi", 2))
# print(n_grams("aabii", 2))
# print(n_grams("abudabi", 3))
# print(dice("abudabi", "abii", 2))

file = open("lines.txt", mode='r')
text_all = list(nlp(file.read(10370)))      # equals first 100 lines
file.close()

# prepare data
stoplist = getStopListWithMostFrequentTokens(text_all)
# print(stoplist)
lines = convertTextToLines(text_all)
lines_stoplist = convertTextToLines(text_all, True, stoplist)

# DICE coefficient

print('Dice not using stoplist')
runClusteringFor(lines, dice, 'dice_clusters.txt')

print('Dice using stoplist')
runClusteringFor(lines_stoplist, dice, 'dice_clusters_using_stoplist.txt')

# cosine metric
print('Cosine not using stoplist')
runClusteringFor(lines, cosineMetric, 'cosine_clusters.txt')

print('Cosine using stoplist')
runClusteringFor(lines_stoplist, cosineMetric, 'cosine_clusters_using_stoplist.txt')

# normalized lavenshtein metric
print('Lavenshtein not using stoplist')
runClusteringFor(lines, editDistance, 'lavenshtein_clusters.txt')

print('Lavenshtein using stoplist')
runClusteringFor(lines_stoplist, editDistance, 'lavenshtein_clusters_using_stoplist.txt')

# normalized LCS metric
print('LCS not using stoplist')
runClusteringFor(lines, LCS, 'lcs_clusters.txt')

print('LCS using stoplist')
runClusteringFor(lines_stoplist, LCS, 'lcs_clusters_using_stoplist.txt')