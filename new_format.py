yield {
    'product_link': product_link,
    'product_name': product_name,
    'brand': brand, 
    'breadcrumb': breadcrumb, # no spaces delimit=|
    'size_without_unit': size_without_unit, # if it has a unit this is blank
    'size_with_unit': size_with_unit, # weight/volume
    'dimension': dimension, # Length x Width x Height
    'alt_identifier_1': alt_identifier_1, # e.g if material is listed, put here.
    # alt_id cannot be mixed and matched. E.g if one product specifies material,
    # and another specifies 'finish', material would be alt_id_1, finish = 2.
    'sku': sku,
    'upc': upc,
    'regular_price': regular_price,
    'regular_qty': regular_qty, # e.g if sold in pack of 7, qty=7
    'regular_unit': regular_unit, #price unit 8$/kg, regular unit = kg
    'discounted_price': discounted_price,
    'discounted_qty': discounted_qty, # same as above
    'discounted_unit': discounted_unit,
    'currency': currency, # 3 letter currency code USD/EUR/CAD.
    'average_rating': average_rating,
    'num_reviews': num_reviews,
    'shipped_by': shipped_by, # if sold by 3rd party, include who its shipped by
    'sold_by_third_party': sold_by_third_party, # 0 or 1,
    'stock_level': stock_level, # In_Stock, Out_Of_Stock, Low_Stock
    'online_only': online_only, # Boolean
    'brief': brief, # short description
    'description': description, # longer description
    'image_link': image_link,
    'data_timestamp': self.data_timestamp,
    'data_year_month': data_year_month, 
    'retailer_code': retailer_code, # no explanation = blank

}