# -*- coding: utf-8 -*-
# needs CANADIAN VPN - otherwise prices are off.
# needs autothrottle - banned otherwise
# 0.5 concurrency = 500 items/min ballpark. Don't try higher, get banned.
import scrapy
import time
import json
import urllib
import math

class EddieApiSpider(scrapy.Spider):
    name = 'eddie_api'
    data_year_month = time.strftime('%Y%m')
    time_now = int(time.time())
    brand = 'Eddie Bauer'
    requested_urls = []
    requested_skus = []
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
        'x-access-token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiYW5vbnltb3VzIiwidXNlcklkIjoiY2tuaWQwdXpmMDFsZjA5anE4b2RnNTJpayIsImlhdCI6MTYxODQ1OTU0Mn0.M99FKvx_2NnWvvx85A9qZjthm1gSNGf2-5KFGPvtkAw',
        'x-site-context': '{"date":"2021-04-15T06:16:35.066Z","siteId":"eddiebauer","channel":"ca","isOutletSite":false,"isCallcenterSite":false,"siteName":"ca","hostname":"awsprod.eddiebauer.ca","searchProvider":"bloomreach","region":{"zipCode":"80206","city":"Denver","state":"CO","country":"USA"},"flags":{"enableAuth":true,"enableCart":true,"enableOrders":true}}'
    }
    

    def start_requests(self):
        categories = [
            '20001', '20094', '20083', '20088',
            '20070', '20061'
            ]
        for category in categories:
            category_body = json.dumps(
                {"operationName":"productSearch","variables":{"keyword":None,"category":category,"facets":[],"sortBy":None,"sortOrder":None,"isClearanceCategory":None,"channel":"ca","bruid":"uid=6653677618884:v=12.0:ts=1618459146285:hc=31","pathname":"/c/20015/mens-jackets-vests?cm_sp=topnav_m_jackets-vests","deviceType":"desktop","offset":0,"limit":200},"query":"query productSearch($keyword: String, $offset: Int, $limit: Int, $sortBy: String, $sortOrder: ProductSortOrder, $category: ID, $facets: [String], $isClearanceCategory: Boolean, $channel: String, $bruid: String, $pathname: String, $deviceType: String) {\n  productSearch(keyword: $keyword, offset: $offset, limit: $limit, sortBy: $sortBy, sortOrder: $sortOrder, category: $category, facets: $facets, isClearanceCategory: $isClearanceCategory, channel: $channel, bruid: $bruid, pathname: $pathname, deviceType: $deviceType) {\n    query {\n      total\n      limit\n      offset\n      sortBy\n      sortOrder\n      keyword\n      category\n      facets\n      categoryTitle\n      isClearanceCategory\n      channel\n      bruid\n      pathname\n      deviceType\n      __typename\n    }\n    filters {\n      id\n      label\n      facets {\n        id\n        label\n        count\n        slug\n        __typename\n      }\n      __typename\n    }\n    productGroups {\n      id\n      label\n      code\n      __typename\n    }\n    results {\n      ...SearchResultProductFragment\n      __typename\n    }\n    campaign {\n      bannerType\n      htmlText\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment SearchResultProductFragment on SearchResultProduct {\n  id\n  code\n  image\n  slug\n  name\n  rating\n  reviewsCount\n  isNewProduct\n  hasNewStyle\n  price {\n    listLow\n    listHigh\n    saleLow\n    saleHigh\n    clearanceLow\n    clearanceHigh\n    currentLow\n    currentHigh\n    __typename\n  }\n  variants {\n    image\n    isDefault\n    colorName\n    isNew\n    __typename\n  }\n  __typename\n}\n"})
            yield scrapy.Request(
                                url='https://www.eddiebauer.ca/graphql',
                                method='POST',
                                callback=self.parse_category,
                                headers=self.headers,
                                body=category_body,
                                meta={
                                    'category': category
                                },
                                dont_filter=True
            )

    def parse_category(self, response):
        category = response.meta.get('category')
        resp = json.loads(response.text)
        product_search = resp.get('data').get('productSearch')
        number_of_products = product_search.get('query').get('total')
        products_left = number_of_products - 200

        for product in product_search.get('results'):
            sku = product.get("id")
            if sku in self.requested_skus:
                continue
            average_rating = product.get('rating')
            num_reviews = product.get('reviewsCount')
            product_body = json.dumps({
                "operationName": "product",
                "variables": {
                    "code": sku,
                    "view": "regularOrSale"
                },
                "query": "query product($code: String, $view: ProductPriceView) {\n  product(code: $code, view: $view) {\n    ...ProductFragment\n    __typename\n  }\n}\n\nfragment ProductItemFragment on ProductItem {\n  code\n  isSkuIdentical\n  isDefaultSku\n  mainImage\n  quantity\n  poQuantity\n  fulfillDate\n  price {\n    list {\n      currency\n      amount\n      kind\n      __typename\n    }\n    current {\n      currency\n      amount\n      kind\n      __typename\n    }\n    __typename\n  }\n  variants {\n    label\n    name\n    value\n    __typename\n  }\n  hemming {\n    label\n    name\n    value\n    __typename\n  }\n  isNew\n  isSoldOut\n  __typename\n}\n\nfragment ProductFragment on Product {\n  code\n  name\n  slug\n  description\n  attributes\n  images\n  videos\n  isNewProduct\n  hasNewStyle\n  items {\n    ...ProductItemFragment\n    __typename\n  }\n  ratings {\n    value\n    count\n    __typename\n  }\n  productGroups {\n    id\n    label\n    code\n    __typename\n  }\n  promo {\n    pdp {\n      promoName\n      promoDisplayContent\n      __typename\n    }\n    __typename\n  }\n  isSoldOut\n  __typename\n}\n"
                })
            yield scrapy.Request(
                                url='https://www.eddiebauer.ca/graphql',
                                method='POST',
                                callback=self.parse_product,
                                body=product_body,
                                meta={
                                    'sku': sku,
                                    'average_rating': average_rating,
                                    'num_reviews': num_reviews
                                },
                                dont_filter=True,
                                headers=self.headers

            )
            self.requested_skus.append(sku)
        if products_left > 0:
            times_to_iterate = math.ceil(products_left / 200)
            for i in range(1, times_to_iterate + 1):
                category_body = json.dumps({"operationName":"productSearch","variables":{"keyword":None,"category":category,"facets":[],"sortBy":None,"sortOrder":None,"isClearanceCategory":None,"channel":"ca","bruid":"uid=6653677618884:v=12.0:ts=1618459146285:hc=31","pathname":"/c/20015/mens-jackets-vests?cm_sp=topnav_m_jackets-vests","deviceType":"desktop","offset":i,"limit":200},"query":"query productSearch($keyword: String, $offset: Int, $limit: Int, $sortBy: String, $sortOrder: ProductSortOrder, $category: ID, $facets: [String], $isClearanceCategory: Boolean, $channel: String, $bruid: String, $pathname: String, $deviceType: String) {\n  productSearch(keyword: $keyword, offset: $offset, limit: $limit, sortBy: $sortBy, sortOrder: $sortOrder, category: $category, facets: $facets, isClearanceCategory: $isClearanceCategory, channel: $channel, bruid: $bruid, pathname: $pathname, deviceType: $deviceType) {\n    query {\n      total\n      limit\n      offset\n      sortBy\n      sortOrder\n      keyword\n      category\n      facets\n      categoryTitle\n      isClearanceCategory\n      channel\n      bruid\n      pathname\n      deviceType\n      __typename\n    }\n    filters {\n      id\n      label\n      facets {\n        id\n        label\n        count\n        slug\n        __typename\n      }\n      __typename\n    }\n    productGroups {\n      id\n      label\n      code\n      __typename\n    }\n    results {\n      ...SearchResultProductFragment\n      __typename\n    }\n    campaign {\n      bannerType\n      htmlText\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment SearchResultProductFragment on SearchResultProduct {\n  id\n  code\n  image\n  slug\n  name\n  rating\n  reviewsCount\n  isNewProduct\n  hasNewStyle\n  price {\n    listLow\n    listHigh\n    saleLow\n    saleHigh\n    clearanceLow\n    clearanceHigh\n    currentLow\n    currentHigh\n    __typename\n  }\n  variants {\n    image\n    isDefault\n    colorName\n    isNew\n    __typename\n  }\n  __typename\n}\n"})
                yield scrapy.Request(
                                    url='https://www.eddiebauer.ca/graphql',
                                    method='POST',
                                    callback=self.parse_category_deeper,
                                    headers=self.headers,
                                    body=category_body,
                                    meta={
                                        'category': category
                                    },
                                    dont_filter=True
                )

    def parse_category_deeper(self, response):
        resp = json.loads(response.text)
        product_search = resp.get('data').get('productSearch')

        for product in product_search.get('results'):
            sku = product.get("id")
            if sku in self.requested_skus:
                continue
            average_rating = product.get('rating')
            num_reviews = product.get('reviewsCount')
            product_body = json.dumps({
                "operationName": "product",
                "variables": {
                    "code": sku,
                    "view": "regularOrSale"
                },
                "query": "query product($code: String, $view: ProductPriceView) {\n  product(code: $code, view: $view) {\n    ...ProductFragment\n    __typename\n  }\n}\n\nfragment ProductItemFragment on ProductItem {\n  code\n  isSkuIdentical\n  isDefaultSku\n  mainImage\n  quantity\n  poQuantity\n  fulfillDate\n  price {\n    list {\n      currency\n      amount\n      kind\n      __typename\n    }\n    current {\n      currency\n      amount\n      kind\n      __typename\n    }\n    __typename\n  }\n  variants {\n    label\n    name\n    value\n    __typename\n  }\n  hemming {\n    label\n    name\n    value\n    __typename\n  }\n  isNew\n  isSoldOut\n  __typename\n}\n\nfragment ProductFragment on Product {\n  code\n  name\n  slug\n  description\n  attributes\n  images\n  videos\n  isNewProduct\n  hasNewStyle\n  items {\n    ...ProductItemFragment\n    __typename\n  }\n  ratings {\n    value\n    count\n    __typename\n  }\n  productGroups {\n    id\n    label\n    code\n    __typename\n  }\n  promo {\n    pdp {\n      promoName\n      promoDisplayContent\n      __typename\n    }\n    __typename\n  }\n  isSoldOut\n  __typename\n}\n"
                })
            yield scrapy.Request(
                                url='https://www.eddiebauer.ca/graphql',
                                method='POST',
                                callback=self.parse_product,
                                body=product_body,
                                meta={
                                    'sku': sku,
                                    'average_rating': average_rating,
                                    'num_reviews': num_reviews
                                },
                                dont_filter=True,
                                headers=self.headers

            )
            self.requested_skus.append(sku)

    def parse_product(self, response):
        style = None
        sku = response.meta.get('sku')
        average_rating = response.meta.get('average_rating')
        num_reviews = response.meta.get('num_reviews')
        resp = json.loads(response.text)
        base_product = resp.get('data').get('product')
        product_name = base_product.get('name')
        crumbs_list = base_product.get("productGroups")
        if not average_rating or not num_reviews:
            average_rating = None
            num_reviews = None
        category = ''
        for crumb in crumbs_list:
            subcat_no_bar = crumb.get('label')
            subcat = subcat_no_bar + '|'
            category += subcat
        category = category.strip('|')
        items = base_product.get('items')
        for product in items:
            image = product.get('mainImage')
            image_link = f'https://eddiebauer.scene7.com/is/image/EddieBauer/{image}'
            sale_price = product.get('price').get('current').get('amount')
            try:
                original_price = product.get('price').get('list').get('amount')
                regular_price = original_price
                discounted_price = sale_price
            except:
                regular_price = sale_price
                discounted_price = None
            is_sold_out = product.get('isSoldOut')
            if is_sold_out:
                in_stock = 'Not_In_Stock'
            else:
                in_stock = 'In_Stock'
            for col_size_style in product.get('variants'):
                if col_size_style.get('name') == 'colorName':
                    color = col_size_style.get('value')
                if col_size_style.get('name') == 'sizeName':
                    size = col_size_style.get('value')
                if col_size_style.get('name') == 'styleName':
                    style = col_size_style.get('value')
            col_dict = {
                'color': color
            }
            size_dict = {
                'size': size
            }
            size_url = urllib.parse.urlencode(size_dict)
            color_url = urllib.parse.urlencode(col_dict)
            if style:
                product_link = f'https://www.eddiebauer.ca/p/{sku}?sp=1&{size_url}&{color_url}&sizeType={style}' 
            else:
                product_link = f'https://www.eddiebauer.ca/p/{sku}?sp=1&{size_url}&{color_url}'
            if product_link in self.requested_urls:
                continue
            self.requested_urls.append(product_link)
            if size == 'ONE SIZE' or size == 'ONESZE':
                size = None

            yield {
                    'product_link': product_link,
                    'product_name': product_name, 
                    'brand': self.brand, 
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
                    'stock_level': in_stock,
                    'sold_by_3rd_party': 0,
                    'shipped_by': None,
                    'data_timestamp': self.time_now,
                    'data_year_month': self.data_year_month
                }
