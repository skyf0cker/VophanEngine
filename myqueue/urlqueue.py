import sys
import threading
from collections import deque
import networkx as nx
import redis

from myqueue.Context import Context

"""
线程安全的单例模式实现的url队列
并且在里面维护了redis连接，url去重
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


# class UrlQueue:
#
#     def __init__(self, level):
#         self.queue = deque()
#         self._connect_redis()
#         self.redis_key = "test_key"
#         self.pagerankpool = []
#
    # def _connect_redis(self):
    #     """
    #     连接redis
    #     :return:
    #     """
    #     self.rd = redis.StrictRedis(host='localhost', port=6379, password='', decode_responses=True)
    #     try:
    #         self.rd.set("test", "test", ex=30)
    #         print("[*]: redis 连接成功")
    #     except redis.exceptions.ConnectionError as e:
    #         sys.exit(e)

#     def add(self, sth):
#         """
#         对双向队列添加方法的封装，并且实现爬取层数和url去重的控制
#         :param sth:添加的Object
#         :return:
#         """
#         flag = self.rd.sadd(self.redis_key, sth)
#         if flag != 0:
#             print("length: ", len(self.pagerankpool))
#             if len(self.pagerankpool) > 1000:
#             #     开始计算PR值
#                 self.pagerank()
#             self.queue.appendleft(sth)
#
    # def pagerank(self):
    #
    #     print("[*]: 正在迭代计算PR值....")
    #     G = nx.DiGraph()  # DiGraph()表示有向图
    #     for i in self.pagerankpool:
    #         G.add_edge(i[0], i[1])
    #     pr_impro_value = nx.pagerank(G, alpha=0.85)
    #     print("[*]: 正在重排链接顺序....")
    #     sorted_list = [i[0] for i in sorted(pr_impro_value.items(), key=lambda x: x[1])]
    #     print("sorted length:", len(sorted_list))
    #     self.queue.clear()
    #     self.queue.extendleft(sorted_list)
    #     self.pagerankpool = []

#     def move(self):
#         """
#         对双向队列添加方法的封装
#         :return:
#         """
#         result = self.queue.pop()
#         return result
#
#     def extend(self, iterable):
#         for i in iterable:
#             self.add(i)
#
#     def length(self):
#         return len(self.rd.smembers(self.redis_key))


@singleton
class UrlQueue:

    def __init__(self):
        self.in_queue = InQueue()
        self.pr_queue = PrQueue()
        self.out_queue = OutQueue()
        self.lock = threading.Lock()

    def _migrate(self):
        self.out_queue.add_all(self.in_queue.get())

    def add(self, context):
        self.in_queue.add(context)
        if len(self.out_queue.queue) == 0:
            self._migrate()

    def add_all(self, iterable):
        self.in_queue.add_all(iterable)
        self.lock.acquire()
        if self.in_queue.length() > 20:
            self.pr_queue.add_all(self.in_queue.get())
            self.pr_queue.pagerank()
            self.out_queue.add_all(self.pr_queue.get_all())
        else:
            self.out_queue.add_all(self.in_queue.get())
        self.lock.release()

    def get(self):
        return self.out_queue.get()


class InQueue:

    def __init__(self):
        self.queue = deque()
        self.redisConnection = self._connect_redis()
        self.redis_key = "Inqueue"
        self.redis_key_valid = "Inqueue_valid"

    def _connect_redis(self):
        """
        连接redis
        :return:
        """
        rd = redis.StrictRedis(host='localhost', port=6379, password='', decode_responses=True)
        try:
            rd.set("test", "test", ex=30)
            print("[*]: redis 连接成功")
            return rd
        except redis.exceptions.ConnectionError as e:
            sys.exit(e)

    def add(self, context):
        flag = self.redisConnection.sadd(self.redis_key_valid, context.url)
        if flag != 0:
            self.redisConnection.sadd(self.redis_key, context.to_string())

    def add_all(self, context_list):
        for context in context_list:
            flag = self.redisConnection.sadd(self.redis_key_valid, context.url)
            if flag != 0:
                self.redisConnection.sadd(self.redis_key, context.to_string())

    def get(self):
        context_string_set = self.redisConnection.smembers(self.redis_key)
        self.redisConnection.delete(self.redis_key)
        context_list = []
        for con_str in context_string_set:
            content_list = con_str.split("|")
            context_list.append(Context(content_list[0], content_list[1], content_list[2], content_list[3], content_list[4]))
        return context_list

    def length(self):
        return self.redisConnection.scard(self.redis_key)


class OutQueue:

    def __init__(self):
        self.queue = deque()

    def add(self, sth):
        self.queue.appendleft(sth)

    def get(self):
        return self.queue.pop()

    def add_all(self, iterable):
        self.queue.extendleft(iterable)

    def clear(self):
        self.queue.clear()


class PrQueue:

    def __init__(self):
        self.queue = deque()
        self.lock = threading.Lock()

    def add(self, context):
        self.queue.appendleft(context)

    def get(self):
        return self.queue.pop()

    def get_all(self):
        result = []
        for i in range(len(self.queue)):
            result.append(self.queue.pop())
        return result

    def add_all(self, iterable):
        self.queue.extendleft(iterable)

    def clear(self):
        self.queue.clear()

    def pagerank(self):
        print("[*]: 正在迭代计算PR值....")
        G = nx.DiGraph()  # DiGraph()表示有向图
        for con in self.queue:
            G.add_edge(con.pre_url, con.url)
        pr_impro_value = nx.pagerank(G, alpha=0.85)
        # print("[*]DEBUG: PR VALUE: ", pr_impro_value)
        print("[*]: 正在重排链接顺序....")
        sorted_list = [Context(url=i[0]) for i in sorted(pr_impro_value.items(), key=lambda x: x[1])]
        self.queue.clear()
        self.queue.extendleft(sorted_list)
