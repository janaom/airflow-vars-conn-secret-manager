from airflow import DAG
from airflow.models import Variable
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
from google.cloud import storage
import logging

default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'snowflake_to_gcs_sm',
    default_args=default_args,
    description='Query Snowflake and save to GCS',
    schedule_interval=timedelta(days=1),
    catchup=False,
)

def transfer_snowflake_to_gcs(**context):
    #Retrieve variables from Airflow UI/Secret Manager
    gcs_bucket = Variable.get('gcs_bucket')
    gcs_path = Variable.get('gcs_path')

    snowflake_query = 'SELECT * FROM goodreads_top.books.books LIMIT 11'
    filename = '/tmp/snowflake_data.csv'

    #Use SnowflakeHook to establish a connection
    hook = SnowflakeHook(snowflake_conn_id='snowflake_default')
    conn = hook.get_conn()
    cursor = conn.cursor()

    try:
        #Execute the query and fetch the data
        cursor.execute(snowflake_query)
        data = cursor.fetchall()

        #Save the data to a file
        with open(filename, 'w') as f:
            for row in data:
                f.write(','.join([str(item) for item in row]) + '\n')

        #Upload the file to GCS
        client = storage.Client()
        bucket = client.bucket(gcs_bucket)
        blob = bucket.blob(gcs_path + 'file.csv')
        blob.upload_from_filename(filename)

        logging.info("Data transfer from Snowflake to GCS completed successfully")

    except Exception as e:
        logging.error(f"Data transfer from Snowflake to GCS failed: {str(e)}")
        raise

    finally:
        #Close the cursor and connection
        cursor.close()
        conn.close()

#Task to transfer data from Snowflake to GCS
transfer_data = PythonOperator(
    task_id='transfer_snowflake_to_gcs',
    python_callable=transfer_snowflake_to_gcs,
    provide_context=True,
    dag=dag,
)
