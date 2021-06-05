# needs canadian vpn
import scrapy
import time

class ScholHtmlSpider(scrapy.Spider):
    name = 'schol_html'
    brand = 'Scholars Choice'
    time_now = int(time.time())
    data_year_month = time.strftime('%Y%m')
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
    }
    requested_skus = []

    def start_requests(self):
        home = 'https://www.scholarschoice.ca/'
        yield scrapy.Request(
            url=home,
            callback=self.parse_for_categories,
            headers=self.headers
        )

    def parse_for_categories(self, response):
        links = response.xpath('//ul[@id="shop-container"]/li/a/@href').getall()
        names = response.xpath('//ul[@id="shop-container"]/li/a/span[1]/text()').getall()
        categories = dict(zip(links, names))
        for link, category in categories.items():
            yield scrapy.Request(
                                url=link,
                                callback=self.parse_category,
                                meta={
                                    'category': category
                                },
                                headers=self.headers
            )

    def parse_category(self, response):
        category = response.meta.get('category')
        links = response.xpath('//a[@class="product-item-link"]/@href').getall()
        skus = response.xpath('//div[@class="product product-item-sku"]/text()').getall()
        links_skus = dict(zip(links, skus))
        for link, sku in links_skus.items():
            if sku not in self.requested_skus:
                yield scrapy.Request(
                                    url=link,
                                    callback=self.parse_product,
                                    meta={
                                        'category': category
                                    },
                                    headers=self.headers
                )
                self.requested_skus.append(sku)
            else:
                continue

        next_page = response.xpath('//a[@class="action  next"]/@href').get()
        if next_page:
            yield scrapy.Request(
                url=next_page,
                callback=self.parse_category,
                headers=self.headers,
                meta={
                    'category': category
                }
            )
    
    def parse_product(self, response):
        product_link = response.url
        product_name = response.xpath('//h1/span/text()').get()
        if ';' in product_name:
            product_name = product_name.replace(';', '')
        if not product_name:
            return
        category = response.meta.get('category')
        category = f'Home|Shop|{category}'
        original_price = response.xpath('//span[@data-price-type="oldPrice"]/@data-price-amount').get()
        sale_price = response.xpath('//span[@data-price-type="specialPrice"]/@data-price-amount').get()
        regular_price = response.xpath('//span[@data-price-type="finalPrice"]/@data-price-amount').get()
        if original_price and sale_price:
            regular_price = float(original_price)
            discounted_price = float(sale_price)
        else:
            regular_price = float(regular_price)
            discounted_price = None
        sku = response.xpath('//div[@itemprop="sku"]/text()').get()
        num_reviews = response.xpath('//a[@class="text-m"]/@aria-label').get()
        if num_reviews:
            num_reviews = num_reviews.replace(' reviews', '')
            num_reviews = int(num_reviews)
        average_rating = response.xpath('//span[@class="sr-only"]/text()').get()
        if average_rating:
            average_rating = average_rating.replace(' star rating', '')
            average_rating = float(average_rating)
            if average_rating:
                average_rating = average_rating
            else:
                average_rating = None
        image_link = response.xpath('//meta[@property="og:image"]/@content').get()
        if ';' in image_link:
            return
        in_stock = response.xpath('//i[@class="icon check"]').get()
        if in_stock:
            stock_level = 'In_Stock'
        else:
            stock_level = 'Out_Of_Stock'
        yield {
            'product_link': product_link,
            'product_name': product_name, 
            'brand': self.brand, 
            'category': category,
            'regular_price': regular_price, 
            'discounted_price': discounted_price,
            'price_unit': None,
            'size': None,
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
            'data_timestamp': self.time_now,
            'data_year_month': self.data_year_month
            }

