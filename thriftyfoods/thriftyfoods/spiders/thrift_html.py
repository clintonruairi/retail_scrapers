# requires canadian VPN before running.
import scrapy
import json
import time
import re


class ThiftHtmlSpider(scrapy.Spider):
    name = 'thift_html'
    allowed_domains = ['thriftyfoods.com']

    def start_requests(self):
        set_store_url = 'https://www.thriftyfoods.com/api/en/Store/setSelectedStore?storeId=e6a6565c-69ab-4dca-baf2-750110ac5e64&fulfillmentMethod=pickup&postalCode=V8X1G8'
        set_store_headers = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'origin': 'https://www.thriftyfoods.com',
            'referer': 'https://www.thriftyfoods.com/find-a-store',
            'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'        
        }
        # setting store as Cloverdale
        set_store_data = {
            'storeId': 'e6a6565c-69ab-4dca-baf2-750110ac5e64',
            'fulfillmentMethod': 'pickup',
            'postalCode': 'V8X1G',     
        }

        yield scrapy.FormRequest(
                                url=set_store_url,
                                method='POST',
                                formdata=set_store_data,
                                headers=set_store_headers,
                                callback=self.call_categories
        )


    def call_categories(self, response):
        modifier = '?page=1&pageSize=1000'
        current_time = int(time.time())
        categories = {
            'https://www.thriftyfoods.com/shop-online/bakery-commercial': 'home|shop online|bakery commercial',
            'https://www.thriftyfoods.com/shop-online/bakery-instore': 'home|shop online|bakery instore',
            'https://www.thriftyfoods.com/shop-online/bulk-foods': 'home|shop online|bulk foods',
            'https://www.thriftyfoods.com/shop-online/deli': 'home|shop online|deli',
            'https://www.thriftyfoods.com/shop-online/floral': 'home|shop online|floral',
            'https://www.thriftyfoods.com/shop-online/frozen': 'home|shop online|frozen',
            'https://www.thriftyfoods.com/shop-online/general-merchandise': 'home|shop online|general merchandise',
            'https://www.thriftyfoods.com/shop-online/grocery': 'home|shop online|grocery',
            'https://www.thriftyfoods.com/shop-online/health-and-beauty': 'home|shop online|health beauty',
            'https://www.thriftyfoods.com/shop-online/magazines': 'home|shop online|magazines',
            'https://www.thriftyfoods.com/shop-online/meat': 'home|shop online|meat',
            'https://www.thriftyfoods.com/shop-online/produce': 'home|shop online|produce',
            'https://www.thriftyfoods.com/shop-online/refrigerated-grocery': 'home|shop online|refrigerated grocery',
            'https://www.thriftyfoods.com/shop-online/seafood': 'home|shop online|seafood',
            'https://www.thriftyfoods.com/shop-online/sushi': 'home|shop online|sushi',
            'https://www.thriftyfoods.com/shop-online/take-it-to-go': 'home|shop online|take it to go',
            'https://www.thriftyfoods.com/shop-online/vitamins-and-more': 'home|shop online|vitamins and more'
        }
        category_headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'
        }


        for link, backup_category in categories.items():
            yield scrapy.Request(
                                url=f'{link}{modifier}',
                                callback=self.parse_categories,
                                meta={
                                    'time': current_time,
                                    'backup_category': backup_category
                                },
                                headers=category_headers

            )
    
    def parse_categories(self, response):
        time = response.meta.get('time')
        backup_category = response.meta.get('backup_category')
        products = response.xpath('//a[@class="js-ga-productname"]/@href').getall()
        base = 'https://www.thriftyfoods.com'
        product_headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'
        }
        for product in products:
            yield scrapy.Request(
                                url=f'{base}{product}',
                                callback=self.parse_product,
                                meta={
                                    'time': time,
                                    'backup_category': backup_category
                                },
                                headers=product_headers
            )
    
    def parse_product(self, response):
        # Note - image link does not open in browser, auto downloads.
        current_time = response.meta.get('time')
        backup_category = response.meta.get('backup_category')
        product_link = response.url
        flavor = None
        size = None
        price_unit = None
        weight = None
        sku_pattern = r'[0-]+_[0-9]+'
        sku_result = re.search(sku_pattern, product_link)
        if sku_result:
            sku = sku_result.group()
        if not sku:
            sku = response.xpath('//input[@name="body_0$main_0$AddToCartButton$FldProduct"]/@value').get()
        product_name = response.xpath('//h1[@class="h3-like product-detail__name js-product-detail__name"][1]/text()').get()
        second_product_name = response.xpath('//h1[@class="h3-like product-detail__name js-product-detail__name"][1]/span/text()').get()
        if second_product_name:
            product_name = product_name.strip()
            product_name = f'{product_name} {second_product_name}'
        product_name = product_name.strip()
        brand = response.xpath('//span[@class="product-detail__brand js-product-detail__brand"]/text()').get()
        if brand:
            brand = brand.strip()
        else:
            brand = 'Thrifty Foods'
        breadcrumbs = response.xpath('//ul[@class="nav breadcrumb push--ends"]/li/a/span/text()').getall()
        if breadcrumbs:
            last_crumb = response.xpath('//ul[@class="nav breadcrumb push--ends"]/li[last()]/text()').get()
            if last_crumb:
                last_crumb = last_crumb.strip()
                breadcrumbs.append(last_crumb)
            category = '|'.join(breadcrumbs)
        else:
            category = backup_category
        regular_price = response.xpath('//span[@class="price"]/text()').get()
        original_price = response.xpath('//del[@class="item-product__price push-half--left"]/span/text()').get()
        if original_price:
            discounted_price = regular_price.replace('$', '')
            price_unit_pattern = r'/ .+'
            price_unit_result = re.search(price_unit_pattern, discounted_price)
            if price_unit_result:
                price_unit = price_unit.strip('/')
                price_unit = price_unit.strip()
            discounted_price = discounted_price.replace(' / lbs', '')
            regular_price = original_price.replace('$', '')
            regular_price = regular_price.replace(' / lbs', '')
        else:
            if regular_price:
                regular_price = regular_price[1:]
                price_unit_pattern = r'/ ?.+'
                price_unit_result = re.search(price_unit_pattern, regular_price)
                if price_unit_result:
                    price_unit = price_unit_result.group()
                    price_unit = price_unit.strip('/')
                    price_unit = price_unit.strip()
                regular_price = regular_price.replace(' / lbs', '')
                discounted_price = None
            else:
                regular_price = None
                discounted_price = None
                price_unit = None
        if not price_unit:
            price_unit = response.xpath('//div[@class="product-detail__info js-product-detail__info"]/text()').get()
            if price_unit:
                price_unit = price_unit.replace('"', '')
                price_unit = price_unit.strip()
                price_unit_pattern = r'/ ?.+'
                price_unit_result = re.search(price_unit_pattern, price_unit)
                if price_unit_result:
                    price_unit = price_unit_result.group()
                    price_unit = price_unit.strip('/')
                    price_unit = price_unit.strip()
        weight = response.xpath('//div[@class="item-product__info--product-detail push-half--bottom js-item-product__info--product-detail"]/text()').get()
        if weight:
            weight = weight.strip()
            weight = weight.replace('Single Stem', '')
            weight = weight.replace('10 Stem', '')
            if weight == 'Juliette':
                flavor = weight
                weight = None
            elif weight == 'French Vanilla':
                flavor = weight
                weight = None
            if weight:
                ea_pattern = r'.*(EA|ea)'
                ea_result = re.search(ea_pattern, weight)
                size_pattern = r'.*(ml|ML|l|L)'
                size_result = re.search(size_pattern, weight)
                weight_pattern = r'[0-9]+ ?\.?x? ?[0-9]+.?(g|G|kg|KG|oz|lb|mg)'
                weight_result = re.search(weight_pattern, weight)
                if ea_result:
                    weight = None
                    size = None
                if size_result:
                    size = size_result.group()
                    weight = None
                if weight_result:
                    size = None
                    weight = weight_result.group()
        image_link = response.xpath('//img[@id="body_0_main_0_ProductImage"]/@src').get()
        out_of_stock = response.xpath('//span[@class="icon icon--large icon--warning"]').get()
        if out_of_stock:
            in_stock = 'Out_Of_Stock'
        else:
            in_stock = 'In_Stock'
        if not regular_price:
            return
        if price_unit.endswith('L') or price_unit.endswith('G'):
            regular_price = None
            discounted_price = None
            sale_price = response.xpath('//div[@class="product-detail__info js-product-detail__info"]/text()').get()
            sale_price = sale_price.strip()
            index = sale_price.index('/')
            sale_price = sale_price[:index - 1]
            regular_price = sale_price.replace('$', '')
            
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
                'flavor': flavor,
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




