# -*- coding: utf-8 -*-
# no vpn needed.
# convert csv to xlsx on command line - 
# needed to correctly display double zeros. csv openoffice removes leading zeros.
import scrapy
import json
import time
import urllib
import re

class ChatHtmlSpider(scrapy.Spider):
    name = 'chat_html'
    time_now = int(time.time())
    data_year_month = time.strftime('%Y%m')

    def start_requests(self):
        categories = [
            'https://www.lechateau.com/en-ca/Dresses/category/cat37630709',
            'https://www.lechateau.com/en-ca/Womens-Clothing/Tops-Blouse/category/catwfr10025',
            'https://www.lechateau.com/en-ca/Womens-Clothing/Sweaters+%26+Cardigans/category/cat43770731',
            'https://www.lechateau.com/en-ca/Womens-Clothing/Blazers+%26+Vests/category/catwfr10030',
            'https://www.lechateau.com/en-ca/Womens-Clothing/Pants+/category/catwfr10028',
            'https://www.lechateau.com/en-ca/Womens-Clothing/Skirts/category/catwfr10029',
            'https://www.lechateau.com/en-ca/Womens-Clothing/Jackets+%26+Coats/category/catwfr10031',
            'https://www.lechateau.com/en-ca/Womens-Clothing/Jumpsuits/category/cat37520707',
            'https://www.lechateau.com/en-ca/browse/subcategoryBanner.jsp?categoryId=cat38060705',
            'https://www.lechateau.com/en-ca/OUTLET+STORE/Dresses/category/cat37310731',
            'https://www.lechateau.com/en-ca/OUTLET+STORE/Tops+/category/cat38951423',
            'https://www.lechateau.com/en-ca/OUTLET+STORE/Sweaters+%26+Cardigans/category/cat37310729',
            'https://www.lechateau.com/en-ca/OUTLET+STORE/Blazers+%26+Vests/category/cat37310737',
            'https://www.lechateau.com/en-ca/OUTLET+STORE/Skirts/category/cat37310735',
            'https://www.lechateau.com/en-ca/OUTLET+STORE/Jackets+%26+Coats/category/cat37310741',
            'https://www.lechateau.com/en-ca/OUTLET+STORE/Jumpsuits/category/cat44980710',
            'https://www.lechateau.com/en-ca/OUTLET+STORE/Accessories/category/cat39310746',
            'https://www.lechateau.com/en-ca/Mens-Clothing/Shirts/category/cat38991707',
            'https://www.lechateau.com/en-ca/Mens-Clothing/Casual-Tops-T-Shirts/category/catmfr20026',
            'https://www.lechateau.com/en-ca/Mens-Clothing/Sweaters-Cardigans-Knitwear/category/catmfr20027',
            'https://www.lechateau.com/en-ca/Mens-Clothing/Blazers+%26+Vests/category/cat43900702',
            'https://www.lechateau.com/en-ca/Mens-Clothing/Pants/category/catmfr20028',
            'https://www.lechateau.com/en-ca/Mens-Clothing/Jackets+%26+Coats/category/catmfr20030',
            'https://www.lechateau.com/style/browse/subcategoryBanner.jsp?categoryId=cat37680833',
            'https://www.lechateau.com/en-ca/OUTLET+STORE/Shirts/category/cat47050703',
            'https://www.lechateau.com/en-ca/OUTLET+STORE/Knits+%26+Tees/category/cat37310747',
            'https://www.lechateau.com/en-ca/OUTLET+STORE/Sweaters+%26+Cardigans/category/cat37310751',
            'https://www.lechateau.com/en-ca/OUTLET+STORE/Blazers+%26+Vests/category/cat37310755',
            'https://www.lechateau.com/en-ca/OUTLET+STORE/Pants+/category/cat37310753',
            'https://www.lechateau.com/en-ca/OUTLET+STORE/Jackets+%26+Coats/category/cat37310757',
            'https://www.lechateau.com/en-ca/OUTLET+STORE/Accessories/category/cat39310747',
            'https://www.lechateau.com/en-ca/Womens-Shoes-Footwear/All+Shoes+%26+Boots/category/cat38531287',
            'https://www.lechateau.com/en-ca/Accessories/Handbags+%26+Wallets/category/cat130018',
            'https://www.lechateau.com/en-ca/Accessories/Hats%2C+Scarves+%26+Gloves/category/cat43810710',
            'https://www.lechateau.com/en-ca/Accessories/Belts+%26+Sashes/category/cat37680817',
            'https://www.lechateau.com/style/browse/subcategoryBanner.jsp?categoryId=cat37680833',
            'https://www.lechateau.com/en-ca/Accessories/Ties+%26+Bow+Ties/category/cat43810703',
            'https://www.lechateau.com/en-ca/Accessories/Belts+%26+Suspenders+/category/cat37680832',
            'https://www.lechateau.com/en-ca/WORK/Blazers/category/catwfr10131',
            'https://www.lechateau.com/en-ca/WORK/Pants+/category/catwfr10231',
            'https://www.lechateau.com/en-ca/WORK/Skirts+/category/catwfr10331',
            'https://www.lechateau.com/en-ca/WORK/Tops+%26+Sweaters/category/cat38871257',
            'https://www.lechateau.com/en-ca/WORK/Dresses+%26+Jumpsuits/category/catwfr10631'
        ]
        for category in categories:
            yield scrapy.Request(
                                url=category,
                                callback=self.parse_category
            )

    def parse_category(self, response):
        base = 'https://www.lechateau.com'
        products = response.xpath('//h3/a/@href').getall()
        for product in products:
            yield scrapy.Request(
                                url=f'{base}{product}',
                                callback=self.parse_product
            )

        next_page = response.xpath('//a[@class="next"]/@href').get()
        if next_page:
            yield scrapy.Request(
                                url=f'{base}{next_page}',
                                callback=self.parse_category
            )

    def parse_product(self, response):
        product_link = response.url
        product_name = response.xpath('//div[@id="productInfoBox"]/h3/text()').get()
        product_name = product_name.strip()
        brand = 'Le Chateau'
        crumbs = response.xpath('//ul[@class="breadcrumbs"]/li/a/text()').getall()
        formatted_crumbs = []
        for crumb in crumbs:
            crumb = crumb.strip()
            formatted_crumbs.append(crumb)
        category = '|'.join(formatted_crumbs)
        original_price = response.xpath('//span[@class="price old"]/strong/text()').get()
        original_price = original_price.strip()
        regular_price = original_price.replace('&nbsp;', '')
        regular_price = regular_price.replace('$', '')
        discounted_price = response.xpath('//span[@class="price sale"]/strong/text()').get()
        if discounted_price:
            discounted_price = discounted_price.strip()
            discounted_price = discounted_price.replace('&nbsp;', '')
            discounted_price = discounted_price.replace('$', '')
        image_link = response.xpath('//img[@class="slidesjs-slide"]/@src').get() # not available in colour resp.
        available_sizes = response.xpath('//div[@class="attribute squares"]/ul/li/a[@class="atg_store_pickerAttribute "]/text()').getall()
        unavailable_sizes = response.xpath('//div[@class="attribute squares"]/ul/li/a[@class="disabled"]/text()').getall()
        color = response.xpath('//div[@class="attribute colors"]/ul/li[@class="selected "]/a/@data-color').get()
        color_code = response.xpath('//div[@class="attribute colors"]/ul/li[@class="selected "]/a/img/@alt').get()
        image_link = f'https://lechateau.scene7.com/is/image/LeChateau/{color_code}_1_469x587.jpg'
        sku_string = response.xpath('//script[@type="application/ld+json"]/text()').get()
        sku_pattern = r'"sku":"[0-9]+"'
        result = re.search(sku_pattern, sku_string)
        unformatted_sku = result.group()
        sku = unformatted_sku[7:-1]
        if available_sizes:
            for size in available_sizes:
                if size[-1] == '½':
                    size =size[:-1] + '.5'
                if not color:
                    continue
                if category.endswith('|'):
                    category = category[:-1]
                if product_link == 'https://www.lechateau.com/en-ca/Geo+Print+Cut+%26+Sew+Knit+V-Neck+Slit+Tunic/productDetail/Sleeveless+Tops/350034/cat38951423?navAction=jump&navCount=6649&categoryNav=true&selectedColor=Bordeaux/Black':
                    category = 'home|outlet store|tops|sleeveless tops'
                if not category:
                    continue
                yield {
                    'product_link': product_link,
                    'product_name': product_name, 
                    'brand': brand, 
                    'category': category,
                    'regular_price': regular_price, 
                    'discounted_price': discounted_price,
                    'price_unit': None,
                    'size': str(size),
                    'color': color,
                    'flavor': None, 
                    'weight': None, 
                    'average_rating': None, 
                    'num_reviews': None, 
                    'image_link': image_link,
                    'sku': sku, 
                    'upc': None,
                    'stock_level': 'In_Stock',
                    'sold_by_3rd_party': 0,
                    'shipped_by': None,
                    'data_timestamp': self.time_now,
                    'data_year_month': self.data_year_month
                        }

        if unavailable_sizes:
            for size in unavailable_sizes:
                if size[-1] == '½':
                    size =size[:-1] + '.5'
                if not color:
                    continue
                if category.endswith('|'):
                    category = category[:-1]
                if product_link == 'https://www.lechateau.com/en-ca/Geo+Print+Cut+%26+Sew+Knit+V-Neck+Slit+Tunic/productDetail/Sleeveless+Tops/350034/cat38951423?navAction=jump&navCount=6649&categoryNav=true&selectedColor=Bordeaux/Black':
                    category = 'home|outlet store|tops|sleeveless tops'
                if not category:
                    continue
                yield {
                    'product_link': product_link,
                    'product_name': product_name, 
                    'brand': brand, 
                    'category': category,
                    'regular_price': regular_price, 
                    'discounted_price': discounted_price,
                    'price_unit': None,
                    'size': str(size),
                    'color': color,
                    'flavor': None, 
                    'weight': None, 
                    'average_rating': None, 
                    'num_reviews': None, 
                    'image_link': image_link,
                    'sku': sku, 
                    'upc': None,
                    'stock_level': 'Not_In_Stock',
                    'sold_by_3rd_party': 0,
                    'shipped_by': None,
                    'data_timestamp': self.time_now,
                    'data_year_month': self.data_year_month
                        }
        variant_colours = response.xpath('//div[@class="attribute colors"]/ul/li[not(@class="selected ")]/a/@data-color').getall()
        product_id = response.xpath('//input[@name="productId"]/@value').get()
        if variant_colours:
            for colour in variant_colours:
                col_dict = {
                    'selectedColor': colour
                }
                col_url = urllib.parse.urlencode(col_dict)
                colour_endpoint = f'https://www.lechateau.com/en-ca/browse/gadgets/pickerContents.jsp?productId={product_id}&{col_url}&locale=en_CA'
                yield scrapy.Request(
                                    url=colour_endpoint,
                                    callback=self.parse_colour_variant,
                                    meta={
                                        'product_name': product_name,
                                        'product_link': product_link,
                                        'brand': brand,
                                        'category': category,
                                        'sku': sku
                                    }
                )
    
    def parse_colour_variant(self, response):
        product_name = response.meta.get('product_name')
        product_link = response.meta.get('product_link')
        brand = response.meta.get('brand')
        category = response.meta.get('category')
        sku = response.meta.get('sku')
        original_price = response.xpath('//span[@class="price old"]/strong/text()').get()
        original_price = original_price.strip()
        regular_price = original_price.replace('&nbsp;', '')
        regular_price = regular_price.replace('$', '')
        discounted_price = response.xpath('//span[@class="price sale"]/strong/text()').get()
        if discounted_price:
            discounted_price = discounted_price.strip()
            discounted_price = discounted_price.replace('&nbsp;', '')
            discounted_price = discounted_price.replace('$', '')
        available_sizes = response.xpath('//div[@class="attribute squares"]/ul/li/a[@class="atg_store_pickerAttribute "]/text()').getall()
        unavailable_sizes = response.xpath('//div[@class="attribute squares"]/ul/li/a[@class="disabled"]/text()').getall()
        color = response.xpath('//div[@class="attribute colors"]/ul/li[@class="selected "]/a/@data-color').get()
        color_code = response.xpath('//div[@class="attribute colors"]/ul/li[@class="selected "]/a/img/@alt').get()
        image_link = f'https://lechateau.scene7.com/is/image/LeChateau/{color_code}_1_469x587.jpg'
        if available_sizes:
            for size in available_sizes:
                if size[-1] == '½':
                    size =size[:-1] + '.5'
                if not color:
                    continue
                if category.endswith('|'):
                    category = category[:-1]
                if product_link == 'https://www.lechateau.com/en-ca/Geo+Print+Cut+%26+Sew+Knit+V-Neck+Slit+Tunic/productDetail/Sleeveless+Tops/350034/cat38951423?navAction=jump&navCount=6649&categoryNav=true&selectedColor=Bordeaux/Black':
                    category = 'home|outlet store|tops|sleeveless tops'
                if not category:
                    continue
                yield {
                    'product_link': product_link,
                    'product_name': product_name, 
                    'brand': brand, 
                    'category': category,
                    'regular_price': regular_price, 
                    'discounted_price': discounted_price,
                    'price_unit': None,
                    'size': str(size),
                    'color': color,
                    'flavor': None, 
                    'weight': None, 
                    'average_rating': None, 
                    'num_reviews': None, 
                    'image_link': image_link,
                    'sku': sku, 
                    'upc': None,
                    'stock_level': 'In_Stock',
                    'sold_by_3rd_party': 0,
                    'shipped_by': None,
                    'data_timestamp': self.time_now,
                    'data_year_month': self.data_year_month
                        }

        if unavailable_sizes:
            for size in unavailable_sizes:
                if size[-1] == '½':
                    size =size[:-1] + '.5'
                if not color:
                    continue
                if category.endswith('|'):
                    category = category[:-1]
                if product_link == 'https://www.lechateau.com/en-ca/Geo+Print+Cut+%26+Sew+Knit+V-Neck+Slit+Tunic/productDetail/Sleeveless+Tops/350034/cat38951423?navAction=jump&navCount=6649&categoryNav=true&selectedColor=Bordeaux/Black':
                    category = 'home|outlet store|tops|sleeveless tops'
                if not category:
                    continue
                yield {
                    'product_link': product_link,
                    'product_name': product_name, 
                    'brand': brand, 
                    'category': category,
                    'regular_price': regular_price, 
                    'discounted_price': discounted_price,
                    'price_unit': None,
                    'size': str(size),
                    'color': color,
                    'flavor': None, 
                    'weight': None, 
                    'average_rating': None, 
                    'num_reviews': None, 
                    'image_link': image_link,
                    'sku': sku, 
                    'upc': None,
                    'stock_level': 'Not_In_Stock',
                    'sold_by_3rd_party': 0,
                    'shipped_by': None,
                    'data_timestamp': self.time_now,
                    'data_year_month': self.data_year_month
                        }





# {'downloader/request_bytes': 4653935,
#  'downloader/request_count': 6842,
#  'downloader/request_method_count/GET': 6842,
#  'downloader/response_bytes': 157402161,
#  'downloader/response_count': 6842,
#  'downloader/response_status_count/200': 6803,
#  'downloader/response_status_count/404': 39,
#  'dupefilter/filtered': 466,
#  'elapsed_time_seconds': 573.870797,
#  'finish_reason': 'finished',
#  'finish_time': datetime.datetime(2021, 4, 21, 8, 33, 42, 568237),
#  'item_scraped_count': 46779,
#  'log_count/DEBUG': 53622,
#  'log_count/ERROR': 8,
#  'log_count/INFO': 20,
#  'memusage/max': 169037824,
#  'memusage/startup': 55513088,
#  'request_depth_max': 12,
#  'response_received_count': 6803,
#  'scheduler/dequeued': 6842,
#  'scheduler/dequeued/memory': 6842,
#  'scheduler/enqueued': 6842,
#  'scheduler/enqueued/memory': 6842,
#  'spider_exceptions/AttributeError': 8,
#  'start_time': datetime.datetime(2021, 4, 21, 8, 24, 8, 697440)}

#  'item_scraped_count': 58735,
# 46119


