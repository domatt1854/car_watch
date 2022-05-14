import pandas as pd
import re
import psycopg2
from bs4 import BeautifulSoup
import requests
from os import environ
from datetime import date


def extract_year(name):
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

def capitalize(dealership):
    
    dealership = re.sub("_", " ", dealership)
    dealership = dealership.split(" ")
    
    dealership = [i.capitalize() for i in dealership]
    
    dealership = " ".join(dealership)
    
    return dealership


def process_text(response_text: str):
    
    name = []
    mileage = []
    dealer_name = []
    rating = []
    rating_count = []
    price = []

    res_rating = ""
    res_dealer = ""
    res_mileage = ""
    res_name = ""
    res_price = ""
    res_rating_cnt = ""
    
    data_dict = []


    try:

        soup = BeautifulSoup(
                response_text,
                'html.parser'
        )

    except Exception as e:
        print("exception encountered.")
        print(e)


    results = soup.find_all('div', {'class': 'vehicle-card-main js-gallery-click-card'})



    for result in results:
            
        try:
            res_name = result.find('h2').get_text()
            year = extract_year(res_name)
            
            name.append(res_name)
        except:
            name.append('None')
            
        try:
            res_mileage = result.find('div', {'class': 'mileage'}).get_text()
            res_mileage = clean_mileage(res_mileage)
            mileage.append(res_mileage)
        
        except:
            mileage.append('None')
        try:
            res_dealer = result.find('div', {'class': 'dealer-name'}).get_text().strip()
            res_dealer = capitalize(res_dealer)
            dealer_name.append(res_dealer)
        except:
            dealer_name.append('None')
        try:
            res_rating = result.find('span', {'class': 'sds-rating__count'}).get_text()
            rating.append(res_rating)
        except:
            rating.append('None')
            
        try:
            res_rating_cnt = result.find('span', {'class': 'sds-rating__link'}).get_text()
            res_rating_cnt = clean_rating_count(res_rating_cnt)
            rating_count.append(res_rating_cnt)
        except:
            rating_count.append('None')
            
        try:
            res_price = result.find('span', {'class': 'primary-price'}).get_text()
            res_price = clean_price(res_price)
            price.append(res_price)
        except:
            price.append('None')

        try:

            car_dict = {
                    'Model': res_name,
                    'Mileage': res_mileage,
                    'Dealer Name': res_dealer,
                    'Rating': res_rating,
                    'Rating Count': res_rating_cnt,
                    'Price': res_price,
                    'Year': year
            }

            data_dict.append(car_dict)
            

        except Exception as e:
            print(e)
            
    return data_dict

def fetch(url):
    response = requests.get(url)
    
    if response.status_code != 200:
        print(response.status_code)
        return
    

    return response.text
    
makes = [
    "acura",
    "buick",
    "cadillac",
    "chevrolet",
    "chrysler",
    "gmc",
    "ford",
    "honda",
    "infiniti",
    "jeep",
    "kia",
    "mitsubishi",
    "nissan",
    "porsche",
    "ram",
    "subaru",
    "toyota",
    "volkswagen",
    "volvo",
    "alfa_romeo",
    "rolls_royce",
    "mini",
    "fiat",
    "aston_martin",
    "maserati",
    "bmw",
    "mercedes_benz"
]



def lambda_handler(event, context):
        

    print("Connecting to database")

    conn = psycopg2.connect(
        host = environ.get("HOST"),
        user = environ.get("USER"),
        password = environ.get("PASSWORD"),
        database = environ.get("DB"),
        port = environ.get("PORT")
    )

    all_results = []

    for make in makes:
        
        cur = conn.cursor()
        
        make_query = capitalize(make)
        
        cur.execute("""SELECT * FROM cars 
                        WHERE make= '{}'
                        ORDER BY ID DESC
                        LIMIT 1000""".format(make_query))
                        
        results = cur.fetchall()
        
        all_results.extend(results)

    print("{} results grabbed from query.".format(len(all_results)))


    df = pd.DataFrame(results)
    df.columns = ['ID', 'Model', 'Make',  'Mileage', 'Dealer Name', 'Rating', 'Rating Count', 'Price', 'Year']

    for make in makes:
        print("querying from url for make: {}".format(make))
        
        url = 'https://www.cars.com/shopping/results/?page={}&page_size=100&list_price_max=&makes[]={}&maximum_distance=all&models[]=&stock_type=cpo&zip='.format('1', make)
        
        response_text = fetch(url)
        print("Done querying. Now looking for duplicates...")
                
        data_dict = process_text(response_text)
        
        
        df_append = pd.DataFrame.from_dict(data_dict, orient = 'columns')
        
        df_append['Year'] = df_append['Year'].astype(int)
        df_append['Mileage'] = df_append['Mileage'].astype(int)
        df_append['Price'] = df_append['Price'].astype(float)
        df_append['Rating'] = df_append['Rating'].astype(float)
        df_append['Dealer Name'] = df_append['Dealer Name']
        df_append['Make'] = capitalize(make)
        
        not_duplicates = []

        df_make = df[df['Make'] == capitalize(make)]
        
        for i, row in df_append.iterrows():

            duplicate_index = df_make[(df_make['Model'] == row['Model'])&\
                                    (df_make['Mileage'] == row['Mileage'])&\
                                    (df_make['Year'] == row['Year'])].index.to_list()
            
            # duplicate was found
            if len(duplicate_index) == 0:
                not_duplicates.append(i)
        
        df_not_duplicate = df_append[df_append.index.isin(not_duplicates)]

        print("found {} new records".format(len(df_not_duplicate)))
        
        insert_script = "INSERT INTO cars (model, make, dealer_name, mileage, rating, rating_cnt, price, year) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        insert_script_new = "INSERT INTO cars_new (date, model, make, dealer_name, mileage, rating, rating_cnt, price, year) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        
        batch_insert = []
        batch_insert_new = []

        for i, row in df_not_duplicate.iterrows():
            
            insert_value = (str(row['Model']), str(row['Make']), str(row['Dealer Name']), int(row['Mileage']), float(row['Rating']), int(row['Rating Count']), float(row['Price']), int(row['Year']))
            
            insert_value_date = (
                str(date.today().strftime("%m/%d/%Y")),
                str(row['Model']),
                str(row['Make']),
                str(row['Dealer Name']),
                int(row['Mileage']),
                float(row['Rating']),
                int(row['Rating Count']),
                float(row['Price']),
                int(row['Year'])
        )
            
            batch_insert.append(insert_value)
            batch_insert_new.append(insert_value_date)
            
            

        cur.executemany(
            insert_script, batch_insert
        )


        cur.executemany(
            insert_script_new, batch_insert_new
        )

        print("finished inserting in the updated database for make: {}".format(make))
        print("for date: {}".format(date.today().strftime("%m/%d/%Y")))

    conn.commit()
