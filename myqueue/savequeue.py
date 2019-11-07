import pickle
import threading
from collections import deque
from utils import predict
import sys
import redis
import hashlib

"""
线程安全的单例模式实现的Save队列
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
class SaveQueue:

    def __init__(self):
        self.queue = deque()
        self.classifier = predict.Predictor("./utils/model_it.dat", "./utils/words_it.dat")
        self.redisConnection = self._connect_redis()
        self.redis_key = "SaveQueue"
        self.MD5 = hashlib.md5()

    def _connect_redis(self):
        """
        连接redis
        :return:
        """
        rd = redis.StrictRedis(host='localhost', port=6380, password='', decode_responses=True)
        try:
            rd.set("test", "test", ex=30)
            print("[*]: redis 连接成功")
            return rd
        except redis.exceptions.ConnectionError as e:
            sys.exit(e)

    def add(self, context):
        content = context.content
        if self.classifier.predict(content) == [1]:
            self.MD5.update(content.encode(encoding='utf-8'))
            flag = self.redisConnection.sadd(self.redis_key, self.MD5.hexdigest())
            if flag != 0:
                self.queue.appendleft(context)
        else:
            print("[*]: 主题判别后跳过...")

    def move(self):
        return self.queue.pop()

    def extend(self, iterable):
        for i in iterable:
            self.add(i)

