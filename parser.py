import csv
import requests
from bs4 import BeautifulSoup

HOST = 'https://auto.ria.com'
URL = 'https://auto.ria.com/newauto/marka-jeep/'
HEADERS = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
  'accept': '*/*'
}
FILE = 'data.csv'

def get_html(url, params=None):
  return requests.get(url, headers=HEADERS, params=params)

def get_pages_count(html):
  soup = BeautifulSoup(html, 'html.parser')
  pagination = soup.find_all('span', class_='mhide')

  if pagination:
    return int(pagination[-1].get_text())
  else:
    return 1

def get_content(html):
  soup = BeautifulSoup(html, 'html.parser')
  items = soup.find_all('section', class_='proposition', id=None)

  content = []
  for item in items:
    title = item.find('h3', class_='proposition_name')
    link = item.find('a', class_='proposition_link')
    price = item.find('div', class_='proposition_price')
    price_usd = price.find('span', class_='size22') if price else False
    price_uah = price.find('span', class_='size16') if price else False
    region = item.find('span', class_='region') if price else False

    if region:
      content.append({
        'title': title.get_text(strip=True),
        'link': HOST + link.get('href') if link else '',
        'price usd': price_usd.get_text(strip=True) if price_usd else '',
        'price uah': price_uah.get_text(strip=True) if price_uah else '',
        'region': region.get_text(strip=True),
      })

  return content

def save_file(items, path):
  with open(path, 'w', newline='') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow(['Model', 'Link', 'USD', 'UAH', 'Region'])

    for item in items:
      writer.writerow([
        item['title'],
        item['link'],
        item['price usd'],
        item['price uah'],
        item['region'],
      ])

def parse():
  html = get_html(URL)
  if html.status_code == 200:
    rows = []
    pages_count = get_pages_count(html.text)

    for page in range(1, pages_count + 1):
      print(f'Parsing page {page} from {pages_count}...')

      params = {
        page: page
      }
      html = get_html(URL, params=params)
      content = get_content(html.text)
      rows.extend(content)

    save_file(rows, FILE)
    print(f'Got {len(rows)} data rows')

  else:
    print('Error:', html.status_code)

parse()