# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
import logging


class JdBarDataSavePipeline(object):
    def __init__(self, mongo_url, mongo_db):
        self.mongo_url = mongo_url
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        logging.info('初始化JdBarDataSavePipeline参数')
        return cls(
            mongo_url=crawler.settings.get('MONGO_URL'),
            mongo_db=crawler.settings.get('MONGO_DB')
        )

    def open_spider(self, spider):
        logging.info('开启mongodb链接')
        self.client = MongoClient(self.mongo_url)
        self.db = self.client[self.mongo_db]

    def process_item(self, item, spider):
        name = item.__class__.__name__
        if name == 'JdBarItem':
            if self.db[name].update_one({'id': item['id']}, {'$set': dict(item)}, True):
                logging.info("保存成功:{}".format(str(item)))
            else:
                logging.info("保存失败:{}".format(str(item)))
        return item

    def close_spider(self, spider):
        logging.info('关闭mongodb链接')
        self.client.close()
