from typing import Set


# Generates typos which duplicates a character
def generate_duplications(input_str: str) -> Set[str]:
    typos = set()

    for i in range(0, len(input_str)):
        if input_str[i] not in "./":
            typos.add(input_str[:i] + input_str[i] + input_str[i::])

    return typos


# Generates typos with a character removed
def generate_removals(input_str: str) -> Set[str]:
    typos = set()

    for i in range(0, len(input_str)):
        typos.add(input_str[:i] + input_str[i + 1::])

    return typos


# Generates typos with adjacent characters swapped
def generate_swaps(input_str: str) -> Set[str]:
    typos = set()

    for i in range(1, len(input_str) - 1):
        swapped_str = input_str[:i] + input_str[i + 1] + input_str[i] + input_str[i + 2::]

        if swapped_str != input_str:
            typos.add(swapped_str)

    return typos


def generate_typos(input_str: str) -> Set[str]:
    return generate_duplications(input_str)\
        .union(generate_removals(input_str))\
        .union(generate_swaps(input_str))
