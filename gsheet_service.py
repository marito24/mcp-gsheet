import os

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")


def get_gsheet_service():
    """Builds and returns an authorized Google Sheets API service object."""
    if not SERVICE_ACCOUNT_FILE:
        raise ValueError(
            "Environment variable GOOGLE_APPLICATION_CREDENTIALS is not set."
        )
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        raise FileNotFoundError(
            f"Service account key file not found at: {SERVICE_ACCOUNT_FILE}"
        )

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(
        filename=SERVICE_ACCOUNT_FILE, scopes=scopes
    )

    try:
        service = build(
            serviceName="sheets",
            version="v4",
            credentials=creds,
            static_discovery=False,
        )
        return service
    except HttpError as err:
        print(f"Error building Sheets service: {err}")
        raise


# Lazy initialization of the service
_gsheet_service = None


def gsheet_service():
    """Returns a cached Sheets service object, initializing if needed."""
    global _gsheet_service
    if _gsheet_service is None:
        _gsheet_service = get_gsheet_service()
    return _gsheet_service
