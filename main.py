from bs4 import BeautifulSoup
import requests
import os
from tqdm import tqdm
import urllib3
from pathvalidate import sanitize_filename


def get_response(url):
    """Функция для получения ответа на запрос по url."""
    urllib3.disable_warnings()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0',
    }
    response = requests.get(url=url, headers=headers, verify=False)
    try:
        response.raise_for_status()
    except requests.HTTPError:
        return None
    if response != 301:
        return response
    elif response == 301:
        new_url = response.headers['Location']
        get_response(new_url)


def get_filename(url):
    """Функция для парсинга названия книги."""
    response = get_response(url)
    soup = BeautifulSoup(response.text, 'lxml')
    title = soup.find('td', class_='ow_px_td').find('h1')
    return [text.strip() for text in title.text.split('::')][0]


def download_txt(url, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    path_to_package = os.getcwd()
    os.makedirs(os.path.join(path_to_package, folder), exist_ok=True)
    filename = sanitize_filename(filename)
    response = get_response(url)
    path_to_file = os.path.join(folder, f'{filename}.txt')
    if response.headers['Content-Type'] == 'text/plain; charset="utf-8"':
        with open(path_to_file, 'w', encoding='utf8') as file:
            file.write(response.text)


if __name__ == '__main__':
    for book_id in tqdm(range(1, 11)):
        name_url = f'https://tululu.org/b{book_id}'
        book_url = f'http://tululu.org/txt.php?id={book_id}'
        filename = f'{book_id}. {get_filename(name_url)}'
        download_txt(book_url, filename)

