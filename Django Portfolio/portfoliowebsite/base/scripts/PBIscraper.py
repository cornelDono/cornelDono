from email import header
from urllib import response
import requests
import datetime
import json
from bs4 import BeautifulSoup
from requests.sessions import session
import sqlite3
import traceback
import sys


headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'headers' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.160 YaBrowser/22.5.1.985 Yowser/2.5 Safari/537.36'
}

data_dict = []
sql_path = r'C:\Users\Admin\Desktop\Python\sqlite_python.db'


def sql_create_table(): #Check for PBISTORAGE table 
    try:
        con = sqlite3.connect(sql_path)
        cursor = con.cursor()
        print("База данных подключена к SQLite")

        cursor.execute('''CREATE TABLE IF NOT EXISTS PBIStorage
               (id INTEGER PRIMARY KEY, Article_title text, Article_date text, Article_short_text text, Aricle_list_tags text, Article_post_link text)''')
        con.commit()
        print("Created table ", cursor.rowcount)
        cursor.close()
    except sqlite3.Error as error:
        print("Не удалось вставить данные в таблицу sqlite")
        print("Класс исключения: ", error.__class__)
        print("Исключение", error.args)
        print("Печать подробноcтей исключения SQLite: ")
        exc_type, exc_value, exc_tb = sys.exc_info()
        print(traceback.format_exception(exc_type, exc_value, exc_tb))
    finally:
        if (con):
            con.close()
            print("Соединение с SQLite закрыто")

def get_last_article_name(): #Get last article name from PBIStorage to check for new posts
    try:
        con = sqlite3.connect(sql_path)
        cursor = con.cursor()
        print("База данных подключена к SQLite")

        cursor.execute('''SELECT Article_title FROM PBIStorage ORDER BY ID DESC LIMIT 1''')
        records = cursor.fetchall()
        print(records)
        arcticle_name = ''.join(records[0])
        return arcticle_name
    except sqlite3.Error as error:
        return ("Ошибка при работе с SQLite", error)
    finally:
        if (con):
            con.close()
            print("Соединение с SQLite закрыто")


def inges_data(data_dict): # Ingest data to PBIStorage
    con = sqlite3.connect(sql_path)
    cursor = con.cursor()
    for data in data_dict:
        cursor.execute('''INSERT INTO PBIStorage (Article_title, Article_date, Article_short_text, Aricle_list_tags, Article_post_link) VALUES (?, ?, ?, ?, ?) ''', 
                        [data['Article_title'], data['Article_date'], data['Article_short_text'], data['Aricle_list_tags'], data['Article_post_link']])
        con.commit()
    print("Переменные Python успешно вставлены в таблицу PBI_storage")
    cursor.close()

def get_url(url): #Get HTML file with first page from PBI Forum
    s = requests.Session()
    response = s.get(url=url, headers=headers)
    with open('index.html', 'w', encoding='utf-8') as file:
        file.write(response.text)


def collect_data(): #Collect all data from PBI Forum
    for i in range(1, 170):    # 170
        print(f'https://powerbi.microsoft.com/en-us/blog/?page={i}')
        s = requests.Session()
        response = s.get(url=f'https://powerbi.microsoft.com/en-us/blog/?page={i}', headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        section = soup.find('div', class_='column large-7')
        posts = section.findAll(class_='post')
        for post in posts:
            list_tags = ''
            title = post.find('a').text.strip()
            date = post.find('div').find('p').text.strip().split(' by')[0]
            date = datetime.datetime.strptime(date, '%B %d, %Y').strftime('%Y-%m-%d')
            link_post = post.find('a', href=True)['href']
            unwanted = post.find('div').find('p')
            unwanted.extract()
            short_text = post.find('div').find('p').text.strip()
            tagsHtml = post.findAll(class_='tag')

            for tagHtml in tagsHtml:
                list_tags += tagHtml.text + ','
            list_tags = list_tags[:-1]
            data = {
                'Article_title' : title,
                'Article_date' : date,
                'Article_short_text' : short_text,
                'Aricle_list_tags' : list_tags,
                'Article_post_link' : link_post
            }

            data_dict.append(data)
    return data_dict
    
def collect_data_increment(last_article_name): # Collect only new data from PBI Forum
    data_dict = []
    data = []
    post_amount = 0
    pages = 2
    i = 1
    while i < pages:
        s = requests.Session()
        response = s.get(url=f'https://powerbi.microsoft.com/en-us/blog/?page={i}', headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        section = soup.find('div', class_='column large-7')
        posts = section.findAll(class_='post')
        post_amount += len(posts)
        for post in posts:
            title = post.find('a').text.strip()
            if last_article_name != title:
                list_tags = ''
                title = post.find('a').text.strip()
                date = post.find('div').find('p').text.strip().split(' by')[0]
                date = datetime.datetime.strptime(date, '%B %d, %Y').strftime('%Y-%m-%d')
                link_post = post.find('a', href=True)['href']
                unwanted = post.find('div').find('p')
                unwanted.extract()
                short_text = post.find('div').find('p').text.strip()
                tagsHtml = post.findAll(class_='tag')
                for tagHtml in tagsHtml:
                    list_tags += tagHtml.text + ','
                list_tags = list_tags[:-1]
                data = {
                    'Article_title' : title,
                    'Article_date' : date,
                    'Article_short_text' : short_text,
                    'Aricle_list_tags' : list_tags,
                    'Article_post_link' : link_post
                }
                data_dict.append(data)
            else:
                break

        i+=1
        if post_amount == len(data_dict):
            pages += 1
    return data_dict



def main():
    # sql_create_table()
    # print(collect_data_increment())
    # if data_dict:
    #     inges_data(data_dict)
    # else:
    #     print('No new data to ingest')
    get_last_article_name()




if __name__=='__main__':
    main()