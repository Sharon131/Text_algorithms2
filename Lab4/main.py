import numpy as np
import spacy
import random
import copy

nlp = spacy.load("pl_core_news_sm")


def delta1(a, b):
    if a == b:
        return 0
    else:
        return 1


def delta2(x, y):
    if x == y:
        return 0
    else:
        return 2


def delta3(x, y):
    if x.text == y.text:
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


def getLcsLenStrings(x, y):
    return (len(x) + len(y) - editDistance(x, y, delta2)[1])/2


def getLcsLenTokens(x, y):
    return (len(x) + len(y) - editDistance(x, y, delta3)[1])/2


def getLongestCommonSubsequenceStrings(comparing_word, compared_word):
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


# def getLongestCommonSubsequenceStrings(comparing_word, compared_word):
#     return getLongestCommonSubsequence(comparing_word, compared_word, delta2)


def getLongestCommonSubsequenceTokens(comparing_text, compared_text):
    edit_table, edit_distance = editDistance(comparing_text, compared_text, delta3)

    actions = getEditDistanceActions(edit_table)
    word_indx = 0
    common = []

    for action in actions:
        if action == 'insert':
            pass
        elif action == 'delete':
            word_indx += 1
        elif action == 'replace':
            word_indx += 1
        else:
            common.append(compared_text[word_indx])
            word_indx += 1

    return common


def cutOutRandomAndSaveToFile(text_list, filename):
    new_text = copy.copy(text_list)

    for i in range(int(len(text_list)*3/100)):
        indx = random.randint(0, len(new_text)-1)
        new_text.pop(indx)

    file = open(filename, mode='w', encoding='utf-8')
    for i in range(len(new_text)):
        file.write(new_text[i].text)
        file.write(new_text[i].whitespace_)
    file.close()
    return new_text


def diffTokens(comparing_text, compared_text):
    common = getLongestCommonSubsequenceTokens(comparing_text, compared_text)
    diffs = []
    text_indx1 = 0
    text_indx2 = 0
    line_number1 = 1
    line_number2 = 1

    for token in common:
        while comparing_text[text_indx1].text != token.text or compared_text[text_indx2].text != token.text:
            if comparing_text[text_indx1].text != token.text:
                diffs.append('<<<<<<<<<< ' + comparing_text[text_indx1].text + ', line ' + str(line_number1))
                line_number1 += comparing_text[text_indx1].text.count('\n')
                text_indx1 += 1
            if compared_text[text_indx2].text != token.text:
                diffs.append('>>>>>>>>>> ' + compared_text[text_indx2].text + ', line ' + str(line_number2))
                line_number2 += compared_text[text_indx2].text.count('\n')
                text_indx2 += 1
            if text_indx1 >= len(comparing_text) or text_indx2 >= len(compared_text):
                print('Error in diff')
                return
        line_number1 += comparing_text[text_indx1].text.count('\n')
        line_number2 += compared_text[text_indx2].text.count('\n')
        text_indx1 += 1
        text_indx2 += 1
    return diffs


# Zadanie 1
table, distance = editDistance('wojtk', 'wjeek', delta1)
print(table)
print(distance)
edit_distance_actions = getEditDistanceActions(table)
print(edit_distance_actions)
print(getVisualisation(edit_distance_actions, 'wojtk', 'wjeek'))
print(getLcsLenStrings('wojtk', 'wjeek'), getLongestCommonSubsequenceStrings('wojtk', 'wjeek'))
print('========================')
print('kloc', 'los')
table1, distance1 = editDistance('kloc', 'los', delta1)
edit_distance_actions1 = getEditDistanceActions(table1)
print(distance1)
print(edit_distance_actions1)
print(getVisualisation(edit_distance_actions1, 'kloc', 'los'))
print(getLcsLenStrings('kloc', 'los'), getLongestCommonSubsequenceStrings('kloc', 'los'))
print('Łódź', 'Lodz')
table2, distance2 = editDistance('Łódź', 'Lodz', delta1)
edit_distance_actions2 = getEditDistanceActions(table2)
print(distance2)
print(edit_distance_actions2)
print(getVisualisation(edit_distance_actions2, 'Łódź', 'Lodz'))
print(getLcsLenStrings('Łódź', 'Lodz'), getLongestCommonSubsequenceStrings('Łódź', 'Lodz'))
print('kwintesencja', 'quintessence')
table3, distance3 = editDistance('kwintesencja', 'quintessence', delta1)
edit_distance_actions3 = getEditDistanceActions(table3)
print(distance3)
print(edit_distance_actions3)
print(getVisualisation(edit_distance_actions3, 'kwintesencja', 'quintessence'))
print(getLcsLenStrings('kwintesencja', 'quintessence'), getLongestCommonSubsequenceStrings('kwintesencja', 'quintessence'))
print('ATGAATCTTACCGCCTCG', 'ATGAGGCTCTGGCCCCTG')
table4, distance4 = editDistance('ATGAATCTTACCGCCTCG', 'ATGAGGCTCTGGCCCCTG', delta1)
edit_distance_actions4 = getEditDistanceActions(table4)
print(distance4)
print(edit_distance_actions4)
print(getVisualisation(edit_distance_actions4, 'ATGAATCTTACCGCCTCG', 'ATGAGGCTCTGGCCCCTG'))
print(getLcsLenStrings('ATGAATCTTACCGCCTCG', 'ATGAGGCTCTGGCCCCTG'), getLongestCommonSubsequenceStrings('ATGAATCTTACCGCCTCG', 'ATGAGGCTCTGGCCCCTG'))

# Zadanie 2
file = open('romeo-i-julia-700.txt', encoding='utf-8')
# tokens = nlp(text_original)
text_original = list(nlp(file.read()))
file.close()
file = open('romeo-i-julia-700-1.txt', encoding='utf-8')
text1 = list(nlp(file.read()))
file.close()
file = open('romeo-i-julia-700-2.txt', encoding='utf-8')
text2 = list(nlp(file.read()))
file.close()
print(text_original[0].text, text1[1].text)
print(text_original[0].text == text1[0].text)
print(text_original[0].text == text1[1].text)
print(len(text_original))
print(len(text1))
print(len(text2))
print(getLcsLenTokens(text_original, text_original))
print(getLcsLenTokens(text_original, text1))
print(getLcsLenTokens(text_original, text2))
print(getLcsLenTokens(text1, text2))

print('===================')
diffs_list = diffTokens(text1, text2)
for diff in diffs_list:
    print(diff)
