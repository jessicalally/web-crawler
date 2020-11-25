import argparse
import concurrent.futures
import re
from collections import deque
from concurrent.futures import Future
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Set

import requests
from bs4 import BeautifulSoup
from requests import RequestException

URL = re.compile('http(s)?://[^/]+')
PROTOCOL = re.compile('^http(s)?://')
PATH = re.compile('/.*$')
DEFAULT_NUM_URLS_TO_SCRAPE = 100
SUCCESS_STATUS_CODE = 200
MAX_WORKER_THREADS = 50


# Converts a relative url to an absolute url
def get_relative_url(url: str, link: str) -> str:
    if link.startswith('/'):
        root_url = re.match(URL, url).group(0)
        return root_url + link
    else:
        return url + '/' + link


# Checks if url is an absolute url or relative url
def get_url(base_url: str, link: str) -> str:
    is_absolute_address = re.match(PROTOCOL, link)

    if is_absolute_address:
        return link
    elif '#' not in link:
        # We want to ignore links to other sections of the webpage as we have already scraped all urls from this page
        return get_relative_url(base_url, link)


# Parses links on given url
def parse_links(base_url: str, parser: BeautifulSoup) -> Set[str]:
    links = set()

    for link in parser.findAll('a'):
        if (link := link.get('href')) is not None:
            if (url := get_url(base_url, link)) is not None:
                links.add(url)

    return links


# Requests url and checks if request has succeeded
def _task(url: str) -> (bool, [str]):
    response = requests.get(url)

    if response.status_code == SUCCESS_STATUS_CODE:
        parser = BeautifulSoup(response.content, 'html.parser', from_encoding="iso-8859-1")
        return True, parse_links(url, parser)

    return False, []


# Checks if the url is contained in the excluded urls
def _is_excluded(url: str, excluded_urls: [str]) -> bool:
    # Strips url to just its domain
    url = re.sub(PROTOCOL, '', url)
    url = re.sub(PATH, '', url)
    url = re.split(r'\.', url)

    for excluded_url in excluded_urls:
        excluded_url = re.split(r'\.', excluded_url)
        num_to_drop = len(url) - len(excluded_url)

        if url[num_to_drop:] == excluded_url:
            return True

    return False


class WebCrawler:
    def __init__(self):
        self._urls_queue = deque()
        self._prev_urls = set()
        self._successful_urls = set()

    # Processes any completed futures
    def _process_futures(self, futures: {Future, str}, done: [Future], verbose: bool):
        for future in done:
            url = futures[future]

            try:
                (success, links) = future.result()
            except (RequestException, UnicodeError) as exc:
                if verbose:
                    print("The scraped url %s generated an exception: %s" % (url, exc))
            else:
                if success:
                    self._successful_urls.add(url)
                    self._urls_queue.extend(links)

    # Crawls
    def scrape_links(self, base_urls: Set[str], verbose: bool, num_urls=None, excluded_urls=None) -> Set[str]:
        if excluded_urls is None:
            excluded_urls = []

        if num_urls is None:
            num_urls = DEFAULT_NUM_URLS_TO_SCRAPE

        self._urls_queue.extend(base_urls)

        with ThreadPoolExecutor(max_workers=MAX_WORKER_THREADS) as executor:
            futures = dict()
            not_done = []

            while len(self._successful_urls) < num_urls and (len(self._urls_queue) != 0 or len(not_done) != 0):
                # Process any incoming urls

                if len(self._urls_queue) > 0:
                    next_url = self._urls_queue.pop()

                    # Checks whether the url has already been scraped to prevent loops, or if it should be excluded
                    if next_url in self._prev_urls or _is_excluded(next_url, excluded_urls):
                        continue

                    if verbose:
                        print("crawling: " + next_url)

                    futures[executor.submit(_task, next_url)] = next_url
                    self._prev_urls.add(next_url)

                done, not_done = concurrent.futures.wait(
                    futures, timeout=0.25,
                    return_when=concurrent.futures.FIRST_COMPLETED)

                self._process_futures(futures, done, verbose)

                for future in done:
                    del futures[future]

        return self._successful_urls


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawls input url with optional num urls to scrape")
    parser.add_argument("-v", "--verbose", help="Increase output verbosity", action="store_true")
    parser.add_argument("url", type=str, help="Input url to crawl")
    parser.add_argument("--num_urls", type=int, help="Number of valid urls to crawl")
    args = parser.parse_args()

    links = WebCrawler().scrape_links({args.url}, args.verbose, args.num_urls)

    print('\n'.join(link for link in links))


if __name__ == "__main__":
    main()
