# -*- coding: utf-8 -*-

''' Synchronised message queue and message class '''

import Queue

msg_queue = Queue.Queue()


class Message(object):
    """
    Message class defining content of a message

    item - string that is either 'fork' or 'philosopher'
    ident - integer denoting concrete fork or philosopher
    is_acquired - boolean denoting action:
        True = acquire
        False = release
    """
    def __init__(self, item, ident, is_acquired):
        self.item = item
        self.ident = ident
        self.is_acquired = is_acquired
