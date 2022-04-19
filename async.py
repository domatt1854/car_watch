import asyncio
from bs4 import BeautifulSoup
import requests


class CarScraper:

    def __init__(self):
        self.ua = []
        self.proxies = []

    async def get_user_agents(self):

        with open('data/useragents.txt', 'r') as f:
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
                self.proxies.append(ip + ":" + port)

                print("{}:{}".format(ip, port))
            
    
    # todo: hit the website with every make and calculate how much pages I should parse
    async def check_num_results(make,)
        




async def main():
    cs = CarScraper()

    get_proxies_task = asyncio.create_task(
        cs.get_proxies()
    )
    
    get_ua_task = asyncio.create_task(
        cs.get_user_agents()
    )

    await get_proxies_task
    await get_ua_task




    