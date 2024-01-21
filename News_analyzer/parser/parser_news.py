import asyncio
import aiohttp
from bs4 import BeautifulSoup

class News_parser:

    def __init__(self, url):
        self.soup = None
        self.url_headers = []
        self.next_url.__str__()
        self.url = url
        if self.url == ' ':
            self.url = self.main_url
        self.tasks = []

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
        task = asyncio.create_task(self.response_parsing_headers())
        self.tasks.append(task)
        task = asyncio.create_task(self.next_url())
        self.tasks.append(task)

        await asyncio.gather(*self.tasks)


class News_headline_parsing(News_parser):

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def __init__(self, url):
        super().__init__(url)
        self.count = 0
        self.url = url
        self.tag = 'div'
        self.class_ = 'article__title'
        # self.get_tag = 'href'

    async def client_request_soup(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                self.soup = BeautifulSoup(await response.text(), 'lxml')

    async def data_parsing(self):
        if self.class_ is None:
            url_headers = self.soup.find(self.tag)
        else:
            url_headers = self.soup.find(class_='article__title')
        for string in url_headers.stripped_strings:
            print(repr(string))

    async def time_parsing(self):
        if self.class_ is None:
            url_headers = self.soup.find(self.tag)
        else:
            url_headers = self.soup.find(class_='article__info-date')
        self.count = 0
        for string in url_headers.stripped_strings:
            self.count += 1
            print(repr(string))

    async def tag_parsing(self):
        if self.class_ is None:
            self.tag_parsing = self.soup.find(self.tag)
        else:
            self.tag_parsing = self.soup.find_all(class_='article__tags-item')
        for headers in self.tag_parsing:
            for string in headers.stripped_strings:
                print(repr(string))

    async def parser_1(self):
        await self.client_request_soup()
        task = asyncio.create_task(self.data_parsing())
        self.tasks.append(task)
        task = asyncio.create_task(self.time_parsing())
        self.tasks.append(task)
        task = asyncio.create_task(self.tag_parsing())
        self.tasks.append(task)

        await asyncio.gather(*self.tasks)


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


b = "https://ria.ru/services/archive/widget/more.html"
for a in range(1, 5):
    c = RiaNews(b)
    asyncio.run(c.parser())
    print(c.url_headers)
    b = c.next_url
    for url in c.url_headers:
        asyncio.run(News_headline_parsing(url).parser_1())
