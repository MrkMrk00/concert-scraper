from os import getcwd, path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from gcalsync.objects import CalendarEvent
from scraper.models import Concert
from datetime import datetime

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

    def insert_event(self, event: CalendarEvent):
        return self.service.events().insert(calendarId=self._calendar_id, body=event.to_dict())


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


class Synchronizer:
    def __init__(self, service: CalendarConnection):
        self._service = service

    def _find_sync_concerts(self, concerts: list[Concert]):
        min_date = None
        max_date = None

        if len(concerts) > 0:
            min_date = min([ d.start for d in concerts ])
            max_date = max([ d.end or d.start for d in concerts ])
        
        all_concert_evts = []
        page_tok = None

        # TIMEZONE IN TIMES
        while True:
            events = self._service.list_events(
                    privateExtendedProperty='created_by=gcalconcertsync',
                    #timeMax=max_date.isoformat(timespec='minutes') if max_date else None,
                    #timeMin=min_date.isoformat(timespec='minutes') if min_date else None,
                    pageToken=page_tok,
                    ).execute()
            all_concert_evts.extend(events['items'])

            for e in events['items']:
                print(e)
            page_tok = events.get('nextPageToken')
            if page_tok is None:
                break

        return all_concert_evts

    def sync_concerts(self, concerts: list[Concert]):
        existsing = self._find_sync_concerts(concerts)
        existsing_names = [ c.summary for c in existsing ]
        to_insert = [ c for c in concerts 
                     if c.name not in existsing_names 
                        and c.start > datetime.now() ]

        for c in to_insert:
            cal_event = CalendarEvent.from_concert(c)
            print(f'Inserting {cal_event=}')
            resp = self._service.insert_event(cal_event).execute()
            print(resp + '\n')

