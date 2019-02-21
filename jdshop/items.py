# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JdBarItem(scrapy.Item):
    id = scrapy.Field()
    content = scrapy.Field()
    productColor = scrapy.Field()
    productSize = scrapy.Field()
    referenceName = scrapy.Field()
