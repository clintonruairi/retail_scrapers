# requires canadian VPN
import scrapy
import re
import json
from scrapy.http import HtmlResponse
import time
import math


class PaulmacsHtmlSpider(scrapy.Spider):
    handle_httpstatus_list = [404]
    name = 'paulmacs_html'
    allowed_domains = ['paulmacs.com']
       
    def start_requests(self):
        current_time = int(time.time())
        data_year_month = time.strftime('%Y%m')
        categories = {
            'Dog': [
                    ['Food', '29'], ['Treats', '31'], ['Toys', '30'], ['Collars &amp; Leashes', '2252'], 
                    ['Grooming', '2295'], ['Apparel', '2260'], ['Beds &amp; Mats', '2264'], ['Bowls &amp; Feeding', '2246'], 
                    ['Crates &amp; Carriers', '2290'], ['Flea &amp; Tick', '2256'], ['Gates &amp; Doors', '2851'], 
                    ['Gifts', '2263'],['Health &amp; Wellness', '2242'], ['House Training', '2249'], 
                    ['Houses, Kennels &amp; Fencing', '2294'], ['Stain &amp; Odour Control', '2250'],
                    ['Training &amp; Behavior', '2305'],['Travel Accessories', '2257'],['Waste Management', '2247']
                    ],
            'Cat': [
                    ['Food', '37'],['Treats', '39'], ['Litter', '38'], ['Toys', '2268'], ['Health &amp; Wellness', '2241'],
                    ['Collars &amp; Leashes', '2255'], ['Beds &amp; Mats', '2262'], ['Bowls &amp; Feeding', '2245'],
                    ['Crates &amp; Carriers', '2288'], ['Furniture &amp; Scratch', '2261'], ['Flea &amp; Tick', '2259'],
                    ['Gates &amp; Doors', '2853'], ['Grooming', '2258'], ['Houses, Kennels &amp; Fencing', '2358'],
                    ['Litter Pans &amp; Accessories', '2244'],['Stain &amp; Odour Control', '2251']
                    ],
            'Small Pets': [
                    ['Health &amp; Wellness', '2932'], ['Litter &amp; Bedding', '53'], ['Toys', '2934'],
                    ['Cages &amp; Hutches', '51'], ['Bowls &amp; Feeding', '2926'], ['Treats', '2927'],['Food', '52'],
                    ['Cage Accessories', '2928']
                    ],
            'Bird': [
                    ['Food', '35'], ['Cage Accessories', '33'], ['Treats', '2329'], ['Bowls &amp; Feeding', '2749'],
                    ['Health &amp; Wellness', '2604']
                    ],
            'Fish': [
                    ['Aquariums &amp; Bowls', '41'], ['Food', '42'], ['Aquarium Decor', '2248'],
                    ['Filters &amp; Filter Media', '2280'], ['Heaters &amp; Accessories', '2281'],
                    ['Water &amp; Fish Care', '43']
                    ],
            'Reptile': [
                    ['Reptile', '47'], ['Habitats', '48'], ['Habitat Accessories', '2283'], ['Lighting &amp; Heating', '2272'],
                    ['Substrate', '2282']
                    ]
        }
        for parentnams, category_list in categories.items():
            for cname_termid in category_list:
                form_action = 'https://paulmacs.com/wp-content/themes/paulmacs/product_ajax.php'
                form_data = {
                    'action': 'product_list',
                    'page_id': '1',
                    'term_id': cname_termid[1],
                    'perpage': '50',
                    'ordering_val': 'asc',
                    'cname': cname_termid[0],
                    'parentnams': parentnams
                }
                yield scrapy.FormRequest(
                                    url=form_action,
                                    formdata=form_data,
                                    callback=self.parse_json_search,
                                    meta={
                                        'time': current_time,
                                        'data_year_month': data_year_month,
                                        'category': f'{parentnams}|{cname_termid[0]}'.replace('amp;', ''),
                                        'parentnams': parentnams,
                                        'cname': cname_termid[0],
                                        'term_id': cname_termid[1]
                                    },
                                    dont_filter=True

                )
        html_categories = {
            'https://paulmacs.com/products/dog/ramps-and-steps/': 'Dog|Ramps & Steps',
            'https://paulmacs.com/products/cat/gifts/': 'Cat|Gifts',
            'https://paulmacs.com/products/cat/ramps-and-steps/': 'Cat|Ramps & Steps',
            'https://paulmacs.com/products/cat/training-and-behavior/': 'Cat|Training & Behavior',
            'https://paulmacs.com/products/cat/travel-accessories/': 'Cat|Travel Accessories',
            'https://paulmacs.com/products/small-pets/cleaning-and-maintenance/': 'Small Pets|Cleaning & Maintenance',
            'https://paulmacs.com/products/small-pets/grooming/': 'Small Pets|Grooming',
            'https://paulmacs.com/products/small-pets/stain-and-odour-control/': 'Small Pets|Stain & Odour Control',
            'https://paulmacs.com/products/small-pets/travel-accessories/': 'Small Pets|Travel Accessories',
            'https://paulmacs.com/products/bird/cages/': 'Bird|Cages',
            'https://paulmacs.com/products/bird/cleaning-and-maintenance/': 'Bird|Cleaning & Maintenance',
            'https://paulmacs.com/products/bird/litter-bedding/': 'Bird|Litter & Bedding',
            'https://paulmacs.com/products/fish/maintenance/': 'Fish|Maintenance',
            'https://paulmacs.com/products/fish/air-pumps-and-accessories/': 'Fish|Air Pumps & Accesories',
            'https://paulmacs.com/products/fish/lighting-and-hoods/': 'Fish|Lighting & Hoods',
            'https://paulmacs.com/products/reptile/health-and-wellness/': 'Reptile|Health & Wellness',
            'https://paulmacs.com/products/reptile/habitat-decor/': 'Reptile|Habitat Decor'
        }
        for link, category in html_categories.items():
            yield scrapy.Request(
                                url=link,
                                callback=self.parse_html_search,
                                meta={
                                    'time': current_time,
                                    'category': category,
                                    'data_year_month': data_year_month
                                }
            )
    
    def parse_json_search(self, response):
        time = response.meta.get('time')
        data_year_month = response.meta.get('data_year_month')
        category = response.meta.get('category')
        parentnams = response.meta.get('parentnams')
        print(f'\n\nparentnams: {parentnams}\n\n')
        cname = response.meta.get('cname')
        print(f'\n\ncname: {cname}\n\n')
        term_id = response.meta.get('term_id')
        print(f'\n\nterm_id: {term_id}\n\n')
        json_resp = json.loads(response.text)
        html = json_resp.get('data_div_right')
        html_response = HtmlResponse(url='my_string', body=html, encoding='utf-8')
        links = html_response.xpath('//div[@class="archiveproinner"]/a/@href').getall()
        for link in links:
            yield scrapy.Request(
                                url=link,
                                callback=self.parse_product,
                                meta={
                                    'time': time,
                                    'data_year_month': data_year_month,
                                    'category': category,

                                }
            )
        number_of_products = int(json_resp.get('product_count'))
        products_left = number_of_products - 50
        if products_left > 0:
            times_to_iterate = math.ceil(products_left / 50)
            page_id_int = 2
            for i in range(1, times_to_iterate + 1):
                page_id = str(page_id_int)
                form_action = 'https://paulmacs.com/wp-content/themes/paulmacs/product_ajax.php'
                form_data = {
                    'action': 'product_list',
                    'page_id': page_id,
                    'term_id': term_id,
                    'perpage': '50',
                    'ordering_val': 'asc',
                    'cname': cname,
                    'parentnams': parentnams
                }
                page_id_int += 1
                yield scrapy.FormRequest(
                                    url=form_action,
                                    formdata=form_data,
                                    callback=self.parse_json_search_further,
                                    meta={
                                        'time': time,
                                        'data_year_month': data_year_month,
                                        'category': category
                                    },
                                    dont_filter=True
                            
                )
    
    def parse_json_search_further(self, response):
        time = response.meta.get('time')
        data_year_month = response.meta.get('data_year_month')
        category = response.meta.get('category')
        json_resp = json.loads(response.text)
        html = json_resp.get('data_div_right')
        html_response = HtmlResponse(url='my_string', body=html, encoding='utf-8')
        links = html_response.xpath('//div[@class="archiveproinner"]/a/@href').getall()
        for link in links:
            yield scrapy.Request(
                                url=link,
                                callback=self.parse_product,
                                meta={
                                    'time': time,
                                    'data_year_month': data_year_month,
                                    'category': category,

                                }
            )
    
    def parse_html_search(self, response):
        time = response.meta.get('time')
        category = response.meta.get('category')
        data_year_month = response.meta.get('data_year_month')
        links = response.xpath('//div[@class="archiveproinner"]/a/@href').getall()
        for link in links:
            yield scrapy.Request(
                                url=link,
                                callback=self.parse_product,
                                meta={
                                    'time': time,
                                    'data_year_month': data_year_month,
                                    'category': category,

                                }
            )



    def parse_product(self, response):
        weight = None
        time = response.meta.get('time')
        data_year_month = response.meta.get('data_year_month')
        category = response.meta.get('category')
        category = f'Home|{category}'
        product_link = response.url
        product_name = response.xpath('//div[@class="product_title"]/text()').get()
        product_name = product_name.replace(';', '')
        brand = response.xpath('//div[@class="brand-name"]/text()').get()
        if product_name.startswith('FerretSheen'):
            brand = 'Ferret Sheen'
        in_stock = 'In_Stock'
        prices_no_discount = response.xpath('//div[@class="item_price"]/text()').getall()
        original_price = response.xpath('//div[@class="item_price sales_pirce"]/text()').getall()
        discounted_prices = response.xpath('//div[@class="item_price discounts_pirce"]/text()').getall()
        unformatted_skus = response.xpath('//div[@class="itemno"]/text()').getall()
        pattern = r'[0-9]+'
        skus = []
        image_link = response.xpath('//div[@class="product_img"]/img/@src').get()
        for sku in unformatted_skus:
            result = re.search(pattern, sku)
            skus.append(result.group())
        weights = response.xpath('//div[@class="itemno"]/span/text()').getall()
        if prices_no_discount and not original_price:
            count = 0
            for price in prices_no_discount:
                regular_price = price[1:]
                regular_price = regular_price.replace(' ea.', '')
                discounted_price = None
                weight = weights[count]
                size = None
                price_unit = None
                price_unit_pattern = r'.*(EA|WT|MO)'
                price_unit_result = re.search(price_unit_pattern, weight)
                if price_unit_result:
                    price_unit = None
                    weight = None
                    size = None
                else:
                    size_pattern = r'.*(IN|PC|pk|QT|SM|MD|LG|PK|XL|XS|XXS|FT|SZ|sz|xs|xl|ft|CM|cm|CP|cp|PT|pt)'
                    size_result = re.search(size_pattern, weight)
                    if size_result:
                        size = weight
                        weight = None
                        price_unit = None
                sku = skus[count]
                count += 1
                if weight:
                    if weight.endswith('.0'):
                        weight = None
                    if weight == '0' or weight == ' 0':
                        weight = None
                if not weight:
                    weight = None
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
                    'stock_level': in_stock,
                    'sold_by_3rd_party': 0,
                    'shipped_by': None,
                    'data_timestamp': time,
                    'data_year_month': data_year_month
                }
        elif original_price and not prices_no_discount:
            count = 0
            for price in original_price:
                regular_price = price[1:]
                regular_price = regular_price.replace(' ea.', '')
                unformatted_discounted_price = discounted_prices[count]
                discounted_price = unformatted_discounted_price[1:]
                discounted_price = discounted_price.replace(' ea.', '')
                weight = weights[count]
                size = None
                price_unit = None
                price_unit_pattern = r'.*(EA|WT|MO)'
                price_unit_result = re.search(price_unit_pattern, weight)
                if price_unit_result:
                    price_unit = None
                    weight = None
                    size = None
                else:
                    size_pattern = r'.*(IN|PC|pk|QT|SM|MD|LG|PK|XL|XS|XXS|FT|SZ|sz|xs|xl|ft|CM|cm|CP|cp|PT|pt)'
                    size_result = re.search(size_pattern, weight)
                    if size_result:
                        size = weight
                        weight = None
                        price_unit = None
                sku = skus[count]
                count += 1
                if weight:
                    if weight.endswith('.0'):
                        weight = None
                    if weight == '0' or weight == ' 0':
                        weight = None
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
                    'stock_level': in_stock,
                    'sold_by_3rd_party': 0,
                    'shipped_by': None,
                    'data_timestamp': time,
                    'data_year_month': data_year_month
                    }
        elif prices_no_discount and original_price:
            both_prices = response.xpath('//div[@class="item_price"]/text() | //div[@class="item_price sales_pirce"]/text()').getall()
            count = 0
            xpath_count = 1
            for price in both_prices:
                regular_price = price[1:]
                regular_price = regular_price.replace(' ea.', '')
                discounted_price = response.xpath(f'//div[@class="item_price discounts_pirce"][{xpath_count}]/text()').get()
                if discounted_price:
                    discounted_price = discounted_price[1:]
                    discounted_price = discounted_price.replace(' ea.', '')
                weight = weights[count]
                size = None
                price_unit = None
                price_unit_pattern = r'.*(EA|WT|MO)'
                price_unit_result = re.search(price_unit_pattern, weight)
                if price_unit_result:
                    price_unit = None
                    weight = None
                    size = None
                else:
                    size_pattern = r'.*(IN|PC|pk|QT|SM|MD|LG|PK|XL|XS|XXS|FT|SZ|sz|xs|xl|ft|CM|cm|CP|cp|PT|pt)'
                    size_result = re.search(size_pattern, weight)
                    if size_result:
                        size = weight
                        weight = None
                        price_unit = None
                sku = skus[count]
                count += 1
                xpath_count += 1
                if weight:
                    if weight.endswith('.0'):
                        weight = None
                if not weight:
                    weight = None
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
                    'stock_level': in_stock,
                    'sold_by_3rd_party': 0,
                    'shipped_by': None,
                    'data_timestamp': time,
                    'data_year_month': data_year_month
                    }


# {'downloader/request_bytes': 3141768,
#  'downloader/request_count': 4613,
#  'downloader/request_method_count/GET': 4493,
#  'downloader/request_method_count/POST': 120,
#  'downloader/response_bytes': 121260128,
#  'downloader/response_count': 4613,
#  'downloader/response_status_count/200': 4613,
#  'dupefilter/filtered': 236,
#  'elapsed_time_seconds': 367.242809,
#  'finish_reason': 'finished',
#  'finish_time': datetime.datetime(2021, 4, 4, 5, 19, 24, 177978),
#  'item_scraped_count': 6733,
#  'log_count/DEBUG': 11347,
#  'log_count/INFO': 17,
#  'memusage/max': 167174144,
#  'memusage/startup': 55431168,
#  'request_depth_max': 2,
#  'response_received_count': 4613,
#  'scheduler/dequeued': 4613,
#  'scheduler/dequeued/memory': 4613,
#  'scheduler/enqueued': 4613,
#  'scheduler/enqueued/memory': 4613,
#  'start_time': datetime.datetime(2021, 4, 4, 5, 13, 16, 935169)}



