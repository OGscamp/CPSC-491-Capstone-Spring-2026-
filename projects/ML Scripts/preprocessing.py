import numpy as np

RANK_MAPPING = {
    "IRON": 0,
    "BRONZE": 1,
    "SILVER": 2,
    "GOLD": 3,
    "PLATINUM": 4,
    "EMERALD": 5,
    "DIAMOND": 6,
    "MASTER": 7,
    "GRANDMASTER": 8,
    "CHALLENGER": 9
}


def rank_to_numeric(rank):
    return RANK_MAPPING.get(rank.upper(), 0)


def safe_divide(a, b):
    if b == 0:
        return 0
    return a / b