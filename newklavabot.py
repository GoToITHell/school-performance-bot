#  parcer
from bs4 import BeautifulSoup
import aiohttp

# users
import re

# console
import logging

# tg_bot
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor

#data_base
import json as json1
import sqlite3

logging.basicConfig(level=logging.INFO)
bot = Bot(token="7597125183:AAEchXNm_t4uNf3qXmHGssUxaEnL1sj7gxc")
    # 6839790964:AAEWILCwYKZw2yQr6GX4_Jtv-o5CKUYXtgE

OWNER_ID = 2124370465
#737844465
dp = Dispatcher(bot)

object_ids = {
    '5': 1730000000016,
    '6': 1730000000016,
    '7': 1730000000016,
    '8': 1730000000016,
    '9': 1730000000016,
    '10': 1730000000256,
    '11': 1730000000256
}
date_ranges = {
    '5': ('2024-09-02T00:00:00', '2024-10-27T00:00:00'),
    '6': ('2024-09-02T00:00:00', '2024-10-27T00:00:00'),
    '7': ('2024-09-02T00:00:00', '2024-10-27T00:00:00'),
    '8': ('2024-09-02T00:00:00', '2024-10-27T00:00:00'),
    '9': ('2024-09-02T00:00:00', '2024-10-27T00:00:00'),
    '10': ('2024-09-02T00:00:00', '2024-12-29T00:00:00'),
    '11': ('2024-09-02T00:00:00', '2024-12-29T00:00:00')
}
total_date_ranges = {
    '5': ('2024-09-01', '2025-05-31'),
    '6': ('2024-09-01', '2025-05-31'),
    '7': ('2024-09-01', '2025-05-31'),
    '8': ('2024-09-01', '2025-05-31'),
    '9': ('2024-09-01', '2025-05-31'),
    '10': ('2024-09-01', '2025-05-31'),
    '11': ('2024-09-01', '2025-05-31')
}


def is_uppercase_cyrillic(s: str) -> bool:

    # Проверяем, что строка состоит только из прописных русских букв и пробелов

    return bool(re.match(r'^[А-ЯЁа-яё ]*$', s))


async def get_obj_id_by_caption(caption_number:str, data:any)->any:
    # большие словари с инфой. Если в словаре с ключом caption (цифра параллели) стоит та же параллель что и
    # цифра в caption_number - возвращает id объекта (большую цифру)
    for item in data:
        if f"{caption_number} параллель" in item['caption']:
            return item['obj_id']
    return None


async def get_obj_id_by_caption_class(caption_number:str, class_letter:any, data:any)->any:
    # большие словари с инфой. Проверяет значение "цифра-буква парааллели"
    # и возвращает id объекта (большую цифру)
    for item in data:
        if f"{caption_number} {class_letter}" in item['caption']:
            return item['obj_id']
    return None


async def get_obj_id_by_name_surname(name_surname:str, data:any)->any:
    # большие словари с инфой. Проверяет значение "имя-фамилия"
    # и возвращает id объекта (большую цифру)
    try:
        name, surname = name_surname.split()
        for item in data:
            if surname in item['caption'] and name in item['caption']:
                return item['obj_id']
        return None
    except ValueError:
        return 'Вы не написали имя или фамилию'

