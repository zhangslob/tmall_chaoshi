#!/usr/bin/env python  
# -*- coding: utf-8 -*-
"""
@author: zhangslob
@file  : handler_csv.py
@time  : 2019-06-15
@desc  :
         将数据清洗为csv
"""
import csv

import pymongo


class CsvHandler(object):
    def __init__(self):
        client = pymongo.MongoClient('mongodb://127.0.0.1:27017/tmall')
        self.c = client.get_database()['tmall']
        self.province_list = self.c.find_one({"item_id": 1})['province_list']
        self.province_data = self.c.find({"item_id": {'$ne': 1}})

    def load_data(self):
        row = ['item_id', 'title']
        for i in self.province_list:
            row.extend(list(i.values()))
        print(row)
        all_item = []
        for item in self.province_data:
            temp = dict().fromkeys(row)
            temp['item_id'] = item['item_id']
            temp['title'] = item['title']
            for province in item['province_list']:
                temp[province] = 1

            all_item.append([i if i else 0 for i in temp.values()])

        self.write_to_csv(row, all_item)

    @staticmethod
    def write_to_csv(first, items):
        with open('tmall_chaoshi.csv', mode='w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            writer.writerow(first)
            for item in items:
                writer.writerow(item)


if __name__ == '__main__':
    CsvHandler().load_data()


