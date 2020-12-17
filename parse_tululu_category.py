import argparse
import json
import os
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from tqdm import tqdm

from main import download_img, download_txt, get_book_comments
from main import get_book_description, get_book_genres, get_response

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
        default=os.path.join(os.getcwd(), os.getenv('FILE_NAME', 'description.json')),
    )
    return parser


def get_rel_url(url):
    """Получение списка id книг."""
    response = get_response(url)
    soup = BeautifulSoup(response.text, 'lxml')
    selector = '.tabs .d_book .bookimage a'
    raw_ids = soup.select(selector)
    return [_['href'] for _ in raw_ids]


if __name__ == '__main__':
    parser = create_parser()
    namespace = parser.parse_args()
    content_path = namespace.dest_folder
    skip_imgs = namespace.skip_imgs
    skip_txt = namespace.skip_txt
    json_path = namespace.json_path
    os.makedirs(os.path.split(json_path)[0], exist_ok=True)
    # Если указан путь только к директории json файла то имя файла возьмем из переменной окружения.
    if not os.path.split(json_path)[1]:
        json_path = os.path.join(json_path, os.getenv('FILE_NAME', 'description.json'))
    books_description = []
    for page in range(namespace.start_page, namespace.end_page):
        url = f'https://tululu.org/l55/{page}'
        books_rel_url = get_rel_url(url)
        for rel_url in tqdm(books_rel_url):
            abs_url = urljoin('https://tululu.org/', rel_url)
            description = get_book_description(abs_url)
            title = description[0]
            author = description[1]
            img_src = None if skip_imgs else download_img(abs_url, content_path)
            book_url = f'http://tululu.org/txt.php?id={rel_url[2:]}'
            book_path = None if skip_txt else download_txt(book_url, title, content_path)
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
            books_description.append(specification)

    with open(json_path, 'w', encoding='utf8') as metadata:
        json.dump(books_description, metadata, ensure_ascii=False)
