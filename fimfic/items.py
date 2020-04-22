# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FimficStory(scrapy.Item):
    shelf_user_id = scrapy.Field()
    shelf_user_name = scrapy.Field()
    shelf_id = scrapy.Field()
    shelf_name = scrapy.Field()
    name = scrapy.Field()
    link = scrapy.Field()
    dl_link = scrapy.Field()
    filename = scrapy.Field()
    body = scrapy.Field()

