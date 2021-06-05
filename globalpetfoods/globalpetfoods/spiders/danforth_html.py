# pylint: disable=import-error
import scrapy
import re
import json
import brands
import time

class DanforthglobalpetfoodsCategoriesSpider(scrapy.Spider):
    name = 'danforthglobalpetfoods_categories'
    data_timestamp = int(time.time())
    data_year_month = time.strftime('%Y%m')

    def start_requests(self):
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'referer': 'https://danforth.globalpetfoods.com/',
            'sec-ch-ua': '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36'
        }
        self.brands = {}
        self.brands_for_title = []
        for line in brands.BRANDS:
            for link, brand in line.items():
                self.brands[link] = brand
                self.brands_for_title.append(brand)
        yield scrapy.Request(
                            url='https://danforth.globalpetfoods.com/products/shop/',
                            callback=self.parse_categories,
                            headers=headers
                            
        )
    
    def parse_categories(self, response):
        categories = response.xpath('//div[@class="col-sm-3 pl-0"]/ul/li/a[not(@class="shop-all-link")]/@href').getall()
        sub_categories = response.xpath('//li[@class="col-sm-3 pl-0"]/a/@href').getall()
        all_categories = categories + sub_categories
        base = 'https://danforth.globalpetfoods.com'
        referer = response.url
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'referer': referer,
            'sec-ch-ua': '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36'

        }
        for sub_category in all_categories:
            yield scrapy.Request(
                                url=f'{base}{sub_category}',
                                callback=self.parse_search_results,
                                headers=headers
            )

    def parse_search_results(self, response):
        category_crumbs = response.xpath('//li[@class="list_category"]/a/text()').getall()
        category = '|'.join(category_crumbs)
        product_links = response.xpath('//div[@class="prdct-detail-box"]/h3/a/@href').getall()
        base = 'https://danforth.globalpetfoods.com'
        referer = response.url
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'referer': referer,
            'sec-ch-ua': '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36'

        }

        for link in product_links:
            link = link.strip()
            yield scrapy.Request(
                                url=f'{base}{link}',
                                meta={
                                    'category': category
                                },
                                headers=headers,
                                callback=self.parse_product
            )

        next_page = response.xpath('//a[text()="Next"]/@href').get()
        if next_page:
            next_page = next_page.strip()
            yield scrapy.Request(
                                url=f'{base}{next_page}',
                                headers=headers,
                                callback=self.parse_search_results
                )

    def parse_product(self, response):
        available_sizes = response.xpath('//div[@class="btn-group radio-group"]/label/a/@href').getall()
        category = response.meta.get('category')
        category = f'Home|{category}'
        base = 'https://danforth.globalpetfoods.com'
        product_link = response.url
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'referer': product_link,
            'sec-ch-ua': '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36'

        }
        if available_sizes:
            for variant in available_sizes:
                variant = variant.strip()
                yield scrapy.Request(
                                    url=f'{base}{variant}',
                                    callback=self.parse_size_variant,
                                    meta={
                                        'category': category
                                    },
                                    headers=headers

                    )

        size_without_unit = None
        size_with_unit = None
        dimension = None
        regular_qty = None
        discounted_qty = None
        product_link = response.url
        product_name = response.xpath('//h1[@tabindex="0"]/text()').get()
        if ',' in product_name:
            index = product_name.index(',')
            product_name = product_name[:index]
        brand = self.brands.get(product_link)
        if not brand:
            for brand_name in self.brands_for_title:
                if product_name.startswith(brand_name):
                    brand = brand_name
            if not brand:
                brand = 'Global Pet Foods'
        breadcrumb = response.meta.get('category')
        regular_price = response.xpath('//span[@class="current-price"]/text()').get()
        regular_price = regular_price[3:]
        discounted_price = None
        average_rating = None
        num_reviews = None
        size_with_unit = response.xpath('//label[contains(text(), "Weight")]/parent::div/following-sibling::div/text()').get()
        image_link = response.xpath('//div[@class="main-item"]/img/@src').get()
        size = response.xpath('//div[@class="size-box"]/h3/text()').get()
        weight_pattern = r'[0-9]*\.?[0-9]+ ?-?(g|ml|kg|mL|oz|lb|L|mg|gram)'
        if size:
            size = size[7:]
            weight_match = re.match(weight_pattern, size, flags=re.IGNORECASE)
            if weight_match:
                size_with_unit = weight_match.group()
            else:
                size_without_unit = size
        elif not size:
            size = response.xpath('//label[contains(text(), "Size")]/parent::div/following-sibling::div/text()').get()
            weight_match = re.match(weight_pattern, size)
            if weight_match:
                size_with_unit = weight_match.group()
            else:
                size_without_unit = size
        stock_level = response.xpath('//button[@class="btn add-cart-btn"]').get()
        if stock_level:
            stock_level = 'In_Stock'
        else:
            stock_level = 'Out_Of_Stock'
        description = response.xpath('//div[@id="description"]/div/div/p/text()').get()
        if size:
            if 'Breeds' in size:
                size = None
        if size:
            # pattern to find if size contains count/pack/-pk
            qty_pattern = r'[0-9]+ ?-?(pk|pack|count|ct)'
            qty_result = re.search(qty_pattern, size, re.IGNORECASE)
            if qty_result:
                # this pattern will extract solely the number for quantity
                count_pattern = r'[0-9]+'
                qty_count_result = re.search(count_pattern, qty_result.group())
                if discounted_price:
                    discounted_qty = qty_count_result.group()
                else:
                    regular_qty = qty_count_result.group()
        yield {
            'product_link': product_link,
            'product_name': product_name,
            'brand': brand, 
            'breadcrumb': breadcrumb,
            'size_without_unit': size_without_unit,
            'size_with_unit': size_with_unit,
            'dimension': dimension,
            'sku': None,
            'upc': None,
            'regular_price': regular_price,
            'regular_qty': regular_qty,
            'regular_unit': None,
            'discounted_price': discounted_price,
            'discounted_qty': discounted_qty,
            'discounted_unit': None,
            'currency': 'CAD',
            'average_rating': average_rating,
            'num_reviews': num_reviews,
            'shipped_by': None,
            'sold_by_third_party': 0, 
            'stock_level': stock_level,
            'online_only': False,
            'brief': None,
            'description': description,
            'image_link': image_link,
            'data_timestamp': self.data_timestamp,
            'data_year_month': self.data_year_month, 
            'retailer_code': None,
            }

    def parse_size_variant(self, response):
        size_without_unit = None
        size_with_unit = None
        dimension = None
        regular_qty = None
        discounted_qty = None
        product_link = response.url
        product_name = response.xpath('//h1[@tabindex="0"]/text()').get()
        if ',' in product_name:
            index = product_name.index(',')
            product_name = product_name[:index]
        brand = self.brands.get(product_link)
        if not brand:
            for brand_name in self.brands_for_title:
                if product_name.startswith(brand_name):
                    brand = brand_name
            if not brand:
                brand = 'Global Pet Foods'
        breadcrumb = response.meta.get('category')
        regular_price = response.xpath('//span[@class="current-price"]/text()').get()
        regular_price = regular_price[3:]
        discounted_price = None
        average_rating = None
        num_reviews = None
        size_with_unit = response.xpath('//label[contains(text(), "Weight")]/parent::div/following-sibling::div/text()').get()
        image_link = response.xpath('//div[@class="main-item"]/img/@src').get()
        size = response.xpath('//div[@class="size-box"]/h3/text()').get()
        weight_pattern = r'[0-9]*\.?[0-9]+ ?-?(g|ml|kg|mL|oz|lb|L|mg|gram)'
        if size:
            size = size[7:]
            weight_match = re.match(weight_pattern, size, flags=re.IGNORECASE)
            if weight_match:
                size_with_unit = weight_match.group()
            else:
                size_without_unit = size
        elif not size:
            size = response.xpath('//label[contains(text(), "Size")]/parent::div/following-sibling::div/text()').get()
            weight_match = re.match(weight_pattern, size)
            if weight_match:
                size_with_unit = weight_match.group()
            else:
                size_without_unit = size
        stock_level = response.xpath('//button[@class="btn add-cart-btn"]').get()
        if stock_level:
            stock_level = 'In_Stock'
        else:
            stock_level = 'Out_Of_Stock'
        description = response.xpath('//div[@id="description"]/div/div/p/text()').get()
        if size:
            if 'Breeds' in size:
                size = None
        if size:
            # pattern to find if size contains count/pack/-pk
            qty_pattern = r'[0-9]+ ?-?(pk|pack|count|ct)'
            qty_result = re.search(qty_pattern, size, re.IGNORECASE)
            if qty_result:
                # this pattern will extract solely the number for quantity
                count_pattern = r'[0-9]+'
                qty_count_result = re.search(count_pattern, qty_result.group())
                if discounted_price:
                    discounted_qty = qty_count_result.group()
                else:
                    regular_qty = qty_count_result.group()
        yield {
            'product_link': product_link,
            'product_name': product_name,
            'brand': brand, 
            'breadcrumb': breadcrumb,
            'size_without_unit': size_without_unit,
            'size_with_unit': size_with_unit,
            'dimension': dimension,
            'sku': None,
            'upc': None,
            'regular_price': regular_price,
            'regular_qty': regular_qty,
            'regular_unit': None,
            'discounted_price': discounted_price,
            'discounted_qty': discounted_qty,
            'discounted_unit': None,
            'currency': 'CAD',
            'average_rating': average_rating,
            'num_reviews': num_reviews,
            'shipped_by': None,
            'sold_by_third_party': 0, 
            'stock_level': stock_level,
            'online_only': False,
            'brief': None,
            'description': description,
            'image_link': image_link,
            'data_timestamp': self.data_timestamp,
            'data_year_month': self.data_year_month, 
            'retailer_code': None,
            }

