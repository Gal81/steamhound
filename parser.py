import requests
from bs4 import BeautifulSoup
from json2html import *

URL = 'https://bitskins.com'
HEADERS = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
  'accept': '*/*'
}
FILE = 'dump/data.html'

def get_html(url, params=None):
  return requests.get(url, headers=HEADERS, params=params)

def get_content(html):
  soup = BeautifulSoup(html, 'html.parser')
  items = soup.find_all('div', class_='item-featured')

  content = []
  for item in items:
    title = item.find('div', class_='item-title')
    price = item.find('span', class_='item-price-display')
    wear = item.find('span', class_='unwrappable-float-pointer')
    floAt = wear.get_text(strip=True).split(',')[0] if wear else 'Nope'
    # link = item.find('span', class_='unwrappable-float-pointer')

    if floAt.startswith('0.00'):
      contentItem = {
        'title': title.get_text(strip=True),
        'price': price.get_text(strip=True),
        'float': floAt,
      }

      print(contentItem)

      content.append(contentItem)

  return content

def save_file(items, path):
  table = json2html.convert(json=items)

  with open(FILE, 'w', encoding='utf-8') as file:
    file.write('%s\n' % table)
    file.close()

  print(f'File {FILE} has been created')

def parse():
  html = get_html(URL)
  if html.status_code == 200:
    rows = []
    PAGES_COUNT = 2

    for page in range(1, PAGES_COUNT + 1):
      print(f'Parsing page {page} from {PAGES_COUNT}...')

      params = {
        'appid': 730,
        'page': page,
      }
      html = get_html(URL, params=params)
      row = get_content(html.text)
      rows.extend(row)

    print(f'Got {len(rows)} data rows')
    save_file(rows, FILE)

  else:
    print('Error:', html.status_code)

parse()