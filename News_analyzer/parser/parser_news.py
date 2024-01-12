import asyncio
import aiohttp
from bs4 import BeautifulSoup

main_url = "https://ria.ru/services/archive/widget/more.html"
tag = 'a'
async def client_reqest (url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as responce:
            html = await responce.text ()
            return html

async def responce_parsing_headers (html_text, tag):
    soup = BeautifulSoup(html_text,'lxml')
    url_headers = soup.find_all(tag)
    return url_headers

html_text = asyncio.run(client_reqest(main_url))
for a in asyncio.run(responce_parsing_headers(html_text, tag)):
    print(a.get('href'))