async def login(message:any, class_number:any, user_id:any, letter:any, full_name:any, message_replied:any, command:any)->any:
    login_url = "https://paragraph.scl511.keenetic.link/login"
    login_params = {
        "user-name": "КовОкс",
        "user-password": "ковалева"
    }
    login_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0"
    }



    async with aiohttp.ClientSession() as session:
        login_response = await session.post(login_url, params=login_params, headers=login_headers) # Объект запроса
        if login_response.status == 200:
            cookies = login_response.cookies # пиздим куки (dict)

            url = "https://paragraph.scl511.keenetic.link/webservice/app.odb/execute"

            object_id = object_ids.get(str(class_number)) #int|None
            params = {
                "action": "tree",
                "obj_id": object_id,
                "level_id": '23'
            }
            headers = {
                "Cookie": "; ".join([f"{name}={value}" for name, value in cookies.items()]),
                "Host": "paragraph.scl511.keenetic.link",
                "Referer": "https://paragraph.scl511.keenetic.link/?app=app.cj",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0"
            }

            response = await session.get(url, params=params, headers=headers)
            if response.status == 200:
                json = await response.json()  # хранятся данные с ещё большей кучей непонятной инфы {'':[{}, {}, {}], '':[{}, {}, {}]}
                data = json["data"] # хранятся данные с кучей ненужной инфы [{}, {}, {}]
                obj_id = await get_obj_id_by_caption(str(class_number), data) # Поиск параллели
                if obj_id:
                    response = await session.get(url, params={"action": "tree", "obj_id": obj_id, "level_id": '23'},
                                                 headers=headers)
                    if response.status == 200:
                        json = await response.json()
                        data = json["data"]
                        obj_id = await get_obj_id_by_caption_class(str(class_number), str(letter), data) # Поиск класса
                        if obj_id:
                            response = await session.get(url, params={"action": "tree", "obj_id": obj_id,
                                                                      "level_id": '23'},
                                                         headers=headers)
                            if response.status == 200:
                                json = await response.json()
                                data = json["data"]
                                obj_id = await get_obj_id_by_name_surname(str(full_name), data) # Поиск (проверка) имени/фамилии
                                if obj_id:
                                    url1 = "https://paragraph.scl511.keenetic.link/webservice/app.cj/execute"
                                    date_from, date_to = date_ranges.get(str(class_number), ('', ''))
                                    params1 = {
                                        "action": "report_do",
                                        "date_from": date_from,
                                        "date_to": date_to,
                                        "report_id": "7",
                                        "obj_id": obj_id,
                                        "parent_id": "1730001580058"
                                    }
                                    response1 = await session.get(url1, params=params1, headers=headers)
                                    if response1.status == 200: # Показ оценок
                                        logging.info(
                                            f"Пользователь {message.from_user.first_name} "
                                            f"{message.from_user.last_name} (ID: {user_id}) "
                                            f"гетнул данные") # Забавно что фраза появляется до показа оценок
                                        soup = BeautifulSoup(await response1.text(), 'html.parser') # парсер
                                        titles = soup.find_all('div', class_='title2')
                                        student_name = titles[0].text.strip()
                                        period = titles[1].text.strip()
                                        rows = soup.find_all('tr', class_='v')
                                        grades_text = f"{student_name}\n{period}\n\n" # выдаёт период
                                        for row in rows:
                                            subject_map = {
                                                'Алгебра и начала математического анализа': 'Алгебра',
                                                'Основы безопасности и защиты Родины': 'ОБЖ',
                                                'Физическая культура': 'Физ-ра',
                                                'Иностранный язык (английский)': 'Английский язык',
                                                'Вероятность и статистика': 'Вероятность',
                                                'Литература': 'Лит-ра',
                                                'Мировая художественная культура': 'МХК',
                                                'Труд (технология)': 'Технология',
                                                'История и культура Санкт-Петербурга': 'История СПб',
                                                'Физическая культура (плавание)': 'Плавание',
                                                'Изобразительное искусство': 'ИЗО',
                                                'Основы духовно-нравственной культуры народов России': 'ОДНКНР',
                                                'Основы религиозных культур и светской этики': 'ОРКиСЭ',
                                                'Литературное чтение': 'Лит-ое чтение',

                                            }
                                            ####### сomands
                                            if command == 'skipgrade':
                                                subject = row.find('div', class_='target journal').text.strip()
                                                subject = subject_map.get(subject, subject)
                                                grade = row.find_all('td')[4].text.strip()
                                                grades_text += f"{subject} || пропусков: {grade}\n"
                                            elif command == 'midgrade':
                                                subject = row.find('div', class_='target journal').text.strip()
                                                subject = subject_map.get(subject, subject)
                                                grade = row.find_all('td')[2].text.strip()
                                                grades_text += f"{subject} || {grade}\n"
                                            elif command == 'totalgrade':
                                                subject = row.find('div', class_='target journal').text.strip()
                                                subject = subject_map.get(subject, subject)
                                                grades = row.find_all('td')[3].find_all('div')
                                                grades_info = []
                                                for grade in grades:
                                                    period = grade['title']
                                                    score = grade.text.strip()
                                                    grades_info.append(f"\n{period} - {score}")
                                                grade_output = "".join(grades_info)
                                                grades_text += f"\n{subject} {grade_output}\n"
                                            elif command == 'allgrade':
                                                subject = row.find('div', class_='target journal').text.strip()
                                                subject = subject_map.get(subject, subject)
                                                grades = []
                                                for color in ['blue', 'violet', 'orange', 'red']:
                                                    grades.extend(
                                                        [grade.text.strip() for grade in
                                                         row.find_all('div', class_='ui circular label dl ' + color)])
                                                grades_str = ' '.join(grades)
                                                grades_text += f"{subject} || {grades_str}\n"

                                        await message_replied.edit_text(grades_text)
                                    else:
                                        await message_replied.edit_text("Произошла ошибка при выполнении команд.")
                                else:
                                    await message_replied.edit_text(
                                        "Имя и фамилия не найдены. Вероятно вы выбрали не тот"
                                        " класс или написали ваше имя и фамилию не так. "
                                        "Обратитесь к создателю - @pakistankiller")
                            else:
                                await message_replied.edit_text('Произошла ошибка, код 5') # проблема с сервером (имя-фамилия)
                        else:
                            await message_replied.edit_text('Произошла ошибка, код 4') # проблема с буквой класса и цифрой параллели
                    else:
                        await message_replied.edit_text('Произошла ошибка, код 3') # проблема  с сервером (буква класса/цифра параллели)
                else:
                    await message_replied.edit_text('Произошла ошибка, код 2') # проблема с цифрой параллели
            else:
                await message_replied.edit_text('Произошла ошибка, код 1') # проблема с сервером (цифра параллели)

