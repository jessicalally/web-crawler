import re
from concurrent.futures._base import Future

import requests
import concurrent.futures
from bs4 import BeautifulSoup
from collections import deque

URL = r'http(s)?://[^/]+'
ABSOLUTE_ADDRESS = r'http(s)?://'
TOTAL_URLS_TO_SCRAPE = 5
TOTAL_URLS_TO_PROCESS = 100
SUCCESS_STATUS_CODE = 200

prev_urls = set()
urls_queue = deque()


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


def task(url: str) -> (bool, [str]):
    response = requests.get(url)

    # checks if request has succeeded
    if response.status_code == SUCCESS_STATUS_CODE:
        parser = BeautifulSoup(response.content, 'html.parser', from_encoding="iso-8859-1")
        print(url)
        return True, parse_links(url, parser)

    return False, []


def process_futures(futures: {Future, str}):
    # check status of futures currently working
    done, not_done = concurrent.futures.wait(
        futures, None,
        return_when=concurrent.futures.FIRST_COMPLETED)

    # processes any completed futures
    for future in done:
        url = futures[future]

        try:
            (success, links) = future.result()
        except Exception as exc:
            print("The scraped url %s generated an exception: %s" % (url, exc))
        else:
            if success:
                urls_queue.extend(links)


def scrape_links(base_url: str) -> None:
    urls_queue.append(base_url)
    processed_urls = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = dict()

        while True:
            # processes any incoming urls
            while len(urls_queue) != 0:
                if processed_urls >= TOTAL_URLS_TO_PROCESS:
                    process_futures(futures)
                    return

                next_url = urls_queue.pop()

                # checks whether url has already been scraped to prevent loops
                if next_url in prev_urls:
                    continue

                futures[executor.submit(task, next_url)] = next_url
                processed_urls += 1
                prev_urls.add(next_url)

            process_futures(futures)


def main() -> None:
    base_url = input("Please enter a valid starting URL: ")

    while not re.match(URL, base_url):
        base_url = input("The url \"{}\" is invalid. Please enter a valid starting URL: ".format(base_url))

    scrape_links(base_url)


main()
