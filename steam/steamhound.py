import os
import re
import json
import time
import math
import config
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

HOST_STEAM = 'https://steamcommunity.com'
URL_STEAM = '/market/search/render/'
FILE_STEAM = 'lots.html'

HOST_CSGO = 'https://api.csgofloat.com'
URL_LOT = 'steam://rungame/730/76561202255233023/+csgo_econ_action_preview%20'

FILE_FILTER = 'filter.txt'

def get_main_params(start_from, count):
  # 'norender': 1,
  # 'search_descriptions': 1,
  return {
    'query': '',
    'start': start_from,
    'count': count,
    'appid': 730,
    'sort_dir': 'asc',
    'sort_column': 'price',
    'category_730_Type[]': [
      'tag_CSGO_Type_Pistol',
      'tag_CSGO_Type_SMG',
      'tag_CSGO_Type_Rifle',
      'tag_CSGO_Type_SniperRifle',
      'tag_CSGO_Type_Shotgun',
      'tag_CSGO_Type_Machinegun',
    ],
    'category_730_Weapon[]': 'any',
    'category_730_ItemSet[]': 'any',
    'category_730_Quality[]': [
      'tag_normal',
      'tag_strange',
    ],
    'category_730_Exterior[]': 'tag_WearCategory0',
    'category_730_ProPlayer[]': 'any',
    'category_730_StickerCapsule[]': 'any',
    'category_730_TournamentTeam[]': 'any',
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
  timeout = TIMEOUT * 180
  time.sleep(timeout)
  print(f'{Back.RED}{Fore.WHITE} » Sleep {timeout}sec…{Back.BLACK}{Fore.RED}█▓▒░')

def print_error(error):
  print(f'{Fore.RED}│')
  print(f'{Back.RED}{Fore.WHITE} ! {error} ')
  time.sleep(TIMEOUT * 5)

def print_status_code(code):
  print(f'{Back.RED}{Fore.WHITE} ! Error: {code}{Back.BLACK}{Fore.RED}█▓▒░')

def send_message_to_chats(message):
  try:
    file = open(config.CHATS_IDS, 'r')
    ids = file.read().split('\n')
    file.close()

    for id in ids:
      chat_data = {
        'chat_id': id,
        'text': message,
      }
      requests.post(f'https://api.telegram.org/bot{config.TELEGRAM_TOKEN}/sendMessage', data=chat_data)

  except Exception as error:
    print_error(error)

def file_write(data):
  json = {
    'name': data['name'],
    'floats': data['floats'],
    'prices': data['prices'],
    'pages': data['pages'],
  }
  html = json2html.convert(json=json)
  chars = [
    ['&lt;', '<'],
    ['&gt;', '>'],
    ['&quot;', '"'],
    ['&amp;', '&'],
  ]

  for char in chars:
    html = html.replace(char[0], char[1])

  try:
    with open(FILE_STEAM, 'a', encoding='utf-8') as file:
      file.write(f'{html}\n')
      file.close()
      print(f'{Fore.YELLOW}█─ File {FILE_STEAM} has been updated')

      chat_message = f'{data["url"]}\nFLOATS: {data["floats"]}\nPRICES: {data["prices"]}\nPAGES: {data["pages"]}'

      if os.path.exists(config.CHATS_IDS):
        send_message_to_chats(chat_message)
        print(f'{Fore.CYAN}█─ Message sent to telegram')

  except Exception as error:
    print_error(error)

def get_filters():
  if os.path.exists(FILE_FILTER):
    print(f'{Back.CYAN}{Fore.BLACK} » File "{FILE_FILTER}" found. Reading…{Back.BLACK}{Fore.CYAN}█▓▒░')

    file = open(FILE_FILTER, 'r')
    data = file.read()
    file.close()

    names = data.split('\n')
    filters = []
    for filter in names:
      if filter:
        filters.append(filter)

    print(f'{Back.CYAN}{Fore.BLACK} » Added {len(filters)} filters{Back.BLACK}{Fore.CYAN}█▓▒░')
    return filters

  else:
    return False

def get_main_list_html(start_from, count):
  url = HOST_STEAM + URL_STEAM
  params = get_main_params(start_from, count)

  try:
    response = requests.get(url, headers=HEADERS, params=params)

    if response.status_code == 200:
      return response
    else:
      print_status_code(response.status_code)
      return False

  except Exception as error:
    print_error(error)

    return False

def get_total_count():
  html = get_main_list_html(0, 1)

  if html:
    json_object = json.loads(html.text)
    return json_object['total_count']
  else:
    return 0

def get_parsed_skins(start_from, count, filters):
  html = get_main_list_html(start_from, count)

  if html:
    json_object = json.loads(html.text)
    text = json_object['results_html']
    soup = BeautifulSoup(text, 'html.parser')

    # Debug
    # print(html.url)

    items = []
    try:
      items = soup.find_all('a', class_='market_listing_row_link', href=True)
    except Exception as error:
      print_error(error)
      items = []

    list = []
    for item in items:
      name_item = item.find('span', class_='market_listing_item_name')
      name = name_item.get_text(strip=True)

      listItem = {
        'name': name,
        'url': item['href'],
      }

      # with open('names.txt', 'a', encoding='utf-8') as file:
      #   file.write(f'{name} : {item["href"]}\n')
      #   file.close()

      if (filters and name in filters) or (filters is False):
        list.append(listItem)

    # print(json.dumps(list, indent=2))
    return list

  else:
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
    'url': URL_LOT + id
  }

  try:
    response = requests.get(HOST_CSGO, headers=HEADERS, params=params)

    if response.status_code == 200:
      data = json.loads(response.text)
      return data['iteminfo']['floatvalue']

    else:
      # print(f'{Back.RED}{Fore.WHITE} ! Error: "api.csgofloat.com" get {response.status_code}{Back.BLACK}{Fore.RED}█▓▒░')
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
    params = get_lots_params()
    html = requests.get(list_item['url'] + '/render/', headers=HEADERS, params=params)

    if html.status_code == 200:
      json_object = json.loads(html.text)
      text = json_object['results_html']
      soup = BeautifulSoup(text, 'html.parser')

      # Debug
      # print(html.url)

      url = list_item['url']
      name = list_item["name"]
      link = f'<a href="{url}" target="_blank">{name}</a>'
      skin = {
        'url': url,
        'name': link,
        'pages': [],
        'floats': [],
        'prices': [],
      }

      skin_index = f' » {list_index + 1}/{len(list)}:'
      print(f'{Back.BLUE}{Fore.WHITE}{skin_index} {Fore.YELLOW}{name}{Back.BLACK}{Fore.BLUE}█▓▒░')

      lots = []
      try:
        lots = soup.find_all('div', class_='market_listing_row', id=True)
      except Exception as error:
        print_error(error)
        lots = []

      lots_count = len(lots)
      if lots_count == 0:
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
            skin['pages'].append(math.ceil((lot_index + 1) / 10))

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

    elif html.status_code == 429:
      sleep_on_error()

    else:
      print_status_code(html.status_code)

