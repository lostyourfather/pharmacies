import scrapy
from ..items import FarmaniItem


class FarmaniSpider(scrapy.Spider):
    name = "farmani"

    def start_requests(self):
        urls = [
            'https://farmani.ru/catalog/lekarstva_i_bady/?PAGEN_1=1'
        ]
        yield scrapy.Request(url=urls[0], callback=self.get_pages)

    def get_pages(self, response):
        max_page = response.css("a.dark_link::text").getall()[-1]
        print('IMPORTANT', max_page)
        max_page = 3
        for page in range(1, int(max_page)):
            yield scrapy.Request(url=f'https://farmani.ru/catalog/lekarstva_i_bady/?PAGEN_1={page}',
                                 callback=self.parse_page)


    def parse_page(self, response):
        for i in range(0, 20):
            print(i)
            header = response.css("div.item-title")[i].css("a.dark_link").css("span::text").get()
            header = header.split(',')
            description = header[1]
            header = header[0]
            print('header', header)
            price = response.css("span.element_price_block")[i].css("span.default_price::text").get()
            price = price.split(' ')
            currency = price[-1][:-1]
            price = price[0]
            print('price', price)
            img_src = "https://farmani.ru/" + response.css("a.thumb.shine")[i].css("img").xpath("@src").get()
            print('img_src', img_src)
            is_prescription = 'img' in response.css("div.recipe")[i].extract()
            print('is_prescription', is_prescription)
            object = FarmaniItem(header=header, description=description, price=price, currency=currency, is_prescription=is_prescription, img_src=img_src)
            yield object
