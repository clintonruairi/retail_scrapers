# -*- coding: utf-8 -*-
import scrapy
import json
import re
import time


class PharmHtmlSpider(scrapy.Spider):
    name = 'pharm_html'
    headers = {
            'language': 'en',
            'site': 'pharmaprix',
            'x-lcl-apikey': '3Yc7hl0uhqqXj4pGE8Wq7Wm3ionNVynM',
            'Content-Type': 'application/json'
            }
    time_now = int(time.time())
    data_year_month = time.strftime('%Y%m')
    
    def start_requests(self):
        home = 'https://www1.pharmaprix.ca/en/home'
        yield scrapy.Request(
                            url=home,
                            callback=self.start_calls
        )
    
    def start_calls(self, response):
        endpoint = 'https://api.shoppersdrugmart.ca/ecommerce'
        payload = json.dumps({
            "operationName": "GetNavigationMobile",
            "variables": {},
            "query": "query GetNavigationMobile {\n  navigationMobile {\n    ...CmsNode\n    child {\n      ...CmsNode\n      child {\n        ...CmsNode\n        child {\n          ...CmsNode\n          child {\n            navPromo {\n              name\n              imageUrl\n              imageLink\n              __typename\n            }\n            ...CmsNode\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment CmsNode on CmsNode {\n  name\n  uid\n  link\n  hasChildren\n  __typename\n}\n"
            })
        yield scrapy.Request(
                            url=endpoint,
                            method='POST',
                            body=payload,
                            headers=self.headers,
                            callback=self.parse_categories_list
        )

        weed_endpoint = 'https://cannabis.pharmaprix.ca/plpJson'
        yield scrapy.Request(
                            url=weed_endpoint,
                            callback=self.parse_weed_category
        )

    def parse_weed_category(self, response):
        resp = json.loads(response.text)
        category = 'Home|Health & Pharmacy|Medical Cannabis'
        base = 'https://cannabis.pharmaprix.ca/en_CA/products/'
        for product in resp:
            product_name = product.get('name')
            brand = product.get('brand_name')
            product_id = product.get('id')
            link = f'{brand} {product_name}/{product_id}'
            link = link.replace(' ', '-')
            product_link = f'{base}{link}'
            product_type = product.get('product_type_name')
            image_link = product.get('product_image')
            skus = product.get('skus')
            for variant in skus:
                original_price = str(variant.get('unit_price'))
                original_price = original_price[:-2] + '.' + original_price[-2:]
                sale_price = variant.get('sale_price')
                if sale_price:
                    sale_price = str(sale_price)
                    sale_price = sale_price[:-2] + '.' + sale_price[-2:]
                    regular_price = original_price
                    discounted_price = sale_price
                else:
                    regular_price = original_price
                    discounted_price = None
                sku = variant.get('id')
                size = variant.get('name')
                in_stock = variant.get('in_stock')
                if in_stock:
                    stock_level = 'In_Stock'
                else:
                    stock_level = 'Out_Of_Stock'
                if product_link == 'https://cannabis.pharmaprix.ca/en_CA/products/Atlas-Growers-Atlas-Growers-AC-DC-CKS-Terp-Sauce-Vape-Pen-Cartridge-/402':
                    product_name = 'Atlas Growers AC DC Cookies Vape Pen Cartridge'
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
                'stock_level': stock_level,
                'sold_by_3rd_party': 0,
                'shipped_by': None,
                'data_timestamp': self.time_now,
                'data_year_month': self.data_year_month
                }

    def parse_categories_list(self, response):
        resp = json.loads(response.text)
        category_codes = []
        category_list = resp.get('data').get('navigationMobile')
        pattern = r'/c/FS.+\?'
        for category in category_list:
            if category.get('name') == 'Shop':
                shop_children = category.get('child')
                for sub_cat in shop_children:
                    sub_children = sub_cat.get('child')
                    for code_cat in sub_children:
                        link = code_cat.get('link')
                        result = re.search(pattern, link)
                        if result:
                            code_to_format = result.group()[3:-1]
                            category_codes.append(code_to_format)
        endpoint = 'https://api.shoppersdrugmart.ca/ecommerce'
        for categoryId in category_codes:
            payload = json.dumps({
                "operationName": "GetProductListData",
                "variables": {
                    "categoryId": categoryId,
                    "queryParam": "",
                    "page": 0,
                    "pageSize": 100,
                    "sort": "trending"
                },
                "query": "query GetProductListData($categoryId: String!, $queryParam: String, $page: Int, $pageSize: Int, $sort: String) {\n  categoryProductList(\n    categoryId: $categoryId\n    queryParam: $queryParam\n    page: $page\n    pageSize: $pageSize\n    sort: $sort\n  ) {\n    ...ProductList\n    sorts {\n      ...Sort\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment ProductList on ProductList {\n  categoryType\n  filterGroups {\n    ...FilterGroup\n    __typename\n  }\n  totalFiltersCount\n  products {\n    brandName\n    name\n    description\n    id\n    flavourAndScent\n    price {\n      numericalPrice\n      formattedPrice\n      __typename\n    }\n    salePrice {\n      numericalPrice\n      formattedPrice\n      __typename\n    }\n    smallThumbnail\n    largeThumbnail\n    rating\n    reviewCount\n    url\n    isOnSale\n    badges {\n      uid\n      name\n      type\n      __typename\n    }\n    isOutOfStock\n    isFavourite\n    variantCount\n    variantUnitDescription\n    priceRange {\n      maxPrice {\n        numericalPrice\n        formattedPrice\n        __typename\n      }\n      minPrice {\n        numericalPrice\n        formattedPrice\n        __typename\n      }\n      __typename\n    }\n    variantType\n    __typename\n  }\n  pagination {\n    currentPage\n    pageSize\n    totalPages\n    totalResults\n    pageSize\n    __typename\n  }\n  breadcrumbs {\n    name\n    url\n    __typename\n  }\n  categoryName\n  subcategories {\n    name\n    code\n    __typename\n  }\n  editorialBrandPageUrl\n  __typename\n}\n\nfragment FilterGroup on FilterGroup {\n  name\n  code\n  count\n  filters {\n    name\n    count\n    queryParam\n    code\n    isSelected\n    shadeIconUrl\n    __typename\n  }\n  __typename\n}\n\nfragment Sort on Sort {\n  value\n  name\n  selected\n  __typename\n}\n"
            })
            yield scrapy.Request(
                                url=endpoint,
                                method='POST',
                                body=payload,
                                headers=self.headers,
                                callback=self.parse_category,
                                meta={
                                    'categoryId': categoryId
                                }

            )
    
    def parse_category(self, response):
        categoryId = response.meta.get('categoryId')
        resp = json.loads(response.text)
        resp_list = resp.get('data').get('categoryProductList')
        products = resp_list.get('products')
        for product in products:
            product_code = product.get('id')
            product_endpoint = f'https://magasiner.pharmaprix.ca/p/variant?productCode={product_code}&lang=en'
            yield scrapy.Request(
                                url=product_endpoint,
                                callback=self.parse_product,
                                meta={
                                    'sku': product_code
                                }
            )
        category_endpoint = 'https://api.shoppersdrugmart.ca/ecommerce'
        total_pages = resp_list.get('pagination').get('totalPages')
        if total_pages > 1:
            for i in range(1, total_pages):
                payload = json.dumps({
                    "operationName": "GetProductListData",
                    "variables": {
                        "categoryId": categoryId,
                        "queryParam": "",
                        "page": i,
                        "pageSize": 100,
                        "sort": "trending"
                    },
                    "query": "query GetProductListData($categoryId: String!, $queryParam: String, $page: Int, $pageSize: Int, $sort: String) {\n  categoryProductList(\n    categoryId: $categoryId\n    queryParam: $queryParam\n    page: $page\n    pageSize: $pageSize\n    sort: $sort\n  ) {\n    ...ProductList\n    sorts {\n      ...Sort\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment ProductList on ProductList {\n  categoryType\n  filterGroups {\n    ...FilterGroup\n    __typename\n  }\n  totalFiltersCount\n  products {\n    brandName\n    name\n    description\n    id\n    flavourAndScent\n    price {\n      numericalPrice\n      formattedPrice\n      __typename\n    }\n    salePrice {\n      numericalPrice\n      formattedPrice\n      __typename\n    }\n    smallThumbnail\n    largeThumbnail\n    rating\n    reviewCount\n    url\n    isOnSale\n    badges {\n      uid\n      name\n      type\n      __typename\n    }\n    isOutOfStock\n    isFavourite\n    variantCount\n    variantUnitDescription\n    priceRange {\n      maxPrice {\n        numericalPrice\n        formattedPrice\n        __typename\n      }\n      minPrice {\n        numericalPrice\n        formattedPrice\n        __typename\n      }\n      __typename\n    }\n    variantType\n    __typename\n  }\n  pagination {\n    currentPage\n    pageSize\n    totalPages\n    totalResults\n    pageSize\n    __typename\n  }\n  breadcrumbs {\n    name\n    url\n    __typename\n  }\n  categoryName\n  subcategories {\n    name\n    code\n    __typename\n  }\n  editorialBrandPageUrl\n  __typename\n}\n\nfragment FilterGroup on FilterGroup {\n  name\n  code\n  count\n  filters {\n    name\n    count\n    queryParam\n    code\n    isSelected\n    shadeIconUrl\n    __typename\n  }\n  __typename\n}\n\nfragment Sort on Sort {\n  value\n  name\n  selected\n  __typename\n}\n"
                })
            yield scrapy.Request(
                                url=category_endpoint,
                                method='POST',
                                body=payload,
                                headers=self.headers,
                                callback=self.parse_category_deeper,
                                meta={
                                    'categoryId': categoryId
                                }

            )
        
    def parse_category_deeper(self, response):
        resp = json.loads(response.text)
        resp_list = resp.get('data').get('categoryProductList')
        products = resp_list.get('products')
        for product in products:
            product_code = product.get('id')
            product_endpoint = f'https://magasiner.pharmaprix.ca/p/variant?productCode={product_code}&lang=en'
            yield scrapy.Request(
                                url=product_endpoint,
                                callback=self.parse_product,
                                meta={
                                    'sku': product_code
                                }
            )
    
    def parse_product(self, response):
        color = None
        size = None
        price_unit = None
        average_rating = None
        resp = json.loads(response.text)
        product_link = resp.get('productUrl')
        product_name = resp.get('name')
        brand = resp.get('brandName')
        category_string = resp.get('url')
        category_pattern = r'(\/Categories\/|\/Collections/).+\/p'
        string_match = re.search(category_pattern, category_string)
        try:
            result = string_match.group()
            fwd_slash_indices = [i.start() for i in re.finditer('/', result)]
            category_string_no_product = result[:fwd_slash_indices[-2]]
            category_to_format = category_string_no_product.replace('/Categories/', '')
            category_to_format = category_to_format.replace('/', '|')
            category_to_format = category_to_format.replace('%2C', ',')
            category_to_format = category_to_format.replace('%26', '&')
            category_to_format = category_to_format.replace("%27", "'")
            category = category_to_format.replace('-', ' ')
            category = category.replace('%C3%A9', 'é')
            category = category.replace('%E2%80%99', "'")
        except Exception as e:
            if 'Daily-Moisturizers' in category_string:
                category = 'Beauty|Skin Care|Face Moisturizers|Moisturizers'
            elif 'Lip' in category_string:
                category = 'Beauty|Makeup|Lips|Lipstick'
            elif 'Primer' in category_string:
                category = 'Beauty|Makeup'
            elif 'Mascara' in category_string:
                category = 'Beauty|Makeup|Eyes|Mascara'
            elif 'Shampoo' in category_string:
                category = 'Beauty|Hair Care'
            elif 'SPF' in category_string:
                category = 'Beauty|Mens|Skin Care For Him|Sun Care'
            elif 'Anti-Spot-Lightening-Cream' in category_string:
                category = 'Beauty|Mens|Skin Care For Him|Sun Care'
            else:
                print(e)
                print(f'CATEGORY STRING: {category_string}')
        regular_price = resp.get('regularPriceValue')
        discounted_price = resp.get('specialPriceValue')
        if discounted_price:
            discounted_price = round(discounted_price, 2)
        num_reviews = resp.get('reviewCount')
        if num_reviews == 0:
            num_reviews = None
        image_link = resp.get('navImage')[-1].get('url')
        rating = resp.get('starRating')
        if rating:
            rating = str(rating / 2)
            average_rating = rating[0] + '.' + rating[1]
        sku = response.meta.get('sku')
        out_of_stock = resp.get('outOfStock')
        stock_level = 'In_Stock'
        if out_of_stock:
            stock_level = 'Out_Of_Stock'
        variants = resp.get('variantOptions')
        measurement_unit = resp.get('uom')
        for variant in variants:
            if 'isSelected' in variant:
                name = variant.get('name')
                if name:
                    if name.isnumeric():
                        size = name + ' ' + measurement_unit
                    else:
                        size = None
                if category[0] == '|':
                    category = category[1:]
                if not brand:
                    brand = 'Pharmaprix'
                if regular_price == discounted_price:
                    discounted_price = None
                if discounted_price:
                    if discounted_price > regular_price:
                        discounted_price = None
                if size:
                    if size[0] == '0':
                        size = None
                color_code = variant.get('colorCode')
                if color_code != '#null':
                    color = variant.get('name')
                    if color:
                        if color.isnumeric():
                            if len(color) == 3:
                                color = color
                            else:
                                color = None
                                size = color + ' ' + measurement_unit
                        if '.' in color:
                            test = color.replace('.', '')
                            if test.isnumeric():
                                color = None
                                size = color + ' ' + measurement_unit
                        if color == 'Cleanse':
                            color = None
                        if color == 'N/A':
                            color = None
                if size:
                    if 'ea' in size or 'EA' in size:
                        price_unit = size
                        size = None
                yield {
                    'product_link': product_link,
                    'product_name': product_name, 
                    'brand': brand, 
                    'category': category,
                    'regular_price': regular_price, 
                    'discounted_price': discounted_price,
                    'price_unit': price_unit,
                    'size': size,
                    'color': color,
                    'flavor': None, 
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
            else:
                product_code = variant.get('code')
                product_endpoint = f'https://magasiner.pharmaprix.ca/p/variant?productCode={product_code}'
                headers = {
                    'Cookie': 'JSESSIONID=419187F6FCE31968A2F06A07C913CA85.app1'
                }
                yield scrapy.Request(
                                    url=product_endpoint,
                                    headers=headers,
                                    callback=self.parse_product_variants,
                                    meta={
                                        'sku': product_code,
                                        'category': category
                                    }
                )
    
    def parse_product_variants(self, response):
        color = None
        size = None
        average_rating = None
        price_unit = None
        resp = json.loads(response.text)
        product_link = resp.get('productUrl')
        product_name = resp.get('name')
        brand = resp.get('brandName')
        category = response.meta.get('category')
        regular_price = resp.get('regularPriceValue')
        discounted_price = resp.get('specialPriceValue')
        if discounted_price:
            discounted_price = round(discounted_price, 2)
        num_reviews = resp.get('reviewCount')
        if num_reviews == 0:
            num_reviews = None
        image_link = resp.get('navImage')[-1].get('url')
        rating = resp.get('starRating')
        if rating:
            rating = str(rating / 2)
            average_rating = rating[0] + '.' + rating[1]
        sku = response.meta.get('sku')
        out_of_stock = resp.get('outOfStock')
        stock_level = 'In_Stock'
        if out_of_stock:
            stock_level = 'Out_Of_Stock'
        variants = resp.get('variantOptions')
        measurement_unit = resp.get('uom')
        for variant in variants:
            if 'isSelected' in variant:
                name = variant.get('name')
                if name:
                    if name.isnumeric():
                        size = name + ' ' + measurement_unit
                    else:
                        size = None
                if category[0] == '|':
                    category = category[1:]
                if not brand:
                    brand = 'Pharmaprix'
                if regular_price == discounted_price:
                    discounted_price = None
                if discounted_price:
                    if discounted_price > regular_price:
                        discounted_price = None
                if size:
                    if size[0] == '0':
                        size = None
                color_code = variant.get('colorCode')
                if color_code != '#null':
                    color = variant.get('name')
                    if color:
                        if color.isnumeric():
                            if len(color) == 3:
                                color = color
                            else:
                                color = None
                                size = color + ' ' + measurement_unit
                        if '.' in color:
                            test = color.replace('.', '')
                            if test.isnumeric():
                                color = None
                                size = color + ' ' + measurement_unit
                        if color == 'Cleanse':
                            color = None
                        if color == 'N/A':
                            color = None
                if size:
                    if 'ea' in size or 'EA' in size:
                        price_unit = size
                        size = None
                yield {
                    'product_link': product_link,
                    'product_name': product_name, 
                    'brand': brand, 
                    'category': category,
                    'regular_price': regular_price, 
                    'discounted_price': discounted_price,
                    'price_unit': None,
                    'size': size,
                    'color': color,
                    'flavor': None, 
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


