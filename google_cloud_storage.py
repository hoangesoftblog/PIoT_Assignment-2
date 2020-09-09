# Imports the Google Cloud client library
from google.cloud import storage
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

"""
TUTORIAL:
https://cloud.google.com/storage/docs/reference/libraries
"""


class GoogleCloudStorage:
    """Google calls files on Cloud Storage as blobs"""

    def __init__(self):
        AUTHORIZATION_SCOPES = [
            'https://www.googleapis.com/auth/devstorage.full_control']

        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token_cloud_storage.pickle'):
            with open('token_cloud_storage.pickle', 'rb') as token:
                creds = pickle.load(token)

        # If not successful, collecting new Token to access Calendar
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials_google.json', AUTHORIZATION_SCOPES)
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open('token_cloud_storage.pickle', 'wb') as token:
                pickle.dump(creds, token)

        # Instantiates a client
        self.storage_client = storage.Client(
            project="piot-assignment2-287110", credentials=creds)

        # Connect to bucket on Cloud Storage
        self.bucket = self.storage_client.get_bucket("facial_img")

    def upload_from_filename(self, file_name, name_on_storage, **keyword_args):
        """
        blob.upload_from_filename has many arguments.\n
        Keywords-arguments keyword_args will store whatever
        params needed for blob.upload_from_filename   
        """
        blob = self.bucket.blob(name_on_storage)
        blob.upload_from_filename(file_name, **keyword_args)
        print(f"Upload file {file_name} and name as {name_on_storage}")

    def upload_from_file(self, file_obj, name_on_storage, **keyword_args):
        """
        file_obj: Using open()\n\n
        blob.upload_from_file has many arguments.\n
        Keywords-arguments keyword_args will store whatever
        params needed for blob.upload_from_file  
        """
        blob = self.bucket.blob(name_on_storage)
        blob.upload_from_file(file_obj, **keyword_args)
        print(f"Upload object {name_on_storage}")

    def download_file(self, source_file_name, destination_file_name, **keyword_args):
        """
        Keywords-arguments keyword_args will store whatever
        params needed for blob.upload_from_file
        """
        blob = self.bucket.blob(source_file_name)
        blob.download_to_filename(destination_file_name, **keyword_args)
        print(f"Download file {source_file_name} and save as {destination_file_name}")

    def download_trainer(self):
        # Connect to bucket on Cloud Storage
        trainer_bucket = self.storage_client.get_bucket("trainer")
        blob = trainer_bucket.blob("trainer.yml")
        blob.download_to_filename("trainer/trainer.yml")
        print("Trainer.yml downloaded")

    def get_all_files(self, **keyword_args):
        """
        Keywords-arguments keyword_args will store whatever
        params needed for Client.list_blobs
        """
        blobs = self.storage_client.list_blobs(
            self.bucket.name, **keyword_args)
        return blobs


if __name__ == "__main__":
    cloud_storage = GoogleCloudStorage()
    cloud_storage.get_all_files()
