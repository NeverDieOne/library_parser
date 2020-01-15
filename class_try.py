import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from exceptions import BookNotExist
from contextlib import suppress
import os
from urllib.parse import urljoin


class Book:
    BASE_URL = 'http://tululu.org'

    def __init__(self, id):
        self.id = id
        self.info_url = requests.get(f'http://tululu.org/b{self.id}/', allow_redirects=False)
        self.info_url.raise_for_status()

        self.file_url = requests.get(f'http://tululu.org/txt.php?id={self.id}', allow_redirects=False)
        self.file_url.raise_for_status()

        self.img_file = requests.get(self._get_img_link())
        self.img_file.raise_for_status()

    def _info_is_exist(self):
        return self.info_url.status_code == 200

    def _file_is_exist(self):
        return self.file_url.status_code == 200

    def _image_file_is_exist(self):
        if self._info_is_exist():
            return self.img_file.status_code == 200
        return None

    def _get_img_link(self):
        if self._info_is_exist():
            soup = BeautifulSoup(self.info_url.text, 'lxml')
            img_link = soup.find('div', class_='bookimage').find('img')['src']
            return urljoin(self.BASE_URL, img_link)
        return None

    def get_author(self):
        if self._info_is_exist():
            soup = BeautifulSoup(self.info_url.text, 'lxml')
            author = soup.find('h1').text.split('::')[1].strip()
            return author
        return None

    def get_title(self):
        if self._info_is_exist():
            soup = BeautifulSoup(self.info_url.text, 'lxml')
            title = soup.find('h1').text.split('::')[0].strip()
            return title
        return None

    def download_book(self, folder='books/'):
        if self._file_is_exist():
            if not os.path.exists(folder):
                os.makedirs(folder)

            filename = sanitize_filename(self.get_title())
            path = os.path.join(folder, f'{filename}.txt')

            with open(path, 'wb') as file:
                file.write(self.file_url.content)

            return path
        return None

    def download_book_img(self, folder='images/'):
        if self._image_file_is_exist():
            if not os.path.exists(folder):
                os.makedirs(folder)

            filename = self._get_img_link().split('/')[-1]
            path = os.path.join(folder, filename)


            with open(path, 'wb') as file:
                file.write(self.img_file.content)

            return path
        return None


if __name__ == '__main__':
    # for id in range(1, 11):
    #     with suppress(BookNotExist):
    #         Book(id).download_book_img()

    book = Book(2)
    print(book.img_file)
