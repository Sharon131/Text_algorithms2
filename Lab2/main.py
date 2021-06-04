import time
import sys
sys.setrecursionlimit(1000000)

first_string = "bbbd"
second_string = "aabbabd"
third_string = "ababcd"
fourth_string = "abcbccd"

file = open("1997_714.txt", "r", encoding="utf-8")
fifth_string = file.read(3500)


class TrieNode:
    list_of_children = []
    node_value = ''

    def __init__(self, value):
        self.node_value = value
        self.list_of_children = []

    def addChild(self, next_child):
        self.list_of_children.append(next_child)

    def addSuffix(self, text):
        if len(text) == 0:
            return
        new_child = TrieNode(text[0])
        self.list_of_children.append(new_child)
        new_child.addSuffix(text[1:])

    def findHead(self, text):
        if len(text) == 0:
            return None, text
        for child in self.list_of_children:
            if child.node_value == text[0]:
                return child.findHead(text[1:])
        return self, text

    def printChildren(self, level):
        for child in self.list_of_children:
            print("level ", level, " ", child.node_value)
            child.printChildren(level+1)


def build_trie(text):
    trie = TrieNode("root")

    # for every suffix
    for i in reversed(range(len(text))):
        suffix = text[i:]
        # check if trie has that suffix
        suffix_head, suffix_to_add = trie.findHead(suffix)
        if suffix_head is not None:
            suffix_head.addSuffix(suffix_to_add)

    return trie


trie = build_trie(second_string)

print("level 0 ", trie.node_value)
trie.printChildren(1)

start1 = time.perf_counter()
trie1 = build_trie(first_string)
end1 = time.perf_counter()

start2 = time.perf_counter()
trie2 = build_trie(second_string)
end2 = time.perf_counter()

start3 = time.perf_counter()
trie3 = build_trie(third_string)
end3 = time.perf_counter()

start4 = time.perf_counter()
trie4 = build_trie(fourth_string)
end4 = time.perf_counter()

start5 = time.perf_counter()
trie5 = build_trie(fifth_string)
end5 = time.perf_counter()

print(len(trie5.list_of_children))

print("Time 1: ", end1-start1)
print("Time 2: ", end2-start2)
print("Time 3: ", end3-start3)
print("Time 4: ", end4-start4)
print("Time 5: ", end5-start5)
