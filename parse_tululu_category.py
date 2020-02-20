from bs4 import BeautifulSoup
import requests


def get_ids(start_page=1, end_page=None):
    ids = []
    url = f'http://tululu.org/l55/{start_page}'

    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()

    if response.status_code == 301:
        return None

    if not end_page:
        soup = BeautifulSoup(response.text, 'lxml')
        end_page = int(soup.select('a.npage')[-1].text)

    for page in range(start_page, end_page + 1):
        url = f'http://tululu.org/l55/{page}/'
        response = requests.get(url, allow_redirects=False)
        response.raise_for_status()

        if response.status_code == 301:
            break

        soup = BeautifulSoup(response.text, 'lxml')
        ids += [book.select_one('a')['href'].split('/')[-2].split('b')[-1] for book in soup.select('div.bookimage')]

    return ids
