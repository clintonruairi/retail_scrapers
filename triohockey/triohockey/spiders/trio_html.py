# -*- coding: utf-8 -*-
import scrapy
import re
import time

class TrioHtmlSpider(scrapy.Spider):
    name = 'trio_html'
    time_now = int(time.time())
    data_year_month = time.strftime('%Y%m')
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Cookie': 'cart=d0b5af47ff6d9a683932d8c6e5d0e984'
    }
    requested_skus = []
    
    def start_requests(self):
        yield scrapy.Request(
                        url='https://www.triohockey.ca/?lang=en',
                        callback=self.parse_categories,
                        headers=self.headers
        )

    def parse_categories(self, response):
        base = 'https://www.triohockey.ca/'
        categories = response.xpath('//li[@class="dropdown mega-dropdown"]/ul/div/li/ul/ul/li/a/@href').getall()
        for link in categories:
            yield scrapy.Request(
                            url=f'{base}{link}',
                            callback=self.parse_category,
                            headers=self.headers
            )
    
    def parse_category(self, response):
        base = 'https://www.triohockey.ca'
        links = response.xpath('//a[@class="product-tile-media"]/@href').getall()
        for link in links:
            yield scrapy.Request(
                                url=f'{base}{link}',
                                callback=self.parse_product,
                                headers=self.headers
            )

        next_page = response.xpath('//a[@aria-label="Next"]/@href').get()
        if next_page:
            yield scrapy.Request(
                                url=f'{base}{next_page}',
                                callback=self.parse_category,
                                headers=self.headers
            )

    def parse_product(self, response):
        size = None
        weight = None
        product_link = response.url
        product_name = response.xpath('//h1/text()').get()
        if product_name == 'Cable Knit Rib Cuffless Jr':
            product_link = 'https://www.triohockey.ca/collections/nhl-beanies/products/outer-stuff-cable-knit-rib-cuffless-jr-172895-en'
        product_info = response.xpath('//script[@type="application/ld+json"]/text()').get()
        brand_pattern = r'"name": ".*"'
        result = re.findall(brand_pattern, product_info)
        brand_string = result[1]
        brand_string = brand_string.replace('"name": ', '')
        brand = brand_string.replace('"', '')
        brand = brand.replace("&#39;", "'")
        crumbs = response.xpath('//ol[@class="breadcrumb"]/li/a/text()').getall()
        category = '|'.join(crumbs)
        original_price = response.xpath('//span[@class="original-price"]/following-sibling::br/following-sibling::span[@class="reg"]/text()').get()
        discounted_price = response.xpath('//span[@class="reg"]/following-sibling::br/following-sibling::span[@class="rebate"]/text()').get()
        if original_price:
            original_price = original_price.strip()
            original_price = original_price.replace('$', '')
            original_price = original_price.replace(',', '')
            regular_price = float(original_price)
            discounted_price = discounted_price.strip()
            discounted_price = discounted_price.replace('$', '')
            discounted_price = discounted_price.replace(',', '')
            discounted_price = float(discounted_price)
        else:
            regular_price = response.xpath('//div[@class="price-list"]/text()').get()
            regular_price = regular_price.strip()
            regular_price = regular_price.replace('$', '')
            discounted_price = None
        image_base = 'https:'
        image_relative = response.xpath('//img[@class="img-responsive"]/@src').get()
        image_link = image_base + image_relative
        sku = response.xpath('//div[@class="variant-sku"]/text()').get()
        sku = sku.strip()
        sku = sku.replace('SKU : ', '')
        if sku in self.requested_skus:
            return
        self.requested_skus.append(sku)
        stock_level = 'In_Stock'
        weight = response.xpath('//li[contains(text(), "Weight:")]/text()').get()
        if weight:
            weight = weight.replace('Weight: ', '')
            if '(' in weight:
                index = weight.index('(')
                weight = weight[:index]
        char_sizes = ['XXS', 'XS', 'S', 'SM', 'M', 'L', 'XL', '2XL', '3XL', '4XL', '5XL', '6XL']
        size = response.xpath('//li[contains(text(), "Size:")]/text()').get()
        available_sizes = response.xpath('//li[contains(text(), "Sizes:")]/text()').get()
        if not available_sizes:
            available_sizes = response.xpath('//li[contains(text(), "Sizes :")]/text()').get()
        if product_link == 'https://www.triohockey.ca/collections/skate-insole/products/superfeet-carbon-pro-hockey-9470-en':
            available_sizes = None
            size = None
        if product_link == 'https://www.triohockey.ca/collections/junior-youth-chest-protector/products/ccm-ytflex-2-540134-en':
            available_sizes = None
            size = None
        if not available_sizes:
            if size:
                size = size.replace('Sizes : ', '')
                size = size.replace('Sizes :', '')
                size = size.replace('Sizes: ', '')
                size = size.replace('Size:', '')
                size = size.replace('Size: ', '')
                size = size.replace('Size :', '')
                size = size.strip()
                if '/' in size:
                    size = size
                if '-' in size:
                    size = size
                else:
                    size_pattern = r'[0-9]+ ?"? ?(cm|to)? ?(to)? ?[0-9]+ ?(cm|")?'
                    result = re.search(size_pattern, size)
                    if result:
                        size = result.group()
                        size = size.strip()
                if '(' in size:
                    index = size.index('(')
                    size = size[:index]
                    size = size.strip()
            if sku == 'SKU :':
                sku = None
            yield {
            'product_link': product_link,
            'product_name': product_name, 
            'brand': brand, 
            'category': category,
            'regular_price': regular_price, 
            'discounted_price': discounted_price,
            'price_unit': None,
            'size': size,
            'color': None,
            'flavor': None, 
            'weight': weight,
            'average_rating': None, 
            'num_reviews': None, 
            'image_link': image_link,
            'sku': sku, 
            'upc': None,
            'stock_level': stock_level,
            'sold_by_3rd_party': 0,
            'shipped_by': None,
            'data_timestamp': self.time_now,
            'data_year_month': self.data_year_month
            }
        elif available_sizes:
            available_sizes = available_sizes.replace('Sizes: ', '')
            if ',' in available_sizes:
                sizes = available_sizes.split(',')
                if 'Sizes' in sizes:
                    sizes.remove('Sizes')
                if ':' in sizes:
                    sizes.remove(':')
                if 'Size' in sizes:
                    sizes.remove('Size')
                if 'Size:' in sizes:
                    sizes.remove('Size:')
                for size in sizes:
                    size = size.strip()
                    if 'Please' in size or 'that' in size or 'because' in size or 'style' in size:
                        continue
                    size = size.replace('Sizes : ', '')
                    if sku == 'SKU :':
                        sku = None
                    if '(' in size:
                        index = size.index('(')
                        size = size[:index]
                        size = size.strip()
                    yield {
                    'product_link': product_link,
                    'product_name': product_name, 
                    'brand': brand, 
                    'category': category,
                    'regular_price': regular_price, 
                    'discounted_price': discounted_price,
                    'price_unit': None,
                    'size': size,
                    'color': None,
                    'flavor': None, 
                    'weight': weight, 
                    'average_rating': None, 
                    'num_reviews': None, 
                    'image_link': image_link,
                    'sku': sku, 
                    'upc': None,
                    'stock_level': stock_level,
                    'sold_by_3rd_party': 0,
                    'shipped_by': None,
                    'data_timestamp': self.time_now,
                    'data_year_month': self.data_year_month
                    }
            else:
                if 'to' in available_sizes:
                    if 'Sizes' in available_sizes:
                        available_sizes = available_sizes.replace('Sizes', '')
                    if ':' in available_sizes:
                        available_sizes = available_sizes.replace(':', '')
                    if 'Size' in available_sizes:
                        available_sizes = available_sizes.replace('Size', '')
                    if 'Size:' in available_sizes:
                        available_sizes = available_sizes.replace('Size:', '')
                    if 'Sizes : ' in available_sizes:
                        available_sizes = available_sizes.replace('Sizes : ', '')
                    try:
                        sizes = available_sizes.split()
                        sizes = [size.strip() for size in sizes]
                        smallest_size = char_sizes.index(sizes[0])
                        biggest_size = char_sizes.index(sizes[-1])
                        for size in char_sizes[smallest_size:biggest_size + 1]:
                            if sku == 'SKU :':
                                sku = None
                            yield {
                                'product_link': product_link,
                                'product_name': product_name, 
                                'brand': brand, 
                                'category': category,
                                'regular_price': regular_price, 
                                'discounted_price': discounted_price,
                                'price_unit': None,
                                'size': size,
                                'color': None,
                                'flavor': None, 
                                'weight': weight, 
                                'average_rating': None, 
                                'num_reviews': None, 
                                'image_link': image_link,
                                'sku': sku, 
                                'upc': None,
                                'stock_level': stock_level,
                                'sold_by_3rd_party': 0,
                                'shipped_by': None,
                                'data_timestamp': self.time_now,
                                'data_year_month': self.data_year_month
                            }
                    except:
                        sizes = available_sizes.split()
                        sizes = [size.strip() for size in sizes]
                        if sizes[-1] == 'XXL' or sizes[-1] == 'XXXL':
                            for size in sizes:
                                char_sizes = ['XXS', 'XS', 'S', 'SM', 'M', 'L', 'XL', 'XXL', 'XXXL']
                                smallest_size = char_sizes.index(sizes[0])
                                biggest_size = char_sizes.index(sizes[-1])
                                for size in char_sizes[smallest_size:biggest_size + 1]:
                                    size = size.replace('Sizes : ', '')
                                    if sku == 'SKU :':
                                        sku = None
                                    yield {
                                        'product_link': product_link,
                                        'product_name': product_name, 
                                        'brand': brand, 
                                        'category': category,
                                        'regular_price': regular_price, 
                                        'discounted_price': discounted_price,
                                        'price_unit': None,
                                        'size': size,
                                        'color': None,
                                        'flavor': None, 
                                        'weight': weight, 
                                        'average_rating': None, 
                                        'num_reviews': None, 
                                        'image_link': image_link,
                                        'sku': sku, 
                                        'upc': None,
                                        'stock_level': stock_level,
                                        'sold_by_3rd_party': 0,
                                        'shipped_by': None,
                                        'data_timestamp': self.time_now,
                                        'data_year_month': self.data_year_month
                                        }
                        else:
                            size = available_sizes.replace('Sizes : ', '')
                            size = size.strip()
                            if sku == 'SKU :':
                                sku = None
                            if '(' in size:
                                index = size.index('(')
                                size = size[:index]
                                size = size.strip()
                            yield {
                                'product_link': product_link,
                                'product_name': product_name, 
                                'brand': brand, 
                                'category': category,
                                'regular_price': regular_price, 
                                'discounted_price': discounted_price,
                                'price_unit': None,
                                'size': size,
                                'color': None,
                                'flavor': None, 
                                'weight': weight, 
                                'average_rating': None, 
                                'num_reviews': None, 
                                'image_link': image_link,
                                'sku': sku, 
                                'upc': None,
                                'stock_level': stock_level,
                                'sold_by_3rd_party': 0,
                                'shipped_by': None,
                                'data_timestamp': self.time_now,
                                'data_year_month': self.data_year_month
                                }
                else:
                    if size:
                        size = size.replace('Sizes : ', '')
                        if '(' in size:
                            index = size.index('(')
                            size = size[:index]
                            size = size.strip()
                    if sku == 'SKU :':
                        sku = None
                    yield {
                        'product_link': product_link,
                        'product_name': product_name, 
                        'brand': brand, 
                        'category': category,
                        'regular_price': regular_price, 
                        'discounted_price': discounted_price,
                        'price_unit': None,
                        'size': size,
                        'color': None,
                        'flavor': None, 
                        'weight': weight, 
                        'average_rating': None, 
                        'num_reviews': None, 
                        'image_link': image_link,
                        'sku': sku, 
                        'upc': None,
                        'stock_level': stock_level,
                        'sold_by_3rd_party': 0,
                        'shipped_by': None,
                        'data_timestamp': self.time_now,
                        'data_year_month': self.data_year_month
                        }



