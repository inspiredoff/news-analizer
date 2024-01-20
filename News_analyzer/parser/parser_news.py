import asyncio
import aiohttp
from bs4 import BeautifulSoup


# main_url = "https://ria.ru/services/archive/widget/more.html"
# tag = 'a'

class News_parser:

    def __init__(self, url):
        self.soup = None
        self.url_headers = []
        self.next_url.__str__()
        self.url = url
        if self.url == ' ':
            self.url = self.main_url

    async def client_request_soup(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                html_text = await response.text()
            self.soup = BeautifulSoup(html_text, 'lxml')

    async def response_parsing_headers(self):
        if self.class_ is None:
            url_headers = self.soup.find_all(self.tag)
        else:
            url_headers = self.soup.find_all(self.tag, class_=self.class_)
        for url_header in url_headers:
            self.url_headers.append(self.url_title + url_header.get(self.get_tag))

    async def next_url(self):
        nexturl = self.soup.find_all(self.tag_next_url, class_=self.class_next_url)
        self.next_url = self.url_title + nexturl[-1].get(self.get_tag_next_url)

    async def parser(self):
        await self.client_request_soup()
        await self.response_parsing_headers()
        await self.next_url()


class RiaNews(News_parser):
    def __init__(self, url):
        self.main_url = "https://ria.ru/services/archive/widget/more.html"
        super().__init__(url)
        self.url_title = "https://ria.ru"
        self.tag = 'a'
        self.class_ = None
        self.get_tag = 'href'
        self.tag_next_url = 'div'
        self.get_tag_next_url = 'data-next'
        self.class_next_url = 'lenta__item'




list1 = RiaNews(' ')
asyncio.run(list1.parser())
print(list1.url_headers)
print(list1.next_url)
list2 = RiaNews(list1.next_url)
asyncio.run(list2.parser())
print(list2.url_headers)
print(list2.next_url)
# list1 = News_parser("https://ria.ru/services/archive/widget/more.html", 'a', 'lenta__item', 'href')
# asyncio.run(list1.parser())
# print(list1.url_headers)
# list2 = News_parser(list1.next_url, 'a', 'lenta__item', 'href')
# asyncio.run(list2.parser())
# print(list2.url_headers)
