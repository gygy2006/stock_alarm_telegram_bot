import requests
from bs4 import BeautifulSoup

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
}


class StockInformation:
    def __init__(self, news_box):
        self.news_box = news_box
        self.closed_days = []

    def make_soup(self, URL):
        response = requests.get(URL, headers=headers)
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        return soup

    def news_box_validate(self, latest_news_title):
        if self.news_box:
            for i in range(len(self.news_box)):
                news = self.news_box[i]
                for title in range(2):
                    news_title = news[title]
                    if latest_news_title == news_title:
                        return False
                    else:
                        return True
        else:
            return True

    def get_news(self):
        URL = "https://news.naver.com/main/main.nhn?mode=LSD&mid=shm&sid1=101"
        soup = self.make_soup(URL)
        news = soup.select(".cluster_item > .cluster_text > a")
        for anews in news:
            if self.news_box_validate(anews.text):
                self.news_box.append([anews["href"], anews.text])
        return True
