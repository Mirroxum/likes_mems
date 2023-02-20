import random


def is_promote(chance=50):
    if chance >= 0 and chance <= 100:
        return random.choices(
            [False, True], weights=[100 - chance, chance]).pop()
    else:
        return False
