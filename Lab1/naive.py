

def naive_algorithm(patt, text):
    to_return = []
    for shift in range(len(text) - len(patt) + 1):
        if patt == text[shift:shift+len(patt)]:
            # print("Przesunięcie {0} jest poprawne".format(shift))
            to_return.append(shift)

    return to_return

