import re
import requests
from bs4 import BeautifulSoup
from collections import deque


def scrape_links(base_url: str) -> None:
    urls = deque()
    urls.append(base_url)
    num_links = 1

    while num_links < 5:
        next_url = urls.pop()
        response = requests.get(next_url)

        if response.status_code == 200:
            root_url = re.match(r'http(s)?://[^/]+', next_url).group(0)
            parser = BeautifulSoup(response.content, 'html.parser')

            for link in parser.findAll('a'):
                link = link.get('href')
                is_absolute_address = re.match(r'http(s)?://', link)

                if is_absolute_address:
                    urls.append(link)
                else:
                    if '#' not in link:
                        # we want to ignore links to other sections of the same webpage as we have already
                        # scraped the urls on the whole of this page
                        if link.startswith('/'):
                            urls.append(root_url + link)
                        else:
                            urls.append(next_url + '/' + link)

            num_links += 1
            print(next_url)


def main() -> None:
    base_url = input("Please enter a starting URL: ")
    scrape_links(base_url)


main()
