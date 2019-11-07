from myqueue.savequeue import SaveQueue
import pymongo


class saver:
    """
    该类用来保存解析得到的内容，以及后续的服务
    """
    def __init__(self):
        self.save_queue = SaveQueue()
        self.kernel = None

    def _get_item_from_save(self):
        return self.save_queue.move()

    def active(self, kernel):
        self.kernel = kernel

    def _save(self):
        context = self._get_item_from_save()
        self.kernel.save(context)

    def save(self):

        while True:
            try:
                self._save()
            except IndexError:
                continue