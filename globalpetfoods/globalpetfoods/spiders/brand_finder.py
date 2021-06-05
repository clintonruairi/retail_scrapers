# NEEDS TO BE RUN FIRST, OUTPUT JSON. NAME JSON = GLOBALPETFOODSBRANDS
import scrapy
from globalpetfoods.items import MySQLItem
import time
import random
import re

class DupontglobalpetfoodsSpider(scrapy.Spider):
    name = 'danforthglobalpetfoods'
    allowed_domains = ['danforth.globalpetfoods.com']

    def start_requests(self):
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'referer': 'https://danforth.globalpetfoods.com/products/shop/',
            'sec-ch-ua': '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36'
        }
        current_time = int(time.time())
        start_url = 'https://danforth.globalpetfoods.com/products/shop-by-brand/'
        yield scrapy.Request(
                            url=start_url,
                            callback=self.parse_brands,
                            meta={
                                'time': current_time
                            },
                            headers=headers
        )
    
    def parse_brands(self, response):
        time = response.meta.get('time')
        brand_links = response.xpath('//div[@class="col-md-3 col-sm-3 col-xs-4 product-list-box equi-height"]/a/@href').getall()
        brand_names = response.xpath('//div[@class="col-md-3 col-sm-3 col-xs-4 product-list-box equi-height"]/a/@title').getall()
        brand_info = dict(zip(brand_links, brand_names))
        referer = response.url
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'referer': referer,
            'sec-ch-ua': '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36'

        }
        for link, brand in brand_info.items():
            yield scrapy.Request(
                                url=f'https://danforth.globalpetfoods.com{link}',
                                callback=self.parse_search_results,
                                meta={
                                    'time': time,
                                    'brand': brand
                                },
                                headers=headers
            )
        next_page = response.xpath('//a[text()="Next"]/@href').get()
        if next_page:
            next_page = next_page.strip()
            yield scrapy.Request(
                                url=f'https://danforth.globalpetfoods.com{next_page}',
                                meta={
                                    'time': time,
                                },
                                headers=headers,
                                callback=self.parse_brands
                )

    def parse_search_results(self, response):
        brand = response.meta.get('brand')
        time = response.meta.get('time')
        product_links = response.xpath('//div[@class="prdct-detail-box"]/h3/a/@href').getall()
        base = 'https://danforth.globalpetfoods.com'
        referer = response.url
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'referer': referer,
            'sec-ch-ua': '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36'

        }
        for link in product_links:
            link = link.strip()
            yield {
                f'{base}{link}': brand
            }

        next_page = response.xpath('//a[text()="Next"]/@href').get()
        if next_page:
            next_page = next_page.strip()
            yield scrapy.Request(
                                url=f'{base}{next_page}',
                                meta={
                                    'brand': brand,
                                    'time': time
                                },
                                headers=headers,
                                callback=self.parse_search_results
                )


