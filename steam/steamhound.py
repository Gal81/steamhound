import os
import re
import json
import time
import requests
from bs4 import BeautifulSoup
from json2html import *
from colorama import init, Fore, Back
init(autoreset=True)

TIMEOUT = 1.00

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
    'count': 100,
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

def sleep_on_429():
  sleep_timeout = TIMEOUT * 60
  print(f'{Back.RED}{Fore.WHITE} » Sleep {sleep_timeout}sec…{Back.BLACK}{Fore.RED}█▓▒░')
  time.sleep(sleep_timeout)

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
    print(f'{Back.RED}{Fore.WHITE} » Error: {html.status_code}{Back.BLACK}{Fore.RED}█▓▒░')

    if html.status_code == 429:
      sleep_on_429()
      return False

def get_tail_by_head(head, data):
  regexp = f'M{head}A%assetid%D(\d{{19}})'
  id = re.search(r'' + regexp, '%s' % data)

  if id:
    id = id.group()
    return id.split('D')[1]
  else:
    print(f'{Fore.CYAN}├─ {Fore.YELLOW}ID no matched')
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
    print(f'{Back.RED}{Fore.WHITE} » Error: "api.csgofloat.com" get {response.status_code}{Back.BLACK}{Fore.RED}█▓▒░')
    return False

def print_lot_status(index, value, added):
  cutter = 1000000
  trim_value = round(value * cutter) / cutter
  float_value = f'{Fore.GREEN}{trim_value}' if added else f'{Fore.WHITE}{trim_value}'

  info_main = f'{Fore.CYAN}├─ {Fore.WHITE}Lot: {Fore.CYAN}{index + 1}{Fore.WHITE}/10'
  info_float = f'float: {float_value}{Fore.WHITE}'
  info_status = f'{Fore.GREEN}Added!' if added else f'{Fore.RED}Skipped'
  print(f'{info_main}; {info_float}; {info_status}')

def parse_main_list_item(list):
  skins = []

  if list is None:
    return False

  for list_index, list_item in enumerate(list):
    html = requests.get(list_item['url'], headers=HEADERS)
    soup = BeautifulSoup(html.text, 'html.parser')
    result = soup.find(id='searchResultsRows')

    data_assets = soup.find_all('script')[-1]

    if result:
      url = list_item['url']
      name = list_item["name"]
      link = f'<a href="{url}" target="_blank">{name}</a>'
      skin = {
        'name': link,
        'floats': [],
        'prices': [],
      }

      lots = result.find_all('div', class_='market_listing_row')
      lot_index = f'» {list_index + 1}/{len(list)}:'

      print(f'{Back.BLUE} {Fore.WHITE}{lot_index} {Fore.YELLOW}{name}{Back.BLACK}{Fore.BLUE}█▓▒░')
      for lot_index, lot in enumerate(lots):
        time.sleep(TIMEOUT) # sleep before data request

        link = lot.find('a', class_='item_market_action_button', href=True)

        if link:
          params = link['href'].replace('javascript:BuyMarketListing(\'listing\', \'', '')
          params = params.replace('\', 730, \'2\'', '')
          params = params.replace('\')', '')
          params = params.split(', \'')

          tail = get_tail_by_head(params[0], data_assets)

          if tail:
            id = f'M{params[0]}A{params[1]}D{tail}'
            float_value = get_float(id)

            price = lot.find('span', class_='market_listing_price_with_fee')

            if float_value and float_value < 0.01:
              skin['floats'].append(float_value)
              skin['prices'].append(price.get_text(strip=True))

              print_lot_status(lot_index, float_value, True)
            elif float_value:
              print_lot_status(lot_index, float_value, False)

        else:
          print(f'{Fore.CYAN}├─ {Fore.YELLOW}link is wrong')

      if len(skin['floats']) != 0:
        skins.append(skin)
        file_write(skins)

  return skins

def main():
  if os.path.exists(STEAM_FILE):
    os.remove(STEAM_FILE)

  print(f'{Back.GREEN}{Fore.BLACK} » Parsing first 100 skins{Back.BLACK}{Fore.GREEN}█▓▒░')

  page = 1
  while True:
    list = parse_main_list(page)

    if list:
      parse_main_list_item(list)
    else:
      print(f'{Back.RED}{Fore.WHITE} » Error. Press Enter to RESTART…{Back.BLACK}{Fore.RED}█▓▒░')
      input()

    print(f'{Back.YELLOW}{Fore.BLACK} » Work is done. RESTARTING…{Back.BLACK}{Fore.YELLOW}█▓▒░')

main()
