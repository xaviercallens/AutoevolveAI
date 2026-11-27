def join_words(words, sep):
    result = ""
    first = True
    for word in words:
        if first:
            result = word
            first = False
        else:
            result = result + sep + word
    return result
