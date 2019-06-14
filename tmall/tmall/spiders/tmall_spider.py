# -*- coding: utf-8 -*-

import re
import scrapy
from scrapy import signals
from random import randint

from ..items import TmallItem
from .base_crawler import Spider


def random_user_id():
    return ''.join(["%s" % randint(0, 9) for num in range(0, 9)])


class TmallSpiderSpider(Spider):
    name = 'tmall_spider'
    allowed_domains = ['tmall.com']

    list_url = 'https://list.tmall.com/search_product.htm?cat=50502048&&user_id=725677994&s={}'
    detail_url = 'https://detail.m.tmall.com/item.htm?id={}'
    area_code = 'https://chaoshi.tmall.com/site/getSiteList.htm'

    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        # 'DOWNLOAD_DELAY': 1,
        'LOG_LEVEL': "DEBUG",
        'ITEM_PIPELINES': {
            'tmall.pipelines.MongoDBPipeline': 300,
        },
        'DOWNLOADER_MIDDLEWARES': {
            "tmall.middlewares.ProxyMiddleware": 200
        },
        'DEFAULT_REQUEST_HEADERS': {
            'authority': "list.tmall.com",
            'upgrade-insecure-requests': "1",
            'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/74.0.3729.169 Safari/537.36",
            'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,"
                      "application/signed-exchange;v=b3",
            'accept-encoding': "gzip, deflate, br",
            'accept-language': "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
            'cache-control': "no-cache",
        }
    }

    detail_headers = {
        'authority': "detail.m.tmall.com",
        'cache-control': "max-age=0,no-cache",
        'upgrade-insecure-requests': "1",
        'user-agent': "Mozilla/5.0 (Linux; Android 8.0.0; Pixel 2 XL Build/OPD1.170816.004) AppleWebKit/537.36 ("
                      "KHTML, like Gecko) Chrome/74.0.3729.169 Mobile Safari/537.36",
        'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,"
                  "application/signed-exchange;v=b3",
        'accept-encoding': "gzip, deflate, br",
        'accept-language': "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
        'Connection': "keep-alive"
    }

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(TmallSpiderSpider, cls).from_crawler(
            crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened, signals.spider_opened)
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)
        return spider

    def spider_opened(self, spider):
        self.logger.info('start tmall_spider')

    def spider_closed(self, spider):
        pass

    def start_requests(self):
        """
        抓取区域代码
        :return:
        """
        headers = {
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0",
            'Accept': "*/*",
            'Accept-Language': "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            # 这里必须加上Referer
            'Referer': "https://chaoshi.tmall.com",
            'Connection': "keep-alive",
            'Cache-Control': "no-cache",
            'accept-encoding': "gzip, deflate",
            'cache-control': "no-cache"
        }
        yield scrapy.Request(self.area_code, headers=headers, dont_filter=True)

    def parse(self, response):
        """
        获取省市地址代码
        抓取第一页
        :param response:
        :return:
        """
        area = response.json()['siteList']['1']['areas']
        province_data = []
        for i in area:
            province_data.append(
                {i['province']['code'][:2]: i['province']['text']}
            )

        url = self.list_url.replace('&s={}', '')
        yield scrapy.Request(url, meta={'area': province_data}, callback=self.parse_list)

    def parse_list(self, response):
        """
        翻页并进入详情页
        每页有40条数据
        :param response:
        :return:
        """
        if 'login' in response.url:
            times_ = response.meta.get('cus_retry_times', 0) + 1

            if times_ < 10:
                r = response.request.copy()
                r = r.replace(url=response.request.meta['redirect_urls'][0])
                r.dont_filter = True
                r.priority = 10
                r.meta['cus_retry_times'] = times_
                yield r
            else:
                self.logger.error('retry too many {}'.format(response.request.meta['redirect_urls'][0]))
            return

        area = response.meta['area']

        # data-id="587075048581"
        item_list = re.findall('data-itemid="(\d+)"', response.text)

        for item in item_list:
            detail_url = self.detail_url.format(item)
            yield scrapy.Request(detail_url, callback=self.parse_detail,
                                 headers=self.detail_headers, meta={'area': area})

        # 在第一页时处理翻页
        if '&s=' not in response.url:
            # 总页数，40 offset
            total_page = response.xpath('//li[@class="quick-page-changer"]/span/text()').extract_first().split('/')[1]
            for i in range(2, int(total_page) + 1):
                url = self.list_url.format((i - 1) * 40)
                yield scrapy.Request(url, callback=self.parse_list, meta={'area': area})

    def parse_detail(self, response):
        """
        抓取html中的soldAreas
        https://detail.m.tmall.com/item.htm?id=12425590998

        :param response:
        :return:
        """
        item = TmallItem()
        item['item_id'] = response.url.split('id=')[1]
        item['title'] = response.xpath('//div[@class="main cell"]/text()').extract_first().strip()

        area = response.meta['area']
        data = re.findall('"soldAreas":\[(.*)]},"currentAreaEnable"', response.text)[0].split(',')
        province_list = []

        unique_area = set([i[:2] for i in data])
        for i in unique_area:
            for j in area:
                if i in j:
                    province_list.append(j[i])

        item['province_list'] = province_list
        yield item
