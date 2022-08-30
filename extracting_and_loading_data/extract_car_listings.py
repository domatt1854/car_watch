import asyncio
from bs4 import BeautifulSoup
import requests
import pandas as pd
import aiohttp
import re
import random


class CarScraper:

    def __init__(self):
        self.ua = []
        self.df = pd.DataFrame()
        self.data_dict = []
        self.number_results = {}
        self.iter = 0
        self.proxies = []
        

    async def get_user_agents(self):

        with open('useragents.txt', 'r') as f:
            lines = f.readlines()

        for line in lines:
            self.ua.append(line.strip())

    async def get_proxies(self):
    
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
            
        self.proxies = proxies
        
            
    
    # todo: hit the website with every make and calculate how much pages I should parse
    async def get_total_results(self, make:str) -> BeautifulSoup:

        website = 'https://www.cars.com/shopping/results/?page={}&page_size=100&list_price_max=&makes[]={}&maximum_distance=all&models[]=&stock_type=cpo&zip='.format("1", make)
        headers = {'User-Agent' : self.ua[random.randint(0,len(self.ua))]}



        response = requests.get(
            url = website,
            headers=headers,
            # proxies=proxy_dict,
            timeout=3,
        )

        if response.status_code != 200:
            print("Error, status code: {}".format(response.status_code))
            return

        soup = BeautifulSoup(
            response.content,
            'html.parser'
        )  


        results = soup.find_all('span', {'class': 'total-entries'})
        total_res = results[0].text.strip()
        total_res = total_res.rstrip(' matches')
        total_res = total_res.rstrip('+')
        total_res = re.sub(',', '', total_res)

        self.number_results[make] = int(total_res)

        return soup

    async def fetch(self, url:str, session: aiohttp.ClientSession) -> str:

        try:
            async with session.get(url) as response:
                html = await response.read()

                return html

        except Exception as e:
            print(e)
            return

    async def process_text(self, response_text:str):
        print('Processing text #: {}'.format(self.iter))
        self.iter += 1

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


        try:

            soup = BeautifulSoup(
                    response_text,
                    'html.parser'
            )
        
        except Exception as e:
            print("exception encountered.")
            print(e)
            return

        results = soup.find_all('div', {'class': 'vehicle-card-main js-gallery-click-card'})


        
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

            try:

                car_dict = {
                        'Name': res_name,
                        'Mileage': res_mileage,
                        'Dealer Name': res_dealer,
                        'Rating': res_rating,
                        'Rating Count': res_rating_cnt,
                        'Price': res_price
                }

                self.data_dict.append(car_dict)

            except Exception as e:
                print(e)
            

        

async def main(make: str):

    cs = CarScraper()

    
    get_ua_task = asyncio.create_task(
        cs.get_user_agents()
    )

    await get_ua_task



    get_number_results_soup = asyncio.create_task(
        cs.get_total_results(make)
    )

    await asyncio.gather(get_number_results_soup)


    tasks = []

    

    async with aiohttp.ClientSession() as session:

        num_results = int(cs.number_results[make] / 100)

        
        for i in range(1, num_results + 2):

            url = 'https://www.cars.com/shopping/results/?page={}&page_size=100&list_price_max=&makes[]={}&maximum_distance=all&models[]=&stock_type=cpo&zip='.format(i, make)

            tasks.append(
                asyncio.create_task(
                    cs.fetch(url, session)
                )
            )

        pages_content = await asyncio.gather(*tasks)
        
        pages_content = [i for i in pages_content if i is not None]
        
        process_html_tasks = []


        for html in pages_content:
            process_html_tasks.append(
                asyncio.create_task(
                    cs.process_text(html)
                )
            )
        
        await asyncio.gather(*process_html_tasks)

    df = pd.DataFrame.from_dict(cs.data_dict, orient = 'columns')

    print(df.head())

    df.to_csv('data/{}.csv'.format(make))


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

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

for i in makes:
    asyncio.run(main(i))
    

