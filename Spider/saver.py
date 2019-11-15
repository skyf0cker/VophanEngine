import asyncio

from myqueue.savequeue import SaveQueue
import pymongo


class saver:
    """
    该类用来保存解析得到的内容，以及后续的服务
    """
    def __init__(self):
        self.save_queue = SaveQueue()
        self.kernel = None
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.loop = asyncio.get_event_loop()

    def _get_item_from_save(self):
        return self.save_queue.move()

    def active(self, kernel):
        self.kernel = kernel

    async def _save(self):
        await self.kernel._init()
        while True:
            try:
                context = self._get_item_from_save()
                await self.kernel.save(context)
            except Exception as e:
                continue

    def save(self):

        self.loop.create_task(self._save())
        self.loop.run_forever()

        # while True:
        #     try:
        #         self._save()
        #     except IndexError:
        #         continue