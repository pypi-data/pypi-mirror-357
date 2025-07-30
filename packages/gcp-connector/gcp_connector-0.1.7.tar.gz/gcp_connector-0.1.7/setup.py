from setuptools import setup, find_packages

setup(
    name="gcp_connector",
    version="0.1.7",
    description="""Libreria de conexion a proyectos GCP,
    uso BigQuery, Google Sheets.""",
    author="Daniel Cristancho",
    author_email="daniersdan81@gmail.com",
    packages=find_packages(),
    install_requires=[
        "pandas==2.2.3",
        "google-auth==2.38.0",
        "google-auth-oauthlib==1.2.1",
        "google-api-python-client==2.160.0",
        "google-auth-httplib2==0.2.0",
        "google-cloud-bigquery==3.29.0",
        "google-crc32c==1.6.0",
        "pygsheets==2.0.6",
        "pyarrow==19.0.0",
        "db-dtypes==1.4.2",
        "google-cloud-storage==3.0.0",
        "google-cloud-bigquery-storage==2.30.0",
    ],
    python_requires=">=3.9",
)
