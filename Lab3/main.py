from bitarray import bitarray
from bitarray import util
import random
import string
import os

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

    return huffmanTree(char_frequency)


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
    length = len(whole_encoding)
    bits_count = util.int2ba(length, 32)
    return bits_count + whole_encoding


def decodeOneCharacter(encoded_text, huffman_node):
    if huffman_node.child1 is None:
        return huffman_node.character, encoded_text
    elif encoded_text[0] is True and huffman_node.child1 is not None:
        return decodeOneCharacter(encoded_text[1:], huffman_node.child1)
    elif encoded_text[0] is False and huffman_node.child2 is not None:
        return decodeOneCharacter(encoded_text[1:], huffman_node.child2)


def decodeText(encoded_text, huffman_tree):
    decoded_text = ''
    while len(encoded_text) > 0:
        character, encoded_text = decodeOneCharacter(encoded_text, huffman_tree)
        decoded_text = decoded_text + character

    return decoded_text


def extractEncodedText(bits):
    upper_bound = util.ba2int(bits[:32])
    return bits[32:32 + upper_bound]


def printHuffmanTree(node, prefix = ""):

    print(prefix, node.weight)
    if node.character is not None:
        print(prefix, node.character)

    if node.child1 is not None:
        printHuffmanTree(prefix + "\t", node.child1)

    if node.child2 is not None:
        printHuffmanTree(prefix+"\t", node.child2)


# testing
node2 = staticHuffman("abracadabra")

printHuffmanTree(node2)

file = open("encoded.txt", mode='wb')
encodeWholeText("abracadabra", node2).tofile(file)
file.close()

print(encodeWholeText("abracadabra", node2)[32:])

a = bitarray()
file = open("encoded.txt", mode='rb')
a.fromfile(file)
file.close()
coding = extractEncodedText(a)
print(coding)

print(decodeText(coding, node2))
print(decodeText(encodeWholeText("abracadabra", node2)[32:], node2))
print("=================")

# TODO: dodać zapisywanie drzewa huffmana do pliku również?
# read all files
# file = open(guttenbergFileName1kB, mode='r', encoding='utf-8')
# guttenberg_1kB = file.read()
# file.close()


# file = open(guttenbergFileName10kB, mode='r', encoding='utf-8')
# guttenberg_10kB = file.read()
# file.close()

file = open(guttenbergFileName1MB, mode='r', encoding='utf-8')
guttenberg_1MB = file.read()
file.close()

node_guttenberg_1MB = staticHuffman(guttenberg_1MB)
encoding_guttenberg_1MB = encodeWholeText(guttenberg_1MB, node_guttenberg_1MB)

file = open("quo_vadis_1MB_encoded.txt", mode='wb')
encoding_guttenberg_1MB.tofile(file)
file.close()

# print(os.path.getsize('quo_vadis_1MB.txt')/1024, " kB")
