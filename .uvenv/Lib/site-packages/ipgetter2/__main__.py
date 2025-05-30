#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Console script for ipgetter2."""

import click
from .ipgetter2 import IPGetter, DEFAULT_URLS


@click.group()
def main():
    """Simple script for get/test external IP."""
    pass


@main.command()
def get():
    """Get the external IP randomly from default servers."""

    getter = IPGetter()
    click.echo(getter.get())


@main.command()
@click.argument("url")
def get_from(url):
    """Get the external IP from specific server."""

    getter = IPGetter()
    click.echo(getter.get_from(url))


@main.command()
def test():
    """Test default servers."""

    getter = IPGetter()
    contexts = []
    failed = []
    counted = dict()

    i = 0
    click.echo("Numbers of Servers : %s" % len(DEFAULT_URLS))
    for url in DEFAULT_URLS:
        i += 1

        try:
            click.echo("[%s/%s] Testing : %s" % (i, len(DEFAULT_URLS), url))
            address = getter.get_from(url)
            contexts.append((address, url))

            if address in counted:
                counted[address] += 1
            else:
                counted[address] = 1
        except Exception as e:
            click.echo(
                "Test failed on %s, with exception : %s" % (url, e), err=True
            )

            failed.append(url)

    click.echo("%s server failed : %s" % (len(failed), failed))

    click.echo(counted)
    max_occur_addr = max(counted.items(), key=lambda item: item[1])
    click.echo(
        "IP's : %s = %s ocurrencies" % (max_occur_addr[0], max_occur_addr[1])
    )


@main.command()
def show_servers():
    """Display default servers' URLs."""

    i = 0
    for url in DEFAULT_URLS:
        click.echo("%s: %s" % (i, url))
        i += 1


if __name__ == "__main__":
    main()
