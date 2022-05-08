from typing import Tuple


def gcd(a: int, b: int) -> int:
    return a if b == 0 else gcd(b, a % b)


def calculate_aspect_ratio(width: int, height: int) -> Tuple[int, int]:
    r = gcd(width, height)
    x = int(width / r)
    y = int(height / r)

    return x, y
