import os
from urllib.parse import urljoin

import requests
import urllib3
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def get_response(url):
    """Функция для получения ответа на запрос по url."""
    urllib3.disable_warnings()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0',
    }
    response = requests.get(url=url, headers=headers, verify=False)  # noqa: S501
    try:
        response.raise_for_status()
    except requests.HTTPError:
        return None
    if response != 301:  # noqa: WPS432
        return response
    elif response == 301:  # noqa: WPS432
        new_url = response.headers['Location']
        get_response(new_url)


def get_book_description(url):
    """Функция для парсинга названия книги и автора."""
    response = get_response(url)
    soup = BeautifulSoup(response.text, 'lxml')
    selector = '.ow_px_td h1'
    title = soup.select_one(selector)
    return [text.strip() for text in title.text.split('::')]


def get_book_genres(url):
    """Функция скачивания жанров."""
    response = get_response(url)
    soup = BeautifulSoup(response.text, 'lxml')
    selector = '.ow_px_td span.d_book a'
    try:
        raw_genres = soup.select(selector)
    except AttributeError:
        return None
    genres = []
    for genre in raw_genres:
        genres.append(genre.text)
    return genres


def get_book_comments(url):
    """Функция для скачивания коментариев к книге."""
    response = get_response(url)
    soup = BeautifulSoup(response.text, 'lxml')
    selector = '.texts span'
    comments = soup.select(selector)
    comments_list = []
    for comment in comments:
        try:
            text = comment.text
        except AttributeError:
            break
        comments_list.append(text)
    return comments_list


def download_img(url, path, folder='image/'):
    """Функция для скачивания обложек."""
    directory = os.path.join(path, folder)
    os.makedirs(directory, exist_ok=True)
    response = get_response(url)
    soup = BeautifulSoup(response.text, 'lxml')
    selector = '.bookimage img'
    img = soup.select_one(selector)
    if not img:
        return None
    abs_img_url = urljoin('https://tululu.org/', img['src'])
    img_name = abs_img_url.split('/')[-1]
    path_to_file = os.path.join(directory, img_name)
    raw_img = get_response(abs_img_url)
    with open(path_to_file, 'wb') as image:
        image.write(raw_img.content)
    return path_to_file


def download_txt(url, filename, path, folder='books/'):
    """Функция для скачивания текстовых файлов."""
    directory = os.path.join(path, folder)
    os.makedirs(directory, exist_ok=True)
    filename = sanitize_filename(filename)
    response = get_response(url)
    path_to_file = os.path.join(directory, f'{filename}.txt')
    if response.headers['Content-Type'] == 'text/plain; charset="utf-8"':
        with open(path_to_file, 'w', encoding='utf8') as book:
            book.write(response.text)
    return path_to_file
