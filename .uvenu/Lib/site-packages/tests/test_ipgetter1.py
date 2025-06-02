# -*- coding: utf-8 -*-

"""Tests for `ipgetter1` package."""

from ipgetter2 import ipgetter1 as ipgetter


def test_myip():
    ipgetter.myip()


def test_get_externalip():
    ipgetter.IPgetter().get_externalip()
