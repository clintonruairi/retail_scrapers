# Needs Canadian VPN. max concurrent reqs = 8.
import scrapy
import time
import json
import re
import random


class HoltrenfrewHtmlSpider(scrapy.Spider):
    name = 'holtrenfrew_html'
    allowed_domains = ['www.holtrenfrew.com']
    
    def start_requests(self):
        current_time = int(time.time())
        data_year_month = time.strftime('%Y%m')
        categories = [
            'https://www.holtrenfrew.com/en/Products/Womens/Womens-Clothing/c/WomensClothing?sort=date-desc&q=%3Arelevance#',
            'https://www.holtrenfrew.com/en/Products/Mens/Mens-Clothing/c/MensMensClothing?sort=date-desc&q=%3Arelevance#',
            'https://www.holtrenfrew.com/en/Products/Kids/c/Kids?sort=date-desc&q=%3Arelevance&show=Page#',
            'https://www.holtrenfrew.com/en/Products/Womens/Womens-Shoes/c/WomensShoes?sort=date-desc&q=%3Arelevance#',
            'https://www.holtrenfrew.com/en/Products/Mens/Mens-Shoes/c/MensMensShoes?sort=date-desc&q=%3Arelevance&show=Page#',
            'https://www.holtrenfrew.com/en/Products/Womens/Womens-Bags/c/WomensBags?sort=date-desc&q=%3Arelevance#',
            'https://www.holtrenfrew.com/en/Products/Mens/Mens-Accessories/Mens-Bags/c/MensMensBags?sort=date-desc&q=%3Arelevance#',
            'https://www.holtrenfrew.com/en/Products/Womens/Womens-Accessories/c/WomensAccessories?sort=date-desc&q=%3Arelevance#',
            'https://www.holtrenfrew.com/en/Products/Mens/Mens-Accessories/c/MensMensAccessories?sort=date-desc&q=%3Arelevance#',
            'https://www.holtrenfrew.com/en/Products/Beauty/c/Beauty?q=%3Adate-desc&page=0',
            'https://www.holtrenfrew.com/en/Products/Mens/c/Mens?sort=date-desc&q=%3Arelevance#',
            'https://www.holtrenfrew.com/en/Products/Gifts/Wellness/c/HomeWellness',
            'https://www.holtrenfrew.com/en/Products/Gifts/Books-Stationery/c/GiftsBooksStationary',
            'https://www.holtrenfrew.com/en/Products/Gifts/Home-D%C3%A9cor/c/GiftsHome',
            'https://www.holtrenfrew.com/en/Products/Gifts/Tech/c/GiftsTechAccessories',
            'https://www.holtrenfrew.com/en/Products/H-Project/c/HProject?sort=date-desc&q=%3Arelevance#',

        ]

        for url in categories:
            yield scrapy.Request(
                                url=url,
                                callback=self.parse_category,
                                meta={
                                    'time': current_time,
                                    'data_year_month': data_year_month
                                }
            )


    def parse_category(self, response):
        data_year_month = response.meta.get('data_year_month')
        time = response.meta.get('time')
        product_links = response.xpath('//li[@class="product-item js-product-item"]/a[@class="details-block js-product-details-link"]/@href').getall()
        base = 'https://www.holtrenfrew.com/'
        for product in product_links:
            yield scrapy.Request(
                                url=f'{base}{product}',
                                callback=self.parse_product,
                                meta={
                                    'time': time,
                                    'data_year_month': data_year_month
                                }
            )
        next_page = response.xpath('//li[@class="pagination-next"][1]/a/@href').get()
        if next_page:
            yield scrapy.Request(
                                url=f'{base}{next_page}',
                                callback=self.parse_category,
                                meta={
                                    'time': time,
                                    'data_year_month': data_year_month
                                }
            )
    
    def parse_product(self, response):
        data_year_month = response.meta.get('data_year_month')
        time = response.meta.get('time')
        product_link = response.url
        size = None
        product_name = response.xpath('//h1[@class="product-details__name"]/text()').get()
        brand = response.xpath('//h2[@class="product-details__brand text-uppercase"]/a/text()').get()
        if not brand:
            brand = response.xpath('//h2[@class="product-details__brand text-uppercase"]/text()').get()
        regular_price = response.xpath('//div[@class="product-details__price"]/sapn/text()').get()
        if regular_price:
            regular_price = regular_price[1:]
            regular_price = regular_price.replace(',', '')
        elif not regular_price:
            regular_price = response.xpath('//div[@class="product-details__price"]/span/text()').get()
            regular_price = regular_price[1:]
            regular_price = regular_price.replace(',', '')
        discounted_price = response.xpath('//span[@class="product-details__price--sale"]/sapn/text()').get()
        if discounted_price:
            regular_price = response.xpath('//span[@class="product-details__price--old"]/sapn/text()').get()
            regular_price = regular_price[1:]
            regular_price = regular_price.replace(',', '')
            discounted_price = discounted_price[1:]
            discounted_price = discounted_price.replace(',', '')
        if not discounted_price:
            discounted_price = response.xpath('//span[@class="product-details__price--sale"]/span/text()').get()
            if discounted_price:
                discounted_price = discounted_price[1:]
                regular_price = response.xpath('//span[@class="product-details__price--old"]/sapn/text()').get()
                regular_price = regular_price[1:]
                regular_price = regular_price.replace(',', '')
        size = response.xpath('//a[@class="size-list__link size-list__link--selected "]/text()').get()
        size_pattern = r'[0-9]+ ?(ml|mL)'
        if size:
            size = size.strip()
        elif not size:
            size = response.xpath('//a[@class="size-list__link size-list__link--selected size-list__link--selected-disabled "]/text()').get()
            if size:
                size = size.strip()
            elif not size:
                size = response.xpath('//li[contains(text(), "ml")]/text()').get()
                if size:
                    size = size.strip()
                    result = re.search(size_pattern, size)
                    if result:
                        size = result.group()
                    elif not result:
                        size = None
                elif not size:
                    size = response.xpath('//li[contains(text(), "mL")]/text()').get()
                    if size:
                        size = size.strip()
                        result = re.search(size_pattern, size)
                        if result:
                            size = result.group()
                        elif not result:
                            size = None
        
        color = response.xpath('//a[@class="color-list__link color-list__link--selected "]/@title').get()
        if color == 'No Color':
            color = None
        bread_crumbs = response.xpath('//ol[@class="breadcrumb"]/li[position() < last()]/a/text()').getall()
        category = '|'.join(bread_crumbs)
        category = category.replace('|Products', '')
        image_element = response.xpath('//img[@class="pdp-carousel__main-img js-carousel-img"][1]/@src').get()
        image_link = f'https:{image_element}'
        pattern = r'[0-9]+'
        sku_element = response.xpath('//*[@class="product-details__id"]/text()').get()
        result = re.search(pattern, sku_element)
        sku = result.group()

        form_headers = {
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://www.holtrenfrew.com',
            'referer': response.url,
            'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'
        }
        base = 'https://www.holtrenfrew.com'
        form_action = response.xpath('//button[@class="btn-select-store btn-pickup-modal text-left js-pickup-in-store-button transactional-true"][1]/@data-actionurl').get()
        csrf_token = response.xpath('//input[@name="CSRFToken"][1]/@value').get()
        form_data = {
            'locationQuery': '',
            'cartPage': 'false',
            'entryNumber': '0',
            'shippingMode': 'PICKUP_IN_STORE',
            'CSRFToken': csrf_token,
        }
        yield scrapy.FormRequest(
                            url=f'{base}{form_action}',
                            method='POST',
                            headers=form_headers,
                            formdata=form_data,
                            callback=self.parse_stock,
                            meta={
                                'data_year_month': data_year_month,
                                'time': time,
                                'product_name': product_name,
                                'product_link': product_link,
                                'brand': brand,
                                'regular_price': regular_price,
                                'discounted_price': discounted_price,
                                'size': size,
                                'color': color,
                                'category': category,
                                'image_link': image_link,
                                'sku': sku
                            }
        )
        alternate_sizes = response.xpath('//a[@class="size-list__link "]/@href').getall()
        other_alt_sizes = response.xpath('//a[@class="size-list__link size-list__link--disabled "]/@href').getall()
        alternate_colors = response.xpath('//a[@class="color-list__link "]/@href').getall()
        other_alt_colors = response.xpath('//a[@class="color-list__link color-list__link--disabled "]/@href').getall()
        variants = alternate_colors + alternate_sizes + other_alt_sizes + other_alt_colors
        if variants:
            for variant in variants:
                yield scrapy.Request(
                                    url=f'{base}{variant}',
                                    callback=self.parse_product,
                                    meta={
                                    'time': time,
                                    'data_year_month': data_year_month
                                }
                )


    def parse_stock(self, response):
        data_year_month = response.meta.get('data_year_month')
        time = response.meta.get('time')
        product_link = response.meta.get('product_link')
        product_name = response.meta.get('product_name')
        brand = response.meta.get('brand')
        regular_price = response.meta.get('regular_price')
        discounted_price = response.meta.get('discounted_price')
        size = response.meta.get('size')
        color = response.meta.get('color')
        category = response.meta.get('category')
        image_link = response.meta.get('image_link')
        sku = response.meta.get('sku')
        json_response = json.loads(response.text)
        store_list = json_response.get("data")
        for store in store_list:
            name = store.get("localizedName")
            if name == "Yorkdale":
                stock_message = store.get("canPickedUp")
                if stock_message:
                    in_stock = 'In_Stock'
                else:
                    in_stock = 'Out_Of_Stock'
    
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
                'average_rating': None,
                'num_reviews': None,
                'image_link': image_link,
                'sku': sku,
                'upc': None,
                'stock_level': in_stock,
                'sold_by_3rd_party': 0,
                'shipped_by': None,
                'data_timestamp': time,
                'data_year_month': data_year_month
            }
