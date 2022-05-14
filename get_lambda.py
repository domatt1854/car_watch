import json
import psycopg2
from datetime import date
import re
from os import environ

def capitalize(dealership):
    
    dealership = re.sub("_", " ", dealership)
    dealership = dealership.split(" ")
    
    dealership = [i.capitalize() for i in dealership]
    
    dealership = " ".join(dealership)
    
    return dealership


conn = psycopg2.connect(
    host = environ.get("HOST"),
    user = environ.get("USERNAME"),
    password = environ.get("PASSWORD"),
    database = environ.get("DB"),
    port = int(environ.get("PORT"))
)

cur = conn.cursor()

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

    make = event['queryStringParameters']['make']

    if make not in makes:
        response = {
            'status': 400,
            'message': "Make '{}' is not a valid make.".format(make)
        }

        return response

    make = capitalize(make)

    cur.execute(
        """SELECT * FROM cars_new
            WHERE make = '{}' AND
            date = (SELECT MAX(date) from cars_new);""".format(make)
    )

    results = cur.fetchall()

    response = {
        'status': 200,
        'cars': results
    }

    return response

