from collections import defaultdict
from bitarray import bitarray
from bitarray import util
import random
import string
import os
import time

guttenbergFileName1kB = "quo_vadis_1kB.txt"
guttenbergFileName10kB = "quo_vadis_10kB.txt"
guttenbergFileName100kB = "quo_vadis_100kB.txt"
guttenbergFileName1MB = "quo_vadis_1MB.txt"
githubFileName1kB = "github_1kB.txt"
githubFileName10kB = "github_10kB.txt"
githubFileName100kB = "github_100kB.txt"
githubFileName1MB = "github_1MB.txt"
randomFileName1kB = "random_chars_1kB.txt"
randomFileName10kB = "random_chars_10kB.txt"
randomFileName100kB = "random_chars_100kB.txt"
randomFileName1MB = "random_chars_1MB.txt"


def getRandomCharsAndSaveToFile(length, filename):
    letters = string.printable
    characters = ''.join(random.choice(letters) for i in range(length))

    text_file = open(filename, "w")
    text_file.write(characters)
    text_file.close()


class Node:
    def __init__(self, weight, character=None, child1=None, child2=None):
        self.character = character
        self.child1 = child1
        self.child2 = child2
        self.weight = weight


def popLeastWeightFrom(first_list, second_list):
    if len(first_list) == 0:
        return second_list.pop(0)
    elif len(second_list) == 0:
        return first_list.pop(0)
    elif second_list[0].weight <= first_list[0].weight:
        return second_list.pop(0)
    else:
        return first_list.pop(0)


def huffmanTree(letter_counts):
    nodes = []
    for a, weight in letter_counts.items():
        nodes.append(Node(weight, character=a))
    internal_nodes = []
    leafs = sorted(nodes, key=lambda n: n.weight)
    while len(leafs) + len(internal_nodes) > 1:
        element_1 = popLeastWeightFrom(leafs, internal_nodes)
        element_2 = popLeastWeightFrom(leafs, internal_nodes)
        internal_nodes.append(Node(element_1.weight + element_2.weight, child1=element_1, child2=element_2))
    return internal_nodes[0]


def staticHuffman(text):
    char_frequency = dict()

    for character in text:
        if character not in char_frequency.keys():
            char_frequency[character] = 0

        char_frequency[character] = char_frequency[character] + 1

    return huffmanTree(char_frequency), char_frequency


def getCharEncoding(character, huffman_node, coding):
    if huffman_node.character is not None and huffman_node.character == character:
        return coding
    elif huffman_node.character is not None and huffman_node.character != character:
        return None
    elif huffman_node.character is None:
        first_code = getCharEncoding(character, huffman_node.child1, coding)
        second_code = getCharEncoding(character, huffman_node.child2, coding)

        if first_code is not None:
            coding.insert(0, 1)
            return coding
        elif second_code is not None:
            coding.insert(0, 0)
            return coding
        else:
            return None


def encodeWholeText(text, huffman_tree):
    whole_encoding = bitarray()
    for character in text:
        encoding = getCharEncoding(character, huffman_tree, bitarray())
        whole_encoding.extend(encoding)
    return whole_encoding


def decodeOneCharacter(encoded_text, indx, huffman_node):
    if huffman_node.child1 is None:
        return huffman_node.character, indx
    elif encoded_text[indx] is True and huffman_node.child1 is not None:
        return decodeOneCharacter(encoded_text, indx+1, huffman_node.child1)
    elif encoded_text[indx] is False and huffman_node.child2 is not None:
        return decodeOneCharacter(encoded_text, indx+1, huffman_node.child2)


def decodeText(encoded_text, huffman_tree):
    decoded_text = ''
    indx = 0
    while indx < len(encoded_text):
        character, indx = decodeOneCharacter(encoded_text, indx, huffman_tree)
        decoded_text = decoded_text + character

    return decoded_text


def printHuffmanTree(node, prefix=""):

    print(prefix, node.weight)
    if node.character is not None:
        print(prefix, node.character)

    if node.child1 is not None:
        printHuffmanTree(node.child1, prefix + "\t")

    if node.child2 is not None:
        printHuffmanTree(node.child2, prefix+"\t")


def getTextFromFile(file_name):
    file_handle = open(file_name, mode='r', encoding='utf-8')
    text = file_handle.read()
    file_handle.close()
    return text


