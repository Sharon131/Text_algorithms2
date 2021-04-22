from naive import *
from automata import *
from KMP import *

from time import time

test_pattern = "ab"
test_text = "abaabaaaaba"


def test_naive():
    match = naive_algorithm(test_pattern, test_text)
    return match == [0, 3, 8]


def test_automata():
    match = automata_algorithm(test_pattern, test_text)
    print(match)
    return match == [0, 3, 8]


def test_KMP():
    match = KMP_algorithm(test_pattern, test_text)
    return match == [0, 3, 8]


def time_naive(patt, text):
    prep_time = 0
    find_match_time = 0

    return prep_time, find_match_time


def time_automata(patt, text):
    prep_time = 0
    find_match_time = 0

    return prep_time, find_match_time


def time_KMP(patt, text):
    prep_time = 0
    find_match_time = 0

    return prep_time, find_match_time


if __name__ == "__main__":

    naive_prep_time, naive_match_time = time_naive(test_pattern, test_text)
    automata_prep_time, automata_match_time = time_automata(test_pattern, test_text)
    KMP_prep_time, KMP_match_time = time_KMP(test_pattern, test_text)

    print("Zmierzone czasy:")
    print("Algorytm naiwny:" + " preprocessing: " + str(naive_prep_time) + "dopasowanie: " + str(naive_match_time))
    print("Algorytm z automatem:" + " preprocessing: " + str(automata_prep_time) + "dopasowanie: " + str(automata_match_time))
    print("Algorytm KMP:" + " preprocessing: " + str(KMP_prep_time) + "dopasowanie: " + str(KMP_match_time))

