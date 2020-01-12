import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from lxml import html


class OpenScraper(object):
    base_url = "https://www.open.online/"

    def _parse_article(self, article):
        return {
            "img_url": article.find("figure/a/img").attrib["src"],
            "news_url": article.find("figure/a").attrib["href"],
            "title": article.find('div[@class="news__inner"]/h2')
            .text_content()
            .replace("\n", ""),
        }

    def _download_page_tree(self, url):
        f = urllib.request.urlopen(url)
        page = f.read().decode("utf-8")
        return html.fromstring(page)

    def retrieve_articles(self, dt, page=1):
        date = dt.strftime("%Y/%m/%d")
        home = self._download_page_tree(self.base_url + date)
        pages = [
            p.attrib["href"]
            for p in home.xpath('//a[@class="pagination-item pagination-inactive"]')
        ]
        trees = [home] + [self._download_page_tree(u) for u in pages]
        return [
            self._parse_article(a) for tree in trees for a in tree.xpath("//article")
        ]


scraper = OpenScraper()
yesterday = datetime.now() - timedelta(days=1)
articles = scraper.retrieve_articles(yesterday)
for a in articles:
    print(a)
