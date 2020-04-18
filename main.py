import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from exceptions import BookNotExist, InvalidPageNumbers
from contextlib import suppress
from urllib.parse import urljoin
import parse_tululu_category
import json
import argparse

DOWNLOAD_URL = 'http://tululu.org/txt.php?id='
INFO_URL = 'http://tululu.org/b'


def get_response_with_book_data(book_id):
    response = requests.get(f'{INFO_URL}{book_id}/', allow_redirects=False)
    response.raise_for_status()

    if response.status_code == 301:
        raise BookNotExist

    return response


def download_txt(book_id, filename, folder='books/'):
    os.makedirs(folder, exist_ok=True)

    response = requests.get(f'{DOWNLOAD_URL}{book_id}', allow_redirects=False)
    response.raise_for_status()

    if response.status_code == 301:
        raise BookNotExist

    filename = sanitize_filename(filename)

    path = os.path.join(folder, f'{filename}.txt')
    with open(path, 'wb') as file:
        file.write(response.content)

    return path


def download_img(book_data, folder='images/'):
    os.makedirs(folder, exist_ok=True)

    image_link = get_book_image_link(book_data)

    response = requests.get(image_link, allow_redirects=False)
    response.raise_for_status()

    filename = sanitize_filename(image_link.split('/')[-1])

    path = os.path.join(folder, filename)
    with open(path, 'wb') as file:
        file.write(response.content)

    return path


def get_title_and_author(book_data):
    soup = BeautifulSoup(book_data.text, 'lxml')

    title_and_author = soup.select_one('h1').text.split('::')

    title = title_and_author[0].strip()
    author = title_and_author[1].strip()

    return title, author


def get_book_image_link(book_data):
    soup = BeautifulSoup(book_data.text, 'lxml')
    img_link = soup.select_one('div.bookimage img')['src']
    return urljoin('http://tululu.org', img_link)


def get_book_comments(book_data):
    soup = BeautifulSoup(book_data.text, 'lxml')

    comments = [comment.select_one('span.black').text for comment in soup.select('div.texts')]

    return comments


def get_genre(book_data):
    soup = BeautifulSoup(book_data.text, 'lxml')

    genre = soup.select_one('span.d_book a').text
    return genre


def get_books(start_page=None, end_page=None):
    books = []
    books_ids = parse_tululu_category.get_ids(start_page, end_page)
    for book_id in books_ids:
        try:
            book_data = get_response_with_book_data(book_id)

            title, author = get_title_and_author(book_data)
            book = {
                'title': title,
                'author': author,
                'img_src': download_img(book_data),
                'book_path': download_txt(book_id, title),
                'comments': get_book_comments(book_data)
            }

            books.append(book)
        except BookNotExist:
            print(f'Книга с id "{book_id}" не найдена')

    return books


def make_json(filename, obj):
    with open(filename, 'w') as file:
        json.dump(obj, file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Парсер библиотеки tululu.org')
    parser.add_argument('--start_page', default=1, help='Номер страницы, с которой начинаем скачивание', type=int)
    parser.add_argument('--end_page', help='Номер страницы, на которой заканчиваем скачивание', type=int)
    parser.add_argument('--filename', default='books.json', help='Имя файла, в который сформировать json')
    args = parser.parse_args()

    if all([
        args.start_page < args.end_page,
        args.start_page > 0,
        args.end_page > 0 if args.end_page else True
    ]):
        books = get_books(args.start_page, args.end_page)
        make_json(args.filename, books)
    else:
        raise InvalidPageNumbers('Указаны некорректные номера страниц')
