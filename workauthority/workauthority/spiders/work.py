# -*- coding: utf-8 -*-
import scrapy
import time
import re
import json
from scrapy_splash import SplashRequest


class WorkSpider(scrapy.Spider):
    name = 'work'
    time_now = int(time.time())
    data_year_month = time.strftime('%Y%m')
    
    def start_requests(self):
        yield scrapy.Request(
                            url='http://workauthority.ca',
                            callback=self.parse_home
        )

    def parse_home(self, response):
        base = 'http://workauthority.ca'
        links = response.xpath('//div[@class="mobile-nav__has-sublist"]/following-sibling::ul/li/a/@href').getall()
        names = response.xpath('//div[@class="mobile-nav__has-sublist"]/following-sibling::ul/li/a/text()').getall()
        links = links[:33]
        names = names[:33]
        links_names = dict(zip(links, names))
        count = 1
        for link, name in links_names.items():
            if count < 14:
                parent = "Men's"
            elif 14 <= count < 22:
                parent = "Women's"
            else:
                parent = 'Accesories'
            yield scrapy.Request(
                                url=f'{base}{link}',
                                callback=self.parse_category,
                                meta={
                                    'category': f'Home|{parent}|{name.lower()}'
                                }
            )
            count += 1
    
    def parse_category(self, response):
        base = 'http://workauthority.ca'
        category = response.meta.get('category')
        product_links = response.xpath('//a[@class="product-card"]/@href').getall()
        for link in product_links:
            yield SplashRequest(
                                url=f'{base}{link}',
                                callback=self.parse_product,
                                meta={
                                    'category': category
                                },
                                args={
<<<<<<< HEAD
                                    'wait': 10
=======
                                    'wait': 15
>>>>>>> 08862872077d4553220534d9747e83a8fda3087d
                                        }
            )

        next_page = response.xpath('//span[@class="next"]/a/@href').get()
        if next_page:
            yield scrapy.Request(
                                url=f'{base}{next_page}',
                                callback=self.parse_category,
                                meta={
                                    'category': category
                                }
            )
   
    def parse_product(self, response):
<<<<<<< HEAD
        flavor = None
=======
>>>>>>> 08862872077d4553220534d9747e83a8fda3087d
        category = response.meta.get('category')
        product_link = response.url
        product_name = response.xpath('//h1/text()').get()
        brand_script = response.xpath('//script[contains(text(), "_learnq")]').get()
        brand_pattern = r'Brand: ".+"'
        brand_result = re.search(brand_pattern, brand_script)
        brand = brand_result.group()[8:-1]
<<<<<<< HEAD
        if '\u0026' in brand:
            brand = brand.replace('\u0026', '&')
=======
>>>>>>> 08862872077d4553220534d9747e83a8fda3087d
        sale_price = response.xpath('//span[@id="ProductPrice"]/text()').get()
        original_price = response.xpath('//p[@id="ComparePrice"]/text()').get()
        if original_price:
            regular_price = original_price.replace('Compare at $', '')
            regular_price = float(regular_price)
            discounted_price = sale_price.replace('$', '')
            discounted_price = float(discounted_price)
        else:
            regular_price = sale_price.replace('$', '')
            regular_price = float(regular_price)
            discounted_price = None
        num_reviews = response.xpath('//span[@class="stamped-badge-caption"]/@data-reviews').get()
        if num_reviews:
            num_reviews = int(num_reviews)
        average_rating = response.xpath('//span[@class="stamped-badge-caption"]/@data-rating').get()
        if average_rating:
            average_rating = float(average_rating)
        color_size_resp = response.xpath('//script[contains(text(), "var meta = ")]/text()').get()
        pattern = r'meta = {.+"}'
        result = re.search(pattern, color_size_resp)
        color_size_dict = json.loads(result.group()[7:])
        all_colors = response.xpath('//label[contains(text(), "Color")]/following-sibling::select/option/text()').getall()
        if not all_colors:
            all_colors = response.xpath('//label[contains(text(), "Colour")]/following-sibling::select/option/text()').getall()
            if not all_colors:
                all_colors = response.xpath('//label[contains(text(), "COLOUR")]/following-sibling::select/option/text()').getall()
        all_sizes = response.xpath('//label[contains(text(), "Size")]/following-sibling::select/option/text()').getall()
        if not all_sizes:
            all_sizes = response.xpath('//label[contains(text(), "SIZE")]/following-sibling::select/option/text()').getall()
