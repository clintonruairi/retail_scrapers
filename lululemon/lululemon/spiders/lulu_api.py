# canadian VPN needed?
import scrapy
import time
import json

class LululemonSpider(scrapy.Spider):
    name = 'lululemon_api'
    data_timestamp = int(time.time())
    data_year_month = time.strftime('%Y%m')


    def start_requests(self):
        # self.categories = {
        #     'womens-leggings/_/N-8s6': 'women|clothes|women_leggings',
        #     'jackets-and-hoodies-jackets/_/N-8s2': 'women|clothes|coats_jackets',
        #     'skirts-and-dresses-dresses/_/N-8s3': 'women|clothes|dresses',
        #     'womens-outerwear/_/N-8s4': 'women|clothes|hoodies_sweatshirts',
        #     'womens-joggers/_/N-8s7': 'women|clothes|joggers',
        #     'women-pants/_/N-7w0': 'women||clothes|pants',
        #     'women-maintops/_/N-815': 'women|clothes|shirts',
        #     'women-shorts/_/N-7we': 'women|clothes|shorts',
        #     'skirts-and-dresses-skirts/_/N-8sb': 'women|clothes|skirts',
        #     'women-socks/_/N-8sg': 'women|clothes|socks',
        #     'women-sports-bras/_/N-7vl': 'women|clothes|sportsbras',
        #     'women-sweaters-and-wraps/_/N-8se': 'women|clothes|sweaters',
        #     'tops-swim/_/N-8sf': 'women|clothes|swimsuits',
        #     'women-underwear/_/N-8sd': 'women|clothes|underwear',
        #     'whats-new/_/N-1z0xcuuZ8te': 'women|whats_new',
        #     'bestsellers/_/N-1z0xcuuZ8td': 'women|bestsellers',
        #     'loungewear/_/N-1z0xcuuZ8la': 'women|loungewear',
        #     'women/_/N-7vfZ1z0xssr': 'women|align_clothes',
        #     'women/_/N-7vfZ1z0xsuz': 'women|wunder_under_clothes',
        #     'women/_/N-1z0vlnkZ7vf': 'women|spring_clothes',
        #     'lab-collection/_/N-1z0xcuuZ8nk': 'women|lab_shop',
        #     'sale/_/N-1z0xcuuZ8t6': 'women|we_made_too_much',
        #     'bags/_/N-1z0xcuuZ8rd': 'women|accessories|bags',
        #     'gloves-mittens/_/N-1z0xcuuZ8pc': 'women|accessories|gloves_mittens',
        #     'hair-accessories/_/N-1z0xcuuZ8pk': 'women|accessories|hair_accessories',
        #     'hats/_/N-1z0xcuuZ8pg': 'women|accessories|hats',
        #     'scarves-wraps/_/N-1z0xcuuZ8pi': 'women|accessories|scarves_wraps',
        #     'water-bottles/_/N-8pe': 'women|accessories|water_bottles',
        #     'yoga-accessories/_/N-8pd': 'women|accessories|yoga_accessories',
        #     'yoga-mats/_/N-8pj': 'women|accessories|yoga_mats',
        #     'women/yoga/_/N-7vfZ1z141d0': 'women|clothes|yoga',
        #     'women/running/_/N-7vfZ1z13zha': 'women|clothes|running',
        #     'women/training/_/N-7vfZ1z13z6f': 'women|clothes|training',
        #     'women/workout/_/N-7vfZ1z0xhwe': 'women|clothes|workout',
        #     'women/casual/_/N-7vfZ1z0xms0': 'women|clothes|casual',
        #     'women/golf/_/N-7vfZ1z13nap': 'women|clothes|golf',
        #     'whats-new/_/N-1z0xcmkZ8te': 'men|whats_new',
        #     'bestsellers/_/N-1z0xcmkZ8td': 'men|bestsellers',
        #     'loungewear/_/N-1z0xcmkZ8la': 'men|loungewear',
        #     'men/_/N-1z0xq2zZ7tu': 'men|anti_ball_crushing_clothes',
        #     'men/_/N-7tuZ1z0xsva': 'men|metal_vent_tech_clothes',
        #     'men/_/N-1z0vlnkZ7tu': 'men|spring_clothes',
        #     'lab-collection/_/N-1z0xcmkZ8nk': 'men|lab_shop',
        #     'sale/_/N-1z0xcmkZ8t6': 'men|we_made_too_much',
        #     'men-joggers/_/N-8rt': 'men|joggers',
        #     'mens-button-down-shirts/_/N-8o7': 'men|button_down_shirts',
        #     'mens-jackets-and-outerwear/_/N-8rm': 'men|coats_jackets',
        #     'mens-jackets-and-hoodies-hoodies/_/N-8rn': 'men|hoodies_sweatshirts',
        #     'men-pants/_/N-7ub': 'men|pants',
        #     'mens-polos/_/N-8kx': 'men|polo_shirts',
        #     'men-tops/_/N-87x': 'men|shirts',
        #     'men-shorts/_/N-7u7': 'men|shorts',
        #     'men-socks/_/N-8s1': 'men|socks',
        #     'mens-swim/_/N-8ru': 'men|swim_trunks',
        #     'mens-tanks/_/N-8ao': 'men|tank_tops',
        #     'mens-trousers/_/N-8rq': 'men|trousers',
        #     'mens-t-shirts/_/N-8ps': 'men|t-shirts',
        #     'men-underwear/_/N-8rv': 'men|underwear',
        #     'bags/_/N-1z0xcmkZ8rd': 'men|accessories|bags',
        #     'gloves-mittens/_/N-1z0xcmkZ8pc': 'men|accessories|gloves_mittens',
        #     'hair-accessories/_/N-1z0xcmkZ8pk': 'men|accessories|hair_accessories',
        #     'hats/_/N-1z0xcmkZ8pg': 'men|accessories|hats',
        #     'men/running/_/N-7tuZ1z13zha': 'men|clothes|running',
        #     'men/training/_/N-7tuZ1z13z6f': 'men|clothes|training',
        #     'men/golf/_/N-7tuZ1z13nap': 'men|clothes|golf',
        #     'men/casual/_/N-7tuZ1z0xms0': 'men|clothes|casual',
        #     'men/yoga/_/N-7tuZ1z141d0': 'men|clothes|yoga',
        #     'men/workout/_/N-7tuZ1z0xhwe': 'men|clothes|workout',
        #     'whats-new/_/N-1z0xb9pZ8te': 'accessories|whats_new',
        #     'selfcare/_/N-8si': 'accessories|selfcare',
        #     'sale/_/N-1z0xb9pZ8t6': 'accessories|we_made_too_much',
        #     'bags/_/N-8rd': 'accessories|bags',
        #     'accessories/yoga/_/N-8pbZ1z141d0': 'accessories|yoga_accessories',
        #     'accessories/running/_/N-8pbZ1z13zha': 'accessories|running_accessories',
        #     'accessories/training/_/N-8pbZ1z13z6f': 'accessories|training_accessories',
        #     'accessories/workout/_/N-8pbZ1z0xhwe': 'accessories|workout_accessories',
        #     'accessories/casual/_/N-8pbZ1z0xms0': 'accessories|casual_accessories',
        #     'accessories/golf/_/N-8pbZ1z13nap': 'accessories|golf_accessories'
        # }
        self.categories = {
            'womens-leggings/_/N-8r6': 'women|clothes|womens leggings',
            'jackets-and-hoodies-jackets/_/N-8qy': 'women|clothes|coats jackets',
            'skirts-and-dresses-dresses/_/N-8c8': 'women|clothes|skirts dresses',
            'womens-outerwear/_/N-8qz': 'women|clothes|hoodies sweatshirts',
            'women-pants/_/N-8r2': 'women|clothes|pants',
            'women-maintops/_/N-88w': 'women|clothes|shirts',
            'women-shorts/_/N-8r9': 'women|clothes|shorts',
            'kirts-and-dresses-skirts/_/N-8ra': 'women|clothes|skirts',
            'women-socks/_/N-8rc': 'women|clothes|socks',
            'women-sports-bras/_/N-7zd': 'women|clothes|sorts bras',
            'women-sweaters-and-wraps/_/N-8r0': 'women|clothes|sweaters',
            'tops-swim/_/N-8r1': 'women|clothes|swimsuits',
            'women-tanks/_/N-891': 'women|clothes|tank tops',
            'women-underwear/_/N-8qx': 'women|clothes|underwear',
            'women/yoga/_/N-7z5Z1z141d0': 'women|clothes|yoga',
            'women/running/_/N-7z5Z1z13zha': 'women|clothes|running',
            'women/bike/_/N-7z5Z1z140nz': 'women|clothes|bike clothes',
            'women/workout/_/N-7z5Z1z0xhwe': 'women|clothes|workout',
            'women/casual/_/N-7z5Z1z0xms0': 'women|clothes|casual',
            'women/golf/_/N-7z5Z1z13nap': 'women|clothes|golf',
            'men-joggers/_/N-8qi': 'men|clothes|joggers',
            'mens-button-down-shirts/_/N-8o6': 'men|clothes|button down shirts',
            'mens-jackets-and-hoodies-jackets/_/N-8qm': 'men|clothes|coats jackets',
            'mens-jackets-and-hoodies-hoodies/_/N-8qo': 'men|clothes|hoodies sweatshirts',
            'men-pants/_/N-7qy': 'men|clothes|pants',
            'mens-polos/_/N-8kw': 'men|clothes|polo shirts',
            'men-tops/_/N-87a': 'men|clothes|shirts',
            'men-shorts/_/N-7qz': 'men|clothes|shorts',
            'men-socks/_/N-8qv': 'men|clothes|socks',
            'mens-swim/_/N-8ql': 'men|clothes|swim trunks',
            'mens-tanks/_/N-8a5': 'men|clothes|tank tops',
            'mens-trousers/_/N-8qg': 'men|clothes|trousers',
            'mens-t-shirts/_/N-8p1': 'men|clothes|t shirts',
            'men-underwear/_/N-8qk': 'men|clothes|underwear',
            'men/running/_/N-7qrZ1z13zha': 'men|clothes|running',
            'men/training/_/N-7qrZ1z13z6f': 'men|clothes|training',
            'men/golf/_/N-7qrZ1z13nap': 'men|clothes|golf',
            'men/casual/_/N-7qrZ1z0xms0': 'men|clothes|casual',
            'men/yoga/_/N-7qrZ1z141d0': 'men|clothes|yoga',
            'men/workout/_/N-7qrZ1z0xhwe': 'men|clothes|workout',
            'bags/_/N-8q8': 'accessories|bags',
            'gloves-mittens/_/N-8or': 'accessories|gloves mittens',
            'hair-accessories/_/N-8os': 'accessories|hair accessories',
            'hats/_/N-8on': 'accessories|hats',
            'scarves-wraps/_/N-8op': 'accessories|scarves wraps',
            'water-bottles/_/N-8ot': 'accessories|water bottles',
            'yoga-accessories/_/N-8oo': 'accessories|yoga',
            'yoga-mats/_/N-8om': 'accessories|yoga mats',
            'selfcare/_/N-8q9': 'accessories|selfcare',
            'whats-new/_/N-1z0xcuuZ8tc': 'women|whats new',
            'bestsellers/_/N-1z0xcuuZ8tb': 'women|bestsellers',
            'loungewear/_/N-1z0xcuuZ8ss': 'women|loungewear',
            'women/_/N-7z5Z1z0xssr': 'women|align shop',
            'women/_/N-7z5Z1z0xsuz': 'women|wunder under shop',
            'women/_/N-1z0vlnkZ7z5': 'women|spring clothes shop',
            'lab-collection/_/N-1z0xcuuZ8nl': 'women|lululemon lab',
            'sale/_/N-1z0xcuuZ8t5': 'women|we made too much',
            'whats-new/_/N-1z0xcmkZ8tc': 'men|whats new',
            'loungewear/_/N-1z0xcmkZ8ss': 'men|loungewear',
            'men/_/N-1z0xq2zZ7qr': 'men|abc shop',
            'men/_/N-7qrZ1z0xsva': 'men|metal vent tech shop',
            'men/_/N-1z0vlnkZ7qr': 'men|spring clothes shop',
            'lab-collection/_/N-1z0xcmkZ8nl': 'men|lululemon lab',
            'sale/_/N-1z0xcmkZ8t5': 'men|we made too much',
            'whats-new/_/N-1z0xb9pZ8tc': 'accessories|whats new',
            'bestsellers/_/N-1z0xb9pZ8tb': 'accessories|bestsellers',
            'sale/_/N-1z0xb9pZ8t5': 'accessories|we made too much'

        }
        self.headers = {
            'Cookie': 'UsrLocale=en_CA;'
        }
        for cat, crumbs in self.categories.items():
            self.category_endpoint = f'https://shop.lululemon.com/api/c/{cat}?page=1&page_size=1000'
            yield scrapy.Request(
                                url=self.category_endpoint,
                                headers=self.headers,
                                callback=self.parse_category,
                                meta={
                                    'crumbs': crumbs
                                }
                        )

    def parse_category(self, response):
        crumbs = response.meta.get('crumbs')
        result = json.loads(response.body)
        for product in result.get("data").get("attributes").get("main-content")[0].get("records"):
            name = product.get("display-name")
            sub_category = product.get("parent-category-unified-id")
            brand = 'Lululemon'
            product_link = f'https://shop.lululemon.com{product.get("pdp-url")}'
            api_link = f'https://shop.lululemon.com/api{product.get("pdp-url")}'
            bazaar_id = product.get('bazaar-voice-id')
            review_endpoint = f"https://api.bazaarvoice.com/data/batch.json?passkey=caOGkxt5ZGxRUy0oZU3zbSlV36IBwxAijWghipc2FSoQY&apiversion=5.5&displaycode=7834-en_us&resource.q0=reviews&filter.q0=isratingsonly%3Aeq%3Afalse&filter.q0=productid:eq:{bazaar_id}&filter.q0=contentlocale%3Aeq%3Aen_US&sort.q0=submissiontime%3Adesc&stats.q0=reviews&filteredstats.q0=reviews&include.q0=authors%2Cproducts%2Ccomments&filter_reviews.q0=contentlocale%3Aeq%3Aen_US&filter_reviewcomments.q0=contentlocale%3Aeq%3Aen_US&filter_comments.q0=contentlocale%3Aeq%3Aen_US&limit.q0=30&offset.q0=0&limit_comments.q0=3"
            review_headers = {
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
                'Connection': 'keep-alive',
                'Host': 'api.bazaarvoice.com',
                'Referer': 'https://shop.lululemon.com/',
                'sec-ch-ua': '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'Sec-Fetch-Dest': 'script',
                'Sec-Fetch-Mode': 'no-cors',
                'Sec-Fetch-Site': 'cross-site',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36'
            }
            yield scrapy.Request(
                url=review_endpoint,
                headers=review_headers,
                callback=self.parse_review,
                meta={
                    'name': name,
                    'sub_category': sub_category,
                    'brand': brand,
                    'api_link': api_link,
                    'product_link': product_link,
                    "product": product,
                    'bazaar_id': bazaar_id,
                    'crumbs': crumbs
                }
            )
    
    def parse_review(self, response):
        crumbs = response.meta.get('crumbs')
        result = json.loads(response.body)
        bazaar_id = response.meta.get('bazaar_id')
        product_link = response.meta.get('product_link')
        name = response.meta.get('name').strip()
        sub_category = response.meta.get('sub_category')
        brand = response.meta.get('brand')
        api_link = response.meta.get('api_link')
        try:
            reviews = result.get("BatchedResults").get('q0').get('TotalResults')
            rating = result.get("BatchedResults").get('q0').get('Includes').get('Products').get(bazaar_id).get('ReviewStatistics').get('AverageOverallRating')
            rating = round(rating, 1)
        except AttributeError:
            reviews = None
            rating = None
        
        yield scrapy.Request(
                            url=api_link,
                            headers=self.headers,
                            callback=self.parse_product,
                            meta={
                                'product_link':product_link,
                                'name': name,
                                'sub_category': sub_category,
                                'brand': brand,
                                'api_link': api_link,
                                'reviews': reviews,
                                'rating': rating,
                                'crumbs': crumbs
                            }
                        )

            
    def parse_product(self, response):
        website = 'https://shop.lululemon.com'
        result = json.loads(response.body)
        crumbs = response.meta.get('crumbs')
        breadcrumb = f'home|{crumbs}'
        average_rating = response.meta.get('rating')
        num_reviews = response.meta.get('reviews')
        product_link = response.meta.get('product_link')
        un_name = response.meta.get('name').strip()
        name = un_name.replace('*', '')
        brand = response.meta.get('brand')
        description = result.get('data').get('attributes').get('product-summary').get('why-we-made-this')
        if description:
            description = " ".join(description.split())
            description = description.replace('&mdash', '')
        else:
            try:
                description = result.get('data').get('attributes').get('whyWeMadeThis').get('text')
                description = " ".join(description.split())
                description = description.replace('&mdash', '')
            except:
                description = None
        for variant in result.get('data').get('attributes').get('child-skus'):
            size_without_unit = variant.get('size')
            currency = variant.get('price-details').get('currency-code')
            print(f'currency\n\n{currency}\n\n')
            color_code = variant.get('color-code')
            for item in result.get('data').get('attributes').get('product-carousel'):
                    if item.get('color-code') == variant['color-code']:
                        color = item.get('swatch-color-name')
                        image_link  = item.get('image-info')[0] 
                        break
            sku = variant.get('id')
            in_stock = variant.get('available')
            if in_stock:
                stock_level = 'In_Stock'
            else:
                stock_level = 'Out_Of_Stock'
            try:
                discounted_price = variant.get('price-details').get('sale-price')
            except:
                discounted_price = None
            regular_price = variant.get('price-details').get('list-price')
            product_id = result.get('data').get('attributes').get('product-summary').get('pdp-url')
            product_link = f'{website}{product_id}?color={color_code}&sz={size_without_unit}'
            product_name = name.strip()

            yield {
            'product_link': product_link,
            'product_name': product_name,
            'brand': brand, 
            'breadcrumb': breadcrumb,
            'size_without_unit': size_without_unit,
            'size_with_unit': None,
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
            'retailer_code': None
        }


