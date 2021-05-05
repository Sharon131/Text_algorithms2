import numpy as np
from spacy.lang.pl import Polish
import spacy
import random
import copy

nlp = spacy.load("pl_core_news_sm")


def delta1(a, b):
    if a == b:
        return 0
    else:
        return 1


def delta2(x,y):
    if x == y:
        return 0
    else:
        return 2


def editDistance(x, y, delta):
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
                                   edit_table[k-1, l-1] + delta(x[i], y[j])])

    return edit_table, edit_table[-1][-1]


def getEditDistanceActions(edit_table):
    indx_i = edit_table.shape[0]-1
    indx_j = edit_table.shape[1]-1
    actions = []

    while indx_i > 0 or indx_j > 0:
        if indx_i >= 0 and indx_j >= 0:
            min_value = min(edit_table[indx_i-1, indx_j],
                               edit_table[indx_i, indx_j-1],
                               edit_table[indx_i-1, indx_j-1])
            if indx_i >= 0 and indx_j >= 0 and edit_table[indx_i-1][indx_j-1] == min_value:
                if edit_table[indx_i-1][indx_j-1] == edit_table[indx_i][indx_j]:
                    actions.append('no action')
                else:
                    actions.append('replace')
                indx_i -= 1
                indx_j -= 1
            elif indx_i >= 0 and edit_table[indx_i-1][indx_j] == min_value:
                actions.append('insert')
                indx_i -= 1
            elif indx_j >= 0 and edit_table[indx_i][indx_j-1] == min_value:
                actions.append('delete')
                indx_j -= 1
            else:
                print("Error in finding")
                return None
        elif indx_i == 0:
            actions.append('d')
            indx_j -= 1
        elif indx_j == 0:
            actions.append('i')
            indx_i -= 1
    actions.reverse()
    return actions


def getVisualisation(edit_distance_actions, comparing_word, compared_word):
    word_indx1 = 0
    word_indx2 = 0
    visualisation = [compared_word]
    modified = compared_word
    for action in edit_distance_actions:
        if action == 'insert':
            visualisation.append(modified[:word_indx2] + '*' + comparing_word[word_indx1] + '*' + modified[word_indx2:])
            modified = modified[:word_indx2] + comparing_word[word_indx1] + modified[word_indx2:]
            word_indx1 += 1
            word_indx2 += 1
        elif action == 'delete':
            visualisation.append(modified[:word_indx2] + '**' + modified[word_indx2+1:])
            modified = modified[:word_indx2] + modified[word_indx2+1:]
        elif action == 'replace':
            visualisation.append(modified[:word_indx2] + '*' + comparing_word[word_indx1] + '*' + modified[word_indx2+1:])
            modified = modified[:word_indx2] + comparing_word[word_indx1] + modified[word_indx2+1:]
            word_indx1 += 1
            word_indx2 += 1
        else:
            word_indx1 += 1
            word_indx2 += 1
    visualisation.append(modified)
    return visualisation


def getLcsLen(x, y):
    return (len(x) + len(y) - editDistance(x, y, delta2)[1])/2


def getLongestCommonSubsequence(comparing_word, compared_word):
    edit_table, edit_distance = editDistance(comparing_word, compared_word, delta2)

    actions = getEditDistanceActions(edit_table)
    word_indx = 0
    common = ''

    for action in actions:
        if action == 'insert':
            pass
        elif action == 'delete':
            word_indx += 1
        elif action == 'replace':
            word_indx += 1
        else:
            common += compared_word[word_indx]
            word_indx += 1

    return common


def cutOutRandom(text_list):
    new_text = copy.copy(text_list)

    for i in range(int(len(text_list)*3/100)):
        indx = random.randint(0, len(new_text)-1)
        new_text.pop(indx)
    return new_text


table, distance = editDistance('wojtk', 'wjeek', delta1)
print(table)
print(distance)
edit_distance_actions = getEditDistanceActions(table)
print(edit_distance_actions)
print(getVisualisation(edit_distance_actions, 'wojtk', 'wjeek'))
print(getLcsLen('wojtk', 'wjeek'), getLongestCommonSubsequence('wojtk', 'wjeek'))
print('========================')
print('kloc', 'los')
table1, distance1 = editDistance('kloc', 'los', delta1)
edit_distance_actions1 = getEditDistanceActions(table1)
print(distance1)
print(edit_distance_actions1)
print(getVisualisation(edit_distance_actions1, 'kloc', 'los'))
print(getLcsLen('kloc', 'los'), getLongestCommonSubsequence('kloc', 'los'))
print('Łódź', 'Lodz')
table2, distance2 = editDistance('Łódź', 'Lodz', delta1)
edit_distance_actions2 = getEditDistanceActions(table2)
print(distance2)
print(edit_distance_actions2)
print(getVisualisation(edit_distance_actions2, 'Łódź', 'Lodz'))
print(getLcsLen('Łódź', 'Lodz'), getLongestCommonSubsequence('Łódź', 'Lodz'))
print('kwintesencja', 'quintessence')
table3, distance3 = editDistance('kwintesencja', 'quintessence', delta1)
edit_distance_actions3 = getEditDistanceActions(table3)
print(distance3)
print(edit_distance_actions3)
print(getVisualisation(edit_distance_actions3, 'kwintesencja', 'quintessence'))
print(getLcsLen('kwintesencja', 'quintessence'), getLongestCommonSubsequence('kwintesencja', 'quintessence'))
print('ATGAATCTTACCGCCTCG', 'ATGAGGCTCTGGCCCCTG')
table4, distance4 = editDistance('ATGAATCTTACCGCCTCG', 'ATGAGGCTCTGGCCCCTG', delta1)
edit_distance_actions4 = getEditDistanceActions(table4)
print(distance4)
print(edit_distance_actions4)
print(getVisualisation(edit_distance_actions4, 'ATGAATCTTACCGCCTCG', 'ATGAGGCTCTGGCCCCTG'))
print(getLcsLen('ATGAATCTTACCGCCTCG', 'ATGAGGCTCTGGCCCCTG'), getLongestCommonSubsequence('ATGAATCTTACCGCCTCG', 'ATGAGGCTCTGGCCCCTG'))


# doc = nlp("Apple szuka GB startupu do kupienia za $1 billion")
# for token in doc:
#     print(token)
file = open('romeo-i-julia-700.txt', encoding='utf-8')
text = file.read()
file.close()
tokens = nlp(text)
for token in tokens:
    print(token.text, bytearray(token.text, encoding='utf-8'))
print(list(tokens))
new_tokens = cutOutRandom(list(tokens))

print(len(tokens))
print(len(new_tokens))
