import re
import json
import time
import requests
import urllib.request
from bs4 import BeautifulSoup

HEADERS = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
  'accept': '*/*'
}

STEAM_HOST = 'https://steamcommunity.com'
STEAM_URL = '/market/search'
STEAM_FILE = 'dump/steam.html'
STEAM_PARAMS = {
  'q': '',
  'descriptions': 1,
  'category_730_ItemSet[]': 'any',
  'category_730_ProPlayer[]': 'any',
  'category_730_StickerCapsule[]':'any',
  'category_730_TournamentTeam[]': 'any',
  'category_730_Weapon[]': 'any',
  'category_730_Exterior[]': 'tag_WearCategory0',
  'appid': 730,
}

def get_listing_page_html(page):
  url = STEAM_HOST + STEAM_URL + page
  return requests.get(url, headers=HEADERS, params=STEAM_PARAMS)

itemIndex = 0
def get_listing_content(html):
  global itemIndex
  soup = BeautifulSoup(html, 'html.parser')
  items = soup.find_all('a', class_='market_listing_row_link', href=True)

  content = []
  for item in items:
    name = item.find('span', class_='market_listing_item_name')

    itemIndex += 1
    contentItem = {
      'index': itemIndex,
      'name': name.get_text(strip=True),
      'url': item['href'],
    }

    content.append(contentItem)

  return content

def get_listing_rows():
  rows = []
  PAGES_COUNT = 1

  for page in range(1, PAGES_COUNT + 1):
    print(f'Parsing page {page} from {PAGES_COUNT}...')

    page = '#p%(page)s_price_asc' % {
      'page': page,
    }
    html = get_listing_page_html(page)
    # print(html.url)

    if html.status_code == 200:
      chunk = get_listing_content(html.text)
      rows.extend(chunk)
    else:
      print('Error:', html.status_code)

    return rows

def get_script_data():
  listing = get_listing_rows()

  if len(listing) != 0:
    list = listing[0]

    url = urllib.request.urlopen(list['url'])
    soup = BeautifulSoup(url.read(), 'html.parser')
    scripts = soup.find_all('script')
    return scripts[-1].string

  else:
    print('Error: response is empty')

SCRIPT_DATA = get_script_data()

def get_item_by_head(head):
  regexp = 'M%(M)sA%%assetid%%D\d{19}' % {
    'M': head,
  }
  # print(regexp)

  id = re.search(r'' + regexp, SCRIPT_DATA)

  if id:
    print(id.group())
  else:
    print('ID with head %(head)s no matched' % {
      'head': head,
    })

def get_skin_variants_html(url):
  return requests.get(url, headers=HEADERS)

def parse_skins():
  listing = get_listing_rows()
  # print(json.dumps(listing, indent=2))

  for list in listing:
    time.sleep(0.1)

    html = get_skin_variants_html(list['url'])
    soup = BeautifulSoup(html.text, 'html.parser')
    result = soup.find(id='searchResultsRows')

    if result:
      items = result.find_all('a', class_='item_market_action_button', href=True)

      skin = {
        'name': list['name'],
        'ids': [],
      }

      for item in items:
        params = item['href'].replace('javascript:BuyMarketListing(\'listing\', \'', '')
        params = params.replace('\', 730, \'2\'', '')
        params = params.replace('\')', '')
        # params = params.replace(', \'', '+')
        params = params.split(', \'')

        get_item_by_head(params[0])

        id = 'M%(M)sA%(A)sD%(D)s' % {
          'M': params[0],
          'A': params[1],
          'D': '===',
        }

        skin['ids'].append(id)

      # print(json.dumps(skin, indent=2))

parse_skins()