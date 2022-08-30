import re
import json
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime

def capitalize(dealership):
    
    dealership = re.sub("_", " ", dealership)
    dealership = dealership.split(" ")
    
    dealership = [i.capitalize() for i in dealership]
    
    dealership = " ".join(dealership)
    
    return dealership




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

client = boto3.client('dynamodb')
DB = boto3.resource('dynamodb')
table = DB.Table("daily_listings")



def lambda_handler(event, context):
    
    print(event)
    print(event['multiValueQueryStringParameters']['make'][0])
    
    make = event['multiValueQueryStringParameters']['make'][0]
    date = event['multiValueQueryStringParameters']['date'][0]
    print("date: {}".format(date))
    

    if make not in makes:
        response = {}
        response['statusCode'] = 400
        response['headers'] = {}
        response['headers']['Content-Type'] = 'application/json'
        response['body'] = "make not in makes"

        return response

    make = capitalize(make)
    

    
    fe = Key('Date-Make').eq('{}-{}'.format(date, capitalize(make))) 
    
    print("Querying for {}-{}".format(date, capitalize(make)))
    
    try:
        response = table.query(
            KeyConditionExpression = fe
        
        )
        
    except Exception as e:
        response = {}
        response['statusCode'] = 400
        response['headers'] = {}
        response['headers']['Content-Type'] = 'application/json'
        response['body'] = str(e)

        return response
    
    results = response['Items']

    response = {}
    response['statusCode'] = 200
    response['headers'] = {}
    response['headers']['Content-Type'] = 'application/json'
    response['body'] = json.dumps(results, default=str)
    

    return response

 