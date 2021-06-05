# import mysql.connector


# class MySQLPipeline(object):
#     def __init__(self):
#         self.conn = mysql.connector.connect(
#             host='db-mysql-tor1-1670-do-user-5048843-0.b.db.ondigitalocean.com',
#             user='cuser-ruari',
#             password='^dh#MX4qa^',
#             database='webscrapping_ruari',
#             port='25060'
#         )
#         self.curr = self.conn.cursor()
#         self.create_table()

#     def create_table(self):
#         try:
#             self.curr.execute("""CREATE TABLE webscraping_thebodyshop_product (
#                             ID INTEGER NOT NULL AUTO_INCREMENT,
#                             product_link VARCHAR(500) NOT NULL,
#                             product_name VARCHAR(500) NOT NULL,
#                             brand VARCHAR(500),
#                             category VARCHAR(500),
#                             regular_price DECIMAL NOT NULL,
#                             discounted_price DECIMAL,
#                             price_unit VARCHAR(500),
#                             size VARCHAR(500),
#                             color VARCHAR(500),
#                             flavor VARCHAR(500),
#                             weight VARCHAR(500),
#                             average_rating DECIMAL,
#                             num_reviews INTEGER,
#                             image_link VARCHAR(500),
#                             sku VARCHAR(500),
#                             upc VARCHAR(500),
#                             stock_level VARCHAR(500),
#                             sold_by_3rd_party INTEGER,
#                             shipped_by VARCHAR(500),
#                             data_timestamp INTEGER NOT NULL,
#                             data_year_month INTEGER,
#                             PRIMARY KEY (ID)
#                             )""")
#         except Exception as e:
#             print(f'\n\nERROR:\n{e}')

#     def process_item(self, item, spider):
#         self.store_db(item)
#         return item

#     def store_db(self, item):
#         sql = """INSERT INTO webscraping_thebodyshop_product (
#                                 product_link, 
#                                 product_name,
#                                 brand,
#                                 category,
#                                 regular_price,
#                                 discounted_price,
#                                 price_unit,
#                                 size,
#                                 color,
#                                 flavor,
#                                 weight,
#                                 average_rating,
#                                 num_reviews,
#                                 image_link,
#                                 sku,
#                                 upc,
#                                 stock_level,
#                                 sold_by_3rd_party,
#                                 shipped_by,
#                                 data_timestamp,
#                                 data_year_month
#                                 ) VALUES (
#                                         %s, %s, %s, %s, %s, %s, %s,
#                                         %s, %s, %s, %s, %s, %s, %s, 
#                                         %s, %s, %s, %s, %s, %s, %s
#                                         )"""

#         values = (
#                 item.get("product_link"),
#                 item.get("product_name"),
#                 item.get("brand"),
#                 item.get("category"),
#                 item.get("regular_price"),
#                 item.get("discounted_price"),
#                 item.get("price_unit"),
#                 item.get("size"),
#                 item.get("color"),
#                 item.get("flavor"),
#                 item.get("weight"),
#                 item.get("average_rating"),
#                 item.get("num_reviews"),
#                 item.get('image_link'),
#                 item.get("sku"),
#                 item.get("upc"),
#                 item.get("stock_level"),
#                 item.get("sold_by_3rd_party"),
#                 item.get("shipped_by"),
#                 item.get("data_timestamp"),
#                 item.get("data_year_month")
#             )
#         try:
#             self.curr.execute(sql, values)
#             self.conn.commit()
#         except Exception as e:
#             print(F'ERROR:\n\n {e}')
#             self.conn.rollback()
