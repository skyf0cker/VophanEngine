import json
import time
from myqueue.urlqueue import Context
from myqueue.urlqueue import UrlQueue
from myqueue.contentqueue import ContentQueue
import requests
import requests.packages.urllib3.exceptions as exc
# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(exc.InsecureRequestWarning)


class fetcher:

    """
    this is the class to fetch the url
    """

    def __init__(self):
        self.config_path = "./Spider/fconfig.json"
        self.config = self._load_config()
        self.url_queue = UrlQueue()
        self.content_queue = ContentQueue()
        self.proxy_src = self.config["proxysrc"]
        self.proxies = {}
        self.header = self.config["Header"]
        self.encode = self.config["encode"]
        self.begin_url = self.config["beginurl"]
        self.frequent = self.config["frequent"]
        self.domain = self.config["domain"]
        print("[*]: 正在设置种子链接...")
        for seed in self.begin_url:
            c = Context(url=seed)
            self._add_item_to_url(c)

    def _get_proxies(self):
        pass

    def _check_proxy_alive(self):
        pass

    def _add_proxies(self, proxies):
        self.proxies = proxies

    def _set_header(self, header):
        self.header = header

    def _get_item_from_url(self):
        return self.url_queue.get()

    def _add_item_to_url(self, item):
        self.url_queue.add(item)

    def _add_item_to_content(self, item):
        self.content_queue.add(item)

    def _request(self):
        context = self._get_item_from_url()

        flag = 0
        for i in self.domain:
            if i in context.url:
                flag = 1
                break
        if flag == 0:
            return

        print("[*]: begin fetching " + context.url)
        try:
            time.sleep(self.frequent)
            response = requests.get(url=context.url, proxies=self.proxies, headers=self.header, verify=False)
        except Exception as e:
            print(e)
            return
        context.content = response.content.decode(self.encode, "ignore")
        self._add_item_to_content(context)

    def _load_config(self):
        """
        加载配置文件
        :return:
        """
        with open(self.config_path, 'r') as r:
            return json.load(r)


    def fetch(self):
        """
        开始fetch
        :return:
        """
        while True:
            try:
                self._request()
            except IndexError:
                continue