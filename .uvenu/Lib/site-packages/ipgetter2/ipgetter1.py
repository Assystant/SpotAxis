# -*- coding: utf-8 -*-

"""Original ipgetter interface simulate module."""

import signal
from functools import wraps
from . import ipgetter2


def timeout(seconds, error_message="Function call timed out"):
    """Decorator that provides timeout to a function

    It's not working on windows system! So maybe your function will freeze if
    it's waiting a long run function.
    """

    def decorated(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        @wraps(func)
        def wrapper(*args, **kwargs):
            if "alarm" in signal.__dict__:

                signal_num = signal.SIGALRM
                signal.signal(signal_num, _handle_timeout)
                signal.alarm(seconds)
                try:
                    result = func(*args, **kwargs)
                finally:
                    signal.alarm(0)

                return result
            else:
                # SIGALRM is not working in win32
                # https://stackoverflow.com/questions/52779920/why-is-signal-sigalrm-not-working-in-python-on-windows
                # https://stackoverflow.com/questions/47545002/python-standard-lib-signal-attributeerror-module-signal-has-no-attribute

                return func(*args, **kwargs)

        return wrapper

    return decorated


@timeout(120)
def myip():
    """Get your external IP"""
    return IPgetter().get_externalip()


class IPgetter(object):
    """This class is designed to fetch your external IP address from the
    internet.

    It is used mostly when behind a NAT.

    It picks your IP randomly from a serverlist to minimize request overhead
    on a single server
    """

    def __init__(self):
        self.server_list = ipgetter2.DEFAULT_URLS
        self._getter = ipgetter2.IPGetter()

    def get_externalip(self):
        """This function gets your IP from a random server
        """
        return str(self._getter.get().v4)

    def fetch(self, server):
        """This function gets your IP from a specific server
        """
        return str(self._getter.get_from(server).v4)

    def test(self):
        """This functions tests the consistency of the servers
        on the list when retrieving your IP.
        All results should be the same.
        """

        resultdict = {}
        for server in self.server_list:
            resultdict.update(**{server: self.fetch(server)})

        ips = sorted(resultdict.values())
        ips_set = set(ips)
        print("\nNumber of servers: {}".format(len(self.server_list)))
        print("IP's :")
        for ip, ocorrencia in zip(
            ips_set, map(lambda x: ips.count(x), ips_set)
        ):
            print(
                "{0} = {1} ocurrenc{2}".format(
                    ip if len(ip) > 0 else "broken server",
                    ocorrencia,
                    "y" if ocorrencia == 1 else "ies",
                )
            )
            print("\n")
        print(resultdict)
