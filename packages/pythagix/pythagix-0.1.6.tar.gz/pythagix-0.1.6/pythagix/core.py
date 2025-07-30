from math import isqrt
from functools import reduce
from typing import List
import math

__all__ = [
    "is_prime",
    "filter_primes",
    "nth_prime",
    "gcd",
    "is_perfect_square",
    "count_factors",
    "triangle_number",
]


def is_prime(n: int) -> bool:
    """Check if a number is prime."""
    if n <= 1:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, isqrt(n) + 1, 2):
        if n % i == 0:
            return False
    return True


def filter_primes(numbers: List[int]) -> List[int]:
    """Return only the prime numbers from the list."""
    return [n for n in numbers if is_prime(n)]


def nth_prime(n: int) -> int:
    """Return the n-th prime number (1-indexed)."""
    if n < 1:
        raise ValueError("Index must be >= 1")

    count = 0
    candidate = 2
    while True:
        if is_prime(candidate):
            count += 1
            if count == n:
                return candidate
        candidate += 1


def gcd(numbers: List[int]) -> int:
    """Return the GCD of a list of numbers."""
    if not numbers:
        raise ValueError("List must not be empty")
    return reduce(math.gcd, numbers)


def is_perfect_square(n: int) -> bool:
    """Check if a number is a perfect square."""
    if n < 0:
        return False
    root = isqrt(n)
    return root * root == n


def count_factors(n: int) -> List[int]:
    """Return all factors of a number."""
    if n <= 0:
        raise ValueError("Number must be positive")

    factors = set()
    for i in range(1, isqrt(n) + 1):
        if n % i == 0:
            factors.add(i)
            factors.add(n // i)
    return sorted(factors)


def triangle_number(n: int) -> int:
    """Return the n-th triangle number."""
    if n < 0:
        raise ValueError("n must be >= 0")
    return n * (n + 1) // 2


# Quick test zone
if __name__ == "__main__":

    def main():
        """Function for testing other functions."""
        print("Primes:", filter_primes([1, 2, 3, 4, 5, 16, 17, 19]))
        print("5th Prime:", nth_prime(5))
        print("GCD of [12, 18, 24]:", gcd([12, 18, 24]))
        print("Is 49 perfect square?", is_perfect_square(49))
        print("Factors of 28:", count_factors(28))
        print("7th triangle number:", triangle_number(7))

    main()
