import os

import logging
import requests
import time
import telegram

# from telegram import ReplyKeyboardMarkup
# from telegram.ext import CommandHandler, Updater

from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv('TOKEN_YP')
TELEGRAM_TOKEN = os.getenv('TOKEN_TG')
TELEGRAM_CHAT_ID = os.getenv('TG_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    bot.send_message(TELEGRAM_CHAT_ID, message)


def get_api_answer(current_timestamp):
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': 0}

    response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    response = response.json()

    return response


def check_response(response):
    if len(response) == 2 and 'homeworks' in response and 'current_date' in response:
        list_hm = response.get('homeworks')
        return list_hm
    return False


def parse_status(homework):
    homework_name = homework.get("homework_name")
    homework_status = homework.get("status")

    if homework_status == 'approved':
        verdict = HOMEWORK_STATUSES.get('approved')
    elif homework_status == 'reviewing':
        verdict = HOMEWORK_STATUSES.get('reviewing')
    elif homework_status == 'rejected':
        verdict = HOMEWORK_STATUSES.get('rejected')

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    if PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        return True
    else:
        return False


def main():
    """Основная логика работы бота."""

    ...

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    # current_timestamp = int(time.time())
    current_timestamp = 0
    response = get_api_answer(current_timestamp)
    homework = check_response(response)[0]
    message = parse_status(homework)
    # print(message)
    send_message(bot, message)
    current_timestamp = response.get("current_date")
    # time.sleep(RETRY_TIME)

    # while True:
    #     try:
    #         response = get_api_answer(current_timestamp)
    #         homework = check_response(response)[0]
    #         message = parse_status(homework)
    #         send_message(bot, message)
    #         current_timestamp = ...
    #         time.sleep(RETRY_TIME)

    #     except Exception as error:
    #         message = f'Сбой в работе программы: {error}'
    #         ...
    #         time.sleep(RETRY_TIME)
    #     else:
    #         ...


if __name__ == '__main__':
    main()
