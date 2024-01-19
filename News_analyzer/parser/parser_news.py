import asyncio
import aiohttp
from bs4 import BeautifulSoup

#main_url = "https://ria.ru/services/archive/widget/more.html"
#tag = 'a'
class list_news:
    main_url = None
    tag = None
    html_text = None
    url_headers = []
    next_url = None


    async def client_reqest(self, url):
        self.main_url = url
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as responce:
                self.html_text = await responce.text()

    async def responce_parsing_headers(self, tag):
        self.tag = tag
        soup = BeautifulSoup(self.html_text, 'lxml')
        url_headers = soup.find_all(tag)
        for url_header in url_headers:
            self.url_headers.append('https://ria.ru' + url_header.get('href'))

    async def next_url (self):
        soup = BeautifulSoup(self.html_text, 'lxml')
        nexturl = soup.find_all('div', class_= 'lenta__item')
        self.next_url = 'https://ria.ru' + nexturl[-1].get('data-next')



list1 = list_news()
asyncio.run(list1.client_reqest("https://ria.ru/services/archive/widget/more.html"))
asyncio.run(list1.responce_parsing_headers('a'))
print(list1.url_headers)
asyncio.run(list1.next_url())
print(list1.next_url)
list2 = list_news()
asyncio.run(list2.client_reqest(list1.next_url))
asyncio.run(list2.responce_parsing_headers('a'))
print(list2.url_headers)