# -*- coding: utf-8 -*-
# no VPN needed
import scrapy
import time
from scrapy_splash import SplashRequest
import re
import json


class PetlandHtmlSpider(scrapy.Spider):
    name = 'petland_html'
    data_timestamp = int(time.time())
    data_year_month = time.strftime('%Y%m')
    requested_urls = []

    def start_requests(self):
        categories = {
            'https://www.petland.ca/pages/dog-products': 'Dog',
            'https://www.petland.ca/pages/cat-products': 'Cat',
            'https://www.petland.ca/pages/small-animal-products': 'Small Animal',
            'https://www.petland.ca/pages/reptile-products': 'Reptile',
            'https://www.petland.ca/pages/fish-products': 'Fish',
            'https://www.petland.ca/pages/bird-products': 'Bird'
        }
        for link, cat_name in categories.items():
            yield scrapy.Request(
                                url=link,
                                callback=self.parse_categories,
                                meta={
                                    'category': cat_name
                                }

            )

    def parse_categories(self, response):
        category = response.meta.get('category')
        base = 'https://www.petland.ca'
        links = response.xpath('//li[@class="columns large-4 small-6 landing-items"]/a/@href').getall()
        cat_names = response.xpath('//li[@class="columns large-4 small-6 landing-items"]/a/div/text()').getall()
        cat_info = dict(zip(links, cat_names))
        for link, cat_name in cat_info.items():
            yield scrapy.Request(
                                url=f'{base}{link}',
                                callback=self.parse_sub_categories,
                                meta={
                                    'category': f'Home|{category}|{cat_name}'
                                }
            )

    def parse_sub_categories(self, response):
        category = response.meta.get('category')
        base = 'https://www.petland.ca'
        product_links = response.xpath('//p[@class="title"]/a/@href').getall()
        for product in product_links:
            yield SplashRequest(
                                url=f'{base}{product}',
                                callback=self.parse_product,
                                meta={
                                    'category': category
                                },
                                    args={
                                        'wait': 3
                                    }
            )

        next_page = response.xpath('//li[@class="arrow right"]/a/@href').get()
        if next_page:
            yield scrapy.Request(
                                url=f'{base}{next_page}',
                                callback=self.parse_sub_categories,
                                meta={
                                    'category': category
                                }
            )


    def parse_product(self, response):
        bread_crumbs = response.xpath('//ul[@class="breadcrumbs colored-links"]/li/a/text()').getall()
        category = '|'.join(bread_crumbs)
        sku_element = response.xpath('//script[contains(text(), "universal_variable")]/text()').get()[:-2]
        sku_pattern = r'"sku":".+"'
        sku_result = re.search(sku_pattern, sku_element)
        sku_to_format = sku_result.group()
        sku = sku_to_format[7:-1]
        product_link = response.url
        variants = response.xpath('//select[@id="variant-listbox"]/option/@value').getall()
        if variants:
            for variant in variants:
                yield SplashRequest(
                                    url=f'{product_link}?variant={variant}',
                                    callback=self.parse_variant,
                                    meta={
                                        'sku': sku
                                    },
                                    args={
                                        'wait': 3
                                    }
                )

    def parse_variant(self, response):
        cm_size = None
        size = None
        flavor = None
        style = None
        the_type = None
        dimension = None
        formula = None
        size_with_unit = None
        size_without_unit = None
        dimension = None
        description = None
        regular_qty = None
        discounted_qty = None
        bread_crumbs = response.xpath('//ul[@class="breadcrumbs colored-links"]/li/a/text()').getall()
        breadcrumb = '|'.join(bread_crumbs)
        description = response.xpath('//div[@itemprop="description"]/p[1]/text()').get()
        product_link = response.url
        sku = response.meta.get('sku')
        product_name = response.xpath('//h1/text()').get()
        if ';' in product_name:
            end = product_name.index(';')
            product_name = product_name[:end]
        brand = response.xpath('//h2/a/text()').get()
        sale_price = response.xpath('//span[@class="actual-price"]/text()').get()
        sale_price = sale_price.strip('$')
        original_price = response.xpath('//span[@class="compare-price"]/text()').get()
        stock_level = 'In_Stock'
        out_of_stock = response.xpath('//div[@class="product-unavailable" and @style="display: block;"]').get()
        if out_of_stock:
            stock_level = 'Out_Of_Stock'
        if original_price:
            discounted_price = sale_price
            regular_price = original_price.replace('Regular Price $', '')
        else:
            regular_price = sale_price
            discounted_price = None
        color = response.xpath('//label[contains(text(), "Colour")]/following-sibling::div/*[@class="current"]/text()').get()
        if not color:
            color = response.xpath('//label[contains(text(), "Colour")]/following-sibling::div/ul/li[@class="selected"]/text()').get()
            if not color:
                color = response.xpath('//label[contains(text(), "Color")]/following-sibling::div/ul/li[@class="selected"]/text()').get()
        size = response.xpath('//label[contains(text(), "Size")]/following-sibling::div/a/text()').get()
        formula = response.xpath('//label[contains(text(), "Formula")]/following-sibling::div/a[@class="current"]/text()').get()
        if not size:
            size = response.xpath('//strong[contains(text(), "Size")]/parent::*/text()').getall()
            if not size:
                cm_size = response.xpath('//span[contains(text(), "Size (Cm) ")]/text()').get()
            if size:
                if size[0] == ':\xa0' or size[0] == '\xa0':
                    size = response.xpath('//strong[contains(text(), "Size")]/following-sibling::*/text()').getall()
            if size:
                if isinstance(size, list):
                    size = ''.join(size)
                size = size.replace('"', '')
                size_unit_pattern = r'[0-9]+ ?\.?x? ?[0-9]?.?(g|G|kg|KG|oz|lb|LB|mg|MG|oz|OZ|l|L|ml|ML|mL|cm|CM|gal)'
                size_unit_result = re.search(size_unit_pattern, size, flags=re.IGNORECASE)
                if size_unit_result:
                    size_with_unit = size_unit_result.group()
                else:
                    size_without_unit = size
        elif size:
            size_unit_pattern = r'[0-9]+ ?\.?x? ?[0-9]?.?(g|G|kg|KG|oz|lb|LB|mg|MG|oz|OZ|l|L|ml|ML|mL|cm|CM|gal)'
            size_unit_result = re.search(size_unit_pattern, size, flags=re.IGNORECASE)
            if size_unit_result:
                size_with_unit = size_unit_result.group()
            else:
                size_without_unit = size
        rating_reviews = response.xpath('//script[@type="application/ld+json"]/text()').get()
        if not rating_reviews:
            average_rating = None
            num_reviews = None
        else:
            rating_reviews_json = json.loads(rating_reviews)
            num_reviews = rating_reviews_json.get('reviewCount')
            average_rating = rating_reviews_json.get('ratingValue')
        confirm_reviews = response.xpath('//span[@class="spr-summary-caption"]/text()').get()
        if confirm_reviews == 'No reviews yet':
            average_rating = None
            num_reviews = None
        image_src = response.xpath('//a[@class="photo active"]/@href').get()
        if not image_src:
            image_src = response.xpath('//div[@class="container clearfix"]/a/@href').get()
            if not image_src:
                image_src = response.xpath('//div[@class="container clearfix"]/a/img/@src').get()
                if not image_src:
                    image_src = response.xpath('//meta[@itemprop="image"]/@content').get()
                    if not image_src:
                        image_src = response.xpath('//div[@class="container clearfix"]/img/@src').get()
        image_link = f'https:{image_src}'
        flavor = response.xpath('//label[contains(text(), "Flavour")]/following-sibling::div/a[@class="current"]/text()').get()
        style = response.xpath('//label[contains(text(), "Style")]/following-sibling::div/a/text()').get()
        the_type = response.xpath('//label[contains(text(), "Type")]/following-sibling::div/a/text()').get()
        if size_with_unit:
            if '(' in size_with_unit:
                index = size_with_unit.index('(')
                size_with_unit = size_with_unit[:index]
        regular_price = regular_price.replace(',', '')
        regular_price = float(regular_price)
        if discounted_price:
            discounted_price = discounted_price.replace(',', '')
        if cm_size:
            size_with_unit = cm_size.replace('Size (Cm) : ', '')
        if size_without_unit:
            if 'pack' in size_without_unit.lower():
                if not discounted_price:
                    regular_qty = size_without_unit.lower().replace('pack', '')
                    regular_qty = regular_qty.strip()
                else:
                    discounted_qty = size_without_unit.lower().replace('pack', '')
                    discounted_qty = discounted_qty.strip()
            if " x " in size_without_unit:
                dimension = size_without_unit
                size_without_unit = None
        yield {
            'product_link': product_link,
            'product_name': product_name,
            'brand': brand, 
            'breadcrumb': breadcrumb,
            'size_without_unit': size_without_unit,
            'size_with_unit': size_with_unit,
            'dimension': dimension,
            'flavor': flavor,
            'type': the_type,
            'style': style,
            'formula': formula,
            'sku': sku,
            'upc': None,
            'regular_price': regular_price,
            'regular_qty': regular_qty,
            'regular_unit': None,
            'discounted_price': discounted_price,
            'discounted_qty': discounted_qty,
            'discounted_unit': None,
            'currency': 'CAD',
            'average_rating': average_rating,
            'num_reviews': num_reviews,
            'shipped_by': None,
            'sold_by_third_party': 0, 
            'stock_level': stock_level,
            'online_only': True,
            'brief': None,
            'description': description,
            'image_link': image_link,
            'data_timestamp': self.data_timestamp,
            'data_year_month': self.data_year_month, 
            'retailer_code': None,
                    }