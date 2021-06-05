import scrapy
import json
import time
import re


class CallitApiSpider(scrapy.Spider):
    name = 'callit_api'
    data_timestamp = int(time.time())
    data_year_month = time.strftime('%Y%m')
    headers = {
            'accept': ' */*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'content-type': 'application/json',
            'referer': 'https://www.callitspring.com/',
            'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
            'x-aldo-api-version': '2',
            'x-aldo-brand': 'callitspring',
            'x-aldo-lang': 'en',
            'x-aldo-region': 'ca',
            'x-aldo-ssr-request-id': '',
            'x-forwarded-akamai-edgescape': 'undefined'
        }


    def start_requests(self):
        urls = [
            'https://www.callitspring.com/api/products/category/1000?currentPage=0&filters=&lang=en&maxFilters=6&pageSize=100&region=ca&showComingSoon=true&showScarce=false&sort=relevance',
            'https://www.callitspring.com/api/products/category/2000?currentPage=0&filters=&lang=en&maxFilters=6&pageSize=100&region=ca&showComingSoon=true&showScarce=false&sort=relevance',
            'https://www.callitspring.com/api/products/category/240?currentPage=0&filters=&lang=en&maxFilters=6&pageSize=100&region=ca&showComingSoon=true&showScarce=false&sort=relevance',
            'https://www.callitspring.com/api/products/category/300?currentPage=0&filters=&lang=en&maxFilters=6&pageSize=100&region=ca&showComingSoon=true&showScarce=false&sort=relevance',
            'https://www.callitspring.com/api/products/category/7176?currentPage=0&filters=&lang=en&maxFilters=6&pageSize=100&region=ca&showComingSoon=true&showScarce=false&sort=relevance',
            'https://www.callitspring.com/api/products/category/332?currentPage=0&filters=&lang=en&maxFilters=6&pageSize=100&region=ca&showComingSoon=true&showScarce=false&sort=relevance',
            'https://www.callitspring.com/api/products/category/331?currentPage=0&filters=&lang=en&maxFilters=6&pageSize=100&region=ca&showComingSoon=true&showScarce=false&sort=relevance'
        ]
        for cat_url in urls:
            yield scrapy.Request(
                                url=cat_url,
                                callback=self.parse_category_response,
                                meta={
                                    'cat_url': cat_url
                                },
                                headers=self.headers
            )
    
    def parse_category_response(self, response):
        category_endpoint = response.meta.get('cat_url')
        product_endpoint = 'https://www.callitspring.com/api/products/'
        base = 'https://www.callitspring.com/ca/en'
        resp = json.loads(response.text)
        products = resp.get("products")
        pages = resp.get('pagination').get('totalPages')
        for product in products:
            link = product.get('url')
            product_link = f'{base}{link}'
            if 'brandStyleName' in product:
                product_name = product.get('brandStyleName')
            else:
                product_name = product.get('name')
            product_code = product.get('code')
            brand = 'callitspring'
            image_src = product.get('image').get('srcTemplate')
            image = image_src.replace('[type]', 'main')
            image = image.replace('[proportion]', 'sq')
            image = image.replace('[background]', 'wt')
            image = image.replace('[dimension]', '800x800')
            image_link = 'https:' + image
            try:
                original_price = product.get("price").get("listPrice")
            except:
                original_price = None
            sale_price = product.get("price").get("value")
            if original_price:
                regular_price = original_price
                discounted_price = sale_price
            else:
                regular_price = sale_price
                discounted_price = None
            crumbs = link.replace('/CIS/', '')
            crumbs = crumbs.replace(f'/{product_name}', '')
            crumbs_pattern = r'/p/[0-9]+'
            crumbs_result = re.search(crumbs_pattern, crumbs)
            crumbs = crumbs.replace(crumbs_result.group(), '')
            category = crumbs.replace('/', '|')
            category = category.replace('Shoulder-Bags-%26-', '')
            category = category.replace('-', ' ')
            category = category.replace('Men|Bags and Accessories|Bags and Wallets', 'Men|Bags and Wallets')
            if category == '|c':
                category = 'Facemasks'
            if 'Men/Shoe-Care/' in link:
                category = 'Men|Footwear|Shoe Care'
            if 'Women/Shoe-Care' in link:
                category = 'Women|Footwear| Shoe Care'
            size_stock_dict = {}
            for size_variant in product.get("variantSizes"):
                size = size_variant.get('size')
                stock_status = size_variant.get("stockLevelStatus")
                if stock_status == "inStock":
                    in_stock = 'In_Stock'
                elif stock_status == 'lowStock':
                    in_stock = 'Low_Stock'
                else:
                    in_stock = 'Out_Of_Stock'
                sku = size_variant.get('code')
                size_stock_dict[size] = [in_stock, sku]
            yield scrapy.Request(
                                url=f'{product_endpoint}{product_code}',
                                callback=self.parse_colour,
                                meta={
                                    'product_link': product_link,
                                    'product_name': product_name,
                                    'brand': brand,
                                    'image_link': image_link,
                                    'regular_price': regular_price,
                                    'discounted_price': discounted_price,
                                    'category': category,
                                    'size_stock_dict': size_stock_dict,
                                    'product_code': product_code
                                },
                                headers=self.headers
            )

        if pages > 1:
            for i in range(1, pages):
                if '/category/1000' in category_endpoint:
                    endpoint = f'https://www.callitspring.com/api/products/category/1000?currentPage={str(i)}&filters=&lang=en&maxFilters=6&pageSize=100&region=ca&showComingSoon=true&showScarce=false&sort=relevance'
                elif '/category/300' in category_endpoint:
                    endpoint = f'https://www.callitspring.com/api/products/category/300?currentPage={str(i)}&filters=&lang=en&maxFilters=6&pageSize=100&region=ca&showComingSoon=true&showScarce=false&sort=relevance',
                elif '/category/2000' in category_endpoint:
                    endpoint = f'https://www.callitspring.com/api/products/category/2000?currentPage={str(i)}&filters=&lang=en&maxFilters=6&pageSize=100&region=ca&showComingSoon=true&showScarce=false&sort=relevance'
                if isinstance(endpoint, tuple):
                    endpoint = endpoint[0]
                yield scrapy.Request(
                                    url=endpoint,
                                    callback=self.parse_category_deeper,
                                    headers=self.headers
                )
    
    def parse_category_deeper(self, response):
        product_endpoint = 'https://www.callitspring.com/api/products/'
        base = 'https://www.callitspring.com/ca/en'
        resp = json.loads(response.text)
        products = resp.get("products")
        for product in products:
            link = product.get('url')
            product_link = f'{base}{link}'
            product_name = product.get('name')
            product_code = product.get('code')
            brand = 'callitspring'
            image_src = product.get('image').get('srcTemplate')
            image = image_src.replace('[type]', 'main')
            image = image.replace('[proportion]', 'sq')
            image = image.replace('[background]', 'wt')
            image = image.replace('[dimension]', '800x800')
            image_link = 'https:' + image
            try:
                original_price = product.get("price").get("listPrice")
            except:
                original_price = None
            sale_price = product.get("price").get("value")
            if original_price:
                regular_price = original_price
                discounted_price = sale_price
            else:
                regular_price = sale_price
                discounted_price = None
            crumbs = link.replace('/CIS/', '')
            crumbs = crumbs.replace(f'/{product_name}', '')
            crumbs_pattern = r'/p/[0-9]+'
            crumbs_result = re.search(crumbs_pattern, crumbs)
            crumbs = crumbs.replace(crumbs_result.group(), '')
            category = crumbs.replace('/', '|')
            category = category.replace('Shoulder-Bags-%26-', '')
            category = category.replace('-', ' ')
            category = category.replace('Men|Bags and Accessories|Bags and Wallets', 'Men|Bags and Wallets')
            if category == '|c':
                category = 'Facemasks'
            size_stock_dict = {}
            for size_variant in product.get("variantSizes"):
                size = size_variant.get('size')
                stock_status = size_variant.get("stockLevelStatus")
                if stock_status == "inStock":
                    in_stock = 'In_Stock'
                elif stock_status == 'lowStock':
                    in_stock = 'Low_Stock'
                else:
                    in_stock = 'Out_Of_Stock'
                sku = size_variant.get('code')
                size_stock_dict[size] = [in_stock, sku]
            
            yield scrapy.Request(
                                url=f'{product_endpoint}{product_code}',
                                callback=self.parse_colour,
                                meta={
                                    'product_link': product_link,
                                    'product_name': product_name,
                                    'brand': brand,
                                    'image_link': image_link,
                                    'regular_price': regular_price,
                                    'discounted_price': discounted_price,
                                    'category': category,
                                    'size_stock_dict': size_stock_dict
                                },
                                headers=self.headers
            )
    

    def parse_colour(self, response):
        dimension = None
        product_link = response.meta.get('product_link')
        product_name = response.meta.get('product_name')
        brand = response.meta.get('brand')
        image_link = response.meta.get('image_link')
        regular_price = response.meta.get('regular_price')
        discounted_price = response.meta.get('discounted_price')
        breadcrumb = response.meta.get('category')
        size_stock_dict = response.meta.get('size_stock_dict')
        product_resp = json.loads(response.text)
        features = product_resp.get('classifications').get('features')
        height = None
        width = None
        depth = None
        material = None
        for feature in features:
            if feature.get('name') == 'Height':
                height = feature.get('featureValues')[0].get('value')
            if feature.get('name') == 'Width':
                width = feature.get('featureValues')[0].get('value')
            if feature.get('name') == 'Depth':
                depth = feature.get('featureValues')[0].get('value')
            if feature.get('name') == 'Upper':
                material = feature.get('featureValues')[0].get('value')
        if height and width and depth:
            dimension = f'{height} x {width} x {depth}'
        description = product_resp.get('description')
        options = product_resp.get("baseOptions")[0]
        color = options.get('selected').get('variantOptionQualifiers')[0].get('value')
        if 'No Colour' in color:
            color = None
        for variant_size, stock_sku in size_stock_dict.items():
            size = variant_size
            if size == 'One Size':
                size = None
            stock_level = stock_sku[0]
            sku = stock_sku[1]
            yield {
                'product_link': product_link,
                'product_name': product_name,
                'brand': brand, 
                'breadcrumb': breadcrumb,
                'size_without_unit': size,
                'size_with_unit': None,
                'dimension': dimension,
                'material': material,
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
                'online_only': True,
                'brief': None,
                'description': description,
                'image_link': image_link,
                'data_timestamp': self.data_timestamp,
                'data_year_month': self.data_year_month, 
                'retailer_code': None
                }

                    
        
        

