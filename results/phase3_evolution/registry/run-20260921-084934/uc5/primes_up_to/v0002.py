def primes_up_to(n):
    if n < 2:
        return []

    is_prime = [True] * (n + 1)
    is_prime[0], is_prime[1] = False, False

    for candidate in range(2, int(n**0.5) + 1):
        if is_prime[candidate]:
            for multiple in range(candidate * candidate, n + 1, candidate):
                is_prime[multiple] = False

    return [num for num, prime in enumerate(is_prime) if prime]
