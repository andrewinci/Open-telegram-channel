import urllib.request
import urllib.parse
from datetime import datetime
from lxml import html
import os
import boto3
import time


class OpenScraper(object):
    base_url = "https://www.open.online/"

    def _get_meta_property(self, article, p_name):
        metas = article.findall(f'head/meta/[@property="{p_name}"]')
        return [t.attrib["content"] for t in metas]

    def parse_article(self, url):
        article = self._download_page_tree(url)
        return {
            "title": self._get_meta_property(article, "og:title")[0],
            "img": self._get_meta_property(article, "og:image")[0],
            "description": self._get_meta_property(article, "og:description")[0],
            "url": url,
            "tags": self._get_meta_property(article, "article:tag"),
        }

    def _download_page_tree(self, url):
        f = urllib.request.urlopen(url)
        page = f.read().decode("utf-8")
        return html.fromstring(page)

    def get_article_urls(self, dt):
        date = dt.strftime("%Y/%m/%d")
        home = self._download_page_tree(self.base_url + date)
        pages = [
            p.attrib["href"]
            for p in home.xpath('//a[@class="pagination-item pagination-inactive"]')
        ]
        trees = [home] + [self._download_page_tree(u) for u in pages]
        return [
            a.attrib["href"] for tree in trees for a in tree.xpath("//article/figure/a")
        ]


class TelegramChannelHelper(object):
    base_url = "https://api.telegram.org/"

    def __init__(self, channel_id, bot_key):
        self.channel_id = channel_id
        self.bot_key = bot_key

    def _prepare_tag_line(self, tags):
        line = " ".join(["#" + t.replace(" ", "") for t in tags])
        for s in "'-":
            line = line.replace(s, "")
        return line

    def publish_img(self, article):
        print(article)
        url = urllib.parse.quote(self.bot_key)
        url += "/sendPhoto?"
        url += f"chat_id={self.channel_id}"
        url += f"&photo={urllib.parse.quote(article['img'])}"
        url += f"&parse_mode=markdown"
        url += "&disable_web_page_preview=true"
        url += "&caption=" + urllib.parse.quote(
            f"*{article['title']}*"
            + f"\n{article['description']}"
            + f"\n{self._prepare_tag_line(article['tags'])}"
            + f"\n{article['url']}"
        )

        urllib.request.urlopen(urllib.parse.urljoin(self.base_url, url))


class OpenLambda(object):
    def __init__(self, scraper, tg_helper, repo):
        self.scraper = scraper
        self.tg_helper = tg_helper
        self.repo = repo

    def handle(self, event, context):
        article_urls = self.scraper.get_article_urls(datetime.now())
        urls_to_publish = [
            a for a in article_urls if not self.repo.already_published(a)
        ]
        urls_to_publish.reverse()
        for url in urls_to_publish:
            article = self.scraper.parse_article(url)
            self.tg_helper.publish_img(article)
            self.repo.add(url)


class LocalRepo(object):
    def __init__(self, repo_name):
        self.repo_name = f".{repo_name}"
        if self.repo_name not in os.listdir():
            open(self.repo_name, "w").close()

    def add(self, text):
        with open(self.repo_name, "a") as repo:
            repo.write(f"{text}\n")

    def already_published(self, text):
        with open(self.repo_name, "r") as repo:
            return f"{text}\n" in repo.readlines()


class DyanomoDbRepo(object):
    def __init__(self):
        dynamodb = boto3.resource("dynamodb")
        self.table = dynamodb.Table("open_daily_history")

    def add(self, text):
        self.table.put_item(Item={"url": text, "ttl": int(time.time() + 60 * 60 * 48)})

    def already_published(self, text):
        t = self.table.get_item(Key={"url": text})
        return t.get("Item") is not None


channel_id = os.environ.get("TGCHANNELID")
bot_key = os.environ.get("TGBOTKEY")
tg_helper = TelegramChannelHelper(channel_id, bot_key)

if os.environ.get("LOCAL") is not None:
    news_repo = LocalRepo("test_repo")
    openLambda = OpenLambda(OpenScraper(), tg_helper, news_repo)
    openLambda.handle(None, None)
else:
    news_repo = DyanomoDbRepo()
    openLambda = OpenLambda(OpenScraper(), tg_helper, news_repo)
    handle = openLambda.handle
