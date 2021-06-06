# -*- coding: utf-8 -*-
# no VPN needed.
import scrapy
import json
import math
import time

class RosenApiSpider(scrapy.Spider):
    name = 'rosen_api'
    data_timestamp = int(time.time())
    data_year_month = time.strftime('%Y%m')
    
    def start_requests(self):
        categories = [
            '_en_shop_casual-wear', '_en_shop_outerwear',
            '_en_shop_intimate-apparel', '_en_shop_dress-shirts',
            '_en_shop_tailored-clothing', '_en_shop_footwear',
            '_en_shop_accessories', '_en_shop_grooming-fragrance',
            '_en_shop_feature-gifts-for-him', '_en_shop_feature-gifts-for-dad',

            ]
        for category in categories:
            endpoint = 'https://cdrobe4gid-1.algolianet.com/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.3.0)%3B%20Browser%20(lite)%3B%20react%20(16.13.0)%3B%20react-instantsearch%20(6.6.0)%3B%20JS%20Helper%20(3.1.2)&x-algolia-api-key=df9894c1db0df79472efc5cf787c50f9&x-algolia-application-id=CDROBE4GID'
            body = {
                "requests":
                    [
                        {
                            "indexName":"styles_production_consumer",
                            "params":f"ruleContexts={category}&page=0&hitsPerPage=1000"
                        }
                    ]
                }
            yield scrapy.Request(
                                url=endpoint,
                                callback=self.parse_category,
                                method='POST',
                                body=json.dumps(body),
                                meta={
                                    'category': category
                                }
            )

    def parse_category(self, response):
        category = response.meta.get('category')
        api_base = 'https://www.harryrosen.com/api/product/'
        data = json.loads(response.text)
        results = data.get('results')[0].get('hits')
        for product in results:
            prod_id = product.get('_id')
            available_online = product.get('webStatus')
            if not available_online:
                continue
            description = product.get('marketingDescription')
            yield scrapy.Request(
                                url=f'{api_base}{prod_id}',
                                callback=self.parse_product,
                                meta={
                                    'description': description
                                }
            )
        products_left = data.get('results')[0].get('nbHits') - 1000
        if products_left > 0:
            iterate = products_left / 1000
            times_to_iterate = math.ceil(iterate)
            for i in range(1, times_to_iterate + 1):
                endpoint = 'https://cdrobe4gid-1.algolianet.com/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.3.0)%3B%20Browser%20(lite)%3B%20react%20(16.13.0)%3B%20react-instantsearch%20(6.6.0)%3B%20JS%20Helper%20(3.1.2)&x-algolia-api-key=df9894c1db0df79472efc5cf787c50f9&x-algolia-application-id=CDROBE4GID'
                body = {
                    "requests":
                        [
                            {
                                "indexName":"styles_production_consumer",
                                "params":f"ruleContexts={category}&page={i}&hitsPerPage=1000"
                            }
                        ]
                    }
                yield scrapy.Request(
                                url=endpoint,
                                callback=self.parse_category_deeper,
                                method='POST',
                                body=json.dumps(body)
                )
    
    def parse_category_deeper(self, response):
        api_base = 'https://www.harryrosen.com/api/product/'
        data = json.loads(response.text)
        results = data.get('results')[0].get('hits')
        for product in results:
            prod_id = product.get('_id')
            available_online = product.get('webStatus')
            if not available_online:
                continue
            description = product.get('marketingDescription')
            yield scrapy.Request(
                                url=f'{api_base}{prod_id}',
                                callback=self.parse_product,
                                meta={
                                    'description': description
                                }
            )

    def parse_product(self, response):
        base_prod_url = 'https://www.harryrosen.com/en/product/'
        data = json.loads(response.text)
        product_key = data.get('key')
        product_link = base_prod_url + product_key
        product_name = data.get('name').get('en-CA')
        if not product_name:
            pass
        else:
            brand = data.get('brandName').get('en-CA')
            cat_1 = data.get('level1Category').get('en-CA')
            cat_2 = data.get('level2Category').get('en-CA')
            cat_3 = data.get('level3Category').get('en-CA')
            category = 'Home' + '|' + cat_1 + '|' + cat_2 + '|' + cat_3
            category = category.replace('||', '|')
            color = data.get('colour').get('en-CA')
            variants = data.get('variants')
            original_price = None
            try:
                original_price = data.get('originalPrice').get('centAmount')
            except:
                original_price = None
            for variant in variants:
                if not original_price:
                    continue
                available_online = variant.get('attributes').get('hasOnlineAts')
                if not available_online:
                    continue
                sale_price = variant.get('prices')[-1].get('value').get('centAmount')
                if sale_price == original_price:
                    regular_price = sale_price
                    discounted_price = None
                else:
                    regular_price = original_price
                    discounted_price = sale_price
                regular_price = str(regular_price)
                regular_price = regular_price[:-2] + '.' + regular_price[-2:]
                if discounted_price:
                    discounted_price = str(discounted_price)
                    discounted_price = discounted_price[:-2] + '.' + discounted_price[-2:]
                size = variant.get('attributes').get('size').get('en-CA')
                image_link = variant.get('images')[0].get('url')
                sku = variant.get('sku')
                if 'One Size' in size:
                    size = None
                if 'NO COLOR' in color:
                    color = None
                dimension = variant.get('attributes').get('dimensionId')
                if size and dimension:
                    size = f'{size} {dimension}'
                yield scrapy.Request(
                                    url=f'https://www.harryrosen.com/api/product/20050467/{sku}/inventory',
                                    callback=self.parse_inventory,
                                    meta={
                                        'product_link': product_link,
                                        'product_name': product_name,
                                        'brand': brand,
                                        'category': category,
                                        'regular_price': regular_price,
                                        'discounted_price': discounted_price,
                                        'size': size,
                                        'color': color,
                                        'image_link': image_link,
                                        'sku': sku       
                                    }
                )

    def parse_inventory(self, response):
        product_link = response.meta.get('product_link')
        product_name = response.meta.get('product_name')
        brand = response.meta.get('brand')
        breadcrumb = response.meta.get('category')
        regular_price = response.meta.get('regular_price')
        discounted_price = response.meta.get('discounted_price')
        size_without_unit = response.meta.get('size')
        color = response.meta.get('color')
        image_link = response.meta.get('image_link')
        sku = response.meta.get('sku')
        resp = json.loads(response.text)
        stock_no = resp.get('online')
        if stock_no == 1:
            stock_level = 'Low_Stock'
        elif stock_no == 0:
            stock_level = 'Out_Of_Stock'
        elif stock_no > 1:
            stock_level = 'In_Stock'
        description = response.meta.get('description')

        yield {
            'product_link': product_link,
            'product_name': product_name,
            'brand': brand, 
            'breadcrumb': breadcrumb,
            'size_without_unit': size_without_unit,
            'size_with_unit': None,
            'dimension': None,
            'color': color,
            'sku': sku,
            'upc': None,
            'regular_price': regular_price,
            'regular_qty': None,
            'regular_unit': None,
            'discounted_price': discounted_price,
            'discounted_qty': None,
            'discounted_unit': None,
            'currency': 'CAD',
            'average_rating': None,
            'num_reviews': None,
            'shipped_by': None,
            'sold_by_third_party': 0, 
            'stock_level': stock_level,
            'online_only': False,
            'brief': None,
            'description': description,
            'image_link': image_link,
            'data_timestamp': self.data_timestamp,
            'data_year_month': self.data_year_month, 
            'retailer_code': None
        }
