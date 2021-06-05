from sqlalchemy import create_engine
import pandas as pd
import mysql.connector as mysql
import time

start = time.perf_counter()
dataframe = pd.read_excel('spiders/aritziav1May.xlsx')

engine = create_engine(
    'mysql+pymysql://cuser-ruari:^dh#MX4qa^@db-mysql-tor1-1670-do-user-5048843-0.b.db.ondigitalocean.com:25060/webscrapping_ruari',
    echo=True
)
def load_all_this_shit():
    try:
        dataframe.to_sql(
            'webscraping_aritzia_202105',
            con=engine,
            if_exists='append',
            index_label='id'
        )
    except Exception as e:
        print(f'ERROR: \n\n {e}\n\n')
        load_all_this_shit()

load_all_this_shit()

end = time.perf_counter()
print(f'TIME TAKEN: {end - start}')




