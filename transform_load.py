import pandas as pd
from os import listdir
import re
import psycopg2
import secret

def capitalize(make):
    
    make = re.sub("_", " ", make)
    make = make.split(" ")
    
    make = [i.capitalize() for i in make]
    
    make = " ".join(make)
    
    return make

def extract_date(name):
    return int(re.search(r"(\d{4})", name).group(1))

def clean_mileage(miles):
    
    mileage = re.sub(',', '', miles)
    mileage = re.sub(' mi.', '', mileage)
    
    return int(mileage)

def clean_rating_count(rating_count):
    
    words_to_remove = ['\(', '\)', ' reviews', ',', ' review']
    
    for i in words_to_remove:
        rating_count = re.sub(i, '', rating_count)
    
    return int(rating_count)

def clean_price(price):
    
    price = re.sub(',', '', price)
    price = price.strip('$')
    
    if price == 'Not Priced':
        return None
    
    return int(price)


# Aggregating and Cleaning the data

files = listdir('data')

data_all = []

for i in files:

    file_path = "data/{}".format(i)
    
    df = pd.read_csv(file_path, on_bad_lines = 'skip')
    df['Make'] = i[:-4]
    df = df.drop(columns=["Unnamed: 0"])
    
    data_all.append(df)
    
df_all = pd.concat(data_all, axis = 0, ignore_index=True)

df_transform = df_all.copy()
df_transform = df_transform.dropna()

df_transform['Make'] = df_all['Make'].apply(lambda x: capitalize(x))
df_transform['Name'].apply(lambda x: extract_date(x))
df_transform['Year'] = df_all['Name'].apply(lambda x: extract_date(x))
df_transform['Mileage'] = df_transform['Mileage'].apply(lambda x: clean_mileage(x))
df_transform['Rating Count'] = df_transform['Rating Count'].apply(lambda x: clean_rating_count(x))
df_transform['Price'] = df_transform['Price'].apply(lambda x: clean_price(x))

df_transform = df_transform.dropna()

## LOADING DATA INTO RDS INSTANCE

conn = psycopg2.connect(
    host = secret.ENDPOINT,
    user = secret.USERNAME,
    password = secret.PASSWORD,
    database = secret.DATABASE,
    port = secret.PORT
)

cur = conn.cursor()

### CREATING THE TABLE

cur.execute(
    """CREATE TABLE cars(
	ID SERIAL PRIMARY KEY,
	model VARCHAR(100),
	make VARCHAR(20),
	mileage int8,
	dealer_name VARCHAR(200),
	rating float8,
	rating_cnt int8,
	price float8,
	year int8
)"""
)

conn.commit()

## Iterating through the dataframe and inserting every value (Will take a while to complete)

insert_script = "INSERT INTO cars (model, make, dealer_name, mileage, rating, rating_cnt, price, year) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

batch_insert = []

for i, row in df_transform.iterrows():
    
    insert_value = (str(row['Name']), str(row['Make']), str(row['Dealer Name']), int(row['Mileage']), float(row['Rating']), int(row['Rating Count']), float(row['Price']), int(row['Year']))
    batch_insert.append(insert_value)
    
    new_str = insert_script.format(insert_value)

    
# insert into the database
cur.executemany(
    insert_script, batch_insert
)

conn.commit()


