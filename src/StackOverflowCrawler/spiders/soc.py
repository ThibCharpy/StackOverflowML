# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class CrawlerSpider(scrapy.Spider):
    name = 'crawler'
    allowed_domains = ['stackoverflow.com']
    start_urls = ['http://stackoverflow.com/']

    rules = (
        Rule(LinkExtractor(allow=(), restrict_css=('.nav-questions',)),
             callback="parse_item"))

    def parse_item(self, response):
        print('Processing..' + response.url)
