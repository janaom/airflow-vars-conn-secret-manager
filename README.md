# Keep Your Airflow Variables and Connections Safe with GCP Secret Manager 🔐

Google Cloud [Secret Manager](https://cloud.google.com/secret-manager/docs/overview) is a robust tool within the Google Cloud Platform (GCP) that facilitates the secure storage, management, and retrieval of sensitive data in the form of binary blobs or text strings. Only authorized users can access and view the contents of these secrets as needed. Secret Manager is particularly useful for handling runtime configuration details such as database passwords, API keys, and TLS certificates, ensuring the safety and integrity of crucial application information within the GCP environment.

In this RP, I will explore the best practices of integrating Google Cloud Secret Manager with Composer. To illustrate these practices, I have created a DAG with several variables and a Snowflake connection. Using this setup, we will establish a connection to Snowflake, execute a query to retrieve relevant data, and subsequently save the result as a CSV file in a GCP bucket. Through this demonstration, you will learn how to effectively utilize Secret Manager with Composer to ensure secure and efficient data processing.

![1 fCTY9UXa7AcAFRjZXjG4DQ](https://github.com/janaom/airflow-vars-conn-secret-manager/assets/83917694/74911cc9-9f9e-47f4-9e5b-6ecd5dd9b049)

# ❄️Snowflake

To demonstrate the process, I set up a Snowflake environment consisting of an account, database, schema, and table. Using the Good Reads Dataset (Top 1000 Books) from [Kaggle](https://www.kaggle.com/datasets/prishasawhney/good-reads-top-1000-books?resource=download), I uploaded a CSV file to the Snowflake table. To ensure the desired functionality, I tested the query I intended to use within the DAG. Ultimately, I decided that my goal would be to extract the top 10 books from the dataset and store them in a CSV file within a GCS bucket.

Access your Snowflake profile and copy the account URL, as we'll need it for the next step.

![Screenshot (1684)](https://github.com/janaom/airflow-vars-conn-secret-manager/assets/83917694/3bb5b4fe-ae30-403f-b2e6-640cc78a0e8b)


# ✨Create Composer 2

To begin, we'll set up a Composer 2 environment.

![1 sWSNdE1LIhMNVjv3D_9leg](https://github.com/janaom/airflow-vars-conn-secret-manager/assets/83917694/d3099b23-321e-40b2-ac70-64a0bf926d53)


If this is your first time setting up Composer 2, ensure you complete the necessary access permissions setup. To do this, grant the Cloud Composer v2 API Service Agent Extension role to the `service-<…>@cloudcomposer-accounts.iam.gserviceaccount.com` service account.

![1 FVrx05c6Aw9jClsTWkMOvA](https://github.com/janaom/airflow-vars-conn-secret-manager/assets/83917694/44cf105d-3190-4284-a5fa-72921c9520a5)


To integrate Snowflake with your Composer environment, you first need to install the [apache-airflow-providers-snowflake](https://pypi.org/project/apache-airflow-providers-snowflake/) package. This package enables Airflow to connect to Snowflake and interact with its resources. Once the installation is complete, you can proceed with adding the Snowflake connection details either in the Airflow UI or within the Secret Manager, depending on your preferred approach for managing sensitive information.

![1 JEGssnt9dmqUpr5lupPSUQ](https://github.com/janaom/airflow-vars-conn-secret-manager/assets/83917694/3a0802d3-153f-4ed5-93b7-fb632f007c65)


The apache-airflow-providers-snowflake package is required for utilizing the `airflow.providers.snowflake` module in your code. Without this package installed in your Composer environment, you won't be able to import the necessary Snowflake-related classes and methods provided by the module. Consequently, any DAGs that rely on `airflow.providers.snowflake` will fail to load, resulting in errors and preventing the successful execution of your Airflow tasks.

![image](https://github.com/janaom/airflow-vars-conn-secret-manager/assets/83917694/a4275f61-409e-4bb4-ab8b-63a0a7f9f031)


# 🗝️Use Secret Manager with Cloud Composer

It is generally not considered a best practice to hardcode variables directly into your code or to input them through the Airflow UI. Doing so can potentially compromise the security and maintainability of your codebase. Instead, it is advisable to utilize an external secrets management solution, such as Google Cloud Secret Manager, to securely store and manage both variables and connection details, ensuring the integrity of your application and promoting best practices in data security.

By using Secret Manager in conjunction with Composer, you can securely store and manage these secrets, reducing the risk of accidental exposure or unauthorized access.

Secret Manager allows you to define fine-grained access controls for secrets, ensuring that only authorized individuals or services can access the sensitive information stored within. This helps enforce the principle of least privilege and strengthens the overall security posture of your Composer environment.

## Enable and configure the Secret Manager backend

Here's how to configure Composer to use Secret Manager and update your DAG accordingly:

Step 1: Configure Composer to Use Secret Manager
- Set up Secret Manager as your secrets backend in Composer by adding the following as Airflow Configuration Overrides to your environment

```bash
[secrets]
backend = airflow.providers.google.cloud.secrets.secret_manager.CloudSecretManagerBackend
backend_kwargs = {"project_id": "<project-id>", "connections_prefix":"example-connections", "variables_prefix":"example-variables", "sep":"-"}
```
Replace `<project-id>` with your actual GCP project ID. Here is an example.

![1 E6KMJZ_rsOHt0QLcG4TlCA](https://github.com/janaom/airflow-vars-conn-secret-manager/assets/83917694/670efb66-b492-49bc-a50c-ccae5340d780)

- Ensure your Composer environment has the correct permissions to access Secret Manager. Use IAM roles to grant the necessary permissions to the service account associated with your Composer environment. Assign the role Secret Manager Secret Accessor to the service account to allow it to access the secret.

Step 2: Store Your Variables and Connections in Secret Manager

- Create secrets in Secret Manager for your variables and connections. Use the following naming conventions:
    - For variables: `airflow-variables-<variable_name>`
    - For connections: `airflow-connections-<connection_id>`
 
For example, to create a secret for the `gcs_bucket` variable, the secret name should be `airflow-variables-gcs_bucket`.

- Add the variables and connections to Secret Manager using the Google Cloud Console or the `gcloud` CLI tool.

![1 xsc3RmtcJIeGZIrcgFYpyw](https://github.com/janaom/airflow-vars-conn-secret-manager/assets/83917694/b6416f4f-e012-4718-847f-1523ae584290)

The following example showcases how a secret appears within the Google Cloud Secret Manager.

![1 2SxOUFbxJrfNvtnRoSgUBQ](https://github.com/janaom/airflow-vars-conn-secret-manager/assets/83917694/d3b4dfc7-9a4c-4843-b44f-ecd1a146d2e4)

If you are granted the required level of access privileges, you will have the ability to view the secret's value.

![1 neiR0li9yKWMQgtX174HvA](https://github.com/janaom/airflow-vars-conn-secret-manager/assets/83917694/8b41be2b-abdf-4f8c-a0a7-86c2afffa8c1)

Certain connections may require a specific value format. For instance, when adding a Snowflake connection value in Secret Manager, consider the following example: If your Snowflake account URL is `https://abc123.europe-west4.gcp.snowflakecomputing.com`, then your connection value should follow this format:

```json
{
  "conn_type": "snowflake",
  "login": "your-login",
  "password": "your-password",
  "host": "abc123",
  "schema": "your-schema",
  "extra": {
    "database": "your-database",
    "warehouse": "your-wh",
    "role": "your-role",
    "account": "abc123.europe-west4.gcp"
  }
}
```

Step 3: Update Your DAG

Modify your DAG to retrieve variables from Secret Manager using the `Variable` class. Since you've configured Secret Manager as the secrets backend, `Variable.get()` will automatically fetch the variables from Secret Manager.

```python
from airflow.models import Variable

    gcs_bucket = Variable.get('gcs_bucket')
    gcs_path = Variable.get('gcs_path')
```

Customize the provided DAG (dag.py) by replacing placeholder variables with your own values and updating the `snowflake_query` logic to align with your project's unique requirements.

Save the DAG file in Composer's "dags" folder to complete the deployment.

![1 sggcD864PmPQ8ETdW4EFbA](https://github.com/janaom/airflow-vars-conn-secret-manager/assets/83917694/5b37c84f-9a74-40f8-875b-f5a83a73d021)

If you have previously added any variables or connections through the Airflow UI, it is recommended to remove them and test the DAG using the updated configuration.

Cloud Composer first attempts to retrieve variables and connections from Secret Manager. If unsuccessful, it then searches the environment variables and the Airflow database for the requested variable or connection.

Refer to the [Configure Secret Manager for your environment](https://cloud.google.com/composer/docs/composer-2/configure-secret-manager) guide for additional information and setup instructions.

![1 aVsEWthpC4ija_pH9odIyQ](https://github.com/janaom/airflow-vars-conn-secret-manager/assets/83917694/e707ab43-f789-4d79-8d42-80b699befc42)

For further details, review the task logs. However, please note that the logs may not explicitly indicate the source of the variables and connections.

```bash
INFO - Using connection ID 'snowflake_default' for task execution.
#This log message indicates the number of rows returned in the first chunk of data fetched from Snowflake.
INFO - Number of results in first chunk: 11
INFO - Data transfer from Snowflake to GCS completed successfully
```

Upon the successful completion of the DAG execution, you will find the CSV file generated by the process within the specified bucket you created.

![1 NC5wmF7CET_TQYLmep5Ekw](https://github.com/janaom/airflow-vars-conn-secret-manager/assets/83917694/964c038e-600e-4291-a86a-b9ab57ecfb4f)

The contents of the file can be examined as follows: If your `snowflake_query` is `'SELECT * FROM goodreads_top.books.books LIMIT 11'`, the query will return a result set containing 11 rows. This dataset includes the header row, followed by the information for the top 10 books as specified in the query.

```text
Book Name,Author,Average Rating,Number of Ratings,Score on Goodreads
To Kill a Mockingbird,Harper Lee,4.26,6129090,17358.0
1984,George Orwell,4.19,4604557,15474.0
Pride and Prejudice,Jane Austen,4.29,4273146,15135.0
Harry Potter and the Sorcerer's Stone (Harry Potter, #1),J.K. Rowling,4.47,10063128,12440.0
The Great Gatsby,F. Scott Fitzgerald,3.93,5244056,10828.0
Jane Eyre,Charlotte Brontë,4.15,2095866,10613.0
Lord of the Flies,William Golding,3.69,2906413,10098.0
Alice's Adventures in Wonderland / Through the Looking-Glass,Lewis Carroll,4.06,564072,9225.0
The Lord of the Rings,J.R.R. Tolkien,4.53,676596,9201.0
The Hobbit (The Lord of the Rings, #0),J.R.R. Tolkien,4.29,3977772,9013.0
```

You can also observe and verify these actions by reviewing the Query History in Snowflake. The Snowflake Query History feature provides a detailed log of all executed queries within your Snowflake account, allowing you to monitor, track, and analyze your data processing activities.

![1 YcGvXQQklSNdyII-LtnA7Q](https://github.com/janaom/airflow-vars-conn-secret-manager/assets/83917694/27202314-5ea6-4bfc-bf84-49b1d3e74095)

If you'd like to share your experiences with Secret Manager or have any thoughts on the topic, feel free to reach out to me on [LinkedIn](https://www.linkedin.com/in/jana-polianskaja/). I'd love to hear from you and connect! 😊


