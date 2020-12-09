import argparse
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

from main import download_img, download_txt, get_comments, get_genres, get_filename, get_response


def create_parser():
    parser = argparse.ArgumentParser(
        description='Закачиватель книжек ;)'
    )
    parser.add_argument(
        '--start_page',
        help='Начальная страница',
        required=True,
        type=int,
    )
    parser.add_argument(
        '--end_page',
        help='Конечная страница',
        type=int,
        default=702,  # не совсем понятно как ограничивать. парсить начальную страницу и смотреть сколько всего их?
    )
    return parser


def get_books_ids(url):
    response = get_response(url)
    soup = BeautifulSoup(response.text, 'lxml')
    selector = '.tabs .d_book .bookimage a'
    raw_ids = soup.select(selector)
    ids = [item['href'] for item in raw_ids]
    return ids


if __name__ == '__main__':
    parser = create_parser()
    namespace = parser.parse_args()

    books_description = []
    for page in range(namespace.start_page, namespace.end_page):
        url = f'https://tululu.org/l55/{page}'
        ids = get_books_ids(url)
        for id in ids:
            link = urljoin('https://tululu.org/', id)
            print(link)
            description = get_filename(link)
            title = description[0]
            author = description[1]
            img_src = download_img(link)
            book_url = f'http://tululu.org/txt.php?id={id[2:]}'
            book_path = download_txt(book_url, title)
            comments = get_comments(link)
            genres = get_genres(link)
            book = {
                'title': title,
                'author': author,
                'img_src': img_src,
                'book_path': book_path,
                'comments': comments,
                'genres': genres,
            }
            books_description.append(book)
    with open('description.json', 'w', encoding='utf8') as file:
        json.dump(books_description, file, ensure_ascii=False)