# фронт работы начинается тут
# здесь создам базу данных, виртуальный курсор и прочее
data_base = sqlite3.connect('user_data.db')
curcor = data_base.cursor()
curcor.execute('CREATE TABLE IF NOT EXISTS users_data (id TEXT  NOT NULL, name TEXT  NOT NULL)')

try:
    with open("user_data.json", "r", encoding="utf-8") as file:
        user_data = json1.load(file)
except FileNotFoundError:
    user_data = {}


def load_user_data():
    with open('user_data.json', 'r', encoding='utf-8') as f:
        return json1.load(f)


@dp.message_handler(commands=['broadcast']) # декоратор, который реагирует на входящие сообщения и содержит в себе функцию ответа
async def broadcast_message(message: types.Message):
    # Проверка, что команду отправил именно вы
    count_success = 0
    count_failed = 0

    if message.from_user.id != OWNER_ID:
        await message.reply("Эта команда доступна только владельцу.")
        return

    # Получение текста сообщения, которое нужно отправить
    text_to_send = message.text[len('/broadcast '):].strip()
    if not text_to_send:
        await message.reply("Пожалуйста, укажите текст сообщения после команды.")
        return

    # Загрузка данных пользователей из файла
    user_data = load_user_data()

    # Отправка сообщения каждому пользователю
    for user_id in user_data.keys():
        try:
            await bot.send_message(user_id, text_to_send)
            count_success += 1
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {user_id}: {e}") # не все данные записываются в json??
            count_failed += 1

    await message.reply(f"Сообщение отправлено всем пользователям.\n\nУспешно - {count_success} людям\n"
                        f"Не успешно - {count_failed} ")

@dp.message_handler(commands=['getusers'])
async def getusers_message(message: types.Message):
    count = 0
    if message.from_user.id != OWNER_ID:
        await message.reply("Эта команда доступна только владельцу.")
        return

    user_data = load_user_data()

    for _ in user_data.keys():
        count += 1

    await message.reply(f"Людей использующих бота - {count}")


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    chat = message.chat.type
    if chat != 'private':
        await message.reply('Данная функция не работает в группах, только в ЛС бота')
        return
    user_id = str(message.from_user.id)
    if user_id in user_data and 'class' in user_data[user_id]:
        await message.reply("Ваш класс уже задан и не может быть изменен. Используйте команду /grade, чтобы "
                            "просмотреть свои оценки.")
        return

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("5"), KeyboardButton("6"), KeyboardButton("7"),
                 KeyboardButton("8"), KeyboardButton("9"), KeyboardButton("10"), KeyboardButton("11"))

    await message.reply("Выберите класс (от 5 до 11):", reply_markup=keyboard)


@dp.message_handler(commands=['info'])
async def get_info(message: types.Message):
    await message.reply('Создатель бота: @pakistankiller\nПо любым вопросам обращайтесь к нему.')


@dp.message_handler(commands=['totalgrade'])
async def get_user_grade(message: types.Message):
    message_replied = await message.reply(
        'Чуть подождите, начинаю получать ваши итоговые оценки по предметам, это займет от 5 до 30 '
        'секунд.')
    user_id = str(message.from_user.id)
    if user_id not in user_data:
        await message_replied.edit_text("Данные о пользователе не найдены. Напишите в ЛС боту /start")
        return

    user_info = user_data[user_id]
    class_number = user_info.get("class", "не указан")
    letter = user_info.get("letter", "не указан")
    full_name = user_info.get("name", "не указан")
    username = user_info.get("username", None)
    if username is None:
        username = message.from_user.username if message.from_user.username else 'нет'
        user_info["username"] = username if username else None
        user_data[str(user_id)] = user_info

        with open("user_data.json", "w", encoding="utf-8") as file:
            json1.dump(user_data, file, ensure_ascii=False, indent=4) # узнать что это

    name_parts = full_name.split()
    if len(name_parts) < 2:
        await message_replied.edit_text("Ошибка: имя и фамилия не указаны или указаны некорректно.")
        return
    logging.info(f"Пользователь {message.from_user.first_name} {message.from_user.last_name} (ID: {user_id}, "
                 f"@{message.from_user.username}) "
                 f"сообщил: {message.text}")

    # await message.reply(f"Класс - {class_number}, буква - {letter}, имя - {first_name}, фамилия - {last_name}.")
    # логин с куки
    await login(message, class_number, user_id, letter, full_name, message_replied, command='totalgrade')


