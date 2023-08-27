from os import getcwd, path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

DEFAULT_SCOPES = ['https://www.googleapis.com/auth/calendar']

class CalendarConnection:

    def __init__(self,
                 calendar_id: str,
                 scopes: list[str] = DEFAULT_SCOPES,
                 secret_path: str = path.join(getcwd(), 'app-secret.json'),
                 user_token_path: str = path.join(getcwd(), 'token.json'),
                 ) -> None:
        self._calendar_id = calendar_id
        self._scopes = scopes
        self._secret_path = secret_path
        self._token_path = user_token_path
        self._service = None


    def _get_credentials(self):
        creds = None
        if path.exists(self._token_path):
            creds = Credentials.from_authorized_user_file(
                    self._token_path,
                    self._scopes,
                    )

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                    self._secret_path, 
                    self._scopes,
                    )
            creds = flow.run_local_server(port=0)

        with open(self._token_path, 'w') as token:
            token.write(creds.to_json())

        return creds


    def _connect(self) -> None:
        creds = self._get_credentials()
        try:
            self._service = build('calendar', 'v3', credentials=creds)
        except HttpError as e:
            print(f'Attempted connection to gcal failed: {e}')


    def list_events(self, **kwargs):
        return self.service.events().list(**kwargs, calendarId=self._calendar_id)


    @property
    def service(self):
        self._connect()
        if self._service is None:
            raise Exception('Connection failed')

        return self._service

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

