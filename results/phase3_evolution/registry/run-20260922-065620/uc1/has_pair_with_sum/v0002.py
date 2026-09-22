def has_pair_with_sum(nums, target):
    seen = set()
    for value in nums:
        if target - value in seen:
            return True
        seen.add(value)
    return False
