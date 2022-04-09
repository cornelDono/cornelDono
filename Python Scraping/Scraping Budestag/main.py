from urllib import response
import requests
import json
from bs4 import BeautifulSoup

# person_url_list = []

# def main():
#     get_urls('https://www.bundestag.de/ajax/filterlist/en/members/863330-863330?limit=9999&view=BTBiographyList') 

# def get_urls(url):
#     s = requests.Session()
#     response = s.get(url=url)

#     soup = BeautifulSoup(response.text, 'lxml')
#     persons = soup.find_all(class_='bt-open-in-overlay')

#     for person in persons:
#         person_page = person.get('href')
#         person_url_list.append(person_page)
    
#     with open('person_list.txt', 'w', encoding='utf-8') as file:
#         for line in person_url_list:
#             file.write(f'{line}\n')




data_dict = []
count = 0

if __name__=='__main__':
    with open('person_list.txt') as file:
        lines = [line.strip() for line in file.readlines()]

    for line in lines:
        s = requests.Session()
        response = s.get(url=line)

        soup = BeautifulSoup(response.text, 'lxml')

        person = soup.find(class_='col-xs-8 col-md-9 bt-biografie-name').find('h3').text
        person_name_company = person.strip().split(',')
        person_name = person_name_company[0]
        person_company = person_name_company[1]

        social_network = []
        links_list_url = soup.find_all(class_='bt-link-extern')
        for link in links_list_url:
            social_network.append(link.get('href'))
        
        data = {
            'person_name': person_name,
            'person_company': person_company,
            'social_network': social_network
        }
        count +=1
        print(count)
        
        data_dict.append(data)

        with open('data.json', 'w', encoding='utf-8') as json_file:
            json.dump(data_dict, json_file, indent=4)



