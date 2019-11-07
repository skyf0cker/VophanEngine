import threading
from collections import deque

"""
线程安全的单例模式实现的Content队列
"""

def synchronized(func):
    func.__lock__ = threading.Lock()

    def synced_func(*args, **kws):
        with func.__lock__:
            return func(*args, **kws)

    return synced_func


def singleton(cls):
    instances = {}

    @synchronized
    def get_instance(*args, **kw):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    return get_instance


@singleton
class ContentQueue:

    def __init__(self):
        self.queue = deque()

    def add(self, sth):
        self.queue.appendleft(sth)

    def move(self):
        return self.queue.pop()

