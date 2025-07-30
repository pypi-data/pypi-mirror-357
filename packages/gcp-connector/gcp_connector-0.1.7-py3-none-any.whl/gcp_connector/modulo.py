from google.oauth2 import service_account
from google.cloud import bigquery
import pygsheets
import pandas as pd
from json import loads
from base64 import b64decode


class GoogleCloudPlatform:

    def __init__(self, credentials, scopes):
        self.credentials = loads(b64decode(credentials))
        self.scopes = scopes

    def read_gsheets_to_df(self, id_file, sheet):
        # Autorización de pygsheets
        credentials = service_account.Credentials.from_service_account_info(
            self.credentials, scopes=self.scopes
        )

        gs = pygsheets.authorize(custom_credentials=credentials)

        # Abrir la hoja de Google Sheets
        wb = gs.open_by_key(id_file)

        # Seleccionar la hoja específica
        ws = wb.worksheet_by_title(sheet)

        # Leer todos los valores como lista de listas
        data = ws.get_all_values(
            include_tailing_empty_rows=True, include_tailing_empty=True
        )

        df = pd.DataFrame(data)

        return df

    def extract_bq_to_df(self, query, project_id):

        credentials = service_account.Credentials.from_service_account_info(
            self.credentials
        )
        client = bigquery.Client(credentials=credentials, project=project_id)

        df = client.query(query).to_dataframe()

        return df

    def execute_query_bq(self, query, project_id):

        credentials = service_account.Credentials.from_service_account_info(
            self.credentials
        )
        client = bigquery.Client(credentials=credentials, project=project_id)
        truncate_query = query
        try:
            query_job = client.query(truncate_query)

            query_job.result()
        except Exception as e:
            print(f"Fail to execute query: {e}")
