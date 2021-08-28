import json
import requests

HOST = 'https://api.csgofloat.com'
HEADERS = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
  'Content-Type': 'application/json',
  'accept': '*/*'
}

LINK_HEAD = 'steam://rungame/730/76561202255233023/+csgo_econ_action_preview%20'
URL1 = LINK_HEAD + 'M3388383706163415278A19283545844D1030284652543335744'
URL2 = LINK_HEAD + 'M3387257806257071617A23213490325D1030284652543335744'

def print_response(data):
  if data.status_code == 200:
    json_object = json.loads(data.text)
    json_str = json.dumps(json_object, indent=2)
    print(json_str)
  else:
    print('Error, status code:', data.status_code)

# TEST POST /bulk
def test_post():
  payload = {
    'links': [
      { 'link': URL1 },
      { 'link': URL2 }
    ]
  }

  response = requests.post(
    HOST + '/bulk',
    headers=HEADERS,
    json=payload,
  )

  print_response(response)

# test_post()

# TEST GET
def test_get():
  response = requests.get(
    HOST,
    headers=HEADERS,
    params={
      'url': URL1
    }
  )

  print_response(response)

test_get()