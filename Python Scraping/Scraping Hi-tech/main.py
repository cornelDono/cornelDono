import zipfile
import requests
import time
from random import randrange
from bs4 import BeautifulSoup
from requests.api import get
from requests.models import Response
import json
import urllib.request
from zipfile import ZipFile

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 YaBrowser/21.11.0.1996 Yowser/2.5 Safari/537.36'
}

def get_articles_urls(url):
    s = requests.Session
    response = get(url=url, headers=headers)
    #with open('index.html', 'w', encoding="utf-8") as file:
    #    file.write(response.text)
    articles_url_list = []
    soup = BeautifulSoup(response.text, 'lxml')
    last_page = int(soup.find('span', class_='navigations').find_all('a')[-1].text)
    for page in range(1, last_page + 1):
        response = get(url=f'https://hi-tech.news/comp/page/{page}/', headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        articles_url = soup.find_all('a', class_='post-title-a')
        for au in articles_url:
            art_aur = au.get('href')
            articles_url_list.append(art_aur)
        #time.sleep(randrange(2,5))
        print(f'Обработал {page}/{last_page}')
    with open('articles_url.txt', 'w') as file:
        for url in articles_url_list:
            file.write(f'{url}\n')

    
def get_data(file_path):
    with open(file_path) as file:
        urls_list = [line.strip() for line in file.readlines()]

    s = requests.Session
    url_count = len(urls_list)
    result_data = []
    count = 0
    for url in enumerate(urls_list):
        response = get(url=url[1], headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        article_title = soup.find('h1', class_='title').text.strip()
        article_date = soup.find('div', class_='post').find('div', class_='tile-views', title='Дата публикации').text.strip()
        article_img = f"https://hi-tech.news{soup.find('div', class_='post-media-full').find('img').get('src')}"
        article_txt = soup.find('div', class_='the-excerpt').text.strip().replace('/n', '')

        result_data.append(
            {
                'original_url': url[1],
                'article_title': article_title,
                'article_date': article_date,
                'article_img': article_img,
                'article_txt': article_txt
            }
        )

        print(f'Обработал: {url[0]}')
        urllib.request.urlretrieve( article_img , f'picture/Статья {url[0]}.jpg')
        with open('result.json', 'w', encoding="utf-8") as file:
            json.dump(result_data, file, indent=4, ensure_ascii=False)
        





def main():
    #(get_articles_urls(url='https://hi-tech.news/comp/'))
    get_data('articles_url.txt')


if __name__ == '__main__':
    main()