<<<<<<< HEAD
        all_inseams = response.xpath('//label[contains(text(), "Inseam")]/following-sibling::select/option/text()').getall()
        if not all_inseams:
            all_inseams = response.xpath('//label[contains(text(), "INSEAM")]/following-sibling::select/option/text()').getall()
        all_widths = response.xpath('//label[contains(text(), "WIDTH")]/following-sibling::select/option/text()').getall()
        if not all_widths:
            all_widths = response.xpath('//label[contains(text(), "WIDTH")]/following-sibling::select/option/text()').getall()
=======
>>>>>>> 08862872077d4553220534d9747e83a8fda3087d
        sku_color_size = {}
        if all_sizes:
            all_sizes.sort(key=len)
            all_sizes.reverse()
<<<<<<< HEAD
        if all_inseams:
            all_inseams.sort(key=len)
            all_sizes.reverse()
        for variant in color_size_dict.get('product').get('variants'):
            color = None
            size = None
            flavor = None
=======
        for variant in color_size_dict.get('product').get('variants'):
            color = None
            size = None
>>>>>>> 08862872077d4553220534d9747e83a8fda3087d
            sku = variant.get('id')
            color_size_string = variant.get('public_title')
            if all_colors:
                for var_color in all_colors:
                    if var_color in color_size_string:
                        color = var_color
                        break
            if all_sizes:
                for var_size in all_sizes:
                    if var_size in color_size_string:
                        size = var_size
                        break
<<<<<<< HEAD
            if all_inseams:
                for var_inseam in all_inseams:
                    if var_inseam in color_size_string:
                        flavor = var_inseam
                        break
            if all_widths:
                for var_width in all_widths:
                    if var_width in color_size_string:
                        if flavor:
                            flavor = f'{flavor} | {var_width}'
                        else:
                            flavor = var_width
                            break
=======
>>>>>>> 08862872077d4553220534d9747e83a8fda3087d
            sku_color_size[sku] = [color, size]
        color_image_raw = response.xpath('//script[contains(text(), "new Shopify.OptionSelectors")]/text()').get()
        pattern = r"'productSelect\', {\n.+},"
        result = re.search(pattern, color_image_raw)
        image_json_to_be = result.group()
        image_json_to_be = image_json_to_be.replace('\'productSelect\', ', '')
        image_json_to_be = image_json_to_be[:-1]
        image_json_to_be = image_json_to_be.replace('{\n      product: ', '')
        image_json = json.loads(image_json_to_be)
<<<<<<< HEAD
        sku_color_size_image_stock_flavor = {}
=======
        sku_color_size_image_stock = {}
>>>>>>> 08862872077d4553220534d9747e83a8fda3087d
        for variant in image_json.get('variants'):
            for sku, color_size in sku_color_size.items():
                if variant.get('id') == sku:
                    image_link = variant.get('featured_image').get('src')
                    in_stock = variant.get('available')
                    if in_stock:
                        stock_level = 'In_Stock'
                    else:
                        stock_level = 'Out_Of_Stock'
<<<<<<< HEAD
                    sku_color_size_image_stock_flavor[sku] = [color_size[0], color_size[1], image_link, stock_level, flavor]
                    break
        for sku, color_size_image_stock in sku_color_size_image_stock_flavor.items():
=======
                    sku_color_size_image_stock[sku] = [color_size[0], color_size[1], image_link, stock_level]
                    break
        for sku, color_size_image_stock in sku_color_size_image_stock.items():
>>>>>>> 08862872077d4553220534d9747e83a8fda3087d
            color = color_size_image_stock[0]
            size = color_size_image_stock[1]
            image_link = color_size_image_stock[2]
            stock_level = color_size_image_stock[3]
<<<<<<< HEAD
            flavor  = color_size_image_stock[4]
            variant_link = f'{product_link}?variant={sku}'
            yield {
                'product_link': variant_link,
=======
            product_link = f'{product_link}?variant={sku}'
            yield {
                'product_link': product_link,
>>>>>>> 08862872077d4553220534d9747e83a8fda3087d
                'product_name': product_name, 
                'brand': brand, 
                'category': category,
                'regular_price': regular_price, 
                'discounted_price': discounted_price,
                'price_unit': None,
                'size': size,
                'color': color,
<<<<<<< HEAD
                'flavor': flavor, 
=======
                'flavor': None, 
>>>>>>> 08862872077d4553220534d9747e83a8fda3087d
                'weight': None,
                'average_rating': average_rating, 
                'num_reviews': num_reviews, 
                'image_link': image_link,
                'sku': sku, 
                'upc': None,
                'stock_level': stock_level,
                'sold_by_3rd_party': 0,
                'shipped_by': None,
                'data_timestamp': self.time_now,
                'data_year_month': self.data_year_month
                }

