def find_duplicates(items):
    result = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j] and items[i] not in result:
                result.append(items[i])
    return result
