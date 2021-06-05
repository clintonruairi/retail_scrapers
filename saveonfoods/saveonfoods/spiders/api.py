# needs canadian vpn
import scrapy
import time
import json
import re

class FoodApiSpider(scrapy.Spider):
    name = 'food_api'
    time_now = int(time.time())
    data_year_month = time.strftime('%Y%m')
    links_added = []
    
    def start_requests(self):
        start = 'https://www.saveonfoods.com/sm/pickup/rsid/937/'
        yield scrapy.Request(
                            url=start,
                            callback=self.parse_home
        )
    
    def parse_home(self, response):
        main_categories = response.xpath('//a[@class="AnchorNoStyle-sc-125lep2 cAZQkd CategoryLink-sc-1gzm5ln emlbuu"]/@href').getall()
        for category in main_categories:
            link = f'https://www.saveonfoods.com{category}'
            yield scrapy.Request(
                                url=link,
                                callback=self.parse_sub_cats
            )

    def parse_sub_cats(self, response):
        sub_cats = response.xpath('//a[@class="AnchorNoStyle-sc-125lep2 cAZQkd CarouselLink-sc-14pqnf7 hxhwIM"]/@href').getall()
        pattern = r'id-[0-9]+'
        for cat in sub_cats:
            result = re.search(pattern, cat)
            code = result.group().replace('id-', '')
            endpoint = f'https://storefrontgateway.saveonfoods.com/api/stores/937/categories/{code}/search?q=*&take=100&page=1'
            yield scrapy.Request(
                                url=endpoint,
                                callback=self.parse_category
            )

    def parse_category(self, response):
        resp = json.loads(response.text)
        for product in resp.get('items'):
            code = product.get('productId')
            category = product.get('defaultCategory')[0].get('categoryBreadcrumb')
            category = category.replace('/', '|')
            category = category.replace('Grocery', 'Home')
            sku = product.get('sku')
            product_link = f'https://www.saveonfoods.com/sm/pickup/rsid/937/product/{sku}'
            if product_link in self.links_added:
                print('link skipped')
                continue
            self.links_added.append(product_link)
            product_endpoint = f'https://storefrontgateway.saveonfoods.com/api/stores/937/products/{code}'
            yield scrapy.Request(
                                url=product_endpoint,
                                callback=self.parse_product,
                                meta={
                                    'category': category
                                }
            )
        pages = resp.get('pagination').get('_links')
        if 'next' in pages:
            next_page = pages.get('next').get('href')
            if next_page:
                endpoint = f'https://storefrontgateway.saveonfoods.com{next_page}'
                yield scrapy.Request(
                                    url=endpoint,
                                    callback=self.parse_category
                )

    def parse_product(self, response):
        size = None
        weight = None
        price_unit = None
        resp = json.loads(response.text)
        sku = resp.get('sku')
        product_link = f'https://www.saveonfoods.com/sm/pickup/rsid/937/product/{sku}'
        product_name = resp.get('name')
        brand = resp.get('brand')
        category = response.meta.get('category')
        number_size = resp.get('unitsOfSize').get('size')
        label_size = resp.get('unitsOfSize').get('label')
        unit_price = resp.get('unitPrice')
        if not unit_price or 'each' in unit_price:
            sale_price = resp.get('price')
            sale_price = sale_price.replace('$', '')
            sale_price = sale_price.replace(' avg/ea', '')
            sale_price = sale_price.replace('/100g', '')
            sale_price = sale_price.replace('/lb', '')
            original_price = resp.get('wasPrice')
            if original_price:
                regular_price = original_price.replace('$', '')
                regular_price = regular_price.replace(' avg/ea', '')
                regular_price = regular_price.replace('/100g', '')
                regular_price = regular_price.replace('/lb', '')
                regular_price = float(regular_price)
                discounted_price = float(sale_price)
            else:
                regular_price = float(sale_price)
                discounted_price = None
            price_unit = f'{number_size} {label_size}'
        elif '/100g' in unit_price:
            price_to_unit = unit_price.split('/')
            regular_price = price_to_unit[0]
            regular_price = regular_price.replace('$', '')
            regular_price = float(regular_price)
            if not regular_price:
                regular_price = resp.get('price')
                regular_price = regular_price.replace('$', '')
                regular_price = float(regular_price)
                discounted_price = None
                price_unit = price_to_unit[1]
                weight = f'{number_size} {label_size}'
            else:
                discounted_price = None
                price_unit = price_to_unit[1]
                weight = f'{number_size} {label_size}'
        elif '/100ml' in unit_price:
            price_to_unit = unit_price.split('/')
            regular_price = price_to_unit[0]
            regular_price = regular_price.replace('$', '')
            regular_price = float(regular_price)
            if not regular_price:
                regular_price = resp.get('price')
                regular_price = regular_price.replace('$', '')
                regular_price = float(regular_price)
                discounted_price = None
                price_unit = price_to_unit[1]
                size = f'{number_size} {label_size}' 
            else:
                discounted_price = None
                price_unit = price_to_unit[1]
                size = f'{number_size} {label_size}' 

        image_link = resp.get('primaryImage').get('details')
        if 'v8content.' in image_link:
            image_link = None
        in_stock = resp.get('available')
        stock_level = 'Out_Of_Stock'
        if in_stock:
            stock_level = 'In_Stock'
        
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