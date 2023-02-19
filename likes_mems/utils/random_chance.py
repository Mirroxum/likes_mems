import random


def is_promote(chance=50):
    return random.choices([False, True], weights=[100 - chance, chance]).pop()
