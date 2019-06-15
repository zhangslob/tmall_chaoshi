#!/usr/bin/env python  
# -*- coding: utf-8 -*-
import re

import requests
from scrapy.selector import Selector

headers = {
    'authority': 'login.taobao.com',
    'cache-control': 'max-age=0',
    'origin': 'https://login.taobao.com',
    'upgrade-insecure-requests': '1',
    'content-type': 'application/x-www-form-urlencoded',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'referer': 'https://login.taobao.com/',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
    'cookie': 'cookieCheck=71888; t=5c9c62b5d999babd74f896ac0370b5ef; cookie2=18fd65b898ec262e856da948cbaa5c93; v=0; _tb_token_=e033308e6ee63',
}

data = {
  'TPL_username': '18513073622',
  'TPL_password': '456813abc.',
  'ncoSig': '',
  'ncoSessionid': '',
  'ncoToken': '',
  'slideCodeShow': 'false',
  'useMobile': 'false',
  'lang': 'zh_CN',
  'loginsite': '0',
  'newlogin': '',
  'TPL_redirect_url': '',
  'from': 'tb',
  'fc': 'default',
  'style': 'default',
  'css_style': '',
  'keyLogin': 'false',
  'qrLogin': 'true',
  'newMini': 'false',
  'newMini2': 'false',
  'tid': '',
  'loginType': '3',
  'minititle': '',
  'minipara': '',
  'pstrong': '',
  'sign': '',
  'need_sign': '',
  'isIgnore': '',
  'full_redirect': '',
  'sub_jump': '',
  'popid': '',
  'callback': '',
  'guf': '',
  'not_duplite_str': '',
  'need_user_id': '',
  'poy': '',
  'gvfdcname': '',
  'gvfdcre': '',
  'from_encoding': '',
  'sub': '',
  'TPL_password_2': '',
  'loginASR': '1',
  'loginASRSuc': '0',
  'allp': '',
  'oslanguage': '',
  'sr': '',
  'osVer': '',
  'naviVer': '',
  'osACN': '',
  'osAV': '',
  'osPF': '',
  'miserHardInfo': '',
  'appkey': '00000000',
  'nickLoginLink': '',
  'mobileLoginLink': 'https://login.taobao.com/member/login.jhtml?useMobile=true',
  'showAssistantLink': ''
}

s = requests.session()
s.headers.update(headers)


def get_nco_token():
    """
    获取登录参数必须的ncoToken
    :return:
    """
    r = s.get('https://login.taobao.com/')
    select = Selector(text=r.text)
    nco_token = select.xpath('//*[@id="J_NcoToken"]/@value').extract_first()
    return nco_token


def get_cookie():
    """
    登录并获取返回的cookies
    :return:
    """
    data['ncoToken'] = get_nco_token()
    response = s.post('https://login.taobao.com/member/login.jhtml?redirectURL=https%3A%2F%2Fwww.taobao.com%2F', data=data)
    s.get('https://chaoshi.tmall.com')
    # r = s.get('https://list.tmall.com/search_product.htm?cat=50502048&&user_id=725677994')
    cookie = dict(response.cookies)
    print(cookie)

    url = 'https://list.tmall.com/search_product.htm?tbpm=3&spm=a3204.7933263.0.0.6d0822585XpGKt&cat=50502048&s={}&sort=s&style=g&search_condition=1&user_id=725677994,2136152958&active=1&industryCatId=50514008&smAreaId=330100#J_Filter'

    for i in range(2, 29):
        res = s.get(url.format(i * 40))
        result = set(re.findall('data-itemid="(\d+)"', res.text))
        print(len(result))

    return cookie


# get_cookie()