import os
import re
import json
import time
import requests
from bs4 import BeautifulSoup
from json2html import *
from colorama import init, Fore, Back
init(autoreset=True)

TIMEOUT = 1.50

HEADERS = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
  'accept': '*/*'
}

STEAM_HOST = 'https://steamcommunity.com'
STEAM_URL = '/market/search/render'
STEAM_FILE = 'data.html'

CSGO_HOST = 'https://api.csgofloat.com'
CSGO_ITEM_HEAD = 'steam://rungame/730/76561202255233023/+csgo_econ_action_preview%20'

def file_write(data):
  html = json2html.convert(json=data)
  chars = [
    ['&lt;', '<'],
    ['&gt;', '>'],
    ['&quot;', '"'],
    ['&amp;', '&'],
  ]

  for char in chars:
    html = html.replace(char[0], char[1])

  try:
    with open(STEAM_FILE, 'a', encoding='utf-8') as file:
      file.write('%s\n' % html)
      file.close()
      print(f'{Fore.CYAN}█─ File {STEAM_FILE} has been updated')
  except Exception as error:
    print(f'{Back.RED}{error}')
    input()

def get_main_params(page):
  return {
    'query': '',
    'start': page,
    'count': 10,
    'search_descriptions': 1,
    'sort_column': 'price',
    'sort_dir': 'asc',
    'appid': 730,
    'category_730_ItemSet[]': 'any',
    'category_730_ProPlayer[]': 'any',
    'category_730_StickerCapsule[]': 'any',
    'category_730_TournamentTeam[]': 'any',
    'category_730_Weapon[]': 'any',
    'category_730_Exterior[]': 'tag_WearCategory0',
  }

def get_main_list_html(page):
  url = STEAM_HOST + STEAM_URL
  params = get_main_params(page)
  return requests.get(url, headers=HEADERS, params=params)

def parse_main_list(page):
  html = get_main_list_html(page)

  if html.status_code == 200:
    json_object = json.loads(html.text)
    text = json_object['results_html']
    soup = BeautifulSoup(text, 'html.parser')
    items = soup.find_all('a', class_='market_listing_row_link', href=True)

    list = []
    for item in items:
      name = item.find('span', class_='market_listing_item_name')

      listItem = {
        'name': name.get_text(strip=True),
        'url': item['href'],
      }

      list.append(listItem)

    # print(json.dumps(list, indent=2))
    return list
  else:
    print(f'{Back.RED}   {Fore.WHITE}Error: {html.status_code}{Back.BLACK}{Fore.RED}█▓▒░')

def get_tail_by_head(head, data):
  regexp = f'M{head}A%assetid%D(\d{{19}})'
  id = re.search(r'' + regexp, '%s' % data)

  if id:
    id = id.group()
    return id.split('D')[1]
  else:
    print(f'{Fore.CYAN}├─ {Fore.WHITE}ID with head {head} no matched')
    return False

def get_float(id):
  params = {
    'url': CSGO_ITEM_HEAD + id
  }

  response = requests.get(CSGO_HOST, headers=HEADERS, params=params)

  if response.status_code == 200:
    data = json.loads(response.text)
    return data['iteminfo']['floatvalue']

  else:
    print(f'{Back.RED}   {Fore.WHITE}Error: {response.status_code}{Back.BLACK}{Fore.RED}█▓▒░')

    if response.status_code == 429:
      print(f'{Back.RED}   {Fore.WHITE}Sleep {TIMEOUT * 5}sec…{Back.BLACK}{Fore.RED}█▓▒░')
      time.sleep(TIMEOUT * 5)

    return False

def print_skin_status(index, value, added):
  float_value = f'{Fore.GREEN}{value}' if added else f'{Fore.WHITE}{value}'

  info_main = f'{Fore.CYAN}├─ {Fore.WHITE}Skin: {Fore.CYAN}{index + 1} {Fore.WHITE}/ 10'
  info_float = f'float: {float_value}{Fore.WHITE}'
  info_status = f'{Fore.GREEN}Added!' if added else f'{Fore.RED}Skipped'
  print(f'{info_main}; {info_float}; {info_status}')

def parse_main_list_item(list):
  skins = []

  if list is None:
    return False

  for item in list:
    html = requests.get(item['url'], headers=HEADERS)
    soup = BeautifulSoup(html.text, 'html.parser')
    result = soup.find(id='searchResultsRows')

    data_assets = soup.find_all('script')[-1]

    if result:
      url = item['url']
      name = item["name"]
      link = f'<a href="{url}" target="_blank">{name}</a>'
      skin = {
        'name': link,
        'floats': [],
        'prices': [],
      }

      items = result.find_all('div', class_='market_listing_row')

      print(f'{Back.BLUE}   {Fore.WHITE}Parsing: {Fore.YELLOW}{name}{Back.BLACK}{Fore.BLUE}█▓▒░')
      for index, item in enumerate(items):
        link = item.find('a', class_='item_market_action_button', href=True)

        if link:
          params = link['href'].replace('javascript:BuyMarketListing(\'listing\', \'', '')
          params = params.replace('\', 730, \'2\'', '')
          params = params.replace('\')', '')
          params = params.split(', \'')

          tail = get_tail_by_head(params[0], data_assets)

          if tail:
            time.sleep(TIMEOUT) # sleep before API request

            id = f'M{params[0]}A{params[1]}D{tail}'
            float_value = get_float(id)

            price = item.find('span', class_='market_listing_price_with_fee')

            if float_value and float_value < 0.01:
              skin['floats'].append(float_value)
              skin['prices'].append(price.get_text(strip=True))

              print_skin_status(index, float_value, True)
            elif float_value:
              print_skin_status(index, float_value, False)

      if len(skin['floats']) != 0:
        skins.append(skin)
        file_write(skins)

  return skins

def main():
  if os.path.exists(STEAM_FILE):
    os.remove(STEAM_FILE)

  pages = 100

  for page in range(1, pages + 1):
    print(f'{Back.GREEN}   {Fore.BLACK}Parsing page {page} from {pages}{Back.BLACK}{Fore.GREEN}█▓▒░')

    list = parse_main_list(page)
    skins = parse_main_list_item(list)

  print(f'{Fore.YELLOW}└─░▒▓█{Back.YELLOW}{Fore.BLACK}Work is done. Press Enter to close…{Back.BLACK}{Fore.YELLOW}█▓▒░')
  input()

main()
