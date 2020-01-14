import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from exceptions import BookNotExist
from contextlib import suppress


def download_txt(url, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
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
    """Функция для получения названия книги и автора.
    Args:
        url (str): Ссылка на книгу, которую хочется скачать.
    Returns:
        list: Список из названия книги и автора
    """
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()

    if response.status_code != 200:
        raise BookNotExist

    soup = BeautifulSoup(response.text, 'lxml')

    title_and_author = soup.find('h1').text.split('::')

    title = title_and_author[0].strip()
    author = title_and_author[1].strip()

    return title, author


if __name__ == '__main__':
    download_url = 'http://tululu.org/txt.php?id='  # Добавить {id}
    info_url = 'http://tululu.org/b'  # Добавить {id}

    for id in range(1, 11):
        with suppress(BookNotExist):
            title, author = get_title_and_author(f'{info_url}{id}/')
            download_txt(f'{download_url}{id}', title)
