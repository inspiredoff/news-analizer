import asyncio
import aiohttp
from bs4 import BeautifulSoup


class News_parser:

    def __init__(self, url):
        self.next_page_url = None
        self.article_url = []
        self.next_page_url.__str__()

    async def client_request(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                html_text = await response.text()
        return html_text

    async def cooking_soup(self):
        html_text = await self.client_request()
        self.soup = BeautifulSoup(html_text, 'lxml')

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

    async def search_for_article_url(self):
        article_url = await self.bs4_parser(self.tag_article_url, self.class_article_url)
        for url in article_url:
            self.article_url.append(self.url_title + url.get(self.get_tag_article_url))

    async def search_for_next_page_url(self):
        next_page_url = await self.bs4_parser(self.tag_next_url, self.class_next_url)
        self.next_page_url = self.url_title + next_page_url[-1].get(self.get_tag_next_url)

    async def parser(self):
        tasks = []
        await self.cooking_soup()
        task = asyncio.create_task(self.search_for_article_url())
        tasks.append(task)
        task = asyncio.create_task(self.search_for_next_page_url())
        tasks.append(task)

        await asyncio.gather(*tasks)


class News_headline_parsing(News_parser):
    def __init__(self, url):
        super().__init__(url)

    async def search_for_news_headline(self):
        news_headline = await self.bs4_parser(self.tag_news_headline, self.class_news_headline)
        for text in news_headline:
            self.news_headline = text.get_text(strip=False)
            print(self.news_headline)

    async def time_headline(self):
        time_headline = await self.bs4_parser(self.tag_time_headline_update, self.class_time_headline_update)
        for text in time_headline:
            time_headline = text.get_text(strip=True)
        if time_headline == '':
            time_headline = await self.bs4_parser(self.tag_time_headline, self.class_time_headline)
            for text in time_headline:
                time_headline = text.get_text(strip=True)
        else:
            time_headline = time_headline[12:-1]
        self.time_headline = time_headline
        print(self.time_headline)

    async def tag_headline(self):
        tag_headline = await self.bs4_parser(self.tag_tag_headline, self.class_tag_headline)
        for text in tag_headline:
            self.tag_headline = text.get_text(strip=True)
            print(self.tag_headline)

    async def razdel(self):
        print('--------------------------------------')

    async def parser_1(self):
        tasks = []
        await self.cooking_soup()
        task = asyncio.create_task(self.search_for_news_headline())
        tasks.append(task)
        task = asyncio.create_task(self.time_headline())
        tasks.append(task)
        task = asyncio.create_task(self.tag_headline())
        tasks.append(task)
        task = asyncio.create_task(self.razdel())
        tasks.append(task)

        await asyncio.gather(*tasks)


class RiaNews(News_headline_parsing, News_parser):
    def __init__(self, url):
        super().__init__(url)
        self.main_url = "https://ria.ru/services/archive/widget/more.html"
        self.url_title = "https://ria.ru"
        self.url = url

        self.tag_article_url = 'a'
        self.class_article_url = None
        self.get_tag_article_url = 'href'

        self.tag_next_url = 'div'
        self.class_next_url = 'lenta__item'
        self.get_tag_next_url = 'data-next'

        self.tag_news_headline = None
        self.class_news_headline = 'article__title'

        self.tag_time_headline = None
        self.class_time_headline = 'article__info-date'
        self.tag_time_headline_update = None
        self.class_time_headline_update = 'article__info-date-modified'

        self.tag_tag_headline = None
        self.class_tag_headline = 'article__tags-item'


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

for page in range(1, 5):
    c = RiaNews(url_)
    asyncio.run(c.parser())
    news_header_url = c.article_url
    print(c.article_url)
    url_ = c.next_page_url


    async def async_for():
        tasks = []
        for url in news_header_url:
            task = asyncio.create_task(RiaNews(url).parser_1())
            tasks.append(task)
        await asyncio.gather(*tasks)


    asyncio.run(async_for())
