import pandas as pd
import re
from bs4 import BeautifulSoup
import requests
from os import environ
from datetime import date
import boto3
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal




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
                    'Name': res_name,
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
        
    table_name = "car_listings"

    client = boto3.client('dynamodb')
    DB = boto3.resource('dynamodb')
    table = DB.Table(table_name)


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
        
        try:
            df_append['Rating'] = df_append['Rating'].astype(float)
        except ValueError:
            continue
        
        df_append['Dealer Name'] = df_append['Dealer Name'].astype(str)
        df_append['Make'] = capitalize(make)
        


        for i, row in df_append.iterrows():

            print(i)
            
            item = {
                    'Dealer Name': row['Dealer Name'],
                    'Price': row['Price'],
                    'Mileage': row['Mileage'],
                    'Year': row['Year'],
                    'Name': row['Name']
                }
            
            response = table.scan(
                FilterExpression= Attr('Name').eq(row['Name']) and
                                  Attr('Mileage').eq(row['Mileage']) and
                                  Attr('Price').eq(Decimal(row['Price']))
            )
            
            

            
            if 'Item' in response:
                print(response['Item'])
            
            else:
                print('item is already in database')
                break


            
lambda_handler('foo', 'bar')  
            