@dp.message_handler(commands=['midgrade'])
async def get_user_grade(message: types.Message):
    message_replied = await message.reply(
        'Чуть подождите, начинаю получать ваши средние оценки по предметам, это займет от 5 до 30 секунд.')
    user_id = str(message.from_user.id)
    if user_id not in user_data:
        await message_replied.edit_text("Данные о пользователе не найдены. Напишите в ЛС боту /start")
        return

    user_info = user_data[user_id]
    class_number = user_info.get("class", "не указан")
    letter = user_info.get("letter", "не указан")
    full_name = user_info.get("name", "не указан")
    username = user_info.get("username", None)
    if username is None:
        username = message.from_user.username if message.from_user.username else 'нет'
        user_info["username"] = username if username else None
        user_data[str(user_id)] = user_info

        with open("user_data.json", "w", encoding="utf-8") as file:
            json1.dump(user_data, file, ensure_ascii=False, indent=4)

    name_parts = full_name.split()
    if len(name_parts) < 2:
        await message_replied.edit_text("Ошибка: имя и фамилия не указаны или указаны некорректно.")
        return
    logging.info(f"Пользователь {message.from_user.first_name} {message.from_user.last_name} (ID: {user_id}, "
                 f"@{message.from_user.username}) "
                 f"сообщил: {message.text}")

    # await message_replied.edit_text(f"Класс - {class_number}, буква - {letter}, имя - {first_name}, фамилия - {last_name}.")
    # логин с куки
    await login(message, class_number, user_id, letter, full_name, message_replied, command='midgrade')


@dp.message_handler(commands=['skipgrade'])
async def get_user_grade(message: types.Message):
    message_replied = await message.reply(
        'Чуть подождите, начинаю получать кол-во пропусков по предметам, это займет от'
        ' 5 до 30 секунд.')
    user_id = str(message.from_user.id)
    if user_id not in user_data:
        await message_replied.edit_text("Данные о пользователе не найдены. Напишите в ЛС боту /start")
        return

    user_info = user_data[user_id]
    class_number = user_info.get("class", "не указан")
    letter = user_info.get("letter", "не указан")
    full_name = user_info.get("name", "не указан")
    username = user_info.get("username", None)
    if username is None:
        username = message.from_user.username if message.from_user.username else 'нет'
        user_info["username"] = username if username else None
        user_data[str(user_id)] = user_info

        with open("user_data.json", "w", encoding="utf-8") as file:
            json1.dump(user_data, file, ensure_ascii=False, indent=4)

    name_parts = full_name.split()
    if len(name_parts) < 2:
        await message_replied.edit_text("Ошибка: имя и фамилия не указаны или указаны некорректно.")
        return
    first_name = name_parts[0]
    last_name = ' '.join(name_parts[1:])
    logging.info(f"Пользователь {message.from_user.first_name} {message.from_user.last_name} (ID: {user_id}, "
                 f"@{message.from_user.username}) "
                 f"сообщил: {message.text}")

    # await message_replied.edit_text(f"Класс - {class_number}, буква - {letter}, имя - {first_name}, фамилия - {last_name}.")
    # логин с куки
    await login(message, class_number, user_id, letter, full_name, message_replied, command='skipgrade')


