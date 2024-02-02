import telebot
from telebot import types
from bs4 import BeautifulSoup
import openai
import sqlite3
import requests

openai.api_key = "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"

con = sqlite3.connect("bot_f.db", check_same_thread=False)
cur = con.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS bot(id INT, chat TEXT, mid TEXT)")
con.commit()

bot = telebot.TeleBot("6039532315:AAHPiho62XGxT5JBUmjF6ZYwZzpMgbQOOyo")


@bot.message_handler(commands=["start"])
def start_message(mess):
    cur.execute(f"SELECT id FROM bot WHERE id={mess.chat.id}")
    row = cur.fetchone()
    if row is None:
        cur.execute(f"INSERT INTO bot(id, chat, mid) VALUES({mess.chat.id}, 'Не было запросов.', 'Не было запросов.')")
        con.commit()
    bot.send_message(mess.chat.id, "Добро пожаловать."
                                   "\nНаши команды:"
                                   "\n/info - информация о боте 🔍📄 (рекомендуется первым)."
                                   "\n/chat - чат-бот с ИИ.🧠🤖 "
                                   "\n/mid - генерация фотографий.🌃🏞 "
                                   "\n/history - последний запрос.📝🤔")


@bot.message_handler(commands=["info"])
def info(mess):
    all1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton("chat")
    button2 = types.KeyboardButton("mid")
    button3 = types.KeyboardButton("О нас")
    button4 = types.KeyboardButton("Меню")
    all1.add(button, button2, button3, button4)
    bot.send_message(mess.chat.id, "Нажми на кнопку о которой хочешь узнать.", reply_markup=all1)


@bot.message_handler(commands=["chat"])
def chat(mess):
    bot.send_message(mess.chat.id, "Что хотите узнать?")
    bot.register_next_step_handler(mess, gpt_bot)


def gpt_bot(mess):
    cur.execute(f"UPDATE bot SET chat = '{mess.text}' WHERE id = {mess.chat.id}")
    con.commit()
    msg = bot.send_message(mess.chat.id, "Идет загрузка...")
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=mess.text,
        temperature=0.5,
        max_tokens=1000,
        top_p=1.0,
        frequency_penalty=0.5,
        presence_penalty=0.0,
    )
    bot.send_message(chat_id=mess.from_user.id, text=response['choices'][0]['text'])
    bot.edit_message_text(text=response['choices'][0]['text'], chat_id=mess.chat.id, message_id=msg.message_id)
    bot.delete_message(mess.chat.id, msg.message_id)


@bot.message_handler(commands=["mid"])
def photo_choices(mess):
    bot.send_message(mess.chat.id, "Какое изображение хотите сгенерировать?")
    bot.register_next_step_handler(mess, photo_generation)


def photo_generation(mess):
    cur.execute(f"UPDATE bot SET mid = '{mess.text}' WHERE id = {mess.chat.id}")
    con.commit()
    msg = bot.send_message(mess.chat.id, "Идет загрузка...")
    response = openai.Image.create(
        prompt=mess.text,
        n=1,
        size="1024x1024"
    )
    image_data = response['data'][0]['url']
    image_url = requests.get(image_data)
    with open("image.jpg", 'wb') as f:
        f.write(image_url.content)
    bot.send_photo(mess.chat.id, f'{image_data}')
    bot.edit_message_text(image_data, chat_id=mess.chat.id, message_id=msg.message_id)
    bot.delete_message(mess.chat.id, msg.message_id)


@bot.message_handler(commands=["history"])
def history_commands(mess):
    all2 = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton("o chat")
    button2 = types.KeyboardButton("o mid")
    all2.add(button, button2)
    bot.send_message(mess.chat.id, "О Каком последнем запросе хочешь узнать?", reply_markup=all2)


@bot.message_handler(func=lambda message: True)
def text_info(mess):
    if mess.text == "О нас":
        bot.send_message(mess.chat.id, "Этот телеграмм-бот был создан:\n"
                                       "Командой TECH THINKERS"
                                       "")
    elif mess.text == "Меню":
        bot.send_message(mess.chat.id, start_message(mess))
    elif mess.text == "chat":
        r = requests.get("https://chat.openai.com/")
        soup = BeautifulSoup(r.text, 'lxml')
        res = soup.find("div", class_="article__text__main").find_all("p")
        list_chat = [i.text for i in res]
        bot.send_message(mess.chat.id, "\n".join(list_chat))
    elif mess.text == "mid":
        r = requests.get("https://forpost-sevastopol.ru/newsfull/533432/chto-takoe-midjourney-midgorni-obyasnyaem-prostymi-slovami.html#:~:text=Midjourney%20%E2%80%94%20%D0%BD%D0%B5%D0%B9%D1%80%D0%BE%D1%81%D0%B5%D1%82%D1%8C%2C%20%D0%BA%D0%BE%D1%82%D0%BE%D1%80%D0%B0%D1%8F%20%D0%B3%D0%B5%D0%BD%D0%B5%D1%80%D0%B8%D1%80%D1%83%D0%B5%D1%82%20%D0%B8%D0%B7%D0%BE%D0%B1%D1%80%D0%B0%D0%B6%D0%B5%D0%BD%D0%B8%D1%8F,%20%D1%80%D0%B0%D1%81%D0%BF%D0%BE%D0%B7%D0%BD%D0%B0%D1%91%D1%82%20%D1%82%D0%B5%D0%BA%D1%81%D1%82%20%D0%B8%20%D0%B2%D1%8B%D0%B4%D0%B0%D1%91%D1%82%20%D0%BA%D0%B0%D1%80%D1%82%D0%B8%D0%BD%D0%BA%D1%83.")
        soup = BeautifulSoup(r.text, 'lxml')
        res = soup.find("div").text
        bot.send_message(mess.chat.id, res)
        bot.send_message(mess.chat.id, "Если хотите узнать подробнее, посетите https://secretmag.ru/enciklopediya/chto-takoe-midjourney-midzhorni-obyasnyaem-prostymi-slovami.htm")
    elif mess.text == "o chat":
        cur.execute(f"SELECT chat FROM bot WHERE id ={mess.chat.id} ")
        row = cur.fetchone()
        bot.send_message(mess.chat.id, "Последний запрос: ")
        bot.send_message(mess.chat.id, row[0])
    elif mess.text == "o mid":
        cur.execute(f"SELECT mid FROM bot WHERE id ={mess.chat.id} ")
        row = cur.fetchone()
        bot.send_message(mess.chat.id, "Последний запрос: ")
        bot.send_message(mess.chat.id, row[0])


bot.polling(none_stop=True, interval=0)
