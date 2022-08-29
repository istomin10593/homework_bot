import logging.config
import requests
import os
import sys
import telegram
import time

from dotenv import load_dotenv
from http import HTTPStatus
from exeption import HTTPStatusError

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


def send_message(bot: telegram.Bot, message: str) -> None:
    """Send message in Telegram bot."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception as error:
        logging.error(f'Message sending error: {error}')
    else:
        logging.info('Message successfully sent')


def get_api_answer(current_timestamp: int) -> dict:
    """Send request to API and get response."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}

    response = requests.get(ENDPOINT, headers=HEADERS, params=params)

    if response.status_code != HTTPStatus.OK:
        logging.error(
            f'Not available ENDPOINT:{ENDPOINT}.'
            f'Status code: {response.status_code}')
        raise HTTPStatusError(response)
    else:
        return response.json()


def check_response(response: dict) -> list:
    """Check response from API."""
    if not isinstance(response, dict):
        message = f'Expected type data - dict, received - {type(response)}'
        logging.error(message)
        raise TypeError(message)

    if response == {}:
        message = 'Response contains empty dict'
        logging.error(message)
        raise KeyError(message)

    if not isinstance(response.get('homeworks'), list):
        type_responce = type(response.get('homeworks'))
        message = f'Expected type data - list, received - {type_responce}'
        logging.error(message)
        raise TypeError(message)

    if ('current_date' in response) and ('homeworks' in response):
        return response.get('homeworks')
    else:
        message = 'Missing expected keys in API response'
        logging.error(message)
        raise KeyError(message)


def parse_status(homework):
    """Handle data from homework and return message with status."""
    homework_name = homework.get("homework_name")
    homework_status = homework.get("status")

    try:
        verdict = HOMEWORK_STATUSES[homework_status]
    except Exception as error:
        message = f'''Homework status in response
        from API does not exist {error}'''
        logging.error(message)
        raise KeyError(message)
    else:
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Check necessary environment variables."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def main():
    """Main function."""
    storage_messages = {}
    storage_errors = {}

    if not check_tokens():
        logging.critical('''
        Missing required environment variables.
         There are  examples environment variables
         in the file ".env.example".''')
        exit()

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if len(homeworks) == 0:
                logging.debug('No homeworks to check.')
                break
            for homework in homeworks:
                message = parse_status(homework)
                if storage_messages.get(homework['homework_name']) != message:
                    send_message(bot, message)
                    storage_messages[homework['homework_name']] = message
            current_timestamp = response.get('current_date')
        except Exception as error:
            message = f'Program error: {error}'
            for save_error in storage_errors:
                if storage_errors[save_error] != message:
                    logging.error(message)
                    send_message(bot, message)
                    storage_errors[str(error)] = message
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stdout
    )
    main()
