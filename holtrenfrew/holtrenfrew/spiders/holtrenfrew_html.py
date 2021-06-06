# Needs Canadian VPN. max concurrent reqs = 8.
import scrapy
import time
import json
import re
import random


class HoltrenfrewHtmlSpider(scrapy.Spider):
    name = 'holtrenfrew_html'
    data_timestamp = int(time.time())
    data_year_month = time.strftime('%Y%m')
    
    def start_requests(self):
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
                                callback=self.parse_category
            )


    def parse_category(self, response):
        product_links = response.xpath('//li[@class="product-item js-product-item"]/a[@class="details-block js-product-details-link"]/@href').getall()
        base = 'https://www.holtrenfrew.com/'
        for product in product_links:
            yield scrapy.Request(
                                url=f'{base}{product}',
                                callback=self.parse_product
            )
        next_page = response.xpath('//li[@class="pagination-next"][1]/a/@href').get()
        if next_page:
            yield scrapy.Request(
                                url=f'{base}{next_page}',
                                callback=self.parse_category
            )
    
    def parse_product(self, response):
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
        description = response.xpath('//div[@class="product-details__descr"]/text()').get()
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
                                'product_name': product_name,
                                'product_link': product_link,
                                'brand': brand,
                                'regular_price': regular_price,
                                'discounted_price': discounted_price,
                                'size': size,
                                'color': color,
                                'category': category,
                                'image_link': image_link,
                                'sku': sku,
                                'description': description
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
                                    callback=self.parse_product
                )


    def parse_stock(self, response):
        size_with_unit = None
        size_without_unit = None
        product_link = response.meta.get('product_link')
        product_name = response.meta.get('product_name')
        brand = response.meta.get('brand')
        regular_price = response.meta.get('regular_price')
        discounted_price = response.meta.get('discounted_price')
        size = response.meta.get('size')
        color = response.meta.get('color')
        breadcrumb = response.meta.get('category')
        image_link = response.meta.get('image_link')
        sku = response.meta.get('sku')
        description = response.meta.get('description')
        json_response = json.loads(response.text)
        store_list = json_response.get("data")
        if 'mask' in size.lower():
            return
        for store in store_list:
            name = store.get("localizedName")
            if name == "Yorkdale":
                stock_message = store.get("canPickedUp")
                if stock_message:
                    stock_level = 'In_Stock'
                else:
                    stock_level = 'Out_Of_Stock'
        if size:
            if 'cm' in size.lower() or 'ml' in size.lower():
                size_with_unit = size
            else:
                size_without_unit = size
    
        yield {
            'product_link': product_link,
            'product_name': product_name,
            'brand': brand, 
            'breadcrumb': breadcrumb,
            'size_without_unit': size_without_unit,
            'size_with_unit': size_with_unit,
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
