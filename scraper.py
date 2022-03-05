from bs4 import BeautifulSoup
import requests
import pandas as pd
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import random
from time import sleep

def get_proxies(num_proxies):
    
    proxy_website = 'https://free-proxy-list.net/'

    response = requests.get(proxy_website)
    proxies = []

    soup = BeautifulSoup(
        response.content,
        'html.parser'
    )       

    for row in soup.find("table").find_all('tr'):
        if(len(row.find_all('td')) > 0):
            ip = str(row.find_all('td')[0]).strip('<td>').strip('</')
            port = str(row.find_all('td')[1]).strip('<td>').strip('</')
            proxies.append(ip + ":" + port)
        
    return proxies

def get_user_agents():
    with open('sample_data/useragents.txt', 'r') as f:
        lines = f.readlines()

    lines = [line.strip() for line in lines]
    
    return lines

name = []
mileage = []
dealer_name = []
rating = []
rating_count = []
price = []


num_proxies = 300

proxies = get_proxies(num_proxies)
user_agents = get_user_agents()


i = 1

proxy_index = 0
user_agent_index = 0


while(i < 501):
    
    website = 'https://www.cars.com/shopping/results/?page={}&page_size=20&list_price_max=&makes[]=mercedes_benz&maximum_distance=all&models[]=&stock_type=cpo&zip='.format(i)
    
    rand_proxy = proxies[proxy_index]
    rand_user_agent = user_agents[user_agent_index]

    http_proxy = "http://{}".format(rand_proxy)
    https_proxy = "https://{}".format(rand_proxy)
    
    proxy_dict = {
      "http": rand_proxy,
      "https": rand_proxy
    }

    headers = {'User-Agent' : rand_user_agent}

    

    try:
        response = requests.get(
            url = website,
            proxies=proxy_dict,
            headers=headers,
            timeout=3
        )
        
        print(response.status_code)
        
        
        
        print("hit: {}".format(website))
        print("i: {}".format(i))
        
        soup = BeautifulSoup(
            response.content,
            'html.parser'
        )     
        
        results = soup.find_all('div', {'class': 'vehicle-card-main js-gallery-click-card'})
        
        print("length of results: {}".format(len(results)))
    
        for result in results:
                
            try:
                res_name = result.find('h2').get_text()
                name.append(res_name)
            except:
                name.append('None')
                
            try:
                res_mileage = result.find('div', {'class': 'mileage'}).get_text()
                mileage.append(res_mileage)
            
            except:
                mileage.append('None')
            try:
                res_dealer = result.find('div', {'class': 'dealer-name'}).get_text().strip()
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
                rating_count.append(res_rating_cnt)
            except:
                rating_count.append('None')
                
            try:
                res_price = result.find('span', {'class': 'primary-price'}).get_text()
                price.append(res_price)
            except:
                price.append('None')
        
        i += 1    
      
   
        
    except Exception as e:
        
        #print("error: {}".format(e))
        
        proxy_index += 1
        user_agent_index += 1
        
        if( proxy_index == num_proxies ):
            print("ran out of proxies.... Grabbing more")
            proxies = get_proxies(num_proxies)
            proxy_index = 0
        
        if( user_agent_index == len(user_agents)):
            user_agent_index = 0
            
        continue
    
    

car_dealer = pd.DataFrame(
    {
        'Name': name,
        'Mileage': mileage,
        'Dealer Name': dealer_name,
        'Rating': rating,
        'Rating Count': rating_count,
        'Price': price
    }
)

car_dealer.head()