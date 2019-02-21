# -*- coding: utf-8 -*-
import scrapy
import json
from urllib.parse import quote
from jdshop.items import JdBarItem
import time


class JdbarSpider(scrapy.Spider):
    name = 'jdbar'
    allowed_domains = ['www.jd.com', 'sclub.jd.com']
    start_urls = ['http://www.jd.com/']

    # 初始化请求
    def start_requests(self):
        # 搜索关键词
        kw = quote(self.settings.get('KEYWORD'))
        # 排序方式
        method = self.settings.get('METHOD')[4]
        # 请求地址
        url = "https://search.jd.com/Search?keyword={}&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq={}{}&click=0"
        if method == 0:
            endurl = url.format(kw, kw, '')
        else:
            endurl = url.format(kw, kw, "&psort={}".format(method))
        # 返回请求
        yield scrapy.Request(url=endurl, callback=self.parse, method="GET")

    # 返回请求处理
    def parse(self, response):
        # 提取商品ID
        goodlist = response.xpath('//*[@id="J_goodsList"]/ul/li[@class="gl-item"]/@data-sku').extract()
        goodlist = set(goodlist)  # 去重
        jsonformat = 'fetchJSON_comment98vv899'
        # print(goodlist)
        for goods in goodlist:
            next_url = "https://sclub.jd.com/comment/productPageComments.action?callback={}&productId={}" \
                       "&score=0&sortType=5&page=0&pageSize=10&isShadowSku=0&fold=1".format(jsonformat, goods)
            time.sleep(1)
            yield scrapy.Request(url=next_url, callback=self.parse_json, method='GET',
                                 meta={'goods': goods, 'jsonformat': jsonformat})

    def get_item(self, data):
        jbi = JdBarItem()
        jbi['id'] = data['id']
        jbi['content'] = data['content']
        jbi['productColor'] = data['productColor']
        jbi['productSize'] = data['productSize']
        jbi['referenceName'] = data['referenceName']
        return jbi

    def parse_json(self, response):
        goods = response.meta['goods']
        jsonformat = response.meta['jsonformat']
        datas = json.loads(response.text.replace(jsonformat + '(', '').replace(');', ''))
        for data in datas['comments']:
            yield self.get_item(data)

        max_page = datas['maxPage']
        for pn in range(2, int(max_page) + 1):
            page_url = "https://sclub.jd.com/comment/productPageComments.action?callback={}&productId={}&score=0&" \
                       "sortType=5&page={}&pageSize=10&isShadowSku=0&rid=0&fold=1".format(jsonformat, goods, pn)
            time.sleep(1)
            yield scrapy.Request(url=page_url, callback=self.parse_next, meta={'jsonformat': jsonformat})

    def parse_next(self, response):
        jsonformat = response.meta['jsonformat']
        print(response.text)
        datas = json.loads(response.text.replace(jsonformat + '(', '').replace(');', ''))
        for data in datas['comments']:
            yield self.get_item(data)
