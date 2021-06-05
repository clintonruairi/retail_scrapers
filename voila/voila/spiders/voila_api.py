# no VPN needed
import scrapy
import json
import time
from voila.items import MySQLItem

class VoilaApiSpider(scrapy.Spider):
    name = 'voila_api'
    allowed_domains = ['voila.ca']

    def start_requests(self):
        current_time = int(time.time())
        endpoint = 'https://voila.ca/api/v4/products/'
        yield scrapy.Request(
                            url=endpoint,
                            callback=self.parse_all,
                            meta={
                                'current_time': current_time
                            }
                        )
    
    def parse_all(self, response):
        current_time = response.meta.get('current_time')
        json_response = json.loads(response.body)
        categories = {}
        for category in json_response.get('result').get('categories'):
            categories[category.get('id')] = category.get('name')
        category_endpoint = 'https://voila.ca/api/v4/products?category='
        for category_id, name in categories.items():
            yield scrapy.Request(
                            url=f'{category_endpoint}{category_id}',
                            callback=self.parse_category,
                            meta={
                                'current_time': current_time,
                                'category_name': name
                            }

            )

    @staticmethod
    def divide_chunks(passed_list, list_length): 
        for i in range(0, len(passed_list), list_length):  
            yield passed_list[i:i + list_length]

    def parse_category(self, response):
        current_time = response.meta.get('current_time')
        crumbs = response.meta.get('category_name')
        json_response = json.loads(response.body)
        categories = {}
        for category in json_response.get('result').get('categories'):
            categories[category.get('id')] = category.get('name')
        category_endpoint = 'https://voila.ca/api/v4/products?category='
        for category_id, name in categories.items():
            yield scrapy.Request(
                            url=f'{category_endpoint}{category_id}',
                            callback=self.parse_sub_category,
                            meta={
                                'current_time': current_time,
                                'sub_category': name,
                                'crumbs': crumbs
                            }

            )

    def parse_sub_category(self, response):
        current_time = response.meta.get('current_time')
        category = response.meta.get('crumbs')
        sub_category = response.meta.get('sub_category')
        trail = f'{category}|{sub_category}'
        json_response = json.loads(response.body)
        product_ids = []
        for product_group in json_response.get('result').get('productGroups'):
            for product_id in product_group.get('products'):
                product_ids.append(product_id)
        list_chunks = list(self.divide_chunks(product_ids, 198))
        product_endpoint = 'https://voila.ca/api/v4/products/decorate?productIds='
        for chunk in list_chunks:
            formatted_ids = ','.join(chunk)
            yield scrapy.Request(
                                url=f'{product_endpoint}{formatted_ids}',
                                callback=self.parse_products,
                                meta={
                                    'current_time': current_time,
                                    'category': trail
                                }    
                            )

    def parse_products(self, response):
        current_time = response.meta.get('current_time')
        category = response.meta.get('category')
        json_response = json.loads(response.body)
        product_endpoint = 'https://voila.ca/api/v4/products/bop?retailerProductId='
        for product in json_response:
            retailer_product_id = product.get('retailerProductId')
            product_id = product.get('productId')
            yield scrapy.Request(
                                url=f'{product_endpoint}{retailer_product_id}',
                                callback=self.parse_individual,
                                meta={
                                    'current_time': current_time,
                                    'category': category,
                                    'retailer_id': retailer_product_id,
                                    'product_id': product_id
                                }
                    )

    def parse_individual(self, response):
        #items = MySQLItem()
        current_time = response.meta.get('current_time')
        category = response.meta.get('category')
        retailer_id = response.meta.get('retailer_id')
        product_id = response.meta.get('product_id')
        json_response = json.loads(response.body)
        product_link = f'https://voila.ca/products/{retailer_id}/details'
        product_name = json_response.get('entities').get('product').get(product_id).get('name')
        if 'brand' in json_response.get('entities').get('product').get(product_id):
            brand = json_response.get('entities').get('product').get(product_id).get('brand')
        else:
            brand = 'Voila'
        category = f'Home|{category}'
        current_price = json_response.get('entities').get('product').get(product_id).get('price').get('current').get('amount')
        if 'original' in json_response.get('entities').get('product').get(product_id).get('price'):
            regular_price = json_response.get('entities').get('product').get(product_id).get('price').get('original').get('amount')
            discounted_price = current_price
        else:
            regular_price = current_price
            discounted_price = None
        if 'size' in json_response.get('entities').get('product').get(product_id):
            size = json_response.get('entities').get('product').get(product_id).get('size').get('value')
            if size[-1].isnumeric():
                qualifier = json_response.get('entities').get('product').get(product_id).get('size').get('uom')
                size = f'{size} {qualifier}'
        else:
            size = None
        image_link = json_response.get('entities').get('product').get(product_id).get('images')[0].get('src')
        sku = retailer_id
        if json_response.get('entities').get('product').get(product_id).get('available'):
            in_stock = 'In_Stock'
        else:
            in_stock = 'Not_In_Stock'

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
                'weight': None,
                'average_rating': None,
                'num_reviews': None,
                'image_link': image_link,
                'sku': sku,
                'upc': None,
                'stock_level': in_stock,
                'sold_by_3rd_party': 0,
                'shipped_by': None,
                'data_timestamp': current_time,
                'data_year_month': time.strftime('%Y%m')
            }


        # items["product_link"] = product_link
        # items["product_name"] = product_name
        # items["brand"] = brand
        # items["category"] = category
        # items["regular_price"] = regular_price
        # items["discounted_price"] = discounted_price
        # items["price_unit"] = price_unit
        # items["size"] = size
        # items["color"] = None
        # items["flavor"] = None
        # items["weight"] = None
        # items["average_rating"] = None
        # items["num_reviews"] = None
        # items["image_link"] = image_link
        # items["sku"] = sku
        # items["upc"] = None
        # items["stock_level"] = in_stock
        # items["sold_by_3rd_party"] = 0
        # items["shipped_by"] = None
        # items["data_timestamp"] = current_time
        # items["data_year_month"] = time.strftime("%Y%m")

        # yield items






