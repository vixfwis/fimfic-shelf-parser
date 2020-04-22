# -*- coding: utf-8 -*-
import scrapy
import re
from fimfic.items import FimficStory

filename_header_re = re.compile(r'filename="(.+)"')
shelf_id_re = re.compile(r'bookshelf/(\d+)/')


class BookshelfSpider(scrapy.Spider):
    name = 'bookshelf'
    allowed_domains = ['fimfiction.net']
    user_ids = ['260203']
    archive_path = '/home/vixfwis/fimfic-archive/archive/'

    def start_requests(self):
        for uid in self.user_ids:
            yield scrapy.Request(
                f'https://www.fimfiction.net/user/{uid}/',
                callback=self.find_user_name,
                meta={'user_id': uid},
                cookies={'view_mature': 'true'}
            )

    def find_user_name(self, response):
        meta = response.meta
        cookies = response.request.cookies
        cookies.update({'view_mature': 'true'})
        uid = meta['user_id']
        name = response.css('.info-container h1 a::text').get()
        meta.update({'user_name': name})
        yield scrapy.Request(
            f'https://www.fimfiction.net/user/{uid}/{name}/library',
            callback=self.parse, meta=meta, cookies=cookies
        )

    def parse(self, response):
        meta = response.meta
        cookies = response.request.cookies
        cookies.update({'view_mature': 'true'})
        shelves = response.css('.bookshelf-card .bookshelf-icon a::attr(href)').getall()
        for link in shelves:
            yield scrapy.Request(response.urljoin(link), callback=self.shelf_parser, meta=meta, cookies=cookies)

    def shelf_parser(self, response):
        meta = response.meta
        cookies = response.request.cookies
        cookies.update({'view_mature': 'true'})
        if 'name' not in meta:
            name = response.css('#bookshelf-selected-list .bookshelf-name a::text').get()
            meta['name'] = name
        if 'id' not in meta:
            id = shelf_id_re.findall(response.url)[0]
            meta['id'] = id
        next_page = response.urljoin(response.css('.page_list a::attr(href)').getall()[-1])
        if next_page != response.url:
            yield scrapy.Request(next_page, callback=self.shelf_parser, meta=meta, cookies=cookies)
        for story in response.css('.story_container'):
            name = story.css('a.story_name::text').get()
            link = response.urljoin(story.css('a.story_name::attr(href)').get())
            dl_link = response.urljoin(story.css('.download .drop-down a::attr(href)').getall()[0])
            meta.update({
                'story_name': name,
                'story_link': link,
                'story_dl_link': dl_link
            })
            yield scrapy.Request(dl_link, callback=self.download_story, meta=meta, cookies=cookies)

    def download_story(self, response):
        meta = response.meta
        header = response.headers['Content-Disposition'].decode('utf-8')
        filename = filename_header_re.findall(header)[0]
        yield FimficStory(
            shelf_user_id=meta['user_id'],
            shelf_user_name=meta['user_name'],
            shelf_id=meta['id'],
            shelf_name=meta['name'],
            name=meta['story_name'],
            link=meta['story_link'],
            dl_link=meta['story_dl_link'],
            filename=filename,
            body=response.body.decode('utf-8')
        )
