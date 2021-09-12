import telebot
import config

bot = telebot.TeleBot(config.TELEGRAM_TOKEN)

def get_saved_ids():
  try:
    file = open(config.CHATS_IDS, 'r')
    ids = file.read().split('\n')
    file.close()
    return ids

  except Exception as error:
    print(error)
    return []

def write_new_id(chat_id):
  try:
    with open(config.CHATS_IDS, 'a', encoding='utf-8') as file:
      file.write('%s\n' % chat_id)
      file.close()

  except Exception as error:
    print(error)
    input()

@bot.message_handler(commands=['start'])
def start(message):
  chat_id = message.chat.id
  ids = get_saved_ids()

  if chat_id not in ids:
    write_new_id(chat_id)

@bot.message_handler(content_types=['text'])
def log(message):
  print(message.chat.id, ' » ', message.text)

# RUN
print(' » Run…')
bot.polling(none_stop=True)
