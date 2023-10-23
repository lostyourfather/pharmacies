# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class PharmaciesPipeline:
    def open_spider(self, spider):
        with open(f'{spider.name}.csv', 'w') as fw:
            fw.write(f"header,price,is_prescription,img_src")

    def process_item(self, item, spider):
        print("IMPORTANT", dir(spider), "NAME", spider.name)
        print("HEADER PIPELINE", item.header)
        with open(f'{spider.name}.csv', 'a') as fw:
            fw.write(f"{item.header},{item.price},{item.is_prescription},{item.img_src}\n")
