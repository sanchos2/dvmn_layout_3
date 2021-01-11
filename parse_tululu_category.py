import argparse
import json
import logging.config  # noqa: WPS301
import os
from urllib.parse import urljoin

import requests
import urllib3
import yaml
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from tqdm import tqdm

from main import download_img, download_txt, get_book_comments  # noqa: I001
from main import get_book_description, get_book_genres, get_response  # noqa: I001

load_dotenv()
logger = logging.getLogger('parser')


def create_parser():
    """Создание аргументов запуска скрипта."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--start_page', help='Начальная страница', required=True, type=int)
    parser.add_argument(
        '--end_page',
        help='Конечная страница',
        type=int,
        default=os.getenv('END_PAGE'),
    )
    parser.add_argument('--dest_folder', help='Путь к каталогу с результатами парсинга', default=os.getcwd())
    parser.add_argument('--skip_imgs', help='Не скачивать картинки', action='store_true')
    parser.add_argument('--skip_txt', help='Не скачивать книги', action='store_true')
    parser.add_argument(
        '--json_path',
        help='Путь к json файлу с результатами парсинга',
        default=os.path.join(os.getcwd(), os.getenv('JSON_FILE_NAME', 'description.json')),
    )
    return parser


def get_rel_book_urls(url):
    """Получает список относительных адресов книг."""
    response = get_response(url)
    soup = BeautifulSoup(response.text, 'lxml')
    tags = soup.select('.tabs .d_book .bookimage a')
    if not tags:
        return None
    return [tag['href'] for tag in tags]


def configure_logging():
    """Конфигурирует работу логгера."""
    try:
        with open(os.getenv('LOG_CONFIG'), 'r') as log_config:
            config = yaml.safe_load(log_config.read())
            logging.config.dictConfig(config)
    except FileNotFoundError as error:
        logging.basicConfig(level=logging.ERROR)
        logger.error(error, exc_info=False)


if __name__ == '__main__':
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    configure_logging()
    parser = create_parser()
    namespace = parser.parse_args()
    logger.info(f'Start parsing with params: {namespace}')
    path, filename = os.path.split(namespace.json_path)
    os.makedirs(path, exist_ok=True)
    if not filename:
        filename = os.getenv('FILE_NAME', 'description.json')
    books = []
    for page in range(namespace.start_page, namespace.end_page):
        url = f'https://tululu.org/l55/{page}'
        try:
            book_rel_urls = get_rel_book_urls(url)
        except requests.exceptions.HTTPError as error:
            logger.error(error, exc_info=True)
            continue
        for rel_url in tqdm(book_rel_urls):
            abs_url = urljoin(url, rel_url)
            try:
                response = get_response(abs_url)
            except requests.exceptions.HTTPError as error:  # noqa: WPS440
                logger.error(error, exc_info=True)
                continue
            soup = BeautifulSoup(response.text, 'lxml')
            title, author = get_book_description(soup)
            comments = get_book_comments(soup)
            genres = get_book_genres(soup)
            if namespace.skip_imgs:
                img_src = None
            else:
                try:
                    img_src = download_img(abs_url, namespace.dest_folder)
                except requests.exceptions.HTTPError as error:  # noqa: WPS440
                    logger.error(error, exc_info=True)
                    continue
            book_url = f'https://tululu.org/txt.php?id={rel_url.split("/b")[-1]}'
            if namespace.skip_txt:
                book_path = None
            else:
                try:
                    book_path = download_txt(book_url, title, namespace.dest_folder)
                except requests.exceptions.HTTPError as error:  # noqa: WPS440
                    logger.error(error, exc_info=True)
                    continue
            specification = {
                'title': title,
                'author': author,
                'img_src': img_src,
                'book_path': book_path,
                'comments': comments,
                'genres': genres,
            }
            books.append(specification)

    with open(os.path.join(path, filename), 'w', encoding='utf8') as metadata:
        json.dump(books, metadata, ensure_ascii=False)
        logger.info(f'Parsing {len(books)} items done!')
