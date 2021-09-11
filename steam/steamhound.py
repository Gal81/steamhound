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
  'Accept': '*/*'
}

STEAM_HOST = 'https://steamcommunity.com'
STEAM_URL = '/market/search/render'
STEAM_FILE = 'lots.html'

CSGO_HOST = 'https://api.csgofloat.com'
CSGO_ITEM_HEAD = 'steam://rungame/730/76561202255233023/+csgo_econ_action_preview%20'

def get_main_params(page, count):
  return {
    'query': '',
    'start': page,
    'count': count,
    'appid': 730,
    'sort_dir': 'asc',
    'sort_column': 'price',
    'search_descriptions': 1,
    'category_730_Weapon[]': 'any',
    'category_730_ItemSet[]': 'any',
    'category_730_ProPlayer[]': 'any',
    'category_730_StickerCapsule[]': 'any',
    'category_730_TournamentTeam[]': 'any',
    'category_730_Exterior[]': 'tag_WearCategory0',
  }

def get_lots_params():
  return {
    'query': '',
    'start': 0,
    'count': 100,
    'country': 'UA',
    'language': 'russian',
    'currency': 1,
  }

def sleep_on_error():
  timeout = TIMEOUT * 60
  time.sleep(timeout)
  print(f'{Back.RED}{Fore.WHITE} » Sleep {timeout}sec…{Back.BLACK}{Fore.RED}█▓▒░')

def print_error(error):
  print()
  print(f'{Back.RED}{Fore.WHITE}{error}')
  input()

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
    print_error(error)

def get_main_list_html(page, count):
  print(f'{Back.YELLOW}{Fore.BLACK} » Skins list loading…{Back.BLACK}{Fore.YELLOW}█▓▒░')
  url = STEAM_HOST + STEAM_URL
  params = get_main_params(page, count)
  return requests.get(url, headers=HEADERS, params=params)

def parse_main_list(page, count):
  html = get_main_list_html(page, count)

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
      sleep_on_error()
      return False

def get_lot_link_tail(link):
  regexp = f'M%listingid%A%assetid%D(\d{{19}})'
  id = re.search(r'' + regexp, '%s' % link)

  if id:
    id = id.group()
    return id.split('D')[1]
  else:
    # print(f'{Fore.CYAN}├─ {Fore.YELLOW}ID no matched')
    return False

def get_float(id):
  params = {
    'url': CSGO_ITEM_HEAD + id
  }

  try: 
    response = requests.get(CSGO_HOST, headers=HEADERS, params=params)

    if response.status_code == 200:
      data = json.loads(response.text)
      return data['iteminfo']['floatvalue']

    else:
      # print(f'{Back.RED}{Fore.WHITE} » Error: "api.csgofloat.com" get {response.status_code}{Back.BLACK}{Fore.RED}█▓▒░')
      return False

  except Exception as error:
    print_error(error)
    return False

# Obsolete
def print_lot_status(index, count, value, added):
  cutter = 1000000
  trim_value = round(value * cutter) / cutter
  float_value = f'{Fore.GREEN}{trim_value}' if added else f'{Fore.WHITE}{trim_value}'

  info_main = f'{Fore.CYAN}├─ {Fore.WHITE}Lot: {Fore.CYAN}{index + 1}{Fore.WHITE}/{count}'
  info_float = f'float: {float_value}{Fore.WHITE}'
  info_status = f'{Fore.GREEN}Added!' if added else f'{Fore.RED}Skipped'
  print(f'{info_main}; {info_float}; {info_status}')

STATUS_ADDED = 'added'
STATUS_SKIPPED = 'skipped'
STATUS_ERROR = 'error'
STATUS_WARNING = 'warning'

def print_progress(status):
  char = f'{Fore.BLACK}'

  if status == STATUS_ADDED:
    char = f'{Fore.GREEN}█'
  elif status == STATUS_ERROR:
    char = f'{Fore.RED}▓'
  elif status == STATUS_WARNING:
    char = f'{Fore.YELLOW}▒'
  else:
    char = f'{Fore.WHITE}░'

  print(f'{char}', end='')

def parse_lots(list):
  if list is None:
    return False

  for list_index, list_item in enumerate(list):
    params=get_lots_params()
    html = requests.get(list_item['url'] + '/render/', headers=HEADERS, params=params)
    json_object = json.loads(html.text)
    text = json_object['results_html']
    soup = BeautifulSoup(text, 'html.parser')

    # Debug
    # print(html.url)

    url = list_item['url']
    name = list_item["name"]
    link = f'<a href="{url}" target="_blank">{name}</a>'
    skin = {
      'name': link,
      'floats': [],
      'prices': [],
    }

    skin_index = f'» {list_index + 1}/{len(list)}:'
    print(f'{Back.BLUE} {Fore.WHITE}{skin_index} {Fore.YELLOW}{name}{Back.BLACK}{Fore.BLUE}█▓▒░')

    lots = soup.find_all('div', class_='market_listing_row', id=True)
    lots_count = len(lots)

    if len(lots) == 0:
      print(f'{Back.RED}{Fore.WHITE} » Fail! Could not get list of lots{Back.BLACK}{Fore.RED}█▓▒░', end='')

    for lot_index, lot in enumerate(lots):
      listing_id = lot['id'].replace('listing_', '')
      listing_info = json_object['listinginfo'][listing_id]
      asset_id = listing_info['asset']['id']
      link = listing_info['asset']['market_actions'][0]['link']
      tail = get_lot_link_tail(link)

      if tail:
        id = f'M{listing_id}A{asset_id}D{tail}'
        float_value = get_float(id)

        price = lot.find('span', class_='market_listing_price_with_fee')

        if float_value and float_value < 0.01:
          skin['floats'].append(float_value)
          skin['prices'].append(price.get_text(strip=True))

          print_progress(STATUS_ADDED)
          # print_lot_status(lot_index, lots_count, float_value, True)
        elif float_value:
          print_progress(STATUS_SKIPPED)
          # print_lot_status(lot_index, lots_count, float_value, False)
        else:
          print_progress(STATUS_ERROR)

      else:
        print_progress(STATUS_WARNING)

    print(' «')

    if len(skin['floats']) != 0:
      file_write(skin)

def main():
  if os.path.exists(STEAM_FILE):
    os.remove(STEAM_FILE)

  skins_count = 100
  print(f'{Back.GREEN}{Fore.BLACK} » Let´s rock!{Back.BLACK}{Fore.GREEN}█▓▒░')

  page = 0
  while True:
    list = parse_main_list(page, skins_count)

    if list:
      parse_lots(list)
    else:
      print(f'{Back.RED}{Fore.WHITE} » Fail! Could not get list of skins. RESTARTING…{Back.BLACK}{Fore.RED}█▓▒░')

    print(f'{Back.YELLOW}{Fore.BLACK} » Work is done. RESTARTING…{Back.BLACK}{Fore.YELLOW}█▓▒░')

main()