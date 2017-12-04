
from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime
import dateutil.parser
import calendar

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

sleep = {'wakeup': '08:00:00', 'bedtime': '23:59:59'}
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
    #
    # events = []

    # page_token = None
    # while True:
    #   calendar_list = service.calendarList().list(pageToken=page_token).execute()
    #   for calendar_list_entry in calendar_list['items']:
    #     #print (calendar_list_entry['summary'])
    #     eventsResult = service.events().list(
    #         calendarId=calendar_list_entry['summary'], timeMin=now, timeMax=stopdate, singleEvents=True,
    #         orderBy='startTime').execute()
    #     events = eventsResult.get('items', events)
    #   page_token = calendar_list.get('nextPageToken')
    #   if not page_token:
    #     break

    conflict_dict = {}
    last_end = sleep['wakeup']
    ed = None
    et = None

    if not events:
        print('No upcoming events found.')
    for event in events:
        #print(event)
        start = event['start'].get('dateTime', event['start'].get('date'))
        day, time = start.split("T")
        # want to get free time until bedtime
        # this isnt right yet
        # print (ed)
        # print (day)
        # print (ed == day)
        # print (et < sleep['bedtime'])
        if et != None and ed != None:
            if (ed != day) and (et < sleep['bedtime']):
                print ("hello")
                breakTime(et, sleep['bedtime']+'-05:00', ed, conflict_dict)
        if day not in conflict_dict:
            conflict_dict[day] = []
            wakeup_format = day + 'T' + sleep['wakeup']
            if start > wakeup_format:
                breakTime(sleep['wakeup']+ '-05:00', time, day, conflict_dict)
        else:
            if (last_end < start) and (ed == day):
                d,t = last_end.split("T")
                breakTime(t,time,d,conflict_dict)
        # need to check bedtime to make sure it doesnt go over
        end = event['end'].get('dateTime', event['end'].get('date'))
        ed, et = end.split("T")
        print(start, event['summary'])
        # just want the end time !!
        last_end = end
        print (conflict_dict)

        # {(12-03, Sunday) : [(8,10), (10-12), (12, 1)]; (12-04, Monday): [(8,10), (10-12), (12, 1)]}
        # want to split 8-3 into 8-11:59, 12-3
        # calendar.day_name[my_date.weekday()]

def breakTime(start,end,day,dic):
    if (end >= '12:00:00') and (start < '12:00:00'):
        dic[day].append((start, '11:59:59-05:00'))
        if end >= '17:00:00':
            dic[day].append(('12:00:00-05:00', '16:59:59-05:00'))
        else:
            dic[day].append(('12:00:00-05:00', end))
    elif (end >='17:00:00') and (start < '17:00:00'):
        dic[day].append((start, '16:59:59-05:00'))
        dic[day].append(('17:00:00-05:00', end))
    else:
        dic[day].append((start, end))

# def createEvent(day, time, descrip, loc):
#     event = {}
#     event = {
#         'summary': descrip[0],
#         'location': loc,
#         'description': descrip[1],
#         'start': {
#             'dateTime': time[0],
#             'timeZone': 'America/New_York',
#         },
#         'end': {
#             'dateTime': '2015-05-28T17:00:00-07:00',
#             'timeZone': 'America/New_York',
#         },
#         'reminders':{
#             'useDefault': True,
#         }
#     }
#     return event


# def addWorkout(event):
#     event = service.events().insert(calendarId='primary', body=event).execute()
#     print 'Event created: %s' % (event.get('htmlLink'))

if __name__ == '__main__':
    main()