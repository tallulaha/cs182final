
from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime
import dateutil.parser

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'

sleep = {'wakeup': '8AM', 'bedtime': '12AM'}
time_preferences = ['morning', 'afternoon', 'evening']
workout_goals = ['lose weight', 'gain muscle', 'increase endurance', 'new skills']

def getDateTimeFromISO8601String(s):
    d = dateutil.parser.parse(s)
    return d

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials



def main():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    #print(datetime.timedelta(days=7))
    now = datetime.datetime.utcnow().isoformat() # 'Z' indicates UTC time
    #todaydate = datetime.datetime.strptime(now,"%Y-%m-%d")
    print (now)
    now, nowtime = now.split("T")
    todaydate = getDateTimeFromISO8601String(now)
    oneweek = datetime.timedelta(days=7)
    stopdate = todaydate + oneweek
    print (now)
    stopdate = stopdate.isoformat()
    #stopdate.replace("+00:00","")
    print (stopdate)
    stopdate, time2 = stopdate.split("T")
    stopdate = stopdate + 'T' + nowtime + 'Z'
    print (stopdate)
    now = now + 'T' + nowtime + 'Z'
    print (now)

    print('Getting the upcoming weeks events')
    # need to think about if there are multiple calendars 
    eventsResult = service.events().list(
        calendarId='primary', timeMin=now, timeMax=stopdate, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])

def createEvent(day, time, descrip, loc):
    event = {}
    event = {
        'summary': descrip[0],
        'location': loc,
        'description': descrip[1],
        'start': {
            'dateTime': time[0],
            'timeZone': 'America/New_York',
        },
        'end': {
            'dateTime': '2015-05-28T17:00:00-07:00',
            'timeZone': 'America/New_York',
        },
        'reminders':{
            'useDefault': True,
        }
    }
    return event


def addWorkout(event):
    event = service.events().insert(calendarId='primary', body=event).execute()
    print 'Event created: %s' % (event.get('htmlLink'))

if __name__ == '__main__':
    main()