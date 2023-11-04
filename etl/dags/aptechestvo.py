import datetime
from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from airflow.operators.bash_operator import BashOperator
import sys
sys.path.append('')
from pharmacies.classes.s3_class import S3Class
from models.base import get_engine
from models.pharmacies import Product, Price, SiteName
from sqlalchemy import select
from sqlalchemy.orm import Session


def upload_data_to_db(**kwargs):
    ti = kwargs['ti']
    file_name = ti.xcom_pull(task_ids='scrapy')
    s3_obj = S3Class(
        'http://minio:9000',
        'minioadmin',
        'minioadmin'
    )
    data = s3_obj.read_file('pharmacies', file_name)
    engine = get_engine()
    with Session(engine) as session:
        statement = select(Product)
        products = session.execute(statement).all()
        statement = select(SiteName)
        site_names = session.execute(statement).all()
        site_names = {site_name[0].title: site_name[0].site_name_id for site_name in site_names}
        products = {product[0].header: product[0].product_id for product in products}
        for i, row in data.iterrows():
            product_id = products.get(row.header)
            if not product_id:
                product = Product(header=row.header, description=row.description,
                                  is_prescription=row.is_prescription, img_src=row.img_src,
                                  site_name_id=site_names[row.site_name], link=row.link)
                session.add(product)
                session.flush()
                session.commit()
                product_id = product.product_id
            price = Price(product_id=product_id, value=row.value, currency=row.currency)
            session.add(price)
            session.flush()
            session.commit()


with DAG(
    dag_id='aptechestvo_etl',
    schedule_interval="0 0 * * *",
    start_date=datetime.datetime(2023, 10, 19),
    catchup=False,
    dagrun_timeout=datetime.timedelta(minutes=360),
    tags=["parser"]
) as dag:
    crawler_task = BashOperator(
          task_id='scrapy',
          bash_command='cd ${AIRFLOW_HOME}/pharmacies/pharmacies/spiders && scrapy crawl aptechestvo',
          do_xcom_push=True)

    upload_data = PythonOperator(
        task_id="upload_data",
        python_callable=upload_data_to_db,
        dag=dag
    )


crawler_task >> upload_data
