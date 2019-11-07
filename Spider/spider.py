from threading import Thread
from Spider.fetcher import fetcher
from Spider.parser import parser
from Spider.saver import saver


class spider:
    """
    该类统筹三个组件的运行，是Spider的入口
    """
    def __init__(self):
        self.fetcher = fetcher()
        self.parser = parser()
        self.saver = saver()

    def active(self, pkernel, skernel):
        """
        激活所有的核
        :param pkernel:
        :param skernel:
        :return:
        """
        print("[*]: begin activing kernels...")
        self.parser.active(pkernel)
        self.saver.active(skernel)

    def crawl(self):
        """
        开始爬虫
        :return:
        """
        f = Thread(target=self.fetcher.fetch)
        p = Thread(target=self.parser.parse)
        s = Thread(target=self.saver.save)

        task_list = [f, p, s]
        for t in task_list:
            t.start()
