import requests
from bs4 import BeautifulSoup

HEADERS = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
  'Accept': '*/*'
}

URL = 'https://www.amalgama-lab.com/'

def get_text():
    html = requests.get(URL, headers=HEADERS)
    # soup = BeautifulSoup(html.text, 'html.parser')
    # nav = soup.find('div', id='az_nav')
    # links = nav.find_all('a', href=True)
    print('nav')




    # items = []
    # for song in songs:
    #     items.append({
    #         'link': song['href'].split('/songs/')[1],
    #         'name': song.get_text(strip=True),
    #     })

    # for item in items:
    #     html = requests.get(URL + item['link'], headers=HEADERS)
    #     soup = BeautifulSoup(html.text, 'html.parser')
    #     lyrics = soup.find('div', class_='lyrics')

    #     if lyrics:
    #         text = lyrics.get_text(strip=True)

    #         print('...', item['name'])

    #         index = text.lower().find('coffee hot')
    #         if (index != -1):
    #             print()
    #             print('>>>>>', item['name'], '<<<<<')
    #             print(text)
    #             print()

get_text()
