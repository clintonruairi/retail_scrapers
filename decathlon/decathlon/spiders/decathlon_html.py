# no vpn needed.
import scrapy
import time
from urllib.parse import urlencode
from scrapy import Request, FormRequest
import json
import requests
import re


class DecathlonSpider(scrapy.Spider):
    name = 'decathlon_html'
    data_timestamp = int(time.time())
    data_year_month = time.strftime('%Y%m')

    def start_requests(self):

        categories = {
            "14503": ["Women", "Activewear", "Shirts & Tops"],
            "14500": ["Women", "Activewear", "Fleeces, Hoodies & Sweaters"],
            "14502": ["Women", "Activewear", "Pants & Leggings"],
            "14501": ["Women", "Activewear", "Short pants, Skirts"],
            "14489": ["Women", "Activewear", "Sport Bras & Underwear"],
            "14488": ["Women", "Activewear", "Base layers"],
            "14490": ["Women", "Activewear", "Socks"],
            "14498": ["Women", "Jackets & Vests", "Raincoats & Wind-stoppers"],
            "14497": ["Women", "Jackets & Vests", "Down Jackets"],
            "14495": ["Women", "Jackets & Vests", "Vests"],
            "14496": ["Women", "Jackets & Vests", "Winter Jackets"],
            "14508": ["Women", "Footwear", "Sport Shoes"],
            "14507": ["Women", "Footwear", "Hiking Shoes"],
            "14506": ["Women", "Footwear", "Boots"],
            "14505": ["Women", "Footwear", "Sandals & Flipflops"],
            "14504": ["Women", "Footwear", "Water Shoes"],
            "14509": ["Women", "Footwear", "Crampons"],
            "14491": ["Women", "Swimwear", "Swimsuits"],
            "14493": ["Women", "Swimwear", "UV tops"],
            "14492": ["Women", "Swimwear", "Wetsuits"],
            "14484": ["Women", "Accessories", "Hats & Caps"],
            "14485": ["Women", "Accessories", "Glasses"],
            "14486": ["Women", "Accessories", "Neck warmer, Scarfs"],
            "14483": ["Women", "Accessories", "Gloves"],
            "14482": ["Women", "Accessories", "Belts"],
            "14458": ["Men", "Activewear", "Shirts & Tops"],
            "14456": ["Men", "Activewear", "Fleeces, Hoodies & Sweaters"],
            "14457": ["Men", "Activewear", "Pants_OverTrousers_Tights"],
            "14460": ["Men", "Activewear", "Underwear"],
            "14461": ["Men", "Activewear", "BaseLayers"],
            "14462": ["Men", "Activewear", "Socks"],
            "14478": ["Men", "Jackets & Vests", "Raincoats & Wind-stoppers"],
            "14480": ["Men", "Jackets & Vests", "Down Jackets"],
            "14481": ["Men", "Jackets & Vests", "Vests"],
            "14479": ["Men", "Jackets & Vests", "Winter Jackets"],
            "14476": ["Men", "Footwear", "Sport Shoes"],
            "14472": ["Men", "Footwear", "Hiking Shoes"],
            "14474": ["Men", "Footwear", "Boots"],
            "14473": ["Men", "Footwear", "Sandals & Flipflops"],
            "14475": ["Men", "Footwear", "Water Shoes"],
            "14471": ["Men", "Footwear", "Crampons"],
            "14464": ["Men", "Swimwear", "Swimsuits"],
            "14465": ["Men", "Swimwear", "UV tops"],
            "14463": ["Men", "Swimwear", "Wetsuits"],
            "14470": ["Men", "Accessories", "Hats & Caps"],
            "14466": ["Men", "Accessories", "Glasses"],
            "14467": ["Men", "Accessories", "Neck warmer, Scarfs"],
            "14468": ["Men", "Accessories", "Gloves"],
            "14469": ["Men", "Accessories", "Belts"],
            "14516": ["Kids", "Babies-Toddlers-1-6", "Clothes & Jackets"],
            "14517": ["Kids", "Babies-Toddlers-1-6", "Shoes & Socks"],
            "14518": ["Kids", "Babies-Toddlers-1-6", "Swimwear"],
            "14519": ["Kids", "Babies-Toddlers-1-6", "UV Protection"],
            "14525": ["Kids", "Activewear-6+", "Shirts & Tops"],
            "14527": ["Kids", "Activewear-6+", "Fleeces, Hoodies & Sweaters"],
            "14526": ["Kids", "Activewear-6+", "Pants & Leggings"],
            "14528": ["Kids", "Activewear-6+", "Shorts, Skirts, Bermudas"],
            "14529": ["Kids", "Activewear-6+", "Tracksuits"],
            "14521": ["Kids", "Activewear-6+", "Underwear,Socks & BaseLayers"],
            "13428": ["Kids", "Jackets & Outerwear-6+", "Raincoats & Wind-stoppers"],
            "13431": ["Kids", "Jackets & Outerwear-6+", "Down Jackets"],
            "13429": ["Kids", "Jackets & Outerwear-6+", "Vests"],
            "13430": ["Kids", "Jackets & Outerwear-6+", "Winter Jackets"],
            "14566": ["Kids", "Jackets & Outerwear-6+", "SnowPants"],
            "14530": ["Kids", "Jackets & Outerwear-6+", "WaterproofPants"],
            "14532": ["Kids", "Footwear-6+", "Indoor Sports Shoes"],
            "14536": ["Kids", "Footwear-6+", "Outdoor Sports Shoes"],
            "14535": ["Kids", "Footwear-6+", "Hiking Boots"],
            "14531": ["Kids", "Footwear-6+", "Boots"],
            "14537": ["Kids", "Footwear-6+", "Sandals & Flipflops"],
            "14533": ["Kids", "Footwear-6+", "Water Shoes"],
            "14534": ["Kids", "Footwear-6+", "Crampons"],
            "14514": ["Kids", "Swimwear-6+", "Girls"],
            "14511": ["Kids", "Swimwear-6+", "Boys"],
            "14512": ["Kids", "Swimwear-6+", "UV tops"],
            "14513": ["Kids", "Swimwear-6+", "Wetsuits"],
            "14540": ["Kids", "Accessories-6+", "Hats & Caps"],
            "14538": ["Kids", "Accessories-6+", "Sunglasses"],
            "14541": ["Kids", "Accessories-6+", "Neckwarmer"],
            "14542": ["Kids", "Accessories-6+", "Beanies & Balaclavas"],
            "14539": ["Kids", "Accessories-6+", "Gloves & Mittens"],
            "12805": ["Sports", "Winter Sports", "Downhill Skiing"],
            "12787": ["Sports", "Winter Sports", "Snow Boarding"],
            "12772": ["Sports", "Winter Sports", "Cross Country Skiing"],
            "13446": ["Sports", "Winter Sports", "Snow Shoeing"],
            "12860": ["Sports", "Winter Sports", "Sledding & WinterClothes"],
            "12830": ["Sports", "Winter Sports", "Ice Skating"],
            "14179": ["Sports", "Winter Sports", "Hockey"],
            "13996": ["Sports", "Exercise & Fitness", "Bodybuilding & CrossTraining"],
            "14092": ["Sports", "Exercise & Fitness", "Boxing"],
            "13033": ["Sports", "Exercise & Fitness", "Cardio Fitness"],
            "13087": ["Sports", "Exercise & Fitness", "Pilates"],
            "13065": ["Sports", "Exercise & Fitness", "Yoga"],
            "13058": ["Sports", "Exercise & Fitness", "Gymnastics"],
            "13073": ["Sports", "Exercise & Fitness", "Dance"],
            "14121": ["Sports", "Team Sports", "Soccer"],
            "14161": ["Sports", "Team Sports", "5 A Side Soccer"],
            "14175": ["Sports", "Team Sports", "Futsal"],
            "14218": ["Sports", "Team Sports", "Floorball"],
            "14184": ["Sports", "Team Sports", "Baseball"],
            "14135": ["Sports", "Team Sports", "Basketball"],
            "14156": ["Sports", "Team Sports", "Volleyball"],
            "13943": ["Sports", "Cycling", "Kids Bikes"],
            "13953": ["Sports", "Cycling", "Endurance Road Bikes"],
            "13952": ["Sports", "Cycling", "Performance Road Bikes"],
            "13939": ["Sports", "Cycling", "Mountain Bikes"],
            "13842": ["Sports", "Cycling", "Bike Accessories"],
            "13932": ["Sports", "Cycling", "Safety"],
            "13917": ["Sports", "Cycling", "Clothing & Protection"],
            "14047": ["Sports", "Outdoor", "Camping"],
            "14006": ["Sports", "Outdoor", "Hiking"],
            "14263": ["Sports", "Outdoor", "Horseback Riding"],
            "14248": ["Sports", "Outdoor", "Climbing"],
            "12230": ["Sports", "Outdoor", "Hunting"],
            "13893": ["Sports", "Outdoor", "Fishing"],
            "1666": ["Sports", "Water Sports", "Swimming"],
            "1260": ["Sports", "Water Sports", "Canoeing & Kayaking"],
            "2116": ["Sports", "Water Sports", "Paddleboarding"],
            "12904": ["Sports", "Water Sports", "Surf"],
            "12918": ["Sports", "Water Sports", "Snorkeling"],
            "12914": ["Sports", "Water Sports", "Aquafitness"],
            "172": ["Sports", "Water Sports", "Sailing"],
            "14321": ["Sports", "Running & Walking", "Running"],
            "14310": ["Sports", "Running & Walking", "Walking"],
            "14290": ["Sports", "Running & Walking", "Trail Running"],
            "14307": ["Sports", "Running & Walking", "Triathlon"],
            "14317": ["Sports", "Running & Walking", "Athletics"],
            "13879": ["Sports", "Racquet Sports", "Tennis"],
            "13868": ["Sports", "Racquet Sports", "Badminton"],
            "13874": ["Sports", "Racquet Sports", "TableTennis"],
            "13889": ["Sports", "Racquet Sports", "Speedball"],
            "13890": ["Sports", "Racquet Sports", "Squash"],
            "1152": ["Sports", "Urban Sports", "Scooters"],
            "12070": ["Sports", "Urban Sports", "Skateboards"],
            "747": ["Sports", "Urban Sports", "Rollerblades"],
            "14220": ["Sports", "Precision Sports", "Golf"],
            "14246": ["Sports", "Precision Sports", "Archery"],
            "14245": ["Sports", "Precision Sports", "Darts & Billiards"],
            "14219": ["Sports", "Precision Sports", "Petanque"],
            "14247": ["Sports", "Precision Sports", "Skittles & Shuffleboard"],
            "14115": ["Sports", "Martial Arts", "Karate"],
            "14106": ["Sports", "Martial Arts", "Judo & Aikido"],
            "14110": ["Sports", "Martial Arts", "Taekwondo"],
            "14001": ["Sports", "Outdoor Activities", "Trampolines"],
            "12157": ["Sports", "Outdoor Activities", "Slacklines"],
            "14078": ["Sports", "Outdoor Activities", "Kites"],
            "14077": ["Sports", "Outdoor Activities", "Flying discs & Boomerangs"],
            "2662": ["Accessories", "Bags & Backpacks", "Backpacks"],
            "2660": ["Accessories", "Bags & Backpacks", "Sportsbags"],
            "2663": ["Accessories", "Bags & Backpacks", "Rucksacks & Suitcases"],
            "2661": ["Accessories", "Bags & Backpacks", "Accessories"],
            "2665": ["Accessories", "Bottles & FoodStorage", "Water Bottle"],
            "2666": ["Accessories", "Bottles & FoodStorage", "Food Box"],
            "13840": ["Accessories", "Bottles & FoodStorage", "Cooler Box"],
            "2680": ["Accessories", "Watches & Orienteering", "Watches & Cameras"],
            "2681": ["Accessories", "Watches & Orienteering", "Earbuds & Smartphone Accessories"],
            "2690": ["Accessories", "Watches & Orienteering", "GPS & Compass"],
            "2684": ["Accessories", "Watches & Orienteering", "Binoculars"],
            "2669": ["Accessories", "Sunglasses", "Adults"],
            "2668": ["Accessories", "Sunglasses", "Baby & Child"],
            "2652": ["Accessories", "Massage & Health", "Massage"],
            "2654": ["Accessories", "Massage & Health", "Muscle & Articulation Support"],
            "2657": ["Accessories", "Massage & Health", "Care"],
            "2658": ["Accessories", "Massage & Health", "Weight Scales Tracker"]
            }

        headers = {
            "accept": "application/json",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language" : "en-GB,en-US;q=0.9,en;q=0.8",
            "Connection" : "keep-alive",
            "content-type" : "application/x-www-form-urlencoded",
            "Host": "xxh6l2io6p-dsn.algolia.net",
            "Origin": "https://www.decathlon.ca",
            "Referer": "https://www.decathlon.ca/",
            "sec-ch-ua" :'"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
        }
        endpoint = "https://xxh6l2io6p-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20vanilla%20JavaScript%20(lite)%203.32.0%3Binstantsearch.js%20(4.10.0)%3BJS%20Helper%20(3.3.4)&x-algolia-application-id=XXH6L2IO6P&x-algolia-api-key=1afed37b35c9d11f1f0a3a7e4aef4f84"
        for k, v in categories.items():
            page = '0'
            json_payload = {
                    "requests": [
                        {
                            "indexName": "prod_en",
                            "params": f"ruleContexts=%5B%22category_{k}%22%5D&clickAnalytics=true&distinct=true&filters=category%20%3D%20{k}&highlightPreTag=__ais-highlight__&highlightPostTag=__%2Fais-highlight__&page={page}&maxValuesPerFacet=20&facets=%5B%22nature%22%2C%22practices%22%2C%22genders%22%2C%22generic_color%22%2C%22size%22%2C%22brand%22%2C%22available%22%2C%22sale%22%5D&tagFilters="
                        }
                    ]
                }
            yield scrapy.Request(url=endpoint,
                            method='POST',
                            headers=headers,
                            body=json.dumps(json_payload),
                            callback=self.iterate_json,
                            meta={
                                "Section": v[0],
                                "Category": v[1],
                                "Sub-Category": v[2],
                                "k": k,
                                "v": v
                                }
                            )


    def iterate_json(self, response):
        result = json.loads(response.body)
        k = response.meta.get("k")
        v = response.meta.get("v")
        number_of_pages = result.get("results")[0].get("nbPages")
        for i in range(0, number_of_pages):
            json_payload = {
                            "requests": [
                                {
                                    "indexName": "prod_en",
                                    "params": f"ruleContexts=%5B%22category_{k}%22%5D&clickAnalytics=true&distinct=true&filters=category%20%3D%20{k}&highlightPreTag=__ais-highlight__&highlightPostTag=__%2Fais-highlight__&page={str(i)}&maxValuesPerFacet=20&facets=%5B%22nature%22%2C%22practices%22%2C%22genders%22%2C%22generic_color%22%2C%22size%22%2C%22brand%22%2C%22available%22%2C%22sale%22%5D&tagFilters="
                                }
                            ]
                        }
            endpoint = "https://xxh6l2io6p-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20vanilla%20JavaScript%20(lite)%203.32.0%3Binstantsearch.js%20(4.10.0)%3BJS%20Helper%20(3.3.4)&x-algolia-application-id=XXH6L2IO6P&x-algolia-api-key=1afed37b35c9d11f1f0a3a7e4aef4f84"
            headers = {
                "accept": "application/json",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language" : "en-GB,en-US;q=0.9,en;q=0.8",
                "Connection" : "keep-alive",
                "content-type" : "application/x-www-form-urlencoded",
                "Host": "xxh6l2io6p-dsn.algolia.net",
                "Origin": "https://www.decathlon.ca",
                "Referer": "https://www.decathlon.ca/",
                "sec-ch-ua" :'"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
                "sec-ch-ua-mobile": "?0",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "cross-site",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
                }
            yield scrapy.FormRequest(
                        url=endpoint,
                        headers=headers,
                        method='POST',
                        body=json.dumps(json_payload),
                        meta={
                            "k": k,
                            "v": v,
                            "Section": v[0],
                            "Category": v[1],
                            "Sub-Category": v[2],
                            },
                        callback=self.parse_json
                        )
    
    def parse_json(self, response):
        result = json.loads(response.body)
        current_time = response.meta.get('current_time')
        for product in result.get("results")[0].get("hits"):
            link = product.get("url")
            section = response.meta.get("Section")
            category = response.meta.get("Category")
            sub_category = response.meta.get('Sub-Category')
            product_name = product.get("product_name")
            brand = product.get("brand")
            in_stock_no = product.get("stock")
            current_price = product.get("prix")
            regular_price = product.get("regular")
            sale_price = ''
            if current_price == regular_price:
                sale_price = None
            if current_price < regular_price:
                sale_price = current_price
            
            if not in_stock_no:
                in_stock = 'Out_Of_Stock'
            else:
                in_stock = 'In_Stock'
            image = product.get("image_url")
            if '40x40' in image:
                image = image.replace('40x40', '800x800')
            if '250x180' in image:
                image = image.replace('250x180', '800x800')
            size = product.get("size")
            yield scrapy.Request(url=link,
                        callback=self.parse_html,
                        meta={"section": section,
                            "category": category,
                            "sub_category": sub_category,
                            "product_name": product_name,
                            "brand": brand,
                            "in_stock": in_stock,
                            "image": image,
                            "size": size,
                            "link": link,
                            "sale_price": sale_price,
                            "regular_price": regular_price,
                            'current_time': current_time
                            }
                        )
            for variant in product.get("variations"):
                link = variant.get("url")
                variant_stock = variant.get("stock")
                if not variant_stock:
                    stock = 'Out_Of_Stock'
                else:
                    stock = 'In_Stock'
                image = variant.get("image_url")
                if '40x40' in image:
                    image = image.replace('40x40', '800x800')
                if '250x180' in image:
                    image = image.replace('250x180', '800x800')

                yield scrapy.Request(url=link,
                            meta={
                                "section": section,
                                "category": category,
                                "sub_category": sub_category,
                                "product_name": product_name,
                                "brand": brand,
                                "in_stock": stock,
                                "image": image,
                                "size": variant.get("size"),
                                "link": variant.get("url"),
                                "sale_price": sale_price,
                                "regular_price": regular_price
                                },
                            callback=self.parse_html,
                                )


    def parse_html(self, response):
        section = response.meta.get("section")
        category = response.meta.get("category")
        sub_category = response.meta.get("sub_category")
        product_name = response.xpath('//h1/text()').get()
        if ';' in product_name:
            product_name = product_name.replace(';', '')
        product_link = response.meta.get("link")
        brand = response.meta.get("brand")
        regular_price = response.meta.get("regular_price")
        discounted_price = response.meta.get("sale_price")
        stock_level = response.meta.get("in_stock")
        image_link = response.meta.get("image")
        size = response.meta.get("size")
        if not size:
            size = response.xpath('//select[@class="form-control form-control-select js-select-size js-select2 select2-hidden-accessible"]/option[@selected="selected"][1]/text()').get()
        color = response.xpath('//div[@class=" product-variant-thumb active"]/@data-name').get()
        if not color:
            color = response.xpath('//div[@class="js-product-variant-thumb product-variant-thumb active"]/@data-name').get()
            if not color:
                color = response.xpath('//select[@class="form-control form-control-select hide js-select-color"]/option[@selected="selected"][1]/text()').get()
        sku = response.xpath('//span[@class="sku js-sku hidden"]/text()').get()
        average_rating = response.xpath('//span[@class="rating oyreviews_score"]/span[1]/text()').get()
        un_reviews = response.xpath('//span[@data-target="#reviewModal"]/small/text()').get()
        if not un_reviews:
            num_reviews = None
        else:
            num_reviews = un_reviews[:-8]
        breadcrumb =f'Home|{section}|{category}|{sub_category}'
        if size:
            if 'No Size' in size:
                size = None
                if size:
                    size_without_unit = size
        description = response.xpath('//div[@class="description"]/text()').get()
        if ';' in description:
            description = description.replace(';', '')

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
