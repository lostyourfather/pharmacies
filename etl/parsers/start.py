from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def spam():
    process = CrawlerProcess(get_project_settings())
    process.crawl('farmani')
    process.start()


if __name__ == '__main__':
    pass
