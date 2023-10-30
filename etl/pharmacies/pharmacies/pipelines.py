import datetime
from io import StringIO
from classes.s3_class import S3Class


class PharmaciesPipeline:

    def open_spider(self, spider):
        print("open spider")
        self.buf = StringIO()
        date_today = datetime.datetime.now().strftime("%d-%m-%Y")
        self.buf.name = f"{spider.name}_{date_today}.csv"
        self.buf.write(f"header;description;value;currency;is_prescription;img_src\n")

    def process_item(self, item, spider):
        print("process spider")
        self.buf.write(f"{item.header.lower()};{item.description};{item.price};{item.currency};{item.is_prescription};{item.img_src}\n")

    def close_spider(self, spider):
        print("close spider", self.buf.getvalue())
        s3_session = S3Class('http://minio:9000', 'minioadmin', 'minioadmin')
        s3_session.upload_file('pharmacies', self.buf.name, self.buf.getvalue())
        print(self.buf.name)
