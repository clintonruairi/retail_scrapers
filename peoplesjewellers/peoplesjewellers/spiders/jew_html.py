# no VPN needed
import scrapy
import math
import time
import re
from scrapy_splash import SplashRequest
import json

class JewHtmlSpider(scrapy.Spider):
    name = 'jew_html'
    time_now = int(time.time())
    data_year_month = time.strftime('%Y%m')
    
    def start_requests(self):
        start = 'https://www.peoplesjewellers.com/'
        yield SplashRequest(
                            url=start,
                            callback=self.find_categories,
                            args={
                                'wait': 2
                            }
        )

    def find_categories(self, response):
        categories = response.xpath('//div[@class="link-label"]/a/@href').getall()
        cat_pattern = r'https://www.peoplesjewellers.com/.+/c/'
        id_pattern = r'/c/[0-9]+'
        for cat in categories:
            if 'view-all' in cat or '-off-clearance' in cat:
                continue
            result = re.search(id_pattern, cat)
            id_to_format = result.group()
            cat_id = id_to_format.replace('/c/', '')
            cat_result = re.search(cat_pattern, cat)
            cat_match = cat_result.group()
            cat_match = cat_match.replace('https://www.peoplesjewellers.com/', '')
            cat_match = cat_match.replace('/c/', '')
            category = cat_match.replace('/', '|')
            category = category.replace('-', ' ')
            if 'vera' in cat:
                category = 'collections|vera wang bridal'
            if 'enchanted' in cat:
                category = 'collections|enchanted disney fine jewellery'
            if 'moments-by-hallmark' in cat:
                category = 'collections|moments by hallmark diamonds'
            if 'lab-created' in cat:
                category = 'collections|lab created diamonds'
            if 'birthstone' in cat:
                category = 'collections|birthstone'
            if 'gold-jewellery' in cat:
                category = 'collections|gold jewellery'
            if 'com/gift-ideas/c/1341162?q=%3A%3Agender%3AMEN' in cat:
                category = 'gift ideas|gifts for him'

            yield scrapy.Request(
                                url=cat,
                                callback=self.parse_category,
                                meta={
                                    'category_id': cat_id,
                                    'category': category
                                }
            )

    def parse_category(self, response):
        category = response.meta.get('category')
        string_items_number = response.xpath('//span[@class="searchstring"]/span/strong/text()').get()
        string_items_number = string_items_number.replace(',', '')
        number_of_items = int(string_items_number)
        base = 'https://www.peoplesjewellers.com'
        links = response.xpath('//div[@class="name"]/a/@href').getall()
        reviews = response.xpath('//span[@class="total-reviews"]/text()').getall()
        link_reviews = dict(zip(links, reviews))
        for product, review in link_reviews.items():
            yield scrapy.Request(
                                url=f'{base}{product}',
                                callback=self.parse_product,
                                meta={
                                    'review': review,
                                    'category': category
                                }
            )
        category_id = response.meta.get('category_id')
        items_left = number_of_items - 18
        if items_left > 0:
            times_to_iterate = math.ceil(items_left / 18)
            for i in range(1, times_to_iterate + 1):
                endpoint = "https://www.peoplesjewellers.com/c/loadMoreHtml"
                body = {
                    'code': str(category_id),
                    'pageNumber': {str(i)}
                }
                headers = {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
                }
                yield scrapy.FormRequest(
                                    url=endpoint,
                                    method='POST',
                                    formdata=body,
                                    headers=headers,
                                    callback=self.parse_category_deeper,
                                    meta={
                                        'category': category
                                    }
                )
        

    def parse_category_deeper(self, response):
        category = response.meta.get('category')
        base = 'https://www.peoplesjewellers.com'
        links = response.xpath('//div[@class="name"]/a/@href').getall()
        reviews = response.xpath('//span[@class="total-reviews"]/text()').getall()
        link_reviews = dict(zip(links, reviews))
        for product, review in link_reviews.items():
            yield scrapy.Request(
                                url=f'{base}{product}',
                                callback=self.parse_product,
                                meta={
                                    'review': review,
                                    'category': category
                                }
            )

    def parse_product(self, response):
        flavor = None
        personalisable = response.xpath('//span[@class="product-tag"]/text()').get()
        if personalisable == 'Personalized':
            return
        average_rating = None
        num_reviews = None
        rating_element = response.xpath('//script[contains(text(), "salePriceProductDataLayer")]/text()').get()
        rating_pattern = r'"rating": "[0-9]+\.?[0-9]*"'
        rating_result = re.search(rating_pattern, rating_element)
        if rating_result:
            unformatted_rating = rating_result.group()
            average_rating = unformatted_rating[11:-1]
            average_rating = float(average_rating)
            average_rating = round(average_rating, 1)
        review_pattern = r'"ratingCount": "[0-9]+\.?[0-9]*"'
        review_result = re.search(review_pattern, rating_element)
        if review_result:
            unformatted_reviews = review_result.group()
            num_reviews = unformatted_reviews[16:-1]
        product_link = response.url
        size = None
        product_name = response.xpath('//h1[@class="name"]/text()').get()
        brand = 'Peoples Jewellers'
        crumbs = response.xpath('//ol[@class="breadcrumb"]/li/a/span/text()').getall()
        category = '|'.join(crumbs)
        if 'View All' in category:
            category = response.meta.get('category')
            category = f'home|{category}'
        sale_price = response.xpath('//span[@class="price"]/span[1]/text()').get()
        original_price_string = response.xpath('//div[@class="original-price"]/div/text()').get()
        if original_price_string:
            regular_price = original_price_string.replace('Orig\xa0$', '')
            regular_price = regular_price.replace(',', '')
            discounted_price = sale_price
        else:
            regular_price = sale_price
            discounted_price = None
        if not regular_price:
            regular_price = response.xpath('//div[@itemprop="price"]/text()').get()
        color = response.xpath('//a[contains(text(), "Colour")]/ancestor::th/following-sibling::*/text()').get()
        weight = response.xpath('//a[contains(text(), "Weight")]/ancestor::th/following-sibling::*/text()').get()
        if weight == 'Diamond Accent':
            weight = None
        image_base = 'https://www.peoplesjewellers.com'
        relative_image = response.xpath('//div[@class="thumb main-image-slot item"]/img/@data-src').get()
        image_link = image_base + relative_image
        sku = response.xpath('//meta[@itemprop="sku"]/@content').get()
        all_sizes = response.xpath('//option[contains(text(), "Size")]/following-sibling::option/span/text()').getall()
        flavor = response.xpath('//label[contains(text(), "Metal Type:")]/strong/text()').get()
        if weight:
            weight = weight + ' CT'
        if not weight:
            pattern = r'[0-9]*\.?[0-9]+ *CT'
            result = re.search(pattern, product_name)
            if result:
                weight = result.group()
        if all_sizes:
            for size in all_sizes:
                if 'Out of Stock' in size:
                    in_stock = 'Out_Of_Stock'
                    size = size.replace('&nbsp- Out of Stock', '')
                else:
                    in_stock = 'In_Stock'
                if not regular_price:
                    continue
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
                    'flavor': flavor, 
                    'weight': weight, 
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
        else:
            if not regular_price:
                return
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
                'flavor': flavor, 
                'weight': weight, 
                'average_rating': average_rating, 
                'num_reviews': num_reviews, 
                'image_link': image_link,
                'sku': sku, 
                'upc': None,
                'stock_level': 'In_Stock',
                'sold_by_3rd_party': 0,
                'shipped_by': None,
                'data_timestamp': self.time_now,
                'data_year_month': self.data_year_month
                    }