def writeEncodedTextToFile(text, characters_freqs, file_name):
    coding = bitarray()
    encoded_text_len = util.int2ba(len(text), length=64)

    for character in characters_freqs.keys():
        character_bits = util.int2ba(ord(character))
        character_len = util.int2ba(len(character_bits), length=5)
        character_weight = util.int2ba(characters_freqs.get(character))
        weight_len = util.int2ba(len(character_weight), length=5)
        coding += character_len + character_bits + weight_len + character_weight

    to_write = encoded_text_len + util.int2ba(len(coding), length=64) + coding + text

    file_handle = open(file_name, mode='wb')
    to_write.tofile(file_handle)
    file_handle.close()


def putCharacterToHuffmanTree(node, indx, character, encoding):

    if len(encoding) == 0:
        node.character = character
    elif encoding[indx] is True:
        if node.child1 is None:
            node.child1 = Node(1)
        putCharacterToHuffmanTree(node.child1, indx+1, character, encoding)
    elif encoding[indx] is False:
        if node.child2 is None:
            node.child2 = Node(1)
        putCharacterToHuffmanTree(node.child2, indx+1, character, encoding)

    return node


def readEncodedTextFromFile(file_name):
    bits_read = bitarray()
    file = open(file_name, mode='rb')
    bits_read.fromfile(file)
    file.close()

    encoded_text_len = util.ba2int(bits_read[:64])
    coding_len = util.ba2int(bits_read[64:128])
    coding = bits_read[128:128+coding_len]
    encoded_text = bits_read[128+coding_len:128+coding_len+encoded_text_len]

    characters_freqs = dict()
    indx = 0
    while indx < coding_len:
        character_length = util.ba2int(coding[indx:indx+5])
        indx += 5
        character = chr(util.ba2int(coding[indx:indx+character_length]))
        indx += character_length
        character_weight_len = util.ba2int(coding[indx:indx+5])
        indx += 5
        character_weight = util.ba2int(coding[indx:indx+character_weight_len])
        indx += character_weight_len
        characters_freqs[character] = character_weight

    huffman_tree = huffmanTree(characters_freqs)
    decoded_text = decodeText(encoded_text, huffman_tree)
    return decoded_text, huffman_tree


def encodeWithTimeMeasurement(text, filename):
    start1 = time.perf_counter_ns()
    node, characters_freqs = staticHuffman(text)
    text_encoded = encodeWholeText(text, node)
    end1 = time.perf_counter_ns()
    writeEncodedTextToFile(text_encoded, characters_freqs, filename)
    start2 = time.perf_counter_ns()
    readEncodedTextFromFile(filename)
    end2 = time.perf_counter_ns()
    return (end1-start1)/1000000, (end2-start2)/1000000


# testing
node2, characters_freqs = staticHuffman("abracadabra")
printHuffmanTree(node2)
example_encoded = encodeWholeText("abracadabra", node2)
print(example_encoded)
print(decodeText(example_encoded, node2))
writeEncodedTextToFile(example_encoded, characters_freqs, 'example.txt')
decoded_text, huffman_tree = readEncodedTextFromFile('example.txt')
print(decoded_text)
printHuffmanTree(huffman_tree)
print("=================")

