"""
lee bot - DONE

MVP - Everyday at the same time one automatic quote for user +

ver 1.0 - Unsubscribe function +

ver 2.0 - Everyday different time +

ver 3.0 - One more quote manually +
"""


import telebot
from environs import Env
from random import randint
from datetime import datetime
import json
from lee_data import random_quote
from apscheduler.schedulers.background import BackgroundScheduler

# Bot initialization and token

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")  # Забираем значение типа token в формате str
bot = telebot.TeleBot(BOT_TOKEN)

# Scheduler defining
scheduler = BackgroundScheduler()

# BLOCK WITH KEYBOARDS: -------------------------------------------------------------------------------------------

# Main keyboard
one_more_quote_button = telebot.types.KeyboardButton('Получить еще одну цитату')
markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, row_width=1)
markup.add(one_more_quote_button)


subscribers = []
hour, minute = '15', '00'


# BLOCK WITH FUNCTIONS: -------------------------------------------------------------------------------------------

# Automatically sending quotes
def auto_send_quote():

    with open('user_start.json') as f:
        data = json.load(f)
        subs = [i for i in data]

    for s in subs:
        bot.send_message(s, random_quote())
        print(f'Quote was automatically sent to Users: {subs}')

    random_time()
    print(f'Time was successfully changed to {hour}:{minute}')


# Manually sending quotes
def one_more_quote(user):
    bot.send_message(user, random_quote())
    print(f'Quote was manually sent to User: {user}')


# Getting new random time
def random_time():
    global hour, minute
    hours = ['10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22']
    minutes = ['00', '10', '15', '20', '25', '30', '35', '40', '45', '50', '55']
    hour = hours[randint(0, 12)]
    minute = minutes[randint(0, 10)]
    return scheduler.reschedule_job(job_id='01', trigger='cron', hour=hour, minute=minute, timezone='Europe/Riga')


# Adding info to list of subs who pressed 'start'
def add_new_user_to_json(message):
    user_id = str(message.from_user.id)
    date = datetime.now().strftime('%m-%d-%Y - %H:%M')

    with open('user_start.json') as f:
        data = json.load(f)
        data[user_id] = [date]

    with open('user_start.json', 'w') as f:
        json.dump(data, f, indent=2)

    print('New user has subscribed')


# BLOCK WITH HANDLERS: -------------------------------------------------------------------------------------------

# Start command handler
@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(
        message.chat.id,
        'Привет! Я - бот, который будет присылать тебе каждый день, в случайное время с 10 до 23 цитату об освобождении.',
        reply_markup=markup
    )
    add_new_user_to_json(message)
    one_more_quote(message.chat.id)


# Subscribers command handler
@bot.message_handler(commands=['subs'])
def subscribers_handler(message):

    if message.from_user.id == 545581329:

        with open('user_start.json') as f:
            data = json.load(f)
            subs = []
            for i in data:
                user = i
                date = data[i]
                subs.append(f'{user} | {date}')

    bot.send_message(message.chat.id, str(subs), reply_markup=markup)


@bot.message_handler(content_types=['text'])
def messages_handler(message):
    if message.text == 'Получить еще одну цитату':
        one_more_quote(message.from_user.id)
    else:
        bot.send_message(message.from_user.id, f'Простите, мой функционал ограничен функциями, предложенными в '
                                               f'главном меню. Воспользуйтесь одной из кнопок')


scheduler.add_job(auto_send_quote, trigger='cron', hour=hour, minute=minute, timezone='Europe/Riga', id='01')
scheduler.start()

bot.polling()
