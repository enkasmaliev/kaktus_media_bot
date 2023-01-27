import json
import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from datetime import date

token = '5688807172:AAFudH5JY2K4NUTOG_i3QilWF4hhjhyVJ5s'
bot = telebot.TeleBot(token)

URL = 'https://kaktus.media/'

def get_html(url: str):
    all_news = f'?lable=8&date={date.today()}&order=time'
    html = requests.get(url + all_news)
    return html.text

def get_cards(html):
    soup = BeautifulSoup(html, 'lxml')
    cards = soup.find_all('div', class_="ArticleItem--data")
    return cards


def get_news_from_cards(cards):
    result = []

    for card in cards[:21]:
        title = card.find('a', class_="ArticleItem--name").text.strip()
        img_link = card.find('img', class_="ArticleItem--image-img").get('src')

        page_link = card.find('a', class_="ArticleItem--name").get('href')
        page = requests.get(page_link)
        soup = BeautifulSoup(page.content, 'lxml')
        description = ''
        descriptions = soup.find_all('p')
        for desc in descriptions:
            description = description + ' ' + desc.text.strip()
        
        obj = {
            'title': title,
            'img_link': img_link,
            'description': description
        }
        result.append(obj)
    return result


def main():
    html = get_html(URL)
    cards = get_cards(html)
    return get_news_from_cards(cards)

@bot.message_handler(commands=['start'])
def hello_func(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('Посмотреть последние новости')
    button2 = types.KeyboardButton('Выйти')
    keyboard.add(button1, button2)
    bot.send_message(message.chat.id, 'Привет! Нажми на кнопку и получи последние новости!', reply_markup=keyboard)
   

    


@bot.message_handler(func=lambda message: message.text == 'Посмотреть последние новости')
def send_message(message: types.Message):
    inline_keyboard = types.InlineKeyboardMarkup()
    call_back_nums = 1
    articles = main()
    for article in articles[:20]:
        inline_button = types.InlineKeyboardButton(article['title'], callback_data=f'{call_back_nums}')
        inline_keyboard.add(inline_button)
        call_back_nums += 1
    bot.send_message(message.chat.id, 'Новости за сегодня!', reply_markup=inline_keyboard)




@bot.callback_query_handler(func=lambda callback: callback.data in [str(i) for i in range(20)])
def answer(callback: types.CallbackQuery):
    call_back_num = int(callback.data)
    articles = main()
    inline_keyboard = types.InlineKeyboardMarkup()
    bot.send_message(callback.message.chat.id, f"<b>{articles[call_back_num+1]['title']}</b>\n\n{articles[call_back_num+1]['description']}\n{articles[call_back_num+1]['img_link']}", parse_mode='html', reply_markup=inline_keyboard)


@bot.message_handler(func=lambda message: message.text == 'Выйти')
def quit_func(message: types.Message):
    
    bot.send_message(message.chat.id, 'До свидания!')
    bot.stop_polling()

bot.polling()