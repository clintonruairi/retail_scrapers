from sqlalchemy import create_engine
import pandas as pd
import mysql.connector as mysql
import time

# dataframe = pd.read_csv('petlandv6.csv')
# pd.to_numeric(dataframe["regular_price"], downcast="float")
# dataframe.to_csv('petlandv7.csv')


start = time.perf_counter()

engine = create_engine(
    'mysql+pymysql://cuser-ruari:^dh#MX4qa^@db-mysql-tor1-1670-do-user-5048843-0.b.db.ondigitalocean.com:25060/webscrapping_ruari',
    echo=True
)
def load_all_this_shit():
    dataframe = pd.read_csv('spiders/petlandMayv5.csv')

    try:
        dataframe.to_sql(
            'webscraping_petland_202105',
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




