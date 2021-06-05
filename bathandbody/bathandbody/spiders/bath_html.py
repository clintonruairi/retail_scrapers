import scrapy
import json
import time


class BathandbodyworksSpider(scrapy.Spider):
    name = 'bathandbodyworks'
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'cache-control': 'max-age=0',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
    }

    def start_requests(self):
        urls = ['https://www.bathandbodyworks.com/c/hand-soaps-sanitizers/all-hand-soaps?start=0&sz=10000&format=ajax',
                'https://www.bathandbodyworks.com/c/body-care/new-body-care?start=0&sz=10000&format=ajax&',
                'https://www.bathandbodyworks.com/c/body-care/customer-favorites?start=0&sz=10000&format=ajax',
                'https://www.bathandbodyworks.com/c/body-care/retired-fragrances?start=0&sz=10000&format=ajax',
                'https://www.bathandbodyworks.com/c/body-care/travel?start=0&sz=10000&format=ajax',
                'https://www.bathandbodyworks.com/c/body-care/all-bath-shower?start=0&sz=10000&format=ajax',
                'https://www.bathandbodyworks.com/c/body-care/all-moisturizers?start=0&sz=10000&format=ajax',
                'https://www.bathandbodyworks.com/c/body-care/all-fragrance?start=0&sz=10000&format=ajax',
                'https://www.bathandbodyworks.com/c/body-care/aromatherapy-body-care?start=0&sz=10000&format=ajax',
                'https://www.bathandbodyworks.com/c/body-care/mens-body-care?start=0&sz=10000&format=ajax',
                'https://www.bathandbodyworks.com/c/hand-soaps-sanitizers/all-hand-soaps?start=0&sz=10000&format=ajax',
                'https://www.bathandbodyworks.com/c/hand-soaps-sanitizers/all-hand-sanitizers?start=0&sz=10000&format=ajax',
                'https://www.bathandbodyworks.com/c/home-fragrance/new-home-fragrance?start=0&sz=10000&format=ajax',
                'https://www.bathandbodyworks.com/c/home-fragrance/white-barn-shop?start=0&sz=10000&format=ajax',
                'https://www.bathandbodyworks.com/c/home-fragrance/all-candles?start=0&sz=10000&format=ajax',
                'https://www.bathandbodyworks.com/c/home-fragrance/all-wallflowers?start=0&sz=10000&format=ajax',
                'https://www.bathandbodyworks.com/c/home-fragrance/room-sprays-mists?start=0&sz=10000&format=ajax',
                'https://www.bathandbodyworks.com/c/home-fragrance/car-fragrance?start=0&sz=10000&format=ajax'
                ]
        a = time.time()
        for url in urls:
            yield scrapy.Request(url=url,
                                 callback=self.parse_search_results,
                                 meta={
                                     'time': a
                                 },
                                 headers=self.headers
                            )

    def parse_search_results(self, response):
        time = response.meta.get('time')
        urls = response.xpath('//div[@class="product-cont"]/a/@href').getall()
        for url in urls:
            if '?cgid' in url:
                index = url.index('?cgid')
                url = url[:index]
            yield scrapy.Request(url=f'https://www.bathandbodyworks.com{url}',
                                 callback=self.parse_product_page,
                                 meta={
                                     'url': url,
                                     'time': time
                                 },
                                 headers=self.headers
                                 )

    def parse_product_page(self, response):
        product_info_json = response.xpath('//button[@id="add-to-cart"]/@data-tealium').get()
        all_info = json.loads(product_info_json)
        product_link = all_info.get('url')
        product_name = all_info.get('name')
        if ';' in product_name:
            product_name = product_name.replace(';', '')
        if '&eacute' in product_name:
            product_name = product_name.replace('&eacute', 'é')
        brand = all_info.get('brand')
        if brand == 'Aromatherapy':
            brand = "Bath and Body Works"
        elif not brand:
            brand = "Bath and Body Works"
        regular_price = all_info.get('original_price')
        discounted_price = all_info.get('price')
        if regular_price == discounted_price:
            discounted_price = None
            regular_price = float(regular_price)
        elif regular_price != discounted_price:
            regular_price = float(regular_price)
            discounted_price = float(discounted_price)
        category = f"home|{all_info.get('category')}|{all_info.get('subcategory')}"
        size = all_info.get('size')
        sku = all_info.get('sku')
        if not sku:
            sku = all_info.get('id')
        image_link = all_info.get('image')
        time = int(response.meta.get('time'))
        stock = response.xpath('//p[@class="in-stock-msg"]/text()').get()
        if stock:
            stock_level = 'In_Stock'
        elif not stock:
            stock_level = 'Out_Of_Stock'
        product_id = all_info.get('id')

        yield scrapy.Request(
            url=f'https://api.bazaarvoice.com/data/display/0.2alpha/product/summary?PassKey=caJ0Jm2EFIFZWkvXJU4Qql6r9tPhnBjOMGK8GFGkKwcbg&productid={product_id}&contentType=reviews&reviewDistribution=primaryRating&rev=0&contentlocale=en_US',
            callback=self.parse_reviews,
            meta={
                'time': time,
                'product_link': product_link,
                'product_name': product_name,
                'brand': brand,
                'category': category,
                'regular_price': regular_price,
                'discounted_price': discounted_price,
                'size': size,
                'image_link': image_link,
                'sku': sku,
                'stock_level': stock_level
            })

    def parse_reviews(self, response):
        current_time = int(response.meta.get('time'))
        product_link = response.meta.get('product_link')
        product_name = response.meta.get('product_name')
        brand = response.meta.get('brand')
        category = response.meta.get('category')
        regular_price = response.meta.get('regular_price')
        discounted_price = response.meta.get('discounted_price')
        size = response.meta.get('size')
        image_link = response.meta.get('image_link')
        sku = response.meta.get('sku')
        stock_level = response.meta.get('stock_level')
        reviews_json = json.loads(response.body)
        num_reviews = reviews_json.get('reviewSummary').get('numReviews')
        average_rating = reviews_json.get('reviewSummary').get('primaryRating').get('average')
        if not num_reviews:
            num_reviews = None
        if average_rating:
            average_rating = round(average_rating, 1)
        elif not average_rating:
            average_rating = None
        category = category.replace('-', ' ')
        yield {
                'product_link': product_link,
                'product_name': product_name,
                'brand': brand,
                'category': category,
                'regular_price': regular_price,
                'discounted_price': discounted_price,
                'price_unit': None,
                'size': size,
                'color': None,
                'flavor': None,
                'weight': None,
                'average_rating': average_rating,
                'num_reviews': num_reviews,
                'image_link': image_link,
                'sku': sku,
                'upc': None,
                'stock_level': stock_level,
                'sold_by_3rd_party': 0,
                'shipped_by': None,
                'data_timestamp': current_time,
                'data_year_month': time.strftime('%Y%m')
            }



