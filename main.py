import websockets

from utils.elasticsearch import *
from Spider.spider import spider
from utils.TextExtract import TextExtractor
import re
import pymongo
import warnings
warnings.filterwarnings("ignore")


class SaveKernel:
    """
    实现Save核
    """
    def __init__(self):
        # websockets
        pass
        # mongodb 储存
        # self.client = pymongo.MongoClient(host="localhost", port=27017)
        # self.db = self.client.spider
        # self.collections = self.db.articles

    async def _init(self):
        self.ws_client = await websockets.connect("ws://localhost:3000/api/v1/elastic")

    async def save(self, context):

        article = {
            "title": context.title,
            "time": context.time,
            "content": context.content
        }
        print("title:", context.title)
        print("time:", context.time)
        print("content:", context.content)
        js = json.dumps(article)
        await self.ws_client.send(js)

        # self.collections.insert(article)
        # try:
        #     result = create_content("articles", article)["result"]
        #     if result != "created":
        #         print("[*]: 保存失败")
        # except KeyError as e:
        #     print("[*]: 保存失败")


class Parsekernel:
    """
    实现解析核
    """
    def LinkExtract(self, content):
        print("[*]: extracting the link....")
        result = re.findall('href="(.*?)"', content)
        return result

    def ContentExtract(self, content):
        print("[*]: extracting the content....")
        t = TextExtractor(content, "./utils/stopword.txt")
        if t.article_flag:
            return [(t.title, t.time, t.text), ]
        else:
            print("[*]: 跳过导航页....")
            return []

if __name__ == "__main__":

    pkernel = Parsekernel()
    skernel = SaveKernel()
    s = spider()
    s.active(pkernel, skernel)
    s.crawl()