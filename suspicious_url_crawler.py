from functools import reduce

from typo_generator import generate_typos
from web_crawler import WebCrawler

MAX_WORKER_THREADS = 50
PROTOCOL = "http://"


def _get_exclusion_sites() -> [str]:
    # Gets legitimate sites that should be ignored when crawling
    urls = []
    with open("data/popular_domains.txt", "r") as file:
        for url in file:
            urls.append(url.rstrip())
    with open("data/benign_domains.txt", "r") as file:
        for url in file:
            urls.append(url.rstrip())

    return urls


class SuspiciousURLCrawler:
    # crawls domains that are misspellings of popular domains to scrape suspicious URLs
    def __init__(self):
        self.web_crawler = WebCrawler()

    def get_suspicious_urls(self, urls: [str]) -> [str]:
        typos = reduce(lambda a, b: set.union(a, b), map(lambda url: generate_typos(url), urls), set())
        typos = set(map(lambda typo: PROTOCOL + typo, typos))
        return self.web_crawler.scrape_links(typos, _get_exclusion_sites())


def main():
    links = SuspiciousURLCrawler().get_suspicious_urls(_get_exclusion_sites())
    print('\n'.join(link for link in links))


if __name__ == "__main__":
    main()
