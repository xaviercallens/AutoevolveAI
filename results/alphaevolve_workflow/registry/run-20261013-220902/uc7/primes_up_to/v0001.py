def primes_up_to(n):
    primes = []
    for candidate in range(2, n + 1):
        is_prime = True
        for divisor in range(2, candidate):
            if candidate % divisor == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(candidate)
    return primes
