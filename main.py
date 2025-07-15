import asyncio
from rnet import Impersonate,Client,Proxy,Response
from bs4 import BeautifulSoup
import json


def create_client() -> Client:
    return Client(impersonate=Impersonate.Firefox136)

async def fetch_urls(client:Client,urls:list):
    tasks=[client.get(url) for url in urls]
    return await asyncio.gather(*tasks)


def parse_resp(response:str) -> list | None:
    urls=[]
    html=BeautifulSoup(response,'lxml')
    json_data=html.find_all('script',{"type":"application/ld+json"})
    for ld in json_data:
        if "ItemList" in ld.text:
            store_product=json.loads(ld.text)
            if store_product is not None:
                for product in store_product['itemListElement']:
                    urls.append(product['url'])
                return urls
        if "Product" in ld.text:
            return json.loads(ld.text)
    return None   

async def main() ->None:
    shop_url=[
        'https://www.etsy.com/uk/shop/DemgorWoodMood',
        # 'https://www.etsy.com/uk/shop/kepun'
    ]
    results=[]
    client=create_client()
    responses=await fetch_urls(client,shop_url)
    for resp in responses:
        print(resp.status_code)
        product_urls=parse_resp(await resp.text())
        if product_urls is not None:
            print("urls found:",product_urls)
            responses=await fetch_urls(client,product_urls)
            for resp in responses:
                product_data=parse_resp(await resp.text())
                results.append(product_data)

    print("total results",len(results))
    with open("results.json","w") as f:
        json.dump(results,f)


if __name__=="__main__":
    asyncio.run(main())



