# -*- coding: utf-8 -*-
# needs canadian vpn
# set to output ; delimited csvs
import scrapy
import time
import json
import math
from pprint import pprint


class ApiSpider(scrapy.Spider):
    name = 'api'
    time_now = int(time.time())
    data_year_month = time.strftime('%Y%m%d')
    brand = "The Childrens Place"
    headers = {
        'Accept-Encoding': ' gzip, deflate, br',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Host': 'api.bazaarvoice.com',
        'Origin': 'https://www.childrensplace.com',
        'Referer': 'https://www.childrensplace.com/',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'sec-ch-ua-mobile': '?0',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
        }
    
    def start_requests(self):
        categories = [
            'https://www.childrensplace.com/ca/c/girls-clothing-school-uniforms',
            'https://www.childrensplace.com/ca/c/toddler-girl-school-uniforms',
            'https://www.childrensplace.com/ca/c/boys-clothes-school-uniforms',
            'https://www.childrensplace.com/ca/c/toddler-boy-school-uniforms',
            'https://www.childrensplace.com/ca/c/baby-girl-clothes',
            'https://www.childrensplace.com/ca/c/mini-me-shop'
        ]
        for category in categories:
            yield scrapy.Request(
                                url=category,
                                callback=self.call_category
            )

    def call_category(self, response):
        all_ids = response.xpath('//li[@class="sc-gsTCUz jaZPax sub-category-item"]/@id').getall()
        if not all_ids:
            all_ids = response.xpath('//li[@class="sc-gsTCUz efGzlB sub-category-item"]/@id').getall()
        all_ids = [ids.replace('list-item-', '') for ids in all_ids]
        for category_id in all_ids:
            category_endpoint = f"https://search.unbxd.io/35594164b71a71a4acf546f74dc23688/ca-childrensplace-com702771526591884/category?start=0&rows=100&variants=false&fields=productid,TCPBazaarVoiceReviewCount,TCPBazaarVoiceRating&pagetype=boolean&p-id=categoryPathId:{category_id}&uid=uid-1622022916754-66954"
            yield scrapy.Request(
                                url=category_endpoint,
                                callback=self.parse_category,
                                meta={
                                    'category_id': category_id
                                }
            )
            

    def parse_category(self, response):
        category_id = response.meta.get('category_id')
        resp = json.loads(response.body)
        products = resp.get('response').get('products')
        for product in products:
            #product_id = product.get('productid')
            unique_id = product.get('uniqueId')
            unique_id = unique_id.split('_')[0]
            review_endpoint = f'https://api.bazaarvoice.com/data/display/0.2alpha/product/summary?PassKey=astw2654err7wm1zw7r05szjx&productid={unique_id}&contentType=reviews&reviewDistribution=primaryRating&rev=0&contentlocale=en_US,en_Ca'
            yield scrapy.Request(
                                url=review_endpoint,
                                callback=self.parse_reviews,
                                meta={
                                    'product_id': unique_id
                                }
            )
        
        number_of_products = resp.get('response').get('numberOfProducts')
        products_left = number_of_products - 100
        if products_left > 0:
            times_to_iterate = math.ceil(products_left / 100)
            for i in range(1, times_to_iterate + 1):
                category_endpoint = f"https://search.unbxd.io/35594164b71a71a4acf546f74dc23688/ca-childrensplace-com702771526591884/category?start={str(i)}00&rows=100&variants=false&fields=productid&pagetype=boolean&p-id=categoryPathId:{category_id}&uid=uid-1622022916754-66954"
                yield scrapy.Request(
                                url=category_endpoint,
                                callback=self.parse_category_deeper     
                )
    
    def parse_category_deeper(self, response):
        resp = json.loads(response.body)
        products = resp.get('response').get('products')
        for product in products:
            #product_id = product.get('productid')
            unique_id = product.get('uniqueId')
            unique_id = unique_id.split('_')[0]
            review_endpoint = f'https://api.bazaarvoice.com/data/display/0.2alpha/product/summary?PassKey=astw2654err7wm1zw7r05szjx&productid={unique_id}&contentType=reviews&reviewDistribution=primaryRating&rev=0&contentlocale=en_US,en_Ca'
            yield scrapy.Request(
                                url=review_endpoint,
                                callback=self.parse_reviews,
                                meta={
                                    'product_id': unique_id
                                }
            )

    def parse_reviews(self, response):
        product_id = response.meta.get('product_id')
        resp = json.loads(response.text)
        num_reviews = resp.get('reviewSummary').get('numReviews')
        if num_reviews:
            average_rating = round(resp.get('reviewSummary').get('primaryRating').get('average'), 1)
        else:
            num_reviews = None
            average_rating = None
        product_endpoint = f"https://search.unbxd.io/35594164b71a71a4acf546f74dc23688/ca-childrensplace-com702771526591884/search?variants=true&variants.count=100&version=V2&rows=20&pagetype=boolean&q={product_id}&promotion=false&fields=productimage,alt_img,style_partno,swatchimage,giftcard,TCPProductIndUSStore,TCPWebOnlyFlagUSStore,TCPWebOnlyFlagCanadaStore,TCPFitMessageUSSstore,TCPFit,product_name,TCPColor,top_rated,imagename,productid,uniqueId,favoritedcount,TCPBazaarVoiceReviewCount,categoryPath3_catMap,categoryPath2_catMap,product_short_description,style_long_description,min_list_price,min_offer_price,TCPBazaarVoiceRating,product_long_description,seo_token,variantCount,prodpartno,variants,v_tcpfit,v_qty,v_tcpsize,style_name,v_item_catentry_id,v_listprice,v_offerprice,v_qty,variantId,auxdescription,list_of_attributes,additional_styles,TCPLoyaltyPromotionTextUSStore,TCPLoyaltyPLCCPromotionTextUSStore,v_variant,low_offer_price,high_offer_price,low_list_price,high_list_price,long_product_title,TCPOutOfStockFlagUSStore,TCPOutOfStockFlagCanadaStore,TCPMultiPackUSStore,TCPMultiPackCanadaStore,TCPMultiPackReferenceUSStore,TCPMultiPackReferenceCanadaStore,single_mapping,multipack_mapping,set_mapping,TCPStyleTypeUS,TCPStyleTypeCA,TCPStyleQTYCA,TCPStyleQTYUS,productfamily,TCPStyleColorCA,TCPStyleColorUS,v_qty_boss&uid=uid-1622022916754-66954"
        yield scrapy.Request(
                            url=product_endpoint,
                            callback=self.parse_product,
                            meta={
                                'average_rating': average_rating,
                                'num_reviews': num_reviews
                            }
        )
        

    def parse_product(self, response):
        resp = json.loads(response.text)
        products = resp.get('response').get('products')
        image_base = 'https://assets.theplace.com/image/upload/v1/ecom/assets/products/tcp/'
        base_url = 'https://www.childrensplace.com/ca/p/'
        average_rating = response.meta.get('average_rating')
        num_reviews = response.meta.get('num_reviews')
        for product in products:
            token = product.get('seo_token')
            product_link = f'{base_url}{token}'
            product_name = product.get('product_name')
            breadcrumbs = product.get('categoryPath3_catMap')
            if breadcrumbs:
                breadcrumbs = breadcrumbs[0]
            else:
                breadcrumbs = product.get('categoryPath2_catMap')
                breadcrumbs = breadcrumbs[0]
            index = breadcrumbs.index('|')
            breadcrumbs = breadcrumbs[index + 1::]
            category = breadcrumbs.replace('>', '|')
            image_id = product.get('style_partno')
            for variant in product.get('variants'):
                sale_price = variant.get('v_offerprice')
                original_price = variant.get('v_listprice')
                if sale_price:
                    regular_price = original_price
                    discounted_price = sale_price
                else:
                    regular_price = original_price
                    discounted_price = None
                raw_size = variant.get('v_tcpsize')
                size = raw_size.split('_')[1]
                flavor = variant.get('v_tcpfit')
                color = variant.get('TCPStyleColorCA')
                if not color:
                    color = variant.get('TCPColor')
                end_image = variant.get('productimage')
                image_link = f'{image_base}{image_id}/{end_image}'
                sku = variant.get('v_variant')
                stock_level = variant.get('v_qty')
                if stock_level:
                    stock_level = 'In_Stock'
                else:
                    stock_level = 'Out_Of_Stock'
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
                    'flavor': flavor, 
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
    