# read gutenberg files
# guttenberg_1kB = getTextFromFile(guttenbergFileName1kB)
# guttenberg_10kB = getTextFromFile(guttenbergFileName10kB)
# guttenberg_100kB = getTextFromFile(guttenbergFileName100kB)
# guttenberg_1MB = getTextFromFile(guttenbergFileName1MB)
#
# guttenberg_1kB_time1, guttenberg_1kB_time2 = encodeWithTimeMeasurement(guttenberg_1kB, 'guttenberg_1kB_encoded.txt')
# guttenberg_10kB_time1, guttenberg_10kB_time2 = encodeWithTimeMeasurement(guttenberg_10kB, 'guttenberg_10kB_encoded.txt')
# guttenberg_100kB_time1, guttenberg_100kB_time2 = encodeWithTimeMeasurement(guttenberg_100kB, 'guttenberg_100kB_encoded.txt')
# guttenberg_1MB_time1, guttenberg_1MB_time2 = encodeWithTimeMeasurement(guttenberg_1MB, 'guttenberg_1MB_encoded.txt')
#
# print('guttenberg 1kB ratio', (1-os.path.getsize('guttenberg_1kB_encoded.txt')/os.path.getsize('quo_vadis_1kB.txt'))*100)
# print('guttenberg 10kB ratio', (1-os.path.getsize('guttenberg_10kB_encoded.txt')/os.path.getsize('quo_vadis_10kB.txt'))*100)
# print('guttenberg 100kB ratio', (1-os.path.getsize('guttenberg_100kB_encoded.txt')/os.path.getsize('quo_vadis_100kB.txt'))*100)
# print('guttenberg 1MB ratio', (1-os.path.getsize('guttenberg_1MB_encoded.txt')/os.path.getsize('quo_vadis_1MB.txt'))*100)
# print('guttenberg 1kB time', guttenberg_1kB_time1, guttenberg_1kB_time2)
# print('guttenberg 10kB time', guttenberg_10kB_time1, guttenberg_10kB_time2)
# print('guttenberg 100kB time', guttenberg_100kB_time1, guttenberg_100kB_time2)
# print('guttenberg 1MB time', guttenberg_1MB_time1, guttenberg_1MB_time2)
#
# # gihub files
# github_1kB = getTextFromFile(githubFileName1kB)
# github_10kB = getTextFromFile(githubFileName10kB)
# github_100kB = getTextFromFile(githubFileName100kB)
# github_1MB = getTextFromFile(githubFileName1MB)
#
# github_1kB_time1, github_1kB_time2 = encodeWithTimeMeasurement(github_1kB, 'github_1kB_encoded.txt')
# github_10kB_time1, github_10kB_time2 = encodeWithTimeMeasurement(github_10kB, 'github_10kB_encoded.txt')
# github_100kB_time1, github_100kB_time2 = encodeWithTimeMeasurement(github_100kB, 'github_100kB_encoded.txt')
# github_1MB_time1, github_1MB_time2 = encodeWithTimeMeasurement(github_1MB, 'github_1MB_encoded.txt')
#
# print('github 1kB ratio', (1-os.path.getsize('github_1kB_encoded.txt')/os.path.getsize('github_1kB.txt'))*100)
# print('github 10kB ratio', (1-os.path.getsize('github_10kB_encoded.txt')/os.path.getsize('github_10kB.txt'))*100)
# print('github 100kB ratio', (1-os.path.getsize('github_100kB_encoded.txt')/os.path.getsize('github_100kB.txt'))*100)
# print('github 1MB ratio', (1-os.path.getsize('github_1MB_encoded.txt')/os.path.getsize('github_1MB.txt'))*100)
# print('github 1kB time', github_1kB_time1, github_1kB_time2)
# print('github 10kB time', github_10kB_time1, github_10kB_time2)
# print('github 100kB time', github_100kB_time1, github_100kB_time2)
# print('github 1MB time', github_1MB_time1, github_1MB_time2)
#
# random_1kB = getTextFromFile(randomFileName1kB)
# random_10kB = getTextFromFile(randomFileName10kB)
# random_100kB = getTextFromFile(randomFileName100kB)
# random_1MB = getTextFromFile(randomFileName1MB)
#
# random_1kB_time1, random_1kB_time2 = encodeWithTimeMeasurement(random_1kB, 'random_1kB_encoded.txt')
# random_10kB_time1, random_10kB_time2 = encodeWithTimeMeasurement(random_10kB, 'random_10kB_encoded.txt')
# random_100kB_time1, random_100kB_time2 = encodeWithTimeMeasurement(random_100kB, 'random_100kB_encoded.txt')
# random_1MB_time1, random_1MB_time2 = encodeWithTimeMeasurement(random_1MB, 'random_1MB_encoded.txt')
#
# print('random 1kB ratio', (1-os.path.getsize('random_1kB_encoded.txt')/os.path.getsize(randomFileName1kB))*100)
# print('random 10kB ratio', (1-os.path.getsize('random_10kB_encoded.txt')/os.path.getsize(randomFileName10kB))*100)
# print('random 100kB ratio', (1-os.path.getsize('random_100kB_encoded.txt')/os.path.getsize(randomFileName100kB))*100)
# print('random 1MB ratio', (1-os.path.getsize('random_1MB_encoded.txt')/os.path.getsize(randomFileName1MB))*100)
# print('random 1kB time', random_1kB_time1, random_1kB_time2)
# print('random 10kB time', random_10kB_time1, random_10kB_time2)
# print('random 100kB time', random_100kB_time1, random_100kB_time2)
# print('random 1MB time', random_1MB_time1, random_1MB_time2)
