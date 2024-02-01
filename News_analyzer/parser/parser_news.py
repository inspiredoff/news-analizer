import asyncio
import aiohttp
import time

import self
from bs4 import BeautifulSoup


class RiaNews:
    def __init__(self):
        self.main_url = "https://ria.ru/services/archive/widget/more.html"
        self.url_title = "https://ria.ru"

        self.tag_article_url = 'a'
        self.class_article_url = None
        self.get_tag_article_url = 'href'

        self.tag_next_url = 'div'
        self.class_next_url = 'lenta__item'
        self.get_tag_next_url = 'data-next'

        self.tag_news_headline = 'meta'
        self.class_news_headline = 'name'
        self.get_news_headline = 'content'

        self.tag_time_headline = None
        self.class_time_headline = 'article__info-date'
        self.tag_time_headline_update = None
        self.class_time_headline_update = 'article__info-date-modified'
        self.itemprop_time_headline_created = 'dateCreated'
        self.itemprop_time_headline_Modified = 'dateModified'
        self.times = "2024-02-01 21:15"
        self.search_depth = time.strptime(self.times, "%Y-%m-%d %H:%M")

        self.tag_tag_headline = None
        self.class_tag_headline = 'article__tags-item'

        self.tag_views_headline = None
        self.class_views_headline = 'article__views'


class NewsParser(RiaNews):

    def __init__(self, url):
        super().__init__()
        self.continuation = True
        self.soup = None
        self.next_page_url = None
        self.url = url
        self.search_result = None
        self.article_url = []
        self.next_page_url = None
        self.news_headline = None
        self.time_headline = None
        self.tags_headline = []
        self.num_views_headline = None

    async def download_translate_html_to_text(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                html_text = await response.text()
            self.soup = BeautifulSoup(html_text, 'lxml')

    async def find_data_in_class(self, tag, class_):
        try:
            if tag is None:
                self.search_result = self.soup.find_all(class_=class_)
            elif class_ is None:
                self.search_result = self.soup.find_all(tag)
            else:
                self.search_result = self.soup.find_all(tag, class_=class_)
        except:
            if tag is None:
                self.search_result = self.soup.find(class_=class_)
            elif class_ is None:
                self.search_result = self.soup.find(tag)
            else:
                self.search_result = self.soup.find(tag, class_=class_)

    async def find_data_in_itemprop(self, tag, itemprop):
        try:
            if tag is None:
                self.search_result = self.soup.find_all(itemprop=itemprop)
            elif itemprop is None:
                self.search_result = self.soup.find_all(tag)
            else:
                self.search_result = self.soup.find_all(tag, itemprop=itemprop)
        except:
            if tag is None:
                self.search_result = self.soup.find(itemprop=itemprop)
            elif itemprop is None:
                self.search_result = self.soup.find(tag)
            else:
                self.search_result = self.soup.find(tag, itemprop=itemprop)

    async def converting_string_to_time(self, time_headline):
        struct_time = time.strptime(time_headline, "%Y-%m-%dT%H:%M")
        return struct_time

    # async def filter_search_result(self):

    async def time_compassion(self):
        var = self.search_depth
        var1 = self.time_headline
        if var >= var1:
            continuation = False
            return continuation


class NewsPageParser(NewsParser):

    async def search_for_article_url(self):
        await self.find_data_in_class(self.tag_article_url, self.class_article_url)
        for url in self.search_result:
            self.article_url.append(self.url_title + url.get(self.get_tag_article_url))

    async def search_for_next_page_url(self):
        await self.find_data_in_class(self.tag_next_url, self.class_next_url)
        self.next_page_url = self.url_title + self.search_result[-1].get(self.get_tag_next_url)

    async def initialize_parser(self):
        await self.download_translate_html_to_text()
        await self.search_for_article_url()
        await self.search_for_next_page_url()


class NewsHeadlineParsing(NewsParser):

    async def search_for_headline_news(self):
        await self.find_data_in_itemprop(self.tag_news_headline, self.class_news_headline)
        self.news_headline = self.search_result[3].get(self.get_news_headline)
        print(self.news_headline)

    async def search_for_time_news(self):
        await self.find_data_in_itemprop(self.tag_time_headline_update, self.itemprop_time_headline_Modified)
        for text in self.search_result:
            time_news = text.get_text(strip=True)
        if time_news == []:
            await self.find_data_in_itemprop(self.tag_time_headline, self.itemprop_time_headline_created)
            for text in self.search_result:
                time_news = text.get_text(strip=True)
        self.time_headline = await self.converting_string_to_time(time_news)

    async def search_for_tag_news(self):
        await self.find_data_in_class(self.tag_tag_headline, self.class_tag_headline)
        for text in self.search_result:
            self.tags_headline.append(text.get_text(strip=True))

    async def initialize_parser(self,list):
        await self.download_translate_html_to_text()
        await self.search_for_headline_news()
        await self.search_for_time_news()
        await self.search_for_tag_news()


class NumberOfHeaderViews(NewsParser):

    async def search_for_number_views(self):
        await self.find_data_in_class(self.tag_views_headline, self.class_views_headline)
        for text in self.search_result:
            num_views_headline = text.get_text().split()
            self.num_views_headline = int(num_views_headline[0])

    async def initialize_parser(self):
        await self.download_translate_html_to_text()
        await self.search_for_number_views()


# news_header_url = []


async def parser():
    url = RiaNews().main_url
    parsers = NewsParser(url)
    continuation = parsers.continuation
    while continuation:
        parser_global_page = NewsPageParser(url)
        await parser_global_page.initialize_parser()
        url = parser_global_page.next_page_url
        for urls in parser_global_page.article_url:
            parser_news_page = NewsHeadlineParsing(urls)
            parser_page_views = NumberOfHeaderViews('https://ria.ru/services/dynamics' + urls[14:-1])
            await parser_news_page.initialize_parser(parser_global_page.article_url)
            await parser_page_views.initialize_parser()
            if await parser_news_page.time_compassion() == False:
                continuation = False
                break


asyncio.run(parser())

#### асинхронный цикл ####

# for page in range(1, 5):
#     news_list = RiaNews(url)
#     asyncio.run(news_list.parser())
#     news_header_url = news_header_url +news_list.url_headers
#     url = news_list.next_url
#
# async def async_for(news_header_url):
#     tasks = []
#     for url in news_header_url:
#         task = asyncio.create_task(NewsHeadlineParsing(url).parser_1())
#         tasks.append(task)
#     await asyncio.gather(*tasks)
#
# asyncio.run(async_for(news_header_url))

#### синхронный цикл ####
#
# for page in range(1, 5):
#     c = RiaNews(url_)
#     asyncio.run(c.parser())
#     news_header_url = c.article_url
#     print(c.article_url)
#     url_ = c.next_page_url
#
#     for url in c.article_url:
#         asyncio.run(RiaNews(url).parser_1())

### полуасинхронный цикл ####

# for page in range(1, 5):
#     c = RiaNews(url_)
#     asyncio.run(c.parser())
#     news_header_url = c.article_url
#     print(c.article_url)
#     url_ = c.next_page_url
#
#
#     async def async_for():
#         tasks = []
#         for url in news_header_url:
#             task = asyncio.create_task(RiaNews(url).parser_1())
#             tasks.append(task)
#
#         await asyncio.gather(*tasks)
