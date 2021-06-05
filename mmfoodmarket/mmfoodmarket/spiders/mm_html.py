# no vpn needed
import scrapy
import time
import json
import re
# from mmfoodmarket.items import MySQLItem

class MmfoodmarketHtmlSpider(scrapy.Spider):
    name = 'mmfoodmarket_html'
    
    def start_requests(self):
        url = "https://mmfoodmarket.com/en/our-food"

        yield scrapy.Request(
                            url=url,
                            callback=self.pre_login
        )

    def pre_login(self, response):
        headers = {
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://mmfoodmarket.com',
            'referer': 'https://mmfoodmarket.com/en/our-food',
            'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'
        }
        url = 'https://mmfoodmarket.com/Mvc/Account/Login?lang=en'
        yield scrapy.Request(
                            url=url,
                            headers=headers,
                            callback=self.login
        )

    def login(self, response):
        token = response.xpath('//input[@name="__RequestVerificationToken"]/@value').get()
        payload = {
            '__RequestVerificationToken': token,
            'Lang': 'en',
            'Email': 'clintonruairi@gmail.com',
            'Password': 'Dayumman1995dec2#'
        }
        headers = {
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://mmfoodmarket.com',
            'referer': 'https://mmfoodmarket.com/en/our-food',
            'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'
        }
        yield scrapy.FormRequest(
                            url='https://mmfoodmarket.com/Mvc/Account/Login',
                            formdata=payload,
                            callback=self.get_category,
                            headers=headers
        )
    
    def get_category(self, response):
        yield scrapy.Request(
                            url='https://mmfoodmarket.com/en/our-food',
                            callback=self.parse_category,
                            dont_filter=True
                            )

    def parse_category(self, response):
        current_time = int(time.time())
        base = 'https://mmfoodmarket.com/en/'
        links = response.xpath('//li[@class="sfitem sflistitem sfClearfix equalheight"]/a/@href').getall()
        unformatted_names = response.xpath('//li[@class="sfitem sflistitem sfClearfix equalheight"]/a/p/text()').getall()
        names = []
        for name in unformatted_names:
            name = name.strip()
            names.append(name)
        category_info = dict(zip(links, names))
        for link, category in category_info.items():
            yield scrapy.Request(
                                url=f'{base}{link}',
                                callback=self.parse_sub_category,
                                meta={
                                    'time': current_time,
                                    'category': category
                                }
            )
    
    def parse_sub_category(self, response):
        time = response.meta.get('time')
        category = response.meta.get('category')
        subcategories = response.xpath('//div[@class="subcategory_title"]/p/text()').getall()
        sublinks = response.xpath('//div[@class="subcategory_title"]/a/@href').getall()
        subcategory_info = dict(zip(sublinks, subcategories))
        for link, subcat in subcategory_info.items():
            yield scrapy.Request(
                                url=link,
                                callback=self.parse_search_result,
                                meta={
                                    'time': time,
                                    'category': f'{category}|{subcat}'
                                }
                )

    def parse_search_result(self, response):
        time = response.meta.get('time')
        category = response.meta.get('category')
        unformatted_products = response.xpath('//div[@class="top"]/a/@href').getall()
        base = 'https://mmfoodmarket.com/en'
        next_base = 'https://mmfoodmarket.com/'
        fixed_products = []
        for product in unformatted_products:
            product = product[5:]
            fixed_products.append(product)
        for product in fixed_products:
            yield scrapy.Request(
                                url=f'{base}{product}',
                                callback=self.parse_product,
                                meta={
                                    'time': time,
                                    'category': category
                                }
                                
            )
        next_page = response.xpath('//a[@class="next"]/@href').get()
        if next_page:
            yield scrapy.Request(
                                url=f'{next_base}{next_page}',
                                callback=self.parse_search_result,
                                meta={
                                    'time': time,
                                    'category': category,

                                }
            )


    def parse_product(self, response):
        # items = MySQLItem()
        current_time = response.meta.get('time')
        un_category = response.meta.get('category')
        category = f'Home|Our Food|{un_category}'
        product_link = response.url
        product_name = response.xpath('//h1/text()').get()
        product_name.strip()
        product_name = product_name.strip()
        brand = 'M&M Food Market'
        discounted_price = response.xpath('//span[@id="Content_FullWidth_C001_lbl_salePrice"]/text()').get()
        if discounted_price:
            discounted_price.strip('$')
            discounted_price = discounted_price[1:]
        regular_price = response.xpath('//span[@id="Content_FullWidth_C001_lbl_regularPrice"]/text()').get()
        regular_price.strip()
        regular_price.strip('$')
        regular_price = regular_price[1:]
        weight_element = response.xpath('//option[@selected="selected"]/text()').get()
        weight_pattern = r'[0-9]*.*\.?x? ?[0-9]+ ?(g|ml|kg|mL)'
        weight_match = re.match(weight_pattern, weight_element)
        if weight_match:
            weight = weight_match.group()
        else:
            weight = None
        image_link = response.xpath('//img[@id="Content_FullWidth_C001_img_product"]/@src').get()
        sku = response.xpath('//*[@id="Content_FullWidth_C001_hdn_ProductSku"]/@value').get()
        in_stock = response.xpath('//div[@class="order"]/input').get()
        if in_stock:
            in_stock = "In_Stock"
        else:
            in_stock = "Out_Of_Stock"
        
        if weight:
            if '/' in weight:
                index = weight.index('/')
                index = index + 2
                weight = weight[index:]
        yield {
                'product_link': product_link,
                'product_name': product_name,
                'brand': brand,
                'category': category,
                'regular_price': regular_price,
                'discounted_price': discounted_price,
                'price_unit': None,
                'size': None,
                'color': None,
                'flavor': None,
                'weight': weight,
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
        




