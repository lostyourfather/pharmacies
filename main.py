from etl.parsers.classes.s3_class import S3Class


if __name__ == '__main__':
    s3 = S3Class('http://localhost:9000', 'minioadmin', 'minioadmin')
    s3.upload_file('pharmacies', '/Users/rodinam/Desktop/pharmacies/parsers/aptechestvo.csv', 'aptechestvo.csv')
    s3.download_file('pharmacies', '/Users/rodinam/Desktop/pharmacies/parsers/aptechestvo.csv', 'aptechestvo.csv')
