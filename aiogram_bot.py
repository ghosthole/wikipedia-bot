from aiogram import Dispatcher, Bot, types
import asyncio
import wikipedia as wiki
import sqlite3 as sql

bot = Bot(token="здесь должен быть токен твоего бота")  # получить его можно, когда создаешь бота в BotFather
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])  # хендлер на команду "/start"
async def start_message(message: types.Message):
    start_text = """Привет, {0.first_name}! Напиши: -w [название статьи] и найду ее по названию!"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    wiki_button = types.KeyboardButton("Wikipedia")
    markup.add(wiki_button)
    await message.answer(text=start_text.format(message.from_user), reply_markup=markup)


def wiki_func(article):
    wiki.set_lang("ru")
    try:
        return wiki.summary(article)
    except wiki.WikipediaException:
        return f'Статьи по запросу {article} не найдено.'


@dp.message_handler(content_types=["text"])
async def answer_user(message: types.Message):
    n = 0  # номер символа в тексте
    user_id = message.from_user.id
    if message.text.strip() == "Wikipedia":
        await message.answer("Введите название статьи, а я найду информацию по ее названию.")
    elif message.text[:2] == "-w":  # команда для работы - "-w"
        user_text = message.text[3:]
        await message.answer(f"Ваш запрос: {user_text}")
        ask = wiki_func(user_text)
        with sql.connect("telebot.db") as con:
            cur = con.cursor()
            cur.execute("""CREATE TABLE IF NOT EXISTS telebot (
            nickname TEXT,
            requests TEXT,
            error TEXT);
            """)  # создание базы данных для записи запросов пользователей
            if f'Статьи по запросу {user_text} не найдено.' in ask:
                cur.execute("""INSERT INTO telebot (nickname, requests, error) VALUES (?, ?, ?)""",
                            (user_id, user_text.lower(), "Yes"))
            else:
                cur.execute("""INSERT INTO telebot (nickname, requests, error) VALUES (?, ?, ?)""",
                            (user_id, user_text.lower(), "No"))

        for i in ask:  # проверка длины выводимого сообщения
            n += 1
            if n > 3800 and i == ".":  # если предложение закончено и n > 3800, тогда обрываем текст
                ask = ask[:n]
        else:
            ask = ask[:4000]
        await message.answer(ask)


async def main():
    await dp.start_polling()


if __name__ == "__main__":
    asyncio.run(main())
