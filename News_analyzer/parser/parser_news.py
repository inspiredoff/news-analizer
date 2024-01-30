import asyncio
import aiohttp
import time
from bs4 import BeautifulSoup



class News_parser:

    news_time = None

    def __init__(self):
        self.continuation = True
        self.soup = None
        self.next_page_url = None
        self.next_page_url.__str__()

    async def cooking_soup(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                html_text = await response.text()
            soup = BeautifulSoup(html_text, 'lxml')
        return soup

    async def bs4_parser(self, tag, class_):
        try:
            if tag is None:
                search_result = self.soup.find_all(class_=class_)
            elif class_ is None:
                search_result = self.soup.find_all(tag)
            else:
                search_result = self.soup.find_all(tag, class_=class_)
        except:
            if tag is None:
                search_result = self.soup.find(class_=class_)
            elif class_ is None:
                search_result = self.soup.find(tag)
            else:
                search_result = self.soup.find(tag, class_=class_)
        return search_result

    async def bs4_parser_itemprop(self, tag, itemprop):
        try:
            if tag is None:
                search_result = self.soup.find_all(itemprop=itemprop)
            elif itemprop is None:
                search_result = self.soup.find_all(tag)
            else:
                search_result = self.soup.find_all(tag, itemprop=itemprop)
        except:
            if tag is None:
                search_result = self.soup.find(itemprop=itemprop)
            elif itemprop is None:
                search_result = self.soup.find(tag)
            else:
                search_result = self.soup.find(tag, itemprop=itemprop)
        return search_result

    async def time_compasion(self, tasks, tasks1, list_url):
        var = RiaNews.search_depth
        var1 = self.news_time
        if var >= var1:
            self.continuation = False
            return tasks.clear(), tasks1.clear(), list_url.clear()

    async def parser(self):
        url = RiaNews.main_url

        while self.continuation == True:
            soup = await self.cooking_soup(url)
            news_headline = await News_page_parser(soup).search_for_article_url()
            url = await News_page_parser(soup).search_for_next_page_url()

            # print(url)

            async def async_for(list_url):

                for url in list_url:
                    tasks = []
                    tasks1 = []
                    task = asyncio.create_task(self.cooking_soup(url))
                    tasks.append(task)
                    task = asyncio.create_task(self.cooking_soup(('https://ria.ru/services/dynamics' + url[14:-1])))
                    tasks.append(task)
                    soup = await asyncio.gather(*tasks)
                    headline_parsing = News_headline_parsing(soup[0])
                    task = asyncio.create_task(headline_parsing.search_for_news_headline())
                    tasks1.append(task)
                    task = asyncio.create_task(headline_parsing.time_headline())
                    tasks1.append(task)
                    task = asyncio.create_task(headline_parsing.tag_headline())
                    tasks1.append(task)
                    task = asyncio.create_task(Number_of_header_views(soup[1]).number_of_views())
                    tasks1.append(task)
                    task = asyncio.create_task(self.time_compasion(tasks, tasks1, list_url))
                    tasks1.append(task)
                    n = await asyncio.gather(*tasks1)
                    print(n)

                # await asyncio.gather(*tasks)

            await async_for(news_headline)


class News_page_parser(News_parser):
    def __init__(self, soup):
        super().__init__()
        self.soup = soup

    async def search_for_article_url(self):
        article_url = []
        list_url = await self.bs4_parser(RiaNews.tag_article_url, RiaNews.class_article_url)
        for url in list_url:
            article_url.append(RiaNews.url_title + url.get(RiaNews.get_tag_article_url))
        # print(article_url)
        return article_url

    async def search_for_next_page_url(self):
        next_page_url = await self.bs4_parser(RiaNews.tag_next_url, RiaNews.class_next_url)
        next_page_url = RiaNews.url_title + next_page_url[-1].get(RiaNews.get_tag_next_url)
        return next_page_url


class News_headline_parsing(News_parser):

    def __init__(self, soup):
        super().__init__()
        self.soup = soup

    async def search_for_news_headline(self):
        news_headline = await self.bs4_parser_itemprop(RiaNews.tag_news_headline, RiaNews.class_news_headline)
        news_headline = news_headline[3].get(RiaNews.get_news_headline)
        # print(news_headline)
        return news_headline

    async def time_headline(self):
        time_headline = await self.bs4_parser_itemprop(RiaNews.tag_time_headline_update,
                                                       RiaNews.itemprop_time_headline_Modified)
        for text in time_headline:
            time_headline = text.get_text(strip=True)
        if time_headline == []:
            time_headline = await self.bs4_parser_itemprop(RiaNews.tag_time_headline,
                                                           RiaNews.itemprop_time_headline_created)
            for text in time_headline:
                time_headline = text.get_text(strip=True)
        times = await Time_recognition().struct_time(time_headline)
        return times

    async def tag_headline(self):
        tags_headline = []
        tag_headline = await self.bs4_parser(RiaNews.tag_tag_headline, RiaNews.class_tag_headline)
        for text in tag_headline:
            tags_headline.append(text.get_text(strip=True))
        # print(tag_headline)
        return tags_headline

    async def razdel(self):
        print('--------------------------------------')


class Number_of_header_views(News_parser):

    def __init__(self, soup):
        super().__init__()
        self.soup = soup

    async def number_of_views(self):
        number_of_views = await self.bs4_parser(RiaNews.tag_views_headline, RiaNews.class_views_headline)
        for text in number_of_views:
            search_result = text.get_text().split()
        # print(int(search_result[0]))
        return int(search_result[0])


class Time_recognition(News_parser):
    def __init__(self):
        News_parser().__init__()

    async def struct_time(self, time_headline):
        struct_time = time.strptime(time_headline, "%Y-%m-%dT%H:%M")
        News_parser.news_time = struct_time
        # print(struct_time)
        return struct_time

    # async def struct_time(self):


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
url_ = "https://ria.ru/services/archive/widget/more.html"

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
