#!/usr/bin/env python  
# -*- coding:utf-8 _*-  
""" 
@author: zhangslob 
@file: base_crawler.py 
@time: 2019/04/17
@desc: 
    
"""
import json
import scrapy
from scrapy.spiders import Spider as SD


class BaseSpider(object):

    def __init__(self, *args, **kwargs):
        import logging
        logger = logging.getLogger('pika')
        logger.setLevel(logging.WARNING)

        def to_json(response):
            return json.loads(response.text)

        def retry_(response, retry_times=15):
            meta = response.meta
            times_ = meta.get('cus_retry_times', 0) + 1

            if times_ == -1:
                # 无限重试
                retires = response.request.copy()
                retires.meta['cus_retry_times'] = times_
                retires.dont_filter = True
                retires.priority = 10

                self.logger.debug('retry times: {}, {}'.format(times_, response.url))
                return retires

            if times_ < retry_times:
                retires = response.request.copy()
                retires.meta['cus_retry_times'] = times_
                retires.dont_filter = True
                retires.priority = 10

                self.logger.debug('retry times: {}, {}'.format(times_, response.url))
                return retires
            else:
                self.logger.info('retry times: {} too many {}'.format(times_, response.url))
                return None

        scrapy.http.Response.json = to_json     # json loads
        scrapy.http.Response.retry = retry_     # 自定义重试


class Spider(BaseSpider, SD):

    def __init__(self, *args, **kwargs):
        BaseSpider.__init__(self, *args, **kwargs)
        SD.__init__(self, *args, **kwargs)


