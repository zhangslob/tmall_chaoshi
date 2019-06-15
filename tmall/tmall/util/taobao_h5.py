#!/usr/bin/env python  
# -*- coding: utf-8 -*-

import re
import json
import requests
from time import time
from hashlib import md5
from urllib.parse import urljoin
from collections import OrderedDict

config_ = {
        "domain": "https://h5api.m.taobao.com",
        "path": "h5",
        "appkey": "12574478",
        "loginURL": "https://login.taobao.com/member/login.jhtml",
        "redirectURL": "https://www.taobao.com/",
        "method": "get"
    }


class Taobao(object):
    def __init__(self, config=None):
        super(Taobao, self).__init__()
        if config is None:
            config = config_
        self.config = config
        self.s = requests.session()
        self.s.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/72.0.3626.121 Safari/537.36 '
        })

        self.__first()

    def __first(self, domain='https://h5api.m.taobao.com', url="/h5/mtop.taobao.wireless.home.load/1.0/?appKey=12574478"):
        """
        必须首先请求一个api来获取到h5token
        有多个API时，需要先获取多个API下面的token
        如果是https://h5api.m.tmall.com下的API也是需要先获取token的
        :param domain: str = 'https://h5api.m.taobao.com'
        :param url: str = "/h5/mtop.taobao.wireless.home.load/1.0/?appKey=12574478"
        :return:
        """
        return self.s.get(urljoin(domain, url))

    @staticmethod
    def h5_sign(token, t, appkey, data):
        """
        加密方式采用淘宝H5网页的加密流程
        data传递使用的是字符串，一是为了少加密一次，二是为了直接说明这个要转成json字符串，还需要去掉空格
        :param token: str
        :param t: str 时间戳、毫秒级别
        :param appkey: str
        :param data: str
        :return:
        """
        sign_str = f'{token}&{t}&{appkey}&{data}'
        return getattr(md5(sign_str.encode('utf-8')), 'hexdigest')()

    def get_cookie(self, name='_m_h5_tk', domain='.taobao.com', start=0, end=32):
        """
        获取Cookie，默认使用H5的token名称，然后取32位
        :param name: str = "_m_h5_tk"
        :param domain: str = '.taobao.com'
        :param start: int = 0
        :param end: int = 32
        :return:
        """
        return self.s.cookies.get(name, domain=domain)[start:end] if\
            self.s.cookies.get(name, default='', domain=domain) else ''

    def execute(self, data_list: dict):
        data = data_list.pop('data', {})
        data_str = json.dumps(data, separators=(',', ':'))
        t = str(int(time() * 1000))
        app_key = self.config.get('appkey')
        domain = re.findall(r'\.[a-zA-Z0-9]+\.[a-z]+$', self.config['domain'])
        domain = domain[0] if domain else '.taobao.com'

        # 获取加密sign
        sign = self.h5_sign(self.get_cookie(domain=domain), t, app_key, data_str)
        data_list.update({'sign': sign, 'data': data_str, 't': t, 'appkey': app_key})

        options = OrderedDict()
        options['method'] = data_list.get('method', 'get')
        if self.config.get('path').find('/rest/') > -1:
            url = '/'.join([self.config.get('domain'), self.config.get('path')])
        else:
            url = '/'.join(
                [self.config.get('domain'), self.config.get('path'), data_list.get('api').lower(), data_list.get('v')])
        options['url'] = url
        if options['method'] == 'get':
            options['params'] = data_list
        else:
            options['data'] = data_list
        return self.s.request(**options)


def get_list_result(tb, page):
    """
    获取列表结果
    :param tb: object
    :param page: int
    :return:
    """
    res = tb.execute({
        'api': 'mtop.chaoshi.aselfshoppingguide.common.icon.subpage',
        'v': '1.0',
        'jsv': '2.4.16',
        'dataType': 'json',
        'type': 'json',
        'data': {"smAreaId": 330100, "logical": "HD", "cityId": 330100, "pageSize": 20, "index": page*20,
                 "iconId": "92",
                 "subLevelId": "867", "queryItem": True, "queryModel": True, "queryActivity": False,
                 "clientUserEmb": "", "userEmbTime": int(time()*1000)}
    })
    return res.json()


def category_list():
    """
    循环抓取，直至没有数据
    :return:
    """
    total_item = set()
    tb = Taobao()

    running = True
    page = 0
    while running:
        result = get_list_result(tb, page)

        if result['data']['items']['hasMore']:
            page += 1
            for item in result['data']['items']['recommendItemVOList']:
                total_item.add(item['itemId'])
        else:
            running = False

    return total_item


# if __name__ == '__main__':
#     main()
