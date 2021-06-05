# no vpn needed
import scrapy
import re
import time
import json


class GapHtmlSpider(scrapy.Spider):
    name = 'gap_html'
    allowed_domains = ['gapcanada.ca']
    start_urls = ['http://gapcanada.ca/']
    time_now = int(time.time())
    data_year_month = time.strftime('%Y%m')

    def start_requests(self):
        categories = [
            '1127938', '1140272','1065871', '1127956', '72485', '1021874',
            '1020009', '1127944', '1065870', '1127146', '1138967', '1177961',
            '1177962', '1127946', '1065850', '1127945', '1065844', '1127952',
            '1127955', '1065851', '1065853', '1127947', '1127948', '1065857',
            '1065859', '1157839', '1157843', '1035086', '1078169', '1026609',
            '1026616'
        ]
        headers = {
            'apikey': 'sUUYuywr9UU9HK8vYHJau88omwJoxQhs'
        }
        for code in categories:
            link = f'https://api.gap.com/ux/web/productdiscovery-web-experience/products/ca/gap?cid={code}&locale=en_CA&isFacetsEnabled=true&globalShippingCountryCode=ca&globalShippingCurrencyCode=CAD&resId=916981618124708&abSeg=%7B%22brand%22%3A%22gap%22%2C%22gap01%22%3A%22a%22%2C%22gap02%22%3A%22a%22%2C%22gap03%22%3A%22a%22%2C%22gap04%22%3A%22a%22%2C%22gap06%22%3A%22a%22%2C%22gap07%22%3A%22a%22%2C%22gap11%22%3A%22a%22%2C%22gap21%22%3A%22a%22%2C%22gap22%22%3A%22a%22%2C%22gap27%22%3A%22a%22%2C%22gap28%22%3A%22a%22%2C%22gap36%22%3A%22a%22%2C%22gap43%22%3A%22a%22%2C%22pgBRCA%22%3A%22p%22%2C%22pgGPCA%22%3A%22p%22%2C%22v%22%3A%222%22%7D&pageId=0'
            yield scrapy.Request(
                            url=link,
                            callback=self.parse_category,
                            meta={
                                'code': code
                            },
                            headers=headers
                )

    def parse_category(self, response):
        resp = json.loads(response.text)
        product_list = resp.get('productCategoryFacetedSearch').get('productCategory').get('childProducts')
        backup_category = resp.get('productCategoryFacetedSearch').get('productCategory').get('name')
        if not product_list:
            try:
                product_list = resp.get('productCategoryFacetedSearch').get('productCategory').get('childCategories')[0].get('childProducts')
                backup_category = resp.get('productCategoryFacetedSearch').get('productCategory').get('name')
            except Exception as e:
                print(e)
                product_list = resp.get('productCategoryFacetedSearch').get('productCategory').get('childCategories').get('childProducts')
                backup_category = resp.get('productCategoryFacetedSearch').get('productCategory').get('name')
        for product in product_list:
            product_code = product.get('businessCatalogItemId')
            link = f'https://www.gapcanada.ca/browse/product.do?pid={product_code}'
            yield scrapy.Request(
                                url=link,
                                callback=self.parse_product,
                                meta={
                                    'link': link, # only needed if they notice I'm not picking up variants. link += vid=1/2/3
                                    'sku': product_code,
                                    'backup_category': backup_category
                                }
            )
        headers = {
            'apikey': 'sUUYuywr9UU9HK8vYHJau88omwJoxQhs'
        }
        code = response.meta.get('code')
        number_of_pages = int(resp.get('productCategoryFacetedSearch').get('productCategory').get('productCategoryPaginator').get('pageNumberTotal'))
        if number_of_pages > 1:
            for i in range(1, number_of_pages):
                link = f'https://api.gap.com/ux/web/productdiscovery-web-experience/products/ca/gap?cid={code}&locale=en_CA&isFacetsEnabled=true&globalShippingCountryCode=ca&globalShippingCurrencyCode=CAD&resId=916981618124708&abSeg=%7B%22brand%22%3A%22gap%22%2C%22gap01%22%3A%22a%22%2C%22gap02%22%3A%22a%22%2C%22gap03%22%3A%22a%22%2C%22gap04%22%3A%22a%22%2C%22gap06%22%3A%22a%22%2C%22gap07%22%3A%22a%22%2C%22gap11%22%3A%22a%22%2C%22gap21%22%3A%22a%22%2C%22gap22%22%3A%22a%22%2C%22gap27%22%3A%22a%22%2C%22gap28%22%3A%22a%22%2C%22gap36%22%3A%22a%22%2C%22gap43%22%3A%22a%22%2C%22pgBRCA%22%3A%22p%22%2C%22pgGPCA%22%3A%22p%22%2C%22v%22%3A%222%22%7D&pageId={i}'
                yield scrapy.Request(
                                    url=link,
                                    callback=self.parse_category_deeper,
                                    headers=headers
                )

    def parse_category_deeper(self, response):
        resp = json.loads(response.text)
        product_list = resp.get('productCategoryFacetedSearch').get('productCategory').get('childProducts')
        backup_category = resp.get('productCategoryFacetedSearch').get('productCategory').get('name')
        if not product_list:
            try:
                product_list = resp.get('productCategoryFacetedSearch').get('productCategory').get('childCategories')[0].get('childProducts')
                backup_category = resp.get('productCategoryFacetedSearch').get('productCategory').get('name')
            except Exception as e:
                print(e)
                product_list = resp.get('productCategoryFacetedSearch').get('productCategory').get('childCategories').get('childProducts')
                backup_category = resp.get('productCategoryFacetedSearch').get('productCategory').get('name')
        for product in product_list:
            product_code = product.get('businessCatalogItemId')
            link = f'https://www.gapcanada.ca/browse/product.do?pid={product_code}'
            yield scrapy.Request(
                                url=link,
                                callback=self.parse_product,
                                meta={
                                    'link': link, # only needed if they notice I'm not picking up variants. link += vid=1/2/3
                                    'sku': product_code,
                                    'backup_category': backup_category
                                }
            )

    def parse_product(self, response):
        backup_sku = response.meta.get('sku')
        product_name = response.xpath('//h1/text()').get()
        if '\x99' in product_name:
            product_name = product_name.replace('\x99', '™')
        brand = 'Gap'
        crumbs = response.xpath('//a[@class="product-breadcrumb__link"]/text()').getall()
        category = '|'.join(crumbs)
        category = f'Home|{category}'
        variant_sku_text = response.xpath('//script[@id="pdpData"]/text()').get()
        json_pattern = r'"{\\"name.+'
        result = re.search(json_pattern, variant_sku_text)
        text_for_json = result.group()
        product_info = json.loads(text_for_json)
        product_info = json.loads(product_info)
        product_info = product_info.get('productData')
        current_price = product_info.get('selectedColor').get('rawCurrentPrice')
        regular_price = product_info.get('selectedColor').get('rawRegularPrice')
        if current_price == regular_price:
            regular_price = current_price
            discounted_price = None
        else:
            regular_price = regular_price
            discounted_price = current_price
        color = product_info.get('selectedColor').get('colorName')
        num_reviews = response.xpath('//div[@class="pdp-mfe-13487st"]/text()').get()
        if num_reviews:
            num_reviews = num_reviews.replace(' Reviews', '')
            num_reviews = num_reviews.replace(' Review', '')
            num_reviews = int(num_reviews)
        average_rating = response.xpath('//div[@class="pdp-mfe-1wylm1o"]/div/@aria-label').get()
        if average_rating:
            if '0 Reviews' in average_rating:
                average_rating = None
            else:
                average_rating = average_rating.replace('Image of 5 stars, ', '')
                average_rating = average_rating.replace(' are filled', '')
                average_rating = float(average_rating)
        image_base = 'https://www.gapcanada.ca'
        relative_image = response.xpath('//a[@class="hover-zoom hover-zoom-in"]/img/@src').get()
        image_link = image_base + relative_image
        all_sizes = product_info.get('selectedColor').get('sizes')
        api_sizes = []
        sizes_on_page = response.xpath('//div[@class="pdp-mfe-1h21uo7 pdp-dimension pdp-dimension--unavailable"]/label/span/text()').getall()
        for variant in all_sizes:
            sku = variant.get('skuId')
            product_link = f'https://www.gapcanada.ca/browse/product.do?pid={sku}'
            in_stock = variant.get('inStock')
            if in_stock:
                stock_level = 'In_Stock'
            else:
                stock_level = 'Out_Of_Stock'
            size = variant.get('sizeDimension1')
            api_sizes.append(api_sizes)
            if category == 'Home|' or category == 'Home| ':
                if 'kids' in product_name.lower():
                    category = 'Home|Girls|New Arrivals'
                if 'Windbuster' in product_name.lower():
                    category = 'Home|Boys|Outerwear'
                if 'sock' in product_name.lower() or 'bandana' in product_name.lower():
                    category = 'Home|Womens|Shoes & Accessories'
                if 'teen' in product_name.lower():
                    category = 'Home|Teen Collection'
                if 'sweater' in product_name.lower():
                    category = 'Home|Boys|Sweaters'
                if 'https://www.gapcanada.ca/browse/product.do?pid=469241013' in product_link:
                    category = 'Home|Boys|Pants'
                if 'leggings' in product_name.lower():
                    category = 'Home|Girls|Leggings & Pants'
                if 'toddler' in product_name.lower():
                    category = 'Home|Todder|New Arrivals'
                if 'slide' in product_name.lower() or 'flip' in product_name.lower():
                    category = 'Home|Womens|New Arrivals'
                if 'baby' in product_name.lower():
                    category = 'Home|Baby|Mix & Match Favorites'
                else:
                    continue
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
        
        # for variant in sizes_on_page:
        #     if variant not in api_sizes:
        #         stock_level = 'Out_Of_Stock'
        #         size = variant
        #         product_link = response.url
        #         sku = backup_sku
        #         yield {
        #             'product_link': product_link,
        #             'product_name': product_name, 
        #             'brand': brand, 
        #             'category': category,
        #             'regular_price': regular_price, 
        #             'discounted_price': discounted_price,
        #             'price_unit': None,
        #             'size': size,
        #             'color': color,
        #             'flavor': None, 
        #             'weight': None, 
        #             'average_rating': average_rating, 
        #             'num_reviews': num_reviews, 
        #             'image_link': image_link,
        #             'sku': sku, 
        #             'upc': None,
        #             'stock_level': stock_level,
        #             'sold_by_3rd_party': 0,
        #             'shipped_by': None,
        #             'data_timestamp': self.time_now,
        #             'data_year_month': self.data_year_month
        #             }
        
        variants = product_info.get('selectedVariant').get('productStyleColors')
        for variant in variants:
            sub_dict = variant[0]
            product_code = sub_dict.get('businessCatalogItemId')
            url = f'https://www.gapcanada.ca/browse/product.do?pid={product_code}'
            yield scrapy.Request(
                                url=url,
                                callback=self.parse_variant,
                                meta={
                                    'sku': backup_sku
                                }
            )

    def parse_variant(self, response):
        backup_sku = response.meta.get('sku')
        product_name = response.xpath('//h1/text()').get()
        if '\x99' in product_name:
            product_name = product_name.replace('\x99', '™')
        brand = 'Gap'
        crumbs = response.xpath('//a[@class="product-breadcrumb__link"]/text()').getall()
        category = '|'.join(crumbs)
        category = f'Home|{category}'
        variant_sku_text = response.xpath('//script[@id="pdpData"]/text()').get()
        json_pattern = r'"{\\"name.+'
        result = re.search(json_pattern, variant_sku_text)
        text_for_json = result.group()
        product_info = json.loads(text_for_json)
        product_info = json.loads(product_info)
        product_info = product_info.get('productData')
        current_price = product_info.get('selectedColor').get('rawCurrentPrice')
        regular_price = product_info.get('selectedColor').get('rawRegularPrice')
        if current_price == regular_price:
            regular_price = current_price
            discounted_price = None
        else:
            regular_price = regular_price
            discounted_price = current_price
        color = product_info.get('selectedColor').get('colorName')
        num_reviews = response.xpath('//div[@class="pdp-mfe-13487st"]/text()').get()
        if num_reviews:
            num_reviews = num_reviews.replace(' Reviews', '')
            num_reviews = num_reviews.replace(' Review', '')
            num_reviews = int(num_reviews)
        average_rating = response.xpath('//div[@class="pdp-mfe-1wylm1o"]/div/@aria-label').get()
        if average_rating:
            if '0 Reviews' in average_rating:
                average_rating = None
            else:
                average_rating = average_rating.replace('Image of 5 stars, ', '')
                average_rating = average_rating.replace(' are filled', '')
                average_rating = float(average_rating)
        image_base = 'https://www.gapcanada.ca'
        relative_image = response.xpath('//a[@class="hover-zoom hover-zoom-in"]/img/@src').get()
        image_link = image_base + relative_image
        all_sizes = product_info.get('selectedColor').get('sizes')
        api_sizes = []
        sizes_on_page = response.xpath('//div[@class="pdp-mfe-1h21uo7 pdp-dimension pdp-dimension--unavailable"]/label/span/text()').getall()
        for variant in all_sizes:
            sku = variant.get('skuId')
            product_link = f'https://www.gapcanada.ca/browse/product.do?pid={sku}'
            in_stock = variant.get('inStock')
            if in_stock:
                stock_level = 'In_Stock'
            else:
                stock_level = 'Out_Of_Stock'
            size = variant.get('sizeDimension1')
            api_sizes.append(api_sizes)
            if category == 'Home|' or category == 'Home| ':
                if 'kids' in product_name.lower():
                    category = 'Home|Girls|New Arrivals'
                if 'Windbuster' in product_name.lower():
                    category = 'Home|Boys|Outerwear'
                if 'sock' in product_name.lower() or 'bandana' in product_name.lower():
                    category = 'Home|Womens|Shoes & Accessories'
                if 'teen' in product_name.lower():
                    category = 'Home|Teen Collection'
                if 'sweater' in product_name.lower():
                    category = 'Home|Boys|Sweaters'
                if 'https://www.gapcanada.ca/browse/product.do?pid=469241013' in product_link:
                    category = 'Home|Boys|Pants'
                if 'leggings' in product_name.lower():
                    category = 'Home|Girls|Leggings & Pants'
                if 'toddler' in product_name.lower():
                    category = 'Home|Todder|New Arrivals'
                if 'slide' in product_name.lower() or 'flip' in product_name.lower():
                    category = 'Home|Womens|New Arrivals'
                if 'baby' in product_name.lower():
                    category = 'Home|Baby|Mix & Match Favorites'
                else:
                    continue
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
        
        # for variant in sizes_on_page:
        #     if variant not in api_sizes:
        #         stock_level = 'Out_Of_Stock'
        #         size = variant
        #         product_link = response.url
        #         sku = backup_sku
        #         yield {
        #             'product_link': product_link,
        #             'product_name': product_name, 
        #             'brand': brand, 
        #             'category': category,
        #             'regular_price': regular_price, 
        #             'discounted_price': discounted_price,
        #             'price_unit': None,
        #             'size': size,
        #             'color': color,
        #             'flavor': None, 
        #             'weight': None, 
        #             'average_rating': average_rating, 
        #             'num_reviews': num_reviews, 
        #             'image_link': image_link,
        #             'sku': sku, 
        #             'upc': None,
        #             'stock_level': stock_level,
        #             'sold_by_3rd_party': 0,
        #             'shipped_by': None,
        #             'data_timestamp': self.time_now,
        #             'data_year_month': self.data_year_month
        #             }