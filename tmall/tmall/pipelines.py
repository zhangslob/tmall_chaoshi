# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo


class MongoDBPipeline(object):
    def __init__(self):
        client = pymongo.MongoClient('mongodb://127.0.0.1:27017/tmall')
        self.c = client.get_database()['tmall']
        self.c.create_index('item_id', unique=True)

    def process_item(self, item, spider):
        try:
            self.c.insert_one(dict(item))
        except pymongo.errors.DuplicateKeyError:
            # spider.logger.debug('DuplicateKeyError')
            pass
        return None
