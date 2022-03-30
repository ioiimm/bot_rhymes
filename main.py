import telebot
import conf
import emoji
from telebot import util
from random_poem import *
from find_rhyme import *
from collections import defaultdict

bot = telebot.TeleBot(conf.TOKEN)

inf_poem = defaultdict(str)

keyboard = telebot.types.InlineKeyboardMarkup()
key_random = telebot.types.InlineKeyboardButton(text='случайное стихотворение', callback_data='random_poem')
keyboard.add(key_random)
key_rhyme = telebot.types.InlineKeyboardButton(text='найти рифму', callback_data='find_rhyme')
keyboard.add(key_rhyme)


@bot.message_handler(commands=['start', 'help'])
def start_message(message):
    bot.send_message(message.chat.id, 'Здравствуй! Этот бот может отвечать рифмованными строчками из стихотворений и отправлять случайное стихотворение.')
    bot.send_message(message.chat.id, emoji.emojize(':herb: :green_heart: Выбери раздел:'), reply_markup=keyboard)


@bot.message_handler(commands=['inf'])
def inf_message(message):
    splitted_text = util.split_string(inf_poem[message.from_user.id], 3000)
    for text in splitted_text:
        bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['poem'])
def poem_message(message):
    bot.send_message(message.chat.id, random_poemf())


@bot.callback_query_handler(
    func=lambda call: call.data == 'random_poem' or call.data == 'find_rhyme')
def callback_worker(call):
    if call.data == 'random_poem':
        bot.send_message(call.message.chat.id, random_poemf())
    elif call.data == 'find_rhyme':
        mesg = bot.send_message(call.message.chat.id, 'Пришли мне какую-нибудь фразу')
        bot.register_next_step_handler(mesg, rhymef)


@bot.message_handler(func=lambda message: True)
def rhymef(message):
    if message.text == '/start' or message.text == '/help':  # проверить надо ли это
        start_message(message)
    elif message.text == '/inf':
        inf_message(message)
    elif message.text == '/poem':
        poem_message(message)
    else:
        # обработка message.text
        given_mes = get_rhyme(message.text)
        res = find_rhymef(given_mes)
        found_rh = res[0]
        inf_poem[message.from_user.id] = res[1]
        if found_rh and found_rh != 'П':
            bot.send_message(message.chat.id, found_rh)
            bot.send_message(message.chat.id, '''Если хотите узнать откуда эта строчка и кто автор, нажмите /inf
Если хотите получить случайное стихотворение, нажмите /poem
Или можете написать что-нибудь еще''')
        else:
            bot.send_message(message.chat.id, 'Прости, кажется, у нас нет для тебя рифмы!\nПопробуй написать что-нибудь еще.')


if __name__ == '__main__':
    bot.polling(none_stop=True)
