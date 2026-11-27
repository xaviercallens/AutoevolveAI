def find_duplicates(items):
    counts = {}
    for item in items:
        counts[item] = counts.get(item, 0) + 1
    return [item for item, count in counts.items() if count > 1]
