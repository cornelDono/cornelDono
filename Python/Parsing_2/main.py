from os import write
import requests
import json
from bs4 import BeautifulSoup
from requests.sessions import session

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'useragent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 YaBrowser/21.11.1.932 Yowser/2.5 Safari/537.36',
    'bx-ajax': 'true'

}
def get_url(url):
    s = requests.Session()
    response = s.get(url=url, headers=headers)

    with open('index.html', 'w', encoding="utf-8") as file:
        file.write(response.text)

def get_json(url):
    s = requests.Session()
    response = s.get(url=url, headers=headers)

    with open('result.json', 'w', encoding="utf-8") as file:
       json.dump(response.json(), file, indent=4, ensure_ascii=False)

def collect_data():
    s = requests.Session()
    response = s.get(url='https://salomon.ru/catalog/muzhchiny/obuv/filter/available-is-y/size-is-10.5%20uk-or-11%20uk/apply/?PAGEN_1=1', headers=headers)

    data = response.json()
    pagionation_count = data.get('pagination').get('pageCount')
    print(pagionation_count)

    result_data = []
    items_url = []

    for page_count in range(1, pagionation_count + 1):
        url = f'https://salomon.ru/catalog/muzhchiny/obuv/filter/available-is-y/size-is-10.5%20uk-or-11%20uk/apply/?PAGEN_1={page_count}'
        r = s.get(url=url, headers=headers)

        data = r.json()
        products = data.get('products')

        for product in products:
            product_colors = product.get('colors')

            for pc in product_colors:
                discount_percent = pc.get('price').get('discountPercent')
                
                if discount_percent != 0 and pc.get('list') not in items_url:
                    items_url.append(pc.get('link'))
                    result_data.append(
                        {
                            'title': pc.get('title'),
                            'category': pc.get('category'),
                            'link': f'https://salomon.ru{pc.get("link")}',
                            'price_base': pc.get('price').get('base'),
                            'price_sale': pc.get('price').get('sale'),
                            'discount_percent': discount_percent
                        }
                    )
        print(f'{page_count}/{pagionation_count}')
    with open('result_data.json', 'w', encoding="utf-8") as file:
        json.dump(result_data, file, indent=4, ensure_ascii=False)





def main():
    #get_url(url='https://salomon.ru/catalog/muzhchiny/obuv/')
    #get_json(url='https://salomon.ru/catalog/muzhchiny/obuv/filter/available-is-y/size-is-10.5%20uk-or-11%20uk/apply/?PAGEN_1=2')
    collect_data()


if __name__ =='__main__':
    main()

