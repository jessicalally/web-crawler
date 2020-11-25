# web-crawler

Implementation of a simple concurrent web crawler in Python. The program crawls a single URL (which is input by the user into the program), retrieving all links on that page. Any links found are also crawled and this is repeated until it has found and validated n URLs (n can be input by the user, or is 100 by default), which are output to stdout.

I have extended this to create a `suspicious_url_crawler`, which generates typos of the 100 most popular domains and crawls these to find valid typosquatting URLs.

## Usage
### Packages
The following packages are required.
* `requests`
* `bs4` (beautifulsoup4)

### Run
To run the web crawler program, enter the following terminal command:
```
python3 web_crawler.py [-v|--verbose] starting_url [--num_urls num_urls_to_scrape]
```
To run the suspicious url crawler program, enter the following terminal command:
```
python3 suspicious_url_crawler.py [-v|--verbose] [--num_urls num_urls_to_scrape]
```

## Examples of Suspicious URLs Identified Using `suspicious_url_crawler`
Many of these are legitimately misleading or malicious, often being filled with spam advertising.
```
pyapal.com
ccraigslist.org
anroid.com
twitte.com
googe.pl
aliexpresss.com
goolge.com.ar
forrbes.com
jjd.com
twitteer.com
ggoogle.com.tw
andrroid.com
miicrosoftonline.com
wikiia.com
microsoftnline.com
oogle.ru
titter.com
reeddit.com
craiglis.org
offcie.com
gogle.co.jp
tiiktok.com
store.steamowered.com
logger.com
microsoftonine.com
businessiinsider.com
goolgeusercontent.com
microsfotonline.com
store.tseampowered.com
pinterrest.com
goole.it
amaon.in
rreddit.com
stacoverflow.com
 ```
