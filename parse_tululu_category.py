import argparse
import json
import os
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from tqdm import tqdm

from main import download_img, download_txt, get_book_comments
from main import get_book_description, get_book_genres, logger, response_handler

load_dotenv()


def create_parser():
    """Парсер аргументов запуска скрипта."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--start_page', help='Начальная страница', required=True, type=int)
    parser.add_argument(
        '--end_page',
        help='Конечная страница',
        type=int,
        default=702,  # не совсем понятно как ограничивать. парсить начальную страницу и смотреть сколько всего их?
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
    """Получение списка относительных адресов книг."""
    response = response_handler(url)
    soup = BeautifulSoup(response.text, 'lxml')
    selector = '.tabs .d_book .bookimage a'
    tags = soup.select(selector)
    if not tags:
        return None
    return [tag['href'] for tag in tags]


if __name__ == '__main__':
    parser = create_parser()
    namespace = parser.parse_args()
    logger.info(f'Start parsing with params: {namespace}')
    path, filename = os.path.split(namespace.json_path)
    os.makedirs(path, exist_ok=True)
    # Если указан путь только к директории json файла то имя файла возьмем из переменной окружения.
    if not filename:
        filename = os.getenv('FILE_NAME', 'description.json')
    books = []
    for page in range(namespace.start_page, namespace.end_page):
        url = f'https://tululu.org/l55/{page}'
        book_rel_urls = get_rel_book_urls(url)
        if not book_rel_urls:
            break
        for rel_url in tqdm(book_rel_urls):
            abs_url = urljoin(url, rel_url)
            title, author = get_book_description(abs_url)
            img_src = None if namespace.skip_imgs else download_img(abs_url, namespace.dest_folder)
            book_id = rel_url.split('/b')[-1]
            book_url = f'https://tululu.org/txt.php?id={book_id}'
            book_path = None if namespace.skip_txt else download_txt(book_url, title, namespace.dest_folder)
            comments = get_book_comments(abs_url)
            genres = get_book_genres(abs_url)
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
