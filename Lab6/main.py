from collections import defaultdict
import queue
import time
from PIL import Image

first_pattern = ["th", "th"]
second_pattern = ["t h", "t h"]


class TrieNode:

    def __init__(self, value):
        self.node_value = value
        self.list_of_children = defaultdict(lambda: None)
        self.fail_link = None
        self.pattern_no = None

    def addPatternRecursive(self, text, index, pattern_no):
        if index >= len(text):
            if self.pattern_no is None:
                self.pattern_no = pattern_no
            return
        if text[index] not in self.list_of_children.keys():
            self.list_of_children[text[index]] = TrieNode(text[index])
        self.list_of_children[text[index]].addPatternRecursive(text, index+1, pattern_no)

    def addPattern(self, text, pattern_no):
        self.addPatternRecursive(text, 0, pattern_no)

    def printChildren(self, level):
        for child in self.list_of_children.values():
            if child != self:
                print("level: ", level+1, " value: ", child.node_value, " fail_link: ", child.fail_link.node_value)
                child.printChildren(level+1)


def buildFailLinks(root_node, alphabet):
    nodes_queue = queue.Queue()

    for character in alphabet:
        if character in root_node.list_of_children.keys():
            child = root_node.list_of_children[character]
            child.fail_link = root_node
            nodes_queue.put(child)
        else:
            root_node.list_of_children[character] = root_node

    while not nodes_queue.empty():
        curr_node = nodes_queue.get()
        for letter in alphabet:
            if letter in curr_node.list_of_children.keys():
                next_node = curr_node.list_of_children[letter]
                nodes_queue.put(next_node)
                fail_link = curr_node.fail_link
                while letter not in fail_link.list_of_children.keys():
                    fail_link = fail_link.fail_link

                next_node.fail_link = fail_link.list_of_children[letter]


# patterns should be unique
def buildTrieFor2DPattern(patterns):
    alphabet = set()
    for pattern in patterns:
        for character in pattern:
            alphabet.add(character)

    trie = TrieNode("root")
    trie.list_of_children = defaultdict(lambda: trie)

    # for every pattern, add to tree
    for index in range(len(patterns)):
        trie.addPattern(patterns[index], index+1)

    buildFailLinks(trie, alphabet)

    return trie


def AhoCorasick(text, trie):
    result = []
    node = trie

    for character in text:
        while node.list_of_children[character] is None:
            node = node.fail_link

        node = node.list_of_children[character]

        if node.pattern_no is not None:
            result.append(node.pattern_no)
        else:
            result.append(0)

    return result


def prepareTextFor2DPatternSearch(lines):
    max_len = len(max(lines, key=len))

    for line in lines:
        for i in range(max_len - len(line)):
            line.append('0')

    return lines


def getVerticalPatternAndUniquePatterns(patterns):
    patterns_unique = []
    vertical_pattern = []

    for pattern in patterns:
        if pattern not in patterns_unique:
            patterns_unique.append(pattern)
        vertical_pattern.append(patterns_unique.index(pattern)+1)

    return vertical_pattern, patterns_unique


def prepareTries(patterns):
    vertical_pattern, patterns_unique = getVerticalPatternAndUniquePatterns(patterns)
    basic_trie = buildTrieFor2DPattern(patterns_unique)
    vertical_pattern_trie = buildTrieFor2DPattern([vertical_pattern])

    return basic_trie, vertical_pattern_trie


# assumption: patterns have the same length
def findPattern2D(lines, trie, vertical_trie):
    results = []

    for line in lines:
        results.append(AhoCorasick(line, trie))

    transposed_result = tuple(zip(*results))   # transpose
    results_2d = []
    for line in transposed_result:
        results_2d.append(AhoCorasick(line, vertical_trie))

    positions = []
    for indx1 in range(len(results_2d)):
        for indx2 in range(len(results_2d[indx1])):
            if results_2d[indx1][indx2] == 1:
                positions.append((indx2+1, indx1+1))

    return positions


def convertImageGrayscaleToListOfLists(img):
    pixel_map = img.load()
    pixels = []
    for row in range(img.height):
        pix = []
        for col in range(img.width):
            pix.append(pixel_map[col, row])
        pixels.append(pix)
    return pixels


def findPattern2dWithTimeMeasurement(lines, patterns, pattern_name):
    start = time.perf_counter_ns()
    trie_basic, trie_vertical = prepareTries(patterns)
    end = time.perf_counter_ns()
    start2 = time.perf_counter_ns()
    positions = findPattern2D(lines, trie_basic, trie_vertical)
    end2 = time.perf_counter_ns()

    print("Positions of pattern ", pattern_name, ":", positions)
    print("Count of found positions: ", len(positions))
    print("Prepare time: ", (end - start) / 1000000, " ms")
    print("Searching time: ", (end2 - start2) / 1000000, " ms")


def findPattern2dWithTimeMeasurementAndPartition(lines, patterns, pattern_name, parts_no):
    print("Partition: ", parts_no)
    partition = int(len(lines) / parts_no)
    for i in range(parts_no):
        findPattern2dWithTimeMeasurement(lines[partition*i:partition*(i+1)], patterns, pattern_name)
        print("-")


