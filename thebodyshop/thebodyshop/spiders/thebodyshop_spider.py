import scrapy
from thebodyshop.spiders import data
from xml.etree import ElementTree as ET
import time
import datetime
import requests
import json

class ThebodyshopSpiderSpider(scrapy.Spider):
    name = "thebodyshop_spider"
    brand = "thebodyshop"
    _data = data.SUBCATEGORY
    _website     = "https://www.thebodyshop.com/en-us" 
    _root_path   = "home"
    _list_product_api = "https://api.thebodyshop.com/rest/v2/thebodyshop-us/products/search"\
        "?fields=products(multiVariant%2Ccode%2CbaseProduct%2Cname%2Csummary%2CvariantsSmallestUnitSize"\
        "%2CmarkDownMessage%2ClistingStrapline%2Cprice(FULL)%2Cimages(DEFAULT)%2Cstock(FULL)"\
        "%2CreviewRating%2CisVariant%2CvariantSize%2CpreviewDescription%2Cvariants%2Curl"\
        "%2CemailMeWhenInStockToggle%2CpotentialPromotions(DEFAULT)%2CwasPrice(DEFAULT)"\
        "%2CdisplayStrikeThrough)%2Cfacets%2Cbreadcrumbs%2Cpagination(DEFAULT)%2Csorts(DEFAULT)"\
        "%2CbreadcrumbCategories(BASIC)%2CfreeTextSearch%2CkeywordRedirectUrl%2CamplienceIdForThirdSlot"\
        "%2CamplienceIdForSixthSlot%2CfindInStoreEnabled"\
        "&query=%3Abestseller%3Acategory%3A{}&pageSize=3000000&lang=en_US&curr=USD"
    _product_api = "https://api.thebodyshop.com/rest/v2/thebodyshop-us/products/{}?fields=DEFAULT&lang=en_US&curr=USD"
    _rating_api  = "https://api.bazaarvoice.com/data/reviews.json?ApiVersion=5.4&Passkey=cayO0mUUWwDLXl2sUDZOeo7FmMMuHwRbuxChNMLUELWuo"\
                    "&Locale=en_US&Include=Products&FilteredStats=Reviews&Filter=ContentLocale:en_US&Filter=productId:{}"\
                    "&Limit=3&Offset=0&Sort=IsFeatured:desc,SubmissionTime:desc"
    _sku_id      = []
    _product_id  = []
    
    def start_requests(self):
        path = ""
        url  = ""
        data = self._data
        root_path = self._root_path
        for category, subcategory in data.items():
            category_path = root_path + "|" + category
            for k, v in data[category].items():
                path = category_path + "|" + data[category][k]["name"]
                url  = self._list_product_api.format(data[category][k]["id"])
                request = scrapy.Request(url=url, callback=self.parse_list_product, cb_kwargs=dict(category=path))
                path = category_path
                yield request

    def parse_list_product(self, response, category):
        root = ET.fromstring(response.text)
        for product in root.findall('./products'):
            code = product.find('./code').text
            url = self._product_api.format(code)
            request = scrapy.Request(url=url, callback=self.parse_product_detail, cb_kwargs=dict(category=category, product_id=code))
            self._product_id.append(code)
            yield request
    
    def parse_product_detail(self, response, category, product_id):
        current_time = int(time.time())
        root = ET.fromstring(response.text)
        try:
            rating_req = requests.get(self._rating_api.format(product_id))
            rating_res = json.loads(rating_req.text)
            ratings = rating_res["Includes"]["Products"][product_id]["FilteredReviewStatistics"]["AverageOverallRating"]
            reviews = rating_res["Includes"]["Products"][product_id]["FilteredReviewStatistics"]["TotalReviewCount"]
        except:
            ratings = 0
            reviews = 0
        for variant in root.findall('./variantOptions'):
            code = variant.find('./code').text
            if code not in self._sku_id:
                stock_level = 'In_Stock' if variant.find('./stock').find('./stockLevelStatus').text == 'inStock' else 'Out_Of_Stock'
                average_rating = "%.1f" % (float(ratings))
                num_reviews = reviews
                if not average_rating or not num_reviews:
                    average_rating = None
                    num_reviews = None
                yield {
                    'product_link': self._website + variant.find('./url').text,
                    'product_name': root.find('./name').text,
                    'brand': self.brand,
                    'category': category,
                    'regular_price': variant.find('./priceData').find('./value').text,
                    'discounted_price': None,
                    'price_unit': None,
                    'size': variant.find('./size').text,
                    'color': variant.find('./colourName').text if variant.find('./colourName') is not None else None,
                    'flavor': None,
                    'weight': None,
                    'average_rating': average_rating,
                    'num_reviews': num_reviews,
                    'image_link': variant.findall('./images')[0].find('./product').find('./url').text,
                    'sku': code,
                    'upc': None,
                    'stock_level': stock_level,
                    'sold_by_3rd_party': 0,
                    'shipped_by': None,
                    'data_timestamp': current_time,
                    'data_year_month': time.strftime('%Y%m')
                }
                self._sku_id.append(code)
                # items["product_link"]  = self._website + variant.find('./url').text
                # items["product_name"]  = root.find('./name').text
                # items["brand"]         = self.brand
                # items["category"]      = category
                # items["regular_price"] = variant.find('./priceData').find('./value').text
                # items["discounted_price"] = None
                # items["price_unit"]    = None
                # items["size"]          = variant.find('./size').text
                # items["color"]         = variant.find('./colourName').text if variant.find('./colourName') is not None else None
                # items["flavor"]        = None
                # items["weight"]        = None
                # items["average_rating"] = "%.1f" % (float(ratings))
                # items["num_reviews"]   = reviews
                # items["image_link"]    = variant.findall('./images')[0].find('./product').find('./url').text
                # items["sku"]           = code
                # items["upc"]           = None
                # items["stock_level"]   = stock_level
                # items["sold_by_3rd_party"] = None
                # items["shipped_by"]    = None
                # items["data_timestamp"]  = current_time
                # items["data_year_month"] = time.strftime("%Y%m")
                
