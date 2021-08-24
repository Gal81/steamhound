import requests
from bs4 import BeautifulSoup

HOST = 'https://auto.ria.com'
URL = 'https://auto.ria.com/newauto/marka-jeep/'
HEADERS = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
  'accept': '*/*'
}

def get_html(url, params=None):
  return requests.get(url, headers=HEADERS, params=params)

def get_content(html):
  soup = BeautifulSoup(html, 'html.parser')
  items = soup.find_all('section', class_='proposition')

  cars = []
  for item in items:
    title = item.find('h3', class_='proposition_name')
    link = item.find('a', class_='proposition_link')
    price = item.find('div', class_='proposition_price')
    price_usd = price.find('span', class_='size22') if price else False
    price_uah = price.find('span', class_='size16') if price else False

    cars.append({
      'title': title.get_text(strip=True),
      'link': HOST + link.get('href') if link else '',
      'price usd': price_usd.get_text(strip=True) if price_usd else '',
      'price uah': price_uah.get_text(strip=True) if price_uah else '',
    })
  print(cars)

def parse():
  html = get_html(URL)
  if html.status_code == 200:
    get_content(html.text)
  else:
    print('Error:', html.status_code)

parse()