import argparse
from functools import reduce

from typo_generator import generate_typos
from web_crawler import WebCrawler

PROTOCOL = "http://"


# Gets a list of legitimate sites that should be ignored when crawling
def _get_exclusion_sites() -> [str]:
    urls = []

    with open("data/benign_domains.txt", "r") as file:
        for url in file:
            urls.append(url.rstrip())

    return urls


# Gets a list of popular domains to generate typos from
def _get_popular_domains() -> [str]:
    urls = []

    with open("data/popular_domains.txt", "r") as file:
        for url in file:
            urls.append(url.rstrip())

    return urls


class SuspiciousURLCrawler:
    def __init__(self):
        self.web_crawler = WebCrawler()

    # Crawls domains that are typos of popular domains to scrape suspicious URLs
    def get_suspicious_urls(self, verbose: bool, num_urls=None) -> [str]:
        typos = reduce(set.union, map(generate_typos, _get_popular_domains()), set())
        typos = set(map(lambda typo: PROTOCOL + typo, typos))
        return self.web_crawler.scrape_links(typos, verbose, num_urls, _get_exclusion_sites())


def main():
    parser = argparse.ArgumentParser(description="Generates typos of popular websites and crawls them to find "
                                                 "malicious sites")
    parser.add_argument("-v", "--verbose", help="Increase output verbosity", action="store_true")
    parser.add_argument("--num_urls", type=int, help="Number of valid urls to crawl")
    args = parser.parse_args()

    links = SuspiciousURLCrawler().get_suspicious_urls(args.verbose, args.num_urls)
    print('\n'.join(link for link in links))


if __name__ == "__main__":
    main()
