from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

from main import download_img, download_txt, get_comments, get_genres, get_filename, get_response


def get_books_ids(url):
    response = get_response(url)
    soup = BeautifulSoup(response.text, 'lxml')
    try:
        raw_ids = soup.find('table', class_='tabs').find_all('table', class_='d_book')
    except AttributeError:
        return None
    ids = []
    for item in raw_ids:
        id = item.find('div', class_='bookimage').find('a')['href']
        ids.append(id)
    return ids


if __name__ == '__main__':
    books_description = []
    for page in range(1, 5):
        url = f'https://tululu.org/l55/{page}'
        ids = get_books_ids(url)
        for id in ids:
            link = urljoin('https://tululu.org/', id)
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

