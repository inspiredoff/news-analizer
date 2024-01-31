import asyncio
import aiohttp
import time
from bs4 import BeautifulSoup


class News_parser:

    def __init__(self, url):
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

    async def cooking_soup(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                html_text = await response.text()
            self.soup = BeautifulSoup(html_text, 'lxml')

    async def bs4_parser(self, tag, class_):
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

    async def bs4_parser_itemprop(self, tag, itemprop):
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

    async def struct_time(self, time_headline):
        struct_time = time.strptime(time_headline, "%Y-%m-%dT%H:%M")
        return struct_time

    # async def filter_search_result(self):

    async def time_compassion(self, list_url):
        var = RiaNews.search_depth
        var1 = self.time_headline
        if var >= var1:
            self.continuation = False
            return list_url.clear()


class News_page_parser(News_parser):
    def __init__(self, url):
        super().__init__(url)

    async def search_for_article_url(self):
        await self.bs4_parser(RiaNews.tag_article_url, RiaNews.class_article_url)
        for url in self.search_result:
            self.article_url.append(RiaNews.url_title + url.get(RiaNews.get_tag_article_url))

    async def search_for_next_page_url(self):
        await self.bs4_parser(RiaNews.tag_next_url, RiaNews.class_next_url)
        self.next_page_url = RiaNews.url_title + self.search_result[-1].get(RiaNews.get_tag_next_url)

    async def parser(self):
        await self.cooking_soup()
        await self.search_for_article_url()
        await self.search_for_next_page_url()


class News_headline_parsing(News_parser):

    def __init__(self, url):
        super().__init__(url)

    async def article_headline(self):
        await self.bs4_parser_itemprop(RiaNews.tag_news_headline, RiaNews.class_news_headline)
        self.news_headline = self.search_result[3].get(RiaNews.get_news_headline)

    async def time_headlines(self):
        await self.bs4_parser_itemprop(RiaNews.tag_time_headline_update,
                                       RiaNews.itemprop_time_headline_Modified)
        for text in self.search_result:
            time_headline = text.get_text(strip=True)
        if time_headline == []:
            await self.bs4_parser_itemprop(RiaNews.tag_time_headline,
                                           RiaNews.itemprop_time_headline_created)
            for text in self.search_result:
                time_headline = text.get_text(strip=True)
        self.time_headline = await self.struct_time(time_headline)

    async def tag_headline(self):
        await self.bs4_parser(RiaNews.tag_tag_headline, RiaNews.class_tag_headline)
        for text in self.search_result:
            self.tags_headline.append(text.get_text(strip=True))

    async def parser(self):
        await self.cooking_soup()
        await self.article_headline()
        await self.time_headlines()
        await self.tag_headline()


class Number_of_header_views(News_parser):

    def __init__(self, url):
        super().__init__(url)
        self.url = 'https://ria.ru/services/dynamics' + url[14:-1]

    async def number_of_views(self):
        await self.bs4_parser(RiaNews.tag_views_headline, RiaNews.class_views_headline)
        for text in self.search_result:
            num_views_headline = text.get_text().split()
            self.num_views_headline = int(num_views_headline[0])

    async def parser(self):
        await self.cooking_soup()
        await self.number_of_views()


class RiaNews(News_parser):
    main_url = "https://ria.ru/services/archive/widget/more.html"
    url_title = "https://ria.ru"

    tag_article_url = 'a'
    class_article_url = None
    get_tag_article_url = 'href'

    tag_next_url = 'div'
    class_next_url = 'lenta__item'
    get_tag_next_url = 'data-next'

    tag_news_headline = 'meta'
    class_news_headline = 'name'
    get_news_headline = 'content'

    tag_time_headline = None
    class_time_headline = 'article__info-date'
    tag_time_headline_update = None
    class_time_headline_update = 'article__info-date-modified'
    itemprop_time_headline_created = 'dateCreated'
    itemprop_time_headline_Modified = 'dateModified'
    times = "2024-01-28 17:00"
    search_depth = time.strptime(times, "%Y-%m-%d %H:%M")

    tag_tag_headline = None
    class_tag_headline = 'article__tags-item'

    tag_views_headline = None
    class_views_headline = 'article__views'


# news_header_url = []


async def parser():
    url = RiaNews.main_url
    parsers = News_parser(url)
    while parsers.continuation:
        page = News_page_parser(url)
        await page.parser()
        url = page.next_page_url
        for urls in page.article_url:
            news_page = News_headline_parsing(urls)
            news_page_views = Number_of_header_views(urls)
            await news_page.parser()
            await news_page_views.parser()
            print(news_page.news_headline)
            await news_page.time_compassion(page.article_url)


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
#         task = asyncio.create_task(News_headline_parsing(url).parser_1())
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


asyncio.run(News_parser().parser())