def findRepeatedCharactersInText(text):
    characters = set()
    positions = defaultdict(lambda: [])
    for line in text:
        for character in line:
            if character not in ['\n', ' ', '\r', '0']:
                characters.add(character)

    for character in characters:
        pattern = [character, character]
        trie_basic, trie_vertical = prepareTries(pattern)
        character_positions = findPattern2D(matrix_of_chars, trie_basic, trie_vertical)
        positions[character].extend(character_positions)

    count = 0
    for character in positions.keys():
        if len(positions[character]) > 0:
            print("Positions of two characters ", character, " in column:", positions[character])
            count += len(positions[character])
    print("Count of characters in the same position in two lines: ", count)

    return positions


print("test1")
trie_test = buildTrieFor2DPattern(["cba", "abc", "aab"])
# trie_test.printChildren(0)
test_res = AhoCorasick("aabcabbcba", trie_test)
print(test_res)

print("-------------------------------")
print("test2")
file = open("haystack.txt")
matrix_of_chars = [list(line.strip()) for line in file.readlines()]
file.close()
prepareTextFor2DPatternSearch(matrix_of_chars)

trie_basic_test, trie_vertical_test = prepareTries(["w", "w"])
test_positions = findPattern2D(matrix_of_chars, trie_basic_test, trie_vertical_test)
print("Positions: ", test_positions)

print("-------------------------------")
print("Find the same characters:")

findRepeatedCharactersInText(matrix_of_chars)

print("-------------------------------")
print("Find all th:")

findPattern2dWithTimeMeasurement(matrix_of_chars, first_pattern, "th")
print("---")
findPattern2dWithTimeMeasurementAndPartition(matrix_of_chars, first_pattern, "th", 2)
print("---")
findPattern2dWithTimeMeasurementAndPartition(matrix_of_chars, first_pattern, "th", 4)
print("---")
findPattern2dWithTimeMeasurementAndPartition(matrix_of_chars, first_pattern, "th", 8)
print("---")

print("Find all t h:")
findPattern2dWithTimeMeasurement(matrix_of_chars, second_pattern, "t h")
print("---")
findPattern2dWithTimeMeasurementAndPartition(matrix_of_chars, first_pattern, "t h", 2)
print("---")
findPattern2dWithTimeMeasurementAndPartition(matrix_of_chars, first_pattern, "t h", 4)
print("---")
findPattern2dWithTimeMeasurementAndPartition(matrix_of_chars, first_pattern, "t h", 8)
print("---")

print("-------------------------------")
img = Image.open('haystack.png').convert('L')
haystack_img = convertImageGrayscaleToListOfLists(img)
img = Image.open('s.png').convert('L')
s_img = convertImageGrayscaleToListOfLists(img)
img = Image.open('k.png').convert('L')
k_img = convertImageGrayscaleToListOfLists(img)
img = Image.open('o.png').convert('L')
o_img = convertImageGrayscaleToListOfLists(img)

print("Find all s:")
findPattern2dWithTimeMeasurement(haystack_img, s_img, "s")
print("---")
findPattern2dWithTimeMeasurementAndPartition(haystack_img, s_img, "s", 2)
print("---")
findPattern2dWithTimeMeasurementAndPartition(haystack_img, s_img, "s", 4)
print("---")
findPattern2dWithTimeMeasurementAndPartition(haystack_img, s_img, "s", 8)
print("---")

print("Find all k:")
findPattern2dWithTimeMeasurement(haystack_img, k_img, "k")
print("---")
findPattern2dWithTimeMeasurementAndPartition(haystack_img, k_img, "k", 2)
print("---")
findPattern2dWithTimeMeasurementAndPartition(haystack_img, k_img, "k", 4)
print("---")
findPattern2dWithTimeMeasurementAndPartition(haystack_img, k_img, "k", 8)
print("---")

print("Find all o:")
findPattern2dWithTimeMeasurement(haystack_img, o_img, "o")
print("---")
findPattern2dWithTimeMeasurementAndPartition(haystack_img, o_img, "o", 2)
print("---")
findPattern2dWithTimeMeasurementAndPartition(haystack_img, o_img, "o", 4)
print("---")
findPattern2dWithTimeMeasurementAndPartition(haystack_img, o_img, "o", 8)
print("---")

print("-------------------------------")
img = Image.open('pattern.png').convert('L')
pattern_img = convertImageGrayscaleToListOfLists(img)
findPattern2dWithTimeMeasurement(haystack_img, pattern_img, "p a t t e r n")
print("---")
findPattern2dWithTimeMeasurementAndPartition(haystack_img, pattern_img, "p a t t e r n", 2)
print("---")
findPattern2dWithTimeMeasurementAndPartition(haystack_img, pattern_img, "p a t t e r n", 4)
print("---")
findPattern2dWithTimeMeasurementAndPartition(haystack_img, pattern_img, "p a t t e r n", 8)
print("---")


