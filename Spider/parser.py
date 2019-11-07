import os
import re
import urllib
from threading import Thread
from urllib import parse

from myqueue.Context import Context
from myqueue.contentqueue import ContentQueue
from myqueue.savequeue import SaveQueue
from concurrent.futures import ThreadPoolExecutor
from myqueue.urlqueue import UrlQueue
import copy


class parser:
    """
    该类是用来解析网页内容，获得link或者content
    """
    def __init__(self):
        self.url_queue = UrlQueue()
        self.content_queue = ContentQueue()
        self.save_queue = SaveQueue()
        self.kernal = None

    def _get_item_from_content(self):
        return self.content_queue.move()

    def _add_item_to_content(self, context):
        self.content_queue.add(context)

    def _add_item_from_save(self, context):
        self.save_queue.add(context)

    def active(self, kernel):
        """
        激活解析核
        :param kernel:
        :return:
        """
        self.kernal = kernel

    def parse(self):
        """
        开始解析内容
        :return:
        """
        def LinkWrap(context):
            url = context.url
            content = context.content
            url_list = self.kernal.LinkExtract(content)
            self.url_queue.add_all([Context(url=u, pre_url=url) for u in url_list])

        def ContentWrap(context):
            url = context.url
            content = context.content
            content_list = self.kernal.ContentExtract(content)
            for c in content_list:
                self.save_queue.add(Context(url=url, content=c[2], time=c[1], title=c[0]))

        while True:
            try:
                content = self._get_item_from_content()
            except IndexError:
                continue
            # LinkWrap(content)
            # ContentWrap(content)
            link = Thread(target=LinkWrap, args=(content, ))
            con = Thread(target=ContentWrap, args=(content, ))

            link.start()
            con.start()

