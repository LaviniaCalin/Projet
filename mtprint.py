# -*- coding: utf-8 -*-

''' Synchronised print function '''

from __future__ import print_function
import threading


print_mutex = threading.Lock()


def mtprint(*args, **kwargs):
    with print_mutex:
        print(*args, **kwargs)
