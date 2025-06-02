# -*- coding: utf-8 -*-

"""Tests for `ipgetter2` package."""

import pytest
from ipgetter2 import IPGetter


@pytest.fixture
def getter():
    return IPGetter()


def test_get(getter):
    print(getter.get())
