#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import random
import sys
import threading
import time

from mtprint import mtprint
from message import msg_queue, Message
import gui


class Fork(object):
    """ Encapsulates identifier and lock """
    def __init__(self, num):
        super(Fork, self).__init__()
        self.num = num
        self.lock = threading.RLock()

    def acquire(self, blocking=True):
        """
        Acquire the lock and send 'fork acquired' message

        Lock acquisition can be blocking or non-blocking
        """
        if self.lock.acquire(blocking):
            msg_queue.put(Message('fork', self.num, True))
            return True
        else:
            return False

    def release(self):
        """ Release lock and send 'fork released' message """
        try:
            msg_queue.put(Message('fork', self.num, False))
            self.lock.release()
        except RuntimeError:
            pass

    def __str__(self):
        return 'Fork {}'.format(self.num)


class Philosopher(object):
    """ Worker thread encapsulating name, index and two fork references """
    def __init__(self, name, index, fork_left, fork_right):
        mtprint('Creating {} with {} and {}'.format(name, fork_left,
                fork_right))
        self.name = name
        self.index = index
        self.fork_left = fork_left
        self.fork_right = fork_right

    def eat(self, try_left_first=True):
        """
        Tries to acquire two forks.

        A philosopher tries to acquire blockingly his left fork and
        if he succeeds tries to acquire his right fork non-blockingly.
        A philosopher releases his acquired forks after every try.

        Returns True if successfully acquired two forks and False if not.
        """
        eaten = False
        if try_left_first is True:
            self.fork_left.acquire()
            mtprint('{} acquired {}'.format(self.name, self.fork_left))

        if self.fork_right.acquire(False):
            msg_queue.put(Message('philosopher', self.index, True))
            mtprint('{} acquired {} and {} and is eating'.format(self.name,
                    self.fork_left, self.fork_right))
            time.sleep(2)
            eaten = True
            mtprint("{} has eaten".format(self.name))
            msg_queue.put(Message('philosopher', self.index, False))
            self.fork_right.release()
            mtprint('{} released {}'.format(self.name, self.fork_right))

        self.fork_left.release()
        mtprint('{} released {}'.format(self.name, self.fork_left))

        return eaten

    def lifecycle(self):
        ''' Entry point for the philosophers' threads

        Should acquire the lock here because of proper RLock ownership
        '''
        self.fork_left.acquire()

        n = 1 if self.eat(False) else 0

        while(n != 10):
            mtprint("{} is thinking".format(self.name))
            if not self.eat():
                continue
            n += 1
        mtprint("{} has eaten {} times".format(self.name, n))


left = lambda arr, i: arr[i]
right = lambda arr, i: arr[(i + 1) % len(arr)]


def main():
    mtprint('Start of main')
    names = ['Dani', 'Kristian', 'Miro', 'Momo', 'Pesho']
    forks = [Fork(x) for x in range(5)]
    phils = [Philosopher(names[i], i, left(forks, i), right(forks, i))
             for i in range(5)]
    [threading.Thread(target=p.lifecycle).start() for p in phils]
    mtprint('End of main')


if __name__ == '__main__':
    app = gui.QtGui.QApplication(sys.argv)
    win = gui.MainWindow()
    main()
    sys.exit(app.exec_())
