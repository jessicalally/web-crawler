import re
import requests
from bs4 import BeautifulSoup
from collections import deque

ROOT_URL = r'http(s)?://[^/]+'
ABSOLUTE_ADDRESS = r'http(s)?://'

unique_urls = set()
urls_queue = deque()


def get_relative_url(url: str, link: str) -> str:
    if link.startswith('/'):
        root_url = re.match(ROOT_URL, url).group(0)
        return root_url + link
    else:
        return url + '/' + link


def get_url(url: str, link: str):
    is_absolute_address = re.match(ABSOLUTE_ADDRESS, link)

    if is_absolute_address:
        urls_queue.append(link)
    else:
        # we want to ignore links to other sections of the same webpage as we have already
        # scraped the urls on the whole of this page
        if '#' not in link:
            urls_queue.append(get_relative_url(url, link))


def parse_links(url: str, parser: BeautifulSoup):
    for link in parser.findAll('a'):
        link = link.get('href')

        if link is not None:
            get_url(url, link)


def scrape_links(base_url: str) -> None:
    num_urls_scraped = 1
    urls_queue.append(base_url)

    while num_urls_scraped <= 10:
        next_url = urls_queue.pop()

        # Checks whether url has already been scraped to prevent loops
        if next_url not in unique_urls:
            response = requests.get(next_url)

            # Checks if request has succeeded
            if response.status_code == 200:
                unique_urls.add(next_url)
                parser = BeautifulSoup(response.content, 'html.parser')
                parse_links(next_url, parser)
                print(next_url)
                num_urls_scraped += 1


def main() -> None:
    base_url = input("Please enter a starting URL: ")
    scrape_links(base_url)


main()
