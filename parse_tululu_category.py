import argparse
import json
import os
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from main import download_img, download_txt, get_comments
from main import get_filename, get_genres, get_response


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
    parser.add_argument('--json_path', help='Путь к json файлу с результатами парсинга', default=os.getcwd())
    return parser


def get_books_ids(url):
    """Получение списка id книг."""
    response = get_response(url)
    soup = BeautifulSoup(response.text, 'lxml')
    selector = '.tabs .d_book .bookimage a'
    raw_ids = soup.select(selector)
    return [_['href'] for _ in raw_ids]


if __name__ == '__main__':
    parser = create_parser()
    namespace = parser.parse_args()
    path = namespace.dest_folder
    skip_imgs = namespace.skip_imgs
    skip_txt = namespace.skip_txt
    json_path = namespace.json_path
    os.makedirs(json_path, exist_ok=True)
    description_file = os.path.join(json_path, 'description.json')
    books_description = []
    for page in range(namespace.start_page, namespace.end_page):
        url = f'https://tululu.org/l55/{page}'
        books = get_books_ids(url)
        for book in books:
            link = urljoin('https://tululu.org/', book)
            description = get_filename(link)
            title = description[0]
            author = description[1]
            img_src = None if skip_imgs else download_img(link, path)
            book_url = f'http://tululu.org/txt.php?id={book[2:]}'
            book_path = None if skip_txt else download_txt(book_url, title, path)
            comments = get_comments(link)
            genres = get_genres(link)
            specification = {
                'title': title,
                'author': author,
                'img_src': img_src,
                'book_path': book_path,
                'comments': comments,
                'genres': genres,
            }
            books_description.append(specification)

    with open(description_file, 'w', encoding='utf8') as metadata:
        json.dump(books_description, metadata, ensure_ascii=False)
