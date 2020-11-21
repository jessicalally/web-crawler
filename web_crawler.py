import re
from concurrent.futures import Future

import requests
import concurrent.futures
from bs4 import BeautifulSoup
from collections import deque

URL = r'http(s)?://[^/]+'
ABSOLUTE_ADDRESS = r'http(s)?://'
TOTAL_URLS_TO_PROCESS = 100
SUCCESS_STATUS_CODE = 200
MAX_WORKER_THREADS = 50


def get_relative_url(url: str, link: str) -> str:
    if link.startswith('/'):
        root_url = re.match(URL, url).group(0)
        return root_url + link
    else:
        return url + '/' + link


def get_url(base_url: str, link: str) -> str:
    is_absolute_address = re.match(ABSOLUTE_ADDRESS, link)

    if is_absolute_address:
        return link
    elif '#' not in link:
        # we want to ignore links to other sections of the same webpage as we have already
        # scraped the urls on the whole of this page
        return get_relative_url(base_url, link)


def parse_links(base_url: str, parser: BeautifulSoup) -> [str]:
    links = set()

    for link in parser.findAll('a'):
        if (link := link.get('href')) is not None:
            if (url := get_url(base_url, link)) is not None:
                links.add(url)

    return links


def _task(url: str) -> (bool, [str]):
    response = requests.get(url)

    # checks if request has succeeded
    if response.status_code == SUCCESS_STATUS_CODE:
        parser = BeautifulSoup(response.content, 'html.parser', from_encoding="iso-8859-1")
        return True, parse_links(url, parser)

    return False, []


class WebCrawler:
    def __init__(self):
        self._urls_queue = deque()
        self._prev_urls = set()

    def _process_futures(self, futures: {Future, str}, done: [Future]):
        # processes any completed futures
        for future in done:
            url = futures[future]

            try:
                (success, links) = future.result()
            except Exception as exc:
                print("The scraped url %s generated an exception: %s" % (url, exc))
            else:
                if success:
                    self._urls_queue.extend(links)

    def scrape_links(self, base_url: str) -> set:
        self._urls_queue.append(base_url)
        processed_urls = 0

        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKER_THREADS) as executor:
            futures = dict()
            not_done = []

            while processed_urls < TOTAL_URLS_TO_PROCESS and (len(self._urls_queue) != 0 or len(not_done) != 0):
                # processes any incoming urls
                while len(self._urls_queue) != 0 and processed_urls < TOTAL_URLS_TO_PROCESS:
                    next_url = self._urls_queue.pop()

                    # checks whether url has already been scraped to prevent loops
                    if next_url in self._prev_urls:
                        continue

                    futures[executor.submit(_task, next_url)] = next_url
                    processed_urls += 1
                    self._prev_urls.add(next_url)

                done, not_done = concurrent.futures.wait(
                    futures, timeout=0.25,
                    return_when=concurrent.futures.FIRST_COMPLETED)

                self._process_futures(futures, done)

        return self._prev_urls


def main() -> None:
    base_url = input("Please enter a valid starting URL: ")

    while not re.match(URL, base_url):
        base_url = input("The url \"{}\" is invalid. Please enter a valid starting URL: ".format(base_url))

    links = WebCrawler().scrape_links(base_url)
    print('\n'.join(link for link in links))


if __name__ == "__main__":
    main()
