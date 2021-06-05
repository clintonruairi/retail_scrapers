# no VPN needed
import scrapy
import time
import re
import json


class AritziaSpider(scrapy.Spider):
    name = 'aritzia'
    data_timestamp = int(time.time())
    data_year_month = time.strftime('%Y%m')

    def start_requests(self):
        category = {
            'https://www.aritzia.com/en/clothing/tshirts?start=0&sz=10000&format=ajax': 'home | clothing | t-shirts',
            'https://www.aritzia.com/en/clothing/bodysuits?start=0&sz=10000&format=ajax': 'home | clothing | bodysuits',
            'https://www.aritzia.com/en/clothing/blouses?start=0&sz=10000&format=ajax': 'home | clothing | blouses',
            'https://www.aritzia.com/en/clothing/sweaters?start=0&sz=10000&format=ajax': 'home | clothing | sweaters',
            'https://www.aritzia.com/en/clothing/pants?start=0&sz=10000&format=ajax': 'home | clothing | pants',
            'https://www.aritzia.com/en/clothing/jeans?start=0&sz=10000&format=ajax': 'home | clothing | denim',
            'https://www.aritzia.com/en/clothing/shorts?start=0&sz=10000&format=ajax': 'home | clothing | shorts',
            'https://www.aritzia.com/en/clothing/skirts?start=0&sz=10000&format=ajax': 'home | clothing | skirts',
            'https://www.aritzia.com/en/clothing/dresses?start=0&sz=10000&format=ajax': 'home | clothing | dresses',
            'https://www.aritzia.com/en/clothing/coats-jackets?start=0&sz=10000&format=ajax': 'home | clothing | coats-jackets',
            'https://www.aritzia.com/en/clothing/accessories?start=0&sz=10000&format=ajax': 'home | clothing | accessories',
            'https://www.aritzia.com/en/clothing/contour-clothing?start=0&sz=10000&format=ajax': 'home|features|contour_clothing',
            'https://www.aritzia.com/en/clothing/garment-dye?start=0&sz=10000&format=ajax': 'home | clothing | garment dye',
            'https://www.aritzia.com/en/clothing/faux-leather-clothes?start=0&sz=10000&format=ajax': 'home | clothing | vegan leather',
            'https://www.aritzia.com/en/clothing/shoulder-pad-tops-dresses?start=0&sz=10000&format=ajax': 'home | clothing | shoulder pads',
            'https://www.aritzia.com/en/clothing/womens-workout-clothes?start=0&sz=10000&format=ajax': 'home | clothing | active wear',
            'https://www.aritzia.com/en/clothing/sweatsuit-sets?start=0&sz=10000&format=ajax': 'home | clothing | sweatsuits',
            'https://www.aritzia.com/en/clothing/linen-clothing?start=0&sz=10000&format=ajax': 'home | clothing | linen',
            'https://www.aritzia.com/en/clothing/sale?start=0&sz=10000&format=ajax': 'home | clothing | sale',
            'https://www.aritzia.com/en/clothing/shoes?start=0&sz=10000&format=ajax': 'home | clothing | shoes',
        }
        for k, v in category.items():
            yield scrapy.Request(url=k,
                                 callback=self.parse_search_results,
                                 meta={'category': v}
                                 )

    def parse_search_results(self, response):
        urls = response.xpath('//div[@class="product-image js-product-plp-image tc"]/a/@href').getall()
        category = response.meta.get('category')
        for url in urls:
            pattern = r'https://www.aritzia.com/en/.+\?'
            result = re.findall(pattern, url)
            base_url = result[0]
            yield scrapy.Request(url=base_url,
                                 callback=self.parse_variants,
                                 meta={
                                     'category': category
                                       }
                                 )

    def parse_variants(self, response):
        lengths = response.xpath('//ul[@class="swatches-collection cf "]/li/a/@href').getall()
        category = response.meta.get('category')
        if lengths:
            for length in lengths:
                pattern = r'https://www.aritzia.com/en/product/variation\?pid=[0-9]+\&'
                result = re.findall(pattern, length)
                url = result[0]
                yield scrapy.Request(url=url,
                                     callback=self.parse_type,
                                     meta={
                                         'category': category
                                     }
                                )
        elif not lengths:
            brand = response.xpath('//div[@class="pdp-product-brand f0"]/a/text()').get()
            if not brand:
                brand = 'Aritzia Community'
            name = response.xpath('//h1[@class="pdp-product-name fl w-60"]/span[1]/text()').get()
            name = name.strip()
            unformatted_rating = response.xpath('//span[@id="TTreviewSummaryAverageRating"]/text()').get()
            reviews = response.xpath('//input[@id="ttReviewCount"]/@value').get()
            if unformatted_rating:
                rating = unformatted_rating[:4].strip()
            else:
                rating = None
                reviews = None
            sku_script = response.xpath('//*[@id="primary"]/script[2]/text()').get()
            pattern = '"[0-9]+"'
            sku_result = re.findall(pattern, sku_script)[0]
            sku = ''
            for letter in sku_result:
                if letter != '"':
                    sku += letter
            colors = response.xpath('//ul[@class="swatches swatches-color clearfix"]/li/div/a/@href').getall()
            for variant in colors:
                yield scrapy.Request(url=variant,
                                     callback=self.yield_variant,
                                     meta={
                                         'brand': brand,
                                         'name': name,
                                         'rating': rating,
                                         'reviews': reviews,
                                         'sku': sku,
                                         'link': variant,
                                         'category': category
                                     })

    def parse_type(self, response):
        brand = response.xpath('//div[@class="pdp-product-brand f0"]/a/text()').get()
        name = response.xpath('//img[@class="ar-product-images__image-media js-product-images__image-media lazyr lazy"][1]/@title').get()
        name = name.strip()
        unformatted_rating = response.xpath('//span[@id="TTreviewSummaryAverageRating"]/text()').get()
        reviews = response.xpath('//input[@id="ttReviewCount"]/@value').get()
        category = response.meta.get('category')
        if unformatted_rating:
            rating = unformatted_rating[:4].strip()
        else:
            rating = None
            reviews = None
        sku_script = response.xpath('//*[@id="primary"]/script[2]/text()').get()
        pattern = '"[0-9]+"'
        sku_result = re.findall(pattern, sku_script)[0]
        sku = ''
        for letter in sku_result:
            if letter != '"':
                sku += letter
        colors = response.xpath('//ul[@class="swatches swatches-color clearfix"]/li/div/a/@href').getall()
        for variant in colors:
            yield scrapy.Request(url=variant,
                                 callback=self.yield_variant,
                                 meta={
                                     'brand': brand,
                                     'name': name,
                                     'rating': rating,
                                     'reviews': reviews,
                                     'sku': sku,
                                     'link': variant,
                                     'category': category
                                 })

    def yield_variant(self, response):
        length = None
        brand = response.meta.get('brand')
        product_name = response.meta.get('name')
        sku = response.meta.get('sku')
        length = response.xpath('//a[@class="dib ba ph2 selected white bg-true-black b--true-black"]/span/text()').get()
        product_link = response.meta.get('link')
        breadcrumb = response.meta.get('category')
        unformatted_price = response.xpath('//span[@class="price-default"]/span/text()').get()
        if not unformatted_price:
            regular_price = response.xpath('//span[@class="price-standard strike dib"]/span/text()').get()[1::]
            regular_price = float(regular_price)
            discounted_price = response.xpath('//span[@class="price-sales red"]/span/text()').get()[1::]
            discounted_price = float(discounted_price)
        else:
            regular_price = unformatted_price[1::]
            discounted_price = None
        rating = response.meta.get('rating')
        reviews = response.meta.get('reviews')
        if rating and reviews:
            average_rating = float(rating)
            num_reviews = int(reviews)
        color = response.xpath('//span[@class="label ttc"]/@data-current-variation').get()
        image_link = response.xpath('//a[@class="ar-product-images__image-link js-product-images__image-link db"][1]/@href').get()
        unavailable_sizes = response.xpath('//li[@class=" unavailable" or @class="unavailable"]/a/@title').getall()
        available_sizes = response.xpath('//ul[@class="swatches swatches-size js-swatches__size cf mb3 mb0-ns"]/li[not(@class="unavailable" or @class=" unavailable")]/a/@title').getall()
        description = response.xpath('//div[@class="js-product-accordion__content f0 mb3 pb2 cf"]/p/text()').get()
        if unavailable_sizes:
            for size in unavailable_sizes:
                size_without_unit = size.strip()
                yield {
                    'product_link': product_link,
                    'product_name': product_name,
                    'brand': brand, 
                    'breadcrumb': breadcrumb,
                    'size_without_unit': size_without_unit,
                    'size_with_unit': None,
                    'dimension': None,
                    'length': length,
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
                    'average_rating': average_rating,
                    'num_reviews': num_reviews,
                    'shipped_by': None,
                    'sold_by_third_party': 0, 
                    'stock_level': 'Out_Of_Stock',
                    'online_only': True,
                    'brief': None,
                    'description': description,
                    'image_link': image_link,
                    'data_timestamp': self.data_timestamp,
                    'data_year_month': self.data_year_month, 
                    'retailer_code': None,
                }
        if available_sizes:
            for size in available_sizes:
                size_without_unit = size.strip()
                yield {
                    'product_link': product_link,
                    'product_name': product_name,
                    'brand': brand, 
                    'breadcrumb': breadcrumb,
                    'size_without_unit': size_without_unit,
                    'size_with_unit': None,
                    'dimension': None,
                    'length': length,
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
                    'average_rating': average_rating,
                    'num_reviews': num_reviews,
                    'shipped_by': None,
                    'sold_by_third_party': 0, 
                    'stock_level': 'In_Stock',
                    'online_only': True,
                    'brief': None,
                    'description': description,
                    'image_link': image_link,
                    'data_timestamp': self.data_timestamp,
                    'data_year_month': self.data_year_month, 
                    'retailer_code': None,
                }













