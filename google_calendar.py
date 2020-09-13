from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pprint

"""TUTORIAL:
https://karenapp.io/articles/how-to-automate-google-calendar-with-python-using-the-calendar-api/
"""


class GoogleCalendar():
    calendarList_id = "b6omo64aca40geo3fa6svitkg4@group.calendar.google.com"

    def __init__(self):
        AUTHORIZATION_SCOPES = ['https://www.googleapis.com/auth/calendar']

        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token_calendar.pickle'):
            with open('token_calendar.pickle', 'rb') as token:
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
            with open('token_calendar.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('calendar', 'v3', credentials=creds)

    def add_event(self, user_id, car_id, start_time: datetime, end_time: datetime, details, **additional_params):
        """
        additional_params is implemented to be put into the body of the request from the API
        The API can be seen at:
        https://developers.google.com/calendar/v3/reference/events/list?authuser=1&apix_params=%7B%22calendarId%22%3A%22b6omo64aca40geo3fa6svitkg4%40group.calendar.google.com%22%7D
        """
        start, end = start_time.isoformat(), end_time.isoformat()
        print(start)

        response = self.service.events().insert(calendarId=self.calendarList_id, body={
            "summary": f"Booking: User {user_id} - Car {car_id}",
            "description": f"""Booking for User {user_id} - Car {car_id}. {details}""",
            "start": {"dateTime": start, "timeZone": "Asia/Ho_Chi_Minh"},
            "end": {"dateTime": end, "timeZone": "Asia/Ho_Chi_Minh"},
            **additional_params
        }).execute()

        # print("Created event")
        # print("ID: ", response['id'])
        # print("Summary: ", response['summary'])
        # print("Starts at: ", response['start']['dateTime'])
        # print("Ends at: ", response['end']['dateTime'])

        return response

    def get_all_events(self, **additional_params):
        """The API can be seen at:
        https://developers.google.com/calendar/v3/reference/events/list?authuser=1&apix_params=%7B%22calendarId%22%3A%22b6omo64aca40geo3fa6svitkg4%40group.calendar.google.com%22%7D
        """
        next_page_token = None
        events = []
        while True:
            events_result = self.service.events().list(pageToken=next_page_token,
                                                       calendarId=self.calendarList_id, **additional_params).execute()
            new_events = events_result.get('items', [])
            print()
            if not new_events:
                print('No upcoming events found.')
            else:
                events.extend(new_events)

            next_page_token = events_result.get("nextPageToken")
            if not next_page_token:
                break

        return events

    def get_all_calendarsList(self):
        # Next page-token is a token used to see next list of calendars
        next_page_token = None

        while True:
            # Each person can have many calendars (Really???????)
            calendars_list = self.service.calendarList().list(pageToken=None).execute()
            calendars = calendars_list.get("items", [])

            # This is just fail-safe case
            if not calendars:
                print("No calendar")
            else:
                for calendar in calendars:
                    summary = calendar['summary']
                    id = calendar['id']
                    primary = "Primary" if calendar.get('primary') else ""
                    print("%s\t%s\t%s" % (summary, id, primary))

            next_page_token = calendars_list.get("nextPageToken")
            if not next_page_token:
                break

    def cancel_event(self, event_id):
        response = self.service.events().delete(
            calendarId=self.calendarList_id, eventId=event_id).execute()
        return response

    def update_event(self, event_id, UID, CID, from_time, to_time, booking_details, **additional_params):
        """
        additional_params is implemented to be put into the body of the Request from the API
        The API can be seen at:
        https://developers.google.com/calendar/v3/reference/events/list?authuser=1&apix_params=%7B%22calendarId%22%3A%22b6omo64aca40geo3fa6svitkg4%40group.calendar.google.com%22%7D
        """
        if from_time is str:
            from_time = datetime.datetime.strptime(
                from_time, "%Y-%m-%d %H:%M:%S")
        if to_time is str:
            to_time = datetime.datetime.strptime(to_time, "%Y-%m-%d %H:%M:%S")

        start, end = from_time.isoformat(), to_time.isoformat()

        response = self.service.events().update(calendarId=self.calendarList_id, eventId=event_id, body={
            "summary": f"Booking: User {UID} - Car {CID}",
            "description": f"""Booking for User {UID} - Car {CID}. {booking_details}""",
            "start": {"dateTime": start, "timeZone": "Asia/Ho_Chi_Minh"},
            "end": {"dateTime": end, "timeZone": "Asia/Ho_Chi_Minh",
            **additional_params
            }
        }).execute()

        return response

    def cancel_all_events(self):
        events = self.get_all_events()
        for event in events:
            self.cancel_event(event["id"])


if __name__ == "__main__":
    calendar = GoogleCalendar()
    # calendar.get_all_calendarsList()
    # print(len(calendar.get_all_events()))
    # calendar.add_event(1, 2, datetime.datetime.now(), datetime.datetime.now() + datetime.timedelta(1), "birthday today")
    # calendar.cancel_all_events()
    # print(len(calendar.get_all_events()))
