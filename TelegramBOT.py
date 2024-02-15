import random
import sqlite3
import threading
import time
from datetime import datetime, timedelta

import telebot



bot = telebot.TeleBot("6856299992:AAHZ3qNfgkG4yXhlSDeYkKfP0Rqab57Xvlo")


def create_tables():
    # Создаем подключение к базе данных
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Создаем таблицу пользователей, если она не существует
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       name TEXT NOT NULL,
                       telegram_id INTEGER UNIQUE NOT NULL)''')

    # Создаем таблицу участников сегодня, если она не существует
    cursor.execute('''CREATE TABLE IF NOT EXISTS today_participants
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       user_id INTEGER UNIQUE NOT NULL,
                       points INTEGER,
                       last_request_time DATETIME,
                       request_count INTEGER)''')

    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()


def add_participant(name, telegram_id):
    text = ""
    # Создаем подключение к базе данных
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Проверяем, существует ли пользователь в таблице пользователей
    cursor.execute("SELECT id FROM users WHERE telegram_id=?", (telegram_id,))
    user = cursor.fetchone()
    if not user:
        # Если пользователь не существует, добавляем его в таблицу пользователей
        cursor.execute("INSERT INTO users (name, telegram_id) VALUES (?, ?)", (name, telegram_id))
        conn.commit()
        user_id = cursor.lastrowid
    else:
        # Если пользователь уже существует, получаем его id
        user_id = user[0]

        # Проверяем, существует ли участник в таблице участников сегодня
    cursor.execute("SELECT id, request_count FROM today_participants WHERE user_id=?", (user_id,))
    today_participant = cursor.fetchone()
    if not today_participant:
        # Если участника нет в таблице, добавляем его
        cursor.execute(
            "INSERT INTO today_participants (user_id, points, last_request_time, request_count) VALUES (?, ?, ?, ?)",
            (user_id, 0, datetime.now(), 0))
        text += "Ты участвуешь! Список участников:\n"
        text += list_participant(cursor)
        conn.commit()
        conn.close()
        return text

    else:
        text += add_point_to_random_participant(cursor, user_id)
        text += list_participant(cursor)
        conn.commit()
        conn.close()
        return text


def remove_participant(telegram_id):
    # Создаем подключение к базе данных
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Получаем ID пользователя по его telegram_id
    cursor.execute("SELECT id FROM users WHERE telegram_id=?", (telegram_id,))
    user = cursor.fetchone()
    if not user:
        print("Пользователь не найден")
        conn.close()
        return

    user_id = user[0]

    # Удаляем участника из таблицы участников сегодня
    cursor.execute("DELETE FROM today_participants WHERE user_id=?", (user_id,))
    conn.commit()
    print("Участник успешно удален")

    # Закрываем соединение
    conn.close()


def list_participant(cursor):
    text = ""
    # Получаем список участников, количество их очков и количество запросов
    cursor.execute("SELECT users.name, today_participants.points, today_participants.request_count FROM "
                   "today_participants INNER JOIN users ON today_participants.user_id=users.id")
    participants = cursor.fetchall()
    for participant in participants:
        name, points, request_count = participant
        text += f"Участник: {name}, Очки: {points}, Количество запросов: {request_count}\n"
    return text


def add_point_to_random_participant(cursor, user_id):
    text = ""
    current_time = datetime.now()
    timeInMinute = 15
    # Проверяем условие: должно пройти больше 2 минут с момента первого запроса
    cursor.execute("SELECT MAX(last_request_time) FROM today_participants")
    last_request_time = cursor.fetchone()[0]  # получаем время первого запроса
    if last_request_time and (
            current_time - datetime.strptime(last_request_time[:19], "%Y-%m-%d %H:%M:%S")) < timedelta(
            minutes=timeInMinute):
        remaining_time = timedelta(minutes=timeInMinute) - (
                    current_time - datetime.strptime(last_request_time[:19], "%Y-%m-%d %H:%M:%S"))
        remaining_minutes = int(remaining_time.total_seconds() // 60)
        remaining_seconds = int(remaining_time.total_seconds() % 60)
        text += "Должно пройти больше 15 минут с момента первого запроса. Осталось времени: {:02d}:{:02d}\n".format(
            remaining_minutes, remaining_seconds)
    else:
        cursor.execute("UPDATE today_participants SET last_request_time = ?, request_count = request_count + 1 WHERE "
                       "user_id = ?", (current_time, user_id,))
        # Выбираем случайного участника среди всех участников
        cursor.execute("SELECT users.name, today_participants.user_id FROM today_participants INNER JOIN users ON "
                       "today_participants.user_id=users.id")
        participants = cursor.fetchall()
        random_participant_name = random.choice(participants)[0]
        random_participant_id = random.choice(participants)[1]  # выбираем случайного участника

        # Добавляем очко выбранному случайному участнику
        cursor.execute("UPDATE today_participants SET points = points + 1 WHERE user_id = ?", (random_participant_id,))
        text += f"Очко добавлено участнику = {random_participant_name} \n"
    return text


def check_time_and_choose_winner():
    while True:
        current_time = datetime.now().strftime("%H:%M")  # получаем текущее время в формате HH:MM

        # Создаем подключение к базе данных
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        message = ""

        # Проверяем, сходится ли текущее время с заданным временем
        if current_time == "17:45":  # замените "12:00" на желаемое время
            # Получаем список участников, количество их очков и количество запросов
            cursor.execute("SELECT users.name, users.telegram_id FROM "
                           "today_participants INNER JOIN users ON today_participants.user_id=users.id")
            participants = cursor.fetchall()

            # Получаем участника(ов) с наибольшим количеством очков
            cursor.execute(
                "SELECT users.name, users.telegram_id, today_participants.points FROM today_participants INNER JOIN users ON "
                "today_participants.user_id=users.id WHERE today_participants.points = "
                "(SELECT MAX(points) FROM today_participants)")
            winners = cursor.fetchall()
            if len(winners) == 1:
                winner_name: object = winners[0][0]
                winne_chat_id: object = winners[0][1]
                message += f"Сегодня упырь дня - {winner_name}! Поздравляю! "
                bot.send_message(winne_chat_id, f"Поздравляем, {winner_name}! Вы упырь!\n")

            else:
                print('else')
                winner = random.choice(winners)
                winner_name: object = winner[0]
                winne_chat_id: object = winners[0][1]
                message += f"Сегодня упырь дня - {winner_name}! Позравляю! "
                bot.send_message(winne_chat_id, f"Поздравляем, {winner_name}! Вы упырь!\n")

            cursor.execute("DROP TABLE today_participants")  # удаляем таблицу участников сегодня
            conn.commit()
            conn.close()

            message += "Участники: \n"
            for participant in participants:
                name, telegram_id = participant
                message += f"{name}\n"

            for participant in participants:
                bot.send_message(participant[1], message)

        print(current_time)
        time.sleep(60)  # здесь 60 означает 60 секунд, то есть 1 минута


create_tables()

# Запускаем функцию проверки времени в отдельном потоке
time_thread = threading.Thread(target=check_time_and_choose_winner)
time_thread.start()


@bot.message_handler(commands=['who'])
def main(message):
    # remove_participant(123456)
    username = str(message.from_user.first_name)
    chat_id = int(message.chat.id)
    bot.send_message(message.chat.id, add_participant(username, chat_id))
    print("из бота")


# bot.polling(none_stop=True)

# Запускаем бота в отдельном потоке
bot_thread = threading.Thread(target=bot.polling, kwargs={"none_stop": True})
bot_thread.start()
