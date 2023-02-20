import requests
import os
from http import HTTPStatus
from datetime import datetime

from django.contrib.auth import get_user_model
from mems.models import Mem
from dotenv import load_dotenv

from utils.data import TEST_DATA_USER
from utils.exception import (HTTPStatusNotOK, EnvironmentVar,
                             JSONError, RequestError)

load_dotenv()
User = get_user_model()
TOKEN_VK_API = os.getenv('TOKEN_VK_API')

# Указать группу для загрузки картинок
DOMAIN = 'memepediaru'
# установите True если хотите удалить данные о пользователях:
ERASE_USER = False
# установите True если хотите удалить данные о мемах:
ERASE_MEM = False
# Указать количество создаваемых мемов
COUNT_MEM = 200


def check_tokens():
    """Проверяет доступность переменных окружения."""
    return TOKEN_VK_API


def get_api_answer(domain, count, offset=0, version='5.120'):
    """Делает запрос к API-сервиса.
    В качестве параметра функция получает слово с для поиска.
    В случае успешного запроса возвращает ответ API, преобразовав его
    из формата JSON к типам данных Python."""
    try:
        response = requests.get('https://api.vk.com/method/wall.get',
                                params={
                                    'access_token': TOKEN_VK_API,
                                    'v': version,
                                    'domain': domain,
                                    'count': count,
                                    'offset': offset,
                                })
        if response.status_code != HTTPStatus.OK:
            raise HTTPStatusNotOK(
                f'API вернул код отличный от 200: {response.status_code}!')
        data = response.json()
    except HTTPStatusNotOK as error:
        raise HTTPStatusNotOK(
            'API вернул код отличный от 200',
            f'Статус: {response.status_code}!') from error
    except ConnectionError as error:
        raise ConnectionError(
            'Произошла ошибка при попытке запроса') from error
    except requests.exceptions.JSONDecodeError as error:
        raise JSONError(
            f'Сбой декодирования JSON из ответа: {response}') from error
    except requests.exceptions.RequestException as error:
        raise RequestError(
            'Ошибка вызванная request. При попытке сделать') from error
    else:
        return data


def check_response_get_img(response):
    """Проверяет ответ API на корректность.
    Если ответ API соответствует ожиданиям,
    то функция список ссылок с картинками.
    """
    img_url = []
    try:
        if not response:
            return False
        data = response['response']['items']
        for post in data:
            img_url.extend(
                attachment['photo']['sizes'][3]['url']
                for attachment in post['attachments']
                if attachment['type'] == 'photo'
            )
        return img_url
    except TypeError as error:
        raise TypeError('Неверный тип переменных') from error


def create_mem_to_bd(img_data):
    """Создает объекты типа Mem"""
    successful = 0
    failed = 0
    try:
        for img in img_data:
            id = datetime.now().strftime('%Y_%m_%d_%M_%S_%f')
            response = requests.get(img)
            with open(
                    f'likes_mems/media/images/img{id}.jpg', "wb") as img_file:
                img_file.write(response.content)
                mem, s = Mem.objects.get_or_create(
                    name=f'Мем №{id}',
                    image=f'/images/img{id}.jpg',
                    author=User.objects.order_by('?').first())
            if s:
                successful += 1
                print(f'Объект успешно создан {mem}:')
    except Exception as error:
        print(f'Не удалось создать объект. Ошибка: {error}')
        failed += 1
    print(
        f'Успешно созданных объектов типа {Mem.__name__}:'
        f'{successful}, ошибок: {failed}.')


def create_test_user_to_bd(data_user):
    """Создает объекты типа User"""
    successful = 0
    failed = 0
    try:
        for data in data_user:
            _, s = User.objects.get_or_create(
                username=data[0],
                password=data[1],
                first_name=data[2],
                last_name=data[3],
                email=data[4])
            if s:
                successful += 1
    except Exception as error:
        print(f'Не удалось создать объект. Ошибка: {error}')
        failed += 1
    print(
        f'Успешно созданных объектов типа {User.__name__}:'
        f'{successful}, ошибок: {failed}.'
    )


def del_objects(type_obj):
    """Удаляет записи из базы данных указанного типа"""
    type_obj.objects.all().delete()
    print(f'Все записи типа {type_obj.__name__} удалены.')


def main():
    """Основная логика"""
    if ERASE_USER:
        del_objects(User)
    if ERASE_MEM:
        del_objects(Mem)
    create_test_user_to_bd(TEST_DATA_USER)
    offset = 0
    while True:
        response = get_api_answer(DOMAIN, COUNT_MEM, offset=offset)
        img_data = check_response_get_img(response)
        if len(img_data) > COUNT_MEM:
            img_data = img_data[:COUNT_MEM]
            break
        offset += COUNT_MEM
    create_mem_to_bd(img_data)


def run():
    if not check_tokens():
        raise EnvironmentVar('Отсутствуют обязательные переменные окружения')
    try:
        main()
    except Exception as error:
        print(f'Сбой в работе программы. Ошибка:{error}')
