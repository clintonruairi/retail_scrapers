# requires non-vn vpn
import scrapy
import json
import time
import math
from pprint import pprint

class ApiSpider(scrapy.Spider):
    name = 'api'
    time_now = int(time.time())
    data_year_month = time.strftime('%Y%m%d')
    headers = {
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json;charset=utf-8',
        'Host': 'api.pcexpress.ca',
        'Origin': 'https://www.fortinos.ca',
        'Referer': 'https://www.fortinos.ca/',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
        'sec-ch-ua-mobile': '?0',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'Site-Banner': 'fortinos',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
        'x-apikey': '1im1hL52q9xvta16GlSdYDsTsG0dmyhF'
        }
    date = time.strftime('%d%m%Y')
    category_endpoint = 'https://api.pcexpress.ca/product-facade/v3/products/category/listing'
    count = 0
    
    def start_requests(self):
        # store set to North York Lawrence Toronto
        categories = ['27985', '27987', '27986', '27995',
                    '27994', '27988', '27990', '27992']
        for category_code in categories:
            category_code = f'{category_code}'
            body = f"""{{\"pagination\":{{\"from\":0,\"size\":48}},\"banner\":\"fortinos\",
                    \"cartId\":\"ce5bc1d7-b888-46cc-9db9-1dc4c7c1c324\",\"lang\":\"en\",
                    \"date\":\"26052021\",\"storeId\":\"1436\",\"pcId\":null,\"pickupType\":\"STORE\",
                    \"enableSeldonIntegration\":true,\"features\":[\"loyaltyServiceIntegration\",
                    \"sunnyValeServiceIntegration\"],\"inventoryInfoRequired\":true,\"sort\":{{\"topSeller\":\"desc\"}},
                    \"categoryId\":\"{category_code}"}}"""
            yield scrapy.Request(
                                url=self.category_endpoint,
                                method='POST',
                                body=body,
                                callback=self.parse_category,
                                meta={
                                    'category_code': category_code
                                },
                                headers=self.headers
            )
    
    def parse_category(self, response):
        resp = json.loads(response.text)
        products = resp.get('results')
        for product in products:
            code = product.get('code')
            product_endpoint = f'https://api.pcexpress.ca/product-facade/v3/products/{code}?lang=en&date={self.date}&pickupType=STORE&storeId=1436&banner=fortinos&features=loyaltyServiceIntegration,inventoryServiceIntegration'
            yield scrapy.Request(
                                url=product_endpoint,
                                callback=self.parse_product,
                                headers=self.headers
            )

        category_code = response.meta.get('category_code')
        total_results = resp.get('pagination').get('totalResults')
        if total_results > 48:
            total_results = total_results - 48
            times_to_iterate = math.ceil(total_results / 48)
            for i in range(1, times_to_iterate + 1):
                body = f"""{{\"pagination\":{{\"from\":{str(i)},\"size\":48}},\"banner\":\"fortinos\",
                    \"cartId\":\"ce5bc1d7-b888-46cc-9db9-1dc4c7c1c324\",\"lang\":\"en\",
                    \"date\":\"26052021\",\"storeId\":\"1436\",\"pcId\":null,\"pickupType\":\"STORE\",
                    \"enableSeldonIntegration\":true,\"features\":[\"loyaltyServiceIntegration\",
                    \"sunnyValeServiceIntegration\"],\"inventoryInfoRequired\":true,\"sort\":{{\"topSeller\":\"desc\"}},
                    \"categoryId\":\"{category_code}"}}"""
                yield scrapy.Request(
                                url=self.category_endpoint,
                                method='POST',
                                body=body,
                                callback=self.parse_category_deeper,
                                meta={
                                    'category_code': category_code
                                },
                                headers=self.headers
            )
    
    def parse_category_deeper(self, response):
        resp = json.loads(response.text)
        products = resp.get('results')
        for product in products:
            code = product.get('code')
            product_endpoint = f'https://api.pcexpress.ca/product-facade/v3/products/{code}?lang=en&date={self.date}&pickupType=STORE&storeId=1436&banner=fortinos&features=loyaltyServiceIntegration,inventoryServiceIntegration'
            yield scrapy.Request(
                                url=product_endpoint,
                                callback=self.parse_product,
                                headers=self.headers
            )

    def parse_product(self, response):
        weight = None
        size = None
        price_unit = None
        resp = json.loads(response.text)
        base_url = 'https://www.fortinos.ca'
        link = resp.get('link')
        product_link = f'{base_url}{link}'
        product_name = resp.get('name')
        product_name = product_name.strip()
        brand = resp.get('brand')
        if not brand:
            brand = 'Fortinos'
        if f'{brand},' in product_name:
            product_name = product_name.replace(f'{brand},', '')
        if ';' in product_name:
            product_name = product_name.replace(';', '')
        bread_crumbs = resp.get('breadcrumbs')
        category = '|'.join([crumb.get('name') for crumb in bread_crumbs])
        stock_level = 'In_Stock'
        sku = resp.get('code')
        if sku == '20652836002_EA':
            return
        image_link = None
        if resp.get('imageAssets'):
            image_link = resp.get('imageAssets')[0].get('mediumUrl')
        price_size_info = resp.get('prices').get('comparisonPrices')[0]
        numeric_value = price_size_info.get('value')
        unit_of_measurement = price_size_info.get('unit')
        quantity = price_size_info.get('quantity')
        if unit_of_measurement.endswith('l') or unit_of_measurement.endswith('g'):
            regular_price = numeric_value
            discounted_price = None
            price_unit = f'{quantity} {unit_of_measurement}'
        else:
            sale_price = resp.get('prices').get('price').get('value')
            if resp.get('prices').get('wasPrice'):
                regular_price = resp.get('prices').get('wasPrice').get('value')
                discounted_price = sale_price
            else:
                regular_price = sale_price
                discounted_price = None
        package_size = resp.get('packageSize')
        if package_size.endswith('l'):
            size = package_size
        elif package_size.endswith('g'):
            weight = package_size
        elif package_size.endswith('a'):
            price_unit = package_size
            
        yield {
            'product_link': product_link,
            'product_name': product_name, 
            'brand': brand, 
            'category': category,
            'regular_price': regular_price, 
            'discounted_price': discounted_price,
            'price_unit': price_unit,
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

        

        

        