@dp.message_handler(commands=['allgrade'])
async def get_user_grade(message: types.Message):
    message_replied = await message.reply('Чуть подождите, начинаю получать ваши оценки, это займет от 5 до 30 секунд.')
    user_id = str(message.from_user.id)
    if user_id not in user_data:
        await message_replied.edit_text("Данные о пользователе не найдены. Напишите в ЛС боту /start")
        return

    user_info = user_data[user_id]
    class_number = user_info.get("class", "не указан")
    letter = user_info.get("letter", "не указан")
    full_name = user_info.get("name", "не указан")
    username = user_info.get("username", None)
    if username is None:
        username = message.from_user.username if message.from_user.username else 'нет'
        user_info["username"] = username if username else None
        user_data[str(user_id)] = user_info

        with open("user_data.json", "w", encoding="utf-8") as file:
            json1.dump(user_data, file, ensure_ascii=False, indent=4)

    name_parts = full_name.split()
    if len(name_parts) < 2:
        await message_replied.edit_text("Ошибка: имя и фамилия не указаны или указаны некорректно.")
        return
    logging.info(f"Пользователь {message.from_user.first_name} {message.from_user.last_name} (ID: {user_id}, "
                 f"@{message.from_user.username}) "
                 f"сообщил: {message.text}")

    # await message_replied.edit_text(f"Класс - {class_number}, буква - {letter}, имя - {first_name}, фамилия - {last_name}.")
    # логин с куки
    await login(message, class_number, user_id, letter, full_name, message_replied, command='allgrade')


@dp.message_handler(commands=['grade'])
async def get_user_grade(message: types.Message):
    await message.reply('Вышло обновление бота\nНовые команды:\n/allgrade - вывод всех оценок\n/midgrade - вывод '
                        'средних баллов\n/skipgrade - вывод кол-ва пропусков по предметам')


@dp.message_handler(
    lambda message: message.text.isdigit() and int(message.text) in range(5, 12) and message.chat.type == "private")
async def choose_class(message: types.Message):
    chat = message.chat.type
    if chat != 'private':
        await message.reply('Данная функция не работает в группах, только в ЛС бота')
        return
    user_id = message.from_user.id
    user_info = user_data.get(str(user_id), {})
    if "class" in user_info:
        await message.reply("Ваш класс уже задан и не может быть изменен.")
        return

    if int(message.text) in range(5, 12):
        user_info["class"] = int(message.text)
    else:
        await message.reply('От 5 до 11')
    user_data[str(user_id)] = user_info

    class_letters = {
        5: 'АБВГДЕЖ',
        6: 'АБВГДЕЖЭ',
        7: 'АБВГДЕЖ',
        8: 'АБВГДЕЖ',
        9: 'АБВГДЕЖЗЭ',
        10: 'АБВГ',
        11: 'АБВГД'
    }
    class_number = int(message.text)
    letters = class_letters.get(class_number, '')

    # Изменить создание клавиатуры для выбора буквы класса
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    row = []
    for letter in letters:
        row.append(KeyboardButton(letter))
        if len(row) == 3:
            keyboard.row(*row)
            row = []
    if row:
        keyboard.row(*row)

    await message.reply("Выберите букву класса:", reply_markup=keyboard)


@dp.message_handler(
    lambda message: message.text.isalpha() and len(message.text) == 1 and message.chat.type == "private")
async def choose_letter(message: types.Message):
    chat = message.chat.type
    if chat != 'private':
        return
    user_id = message.from_user.id
    user_info = user_data.get(str(user_id), {})
    if "letter" in user_info:
        await message.reply("Буква вашего класса уже выбрана и не может быть изменена.")
        return

    user_info["letter"] = message.text.lower()
    user_data[str(user_id)] = user_info

    await message.reply("Введите ваше имя и фамилию:")
    await message.reply("Используйте формат 'Полное Имя Полная Фамилия'")


@dp.message_handler(content_types=['text'])
async def save_user_data(message: types.Message):
    chat = message.chat.type
    if chat != 'private':
        return
    user_id = message.from_user.id
    username = message.from_user.username if message.from_user.username else None
    user_info = user_data.get(str(user_id), {})
    text = message.text.strip()

    if "name" in user_info:
        await message.reply("Ваше имя и фамилия уже указаны и не могут быть изменены.")
        return

    if len(text.split()) == 2:
        if all(is_uppercase_cyrillic(name) for name in text.split()):
            name = text
            if not name:
                await message.reply("Пожалуйста, введите ваше имя и фамилию.")
                return

            for data in user_data.values():
                if "name" in data and data["name"] == name:
                    await message.reply("Такой пользователь уже существует в базе данных. Пожалуйста, введите "
                                        "другое имя и фамилию.")
                    return

            user_info["name"] = name
            user_info["username"] = username if username else 'нет'
            user_data[str(user_id)] = user_info

            with open("user_data.json", "w", encoding="utf-8") as file:
                json1.dump(user_data, file, ensure_ascii=False, indent=4)

            await message.reply("Данные успешно сохранены!")
        else:
            await message.reply('Пишите имя и фамилию только русскими буквами')
    else:
        await message.reply('Имя и фамилию в формате "Имя Фамилия"')

data_base.close()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
