# -*- coding: utf-8 -*-

"""Tests for `compatible` package."""


def test_backport_random():
    """Test the backport randome for python 3.5"""

    import random
    from ipgetter2.compatible import backport_random_choices

    population = range(1, 6)
    choices = backport_random_choices(random._inst, population)
    assert len(set(choices) & set(population)) > 0
