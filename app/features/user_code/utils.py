import random


def generate_code() -> str:
    """
    Generate a user code like "1234"
    Returns:
        str: "1234"
    """
    return "".join([str(random.randint(0, 9)) for _ in range(4)])
