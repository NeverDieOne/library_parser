import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from exceptions import BookNotExist
from contextlib import suppress
from urllib.parse import urljoin


def download_txt(url, filename, folder='books/'):
    if not os.path.exists(folder):
        os.makedirs(folder)

    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()

    if response.status_code != 200:
        raise BookNotExist

    filename = sanitize_filename(filename)

    path = os.path.join(folder, f'{filename}.txt')
    with open(path, 'wb') as file:
        file.write(response.content)

    return path


def get_title_and_author(url):
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()

    if response.status_code != 200:
        raise BookNotExist

    soup = BeautifulSoup(response.text, 'lxml')

    title_and_author = soup.find('h1').text.split('::')

    title = title_and_author[0].strip()
    author = title_and_author[1].strip()

    return title, author


def get_book_image_link(url):
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()

    if response.status_code != 200:
        raise BookNotExist

    soup = BeautifulSoup(response.text, 'lxml')
    img_link = soup.find('div', class_='bookimage').find('img')['src']
    return urljoin('http://tululu.org', img_link)


def download_img(url, folder='images/'):
    if not os.path.exists(folder):
        os.makedirs(folder)

    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()

    if response.status_code != 200:
        raise BookNotExist

    filename = sanitize_filename(url.split('/')[-1])
    path = os.path.join(folder, filename)

    with open(path, 'wb') as file:
        file.write(response.content)

    return path


if __name__ == '__main__':
    download_url = 'http://tululu.org/txt.php?id='  # Добавить {id}
    info_url = 'http://tululu.org/b'  # Добавить {id}

    for id in range(1, 11):
        with suppress(BookNotExist):
            title, author = get_title_and_author(f'{info_url}{id}/')
            img_link = get_book_image_link(f"{info_url}{id}/")

            download_img(img_link)