def get_skins_list(filters):
  page = 0
  skins = []
  chunk_count = 100
  total_count = get_total_count()
  time.sleep(TIMEOUT * 2)

  try:
    while page * chunk_count < total_count:
      shift = 0 if page == 0 else 1
      start_from = chunk_count * page + shift

      current_range = [chunk_count * page + 1, chunk_count * (page + 1)]
      print_range = f'{current_range[0]}-{current_range[1]}'

      print(f'{Back.YELLOW}{Fore.BLACK} » Skins {print_range} from {total_count} loading…{Back.BLACK}{Fore.YELLOW}█▓▒░')
      loaded = get_parsed_skins(start_from, chunk_count, filters)

      if loaded:
        skins += loaded

      page += 1

      if (page % 5 == 0):
        time.sleep(TIMEOUT * 10)
      else:
        time.sleep(TIMEOUT * 2)

  except Exception as error:
    print_error(error)

  return skins

def remove_old_lots():
  if os.path.exists(FILE_STEAM):
    os.remove(FILE_STEAM)

def main():
  remove_old_lots()
  print(f'{Back.GREEN}{Fore.BLACK} » Let´s rock!{Back.BLACK}{Fore.GREEN}█▓▒░')

  filters = get_filters()
  while True:
    skins = get_skins_list(filters)

    if skins:
      parse_lots(skins)
    else:
      print(f'{Back.RED}{Fore.WHITE} » Fail! Skins list is empty. Restarting…{Back.BLACK}{Fore.RED}█▓▒░')
      time.sleep(TIMEOUT)

    print(f'{Back.YELLOW}{Fore.BLACK} » Work is done. Restarting…{Back.BLACK}{Fore.YELLOW}█▓▒░')

main()
