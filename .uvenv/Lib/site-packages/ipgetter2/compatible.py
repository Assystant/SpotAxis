# -*- coding: utf-8 -*-

"""Compatible Module

Backport functions.
"""

import sys
import random


def backport_random_choices(
    self, population, weights=None, *, cum_weights=None, k=1
):
    """Return a k sized list of population elements chosen with replacement.
    If the relative weights or cumulative weights are not specified,
    the selections are made with equal probability.

    Which copy and modified from python 3.6's random module.
    """
    import bisect
    import itertools

    if cum_weights is None:
        if weights is None:
            total = len(population)
            return [population[int(self.random() * total)] for i in range(k)]
        cum_weights = list(itertools.accumulate(weights))
    elif weights is not None:
        raise TypeError("Cannot specify both weights and cumulative weights")
    if len(cum_weights) != len(population):
        raise ValueError("The number of weights does not match the population")

    total = cum_weights[-1]
    hi = len(cum_weights) - 1

    return [
        population[bisect.bisect(cum_weights, random() * total, 0, hi)]
        for i in range(k)
    ]


if sys.version_info < (3, 6):
    import functools

    random_choices = functools.partial(backport_random_choices, random._inst)
else:
    random_choices = random.choices
