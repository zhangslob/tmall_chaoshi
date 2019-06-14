# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TmallItem(scrapy.Item):
    item_id = scrapy.Field()
    title = scrapy.Field()
    province_list = scrapy.Field()
