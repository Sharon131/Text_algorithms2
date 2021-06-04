from collections import defaultdict
import queue


class TrieNode:

    def __init__(self, value):
        self.node_value = value
        self.list_of_children = {}
        self.fail_link = None
        self.pattern_no = None

    def addPatternRecursive(self, text, index, pattern_no):
        if index >= len(text):
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


def buildTrieFor2DPattern(patterns):
    alphabet = set()
    for pattern in patterns:
        for character in pattern:
            alphabet.add(character)

    trie = TrieNode("root")
    trie.list_of_children = defaultdict(lambda: trie)

    # for every pattern, add to tree
    for index in range(len(patterns)):
        trie.addPattern(patterns[index], index)

    buildFailLinks(trie, alphabet)

    return trie


def findPattern2D(text, trie, patterns):
    
    pass


trie_test = buildTrieFor2DPattern(["cba", "abc", "aab"])
trie_test.printChildren(0)


