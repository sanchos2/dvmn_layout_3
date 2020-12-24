import logging
import os

from logging.handlers import RotatingFileHandler
from urllib.parse import urljoin

import requests
import urllib3

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from pathvalidate import sanitize_filename

load_dotenv()

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(  # noqa: WPS110
    os.getenv('LOG_FILE_NAME', 'parser.log'),
    maxBytes=102400,  # noqa: WPS432
    backupCount=3,
)
formatter = logging.Formatter('%(asctime)s %(process)d %(levelname)s %(message)s')  # noqa: WPS323
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_response(url):
    """Функция для получения ответа на запрос по url."""
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0',
    }
    response = requests.get(url=url, headers=headers, verify=False)  # noqa: S501
    response.raise_for_status()
    return response


def response_handler(url):
    """Функция обработки ответа на запрос."""
    try:
        response = get_response(url)
    except requests.HTTPError as err:
        logger.error(err, exc_info=True)
    else:
        return response


def get_book_description(url):
    """Функция для парсинга названия книги и автора."""
    response = response_handler(url)
    soup = BeautifulSoup(response.text, 'lxml')
    selector = '.ow_px_td h1'
    title = soup.select_one(selector)
    return [text.strip() for text in title.text.split('::')]


def get_book_genres(url):
    """Функция получения жанров книги."""
    response = response_handler(url)
    soup = BeautifulSoup(response.text, 'lxml')
    selector = '.ow_px_td span.d_book a'
    raw_genres = soup.select(selector)
    if not raw_genres:
        return None
    genres = []
    for genre in raw_genres:
        genres.append(genre.text)
    return genres


def get_book_comments(url):
    """Функция для скачивания коментариев к книге."""
    response = response_handler(url)
    soup = BeautifulSoup(response.text, 'lxml')
    selector = '.texts span'
    comment_tags = soup.select(selector)
    if not comment_tags:
        return None
    comments = []
    for comment in comment_tags:
        comments.append(comment.text)
    return comments


def download_img(url, path, folder='image/'):
    """Функция для скачивания обложек."""
    directory = os.path.join(path, folder)
    os.makedirs(directory, exist_ok=True)
    response = response_handler(url)
    soup = BeautifulSoup(response.text, 'lxml')
    selector = '.bookimage img'
    img = soup.select_one(selector)
    if not img:
        return None
    abs_img_url = urljoin('https://tululu.org/', img['src'])
    img_name = abs_img_url.split('/')[-1]
    path_to_file = os.path.join(directory, img_name)
    raw_img = response_handler(abs_img_url)
    with open(path_to_file, 'wb') as image:
        image.write(raw_img.content)
    return path_to_file


def download_txt(url, filename, path, folder='books/'):
    """Функция для скачивания текстовых файлов."""
    directory = os.path.join(path, folder)
    os.makedirs(directory, exist_ok=True)
    filename = sanitize_filename(filename)
    response = response_handler(url)
    path_to_file = os.path.join(directory, f'{filename}.txt')
    if response.headers['Content-Type'] == 'text/plain; charset="utf-8"':
        with open(path_to_file, 'w', encoding='utf8') as book:
            book.write(response.text)
    return path_to_file
