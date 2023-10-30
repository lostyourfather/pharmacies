import boto3
import pandas as pd
import io


class S3Class:

    def __init__(self, endpoint_url, key_id, access_key):
        self.s3 = boto3.resource('s3',
                                 endpoint_url=endpoint_url,
                                 aws_access_key_id=key_id,
                                 aws_secret_access_key=access_key,
                                 verify=False)

    def upload_file(self, bucket_name, file_name, data):
        # self.s3.Bucket(bucket_name).upload_file(file_path, file_name)
        self.s3.Object(bucket_name, file_name).put(Body=data)
    def download_file(self, bucket_name, file_path, file_name):
        self.s3.Bucket(bucket_name).download_file(file_name, file_path)

    def read_file(self, bucket_name, file_name):
        obj = self.s3.Object(bucket_name, file_name).get()
        df = pd.read_csv(io.BytesIO(obj['Body'].read()), sep=';')
        return df
# s3 = S3Class('http://localhost:9000',
#              'minioadmin',
#              'minioadmin')
# s3.upload_file('pharmacies', 'smth.csv', 'afs\nfad\n')