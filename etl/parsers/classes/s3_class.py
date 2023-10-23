import boto3


class S3Class:

    def __init__(self, endpoint_url, key_id, access_key):
        self.s3 = boto3.resource('s3',
                                 endpoint_url=endpoint_url,
                                 aws_access_key_id=key_id,
                                 aws_secret_access_key=access_key)

    def upload_file(self, bucket_name, file_path, file_name):
        self.s3.Bucket(bucket_name).upload_file(file_path, file_name)

    def download_file(self, bucket_name, file_path, file_name):
        self.s3.Bucket(bucket_name).download_file(file_name, file_path)
