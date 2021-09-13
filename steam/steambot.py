import os
import time
import telebot
import config

bot = telebot.TeleBot(config.TELEGRAM_TOKEN, threaded=False)

def get_saved_chats():
  try:
    if os.path.exists(config.CHATS_IDS):
      file = open(config.CHATS_IDS, 'r')
      data = file.read()
      file.close()
      return data.split('\n')
    else:
      return []

  except Exception as error:
    print(f' ! Get chats: {error}')
    input()

def write_new_id(chat_id):
  try:
    with open(config.CHATS_IDS, 'a', encoding='utf-8') as file:
      file.write(f'{chat_id}\n')
      file.close()

  except Exception as error:
    print(f' ! Add new chat: {error}')
    input()

@bot.message_handler(commands=['start'])
def start(message):
  chat_id = str(message.chat.id)
  chats = get_saved_chats()

  if chat_id not in chats:
    write_new_id(chat_id)
    print(f' » New chat "{chat_id}" has been added')

  try:
    bot.send_message(message.chat.id, 'You have been subscribed')
  except Exception as error:
    print(f' ! Bot says: {error}')
    input()

@bot.message_handler(content_types=['text'])
def log(message):
  print(f' » {message.chat.id}: {message.text}')

print(' » Run…')
while True:
  try:
    bot.polling(none_stop=True)

  except Exception as error:
    print(f' ! Try polling: {error}')
    time.sleep(15)
