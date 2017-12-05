
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
    print ("Events", events)
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
        #print(start, event['summary'])
        # just want the end time !!
        last_end = end
        #print ("this is the available time calendar")
    #print (conflict_dict)
    conflict_dict = orderTimes(conflict_dict, 'afternoon')
    conflict_dict = orderDays(conflict_dict)
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

def orderTimes(availabledict, timepref):
    # https://stackoverflow.com/questions/3096953/how-to-calculate-the-time-interval-between-two-time-strings
    from datetime import datetime

    for day, timelist in availabledict.iteritems():
        # create a new list of sorted times
        sorttimes = []
        timeinpref = datetime.strptime('00:00:00', '%H:%M:%S')
        totaltime = datetime.strptime('00:00:00', '%H:%M:%S')
        for (start, end) in timelist:
            startdate = datetime.strptime(start[0:8], '%H:%M:%S')
            enddate = datetime.strptime(end[0:8], '%H:%M:%S')
            time = enddate - startdate
            if timepref == 'morning':
                # should be wake time
                scutoff = datetime.strptime('05:00:00', '%H:%M:%S')
                ecutoff = datetime.strptime('11:59:59', '%H:%M:%S')
            elif timepref == 'afternoon':
                scutoff = datetime.strptime('12:00:00', '%H:%M:%S')
                ecutoff = datetime.strptime('16:59:59', '%H:%M:%S')
            else:
                scutoff = datetime.strptime('17:00:00', '%H:%M:%S')
                ecutoff = datetime.strptime('23:59:59', '%H:%M:%S')
            # add times that fit within the workout pref time to the front
            if scutoff <= startdate and enddate <= ecutoff:
                sorttimes.insert(0, (start, end))
                # get the amt of time you have in your workout pref time
                timeinpref += time 
            # add remaining times to the end (don't fit workout pref time)
            else:
                sorttimes.append((start, end))
            totaltime += time
        timeinpref = calcTotalTime(timeinpref.hour, timeinpref.minute, timeinpref.second)
        totaltime = calcTotalTime(totaltime.hour, totaltime.minute, totaltime.second)
        #timeinpref = timeinpref.time()
        #totaltime = totaltime.time()
        sorttimes.insert(0, timeinpref)
        sorttimes.insert(0, totaltime)
        availabledict[day] = sorttimes
    return availabledict

def calcTotalTime(hour, minute, second):
    # return in minutes
    return (hour*60 + minute + second/60.)

def orderDays(availabledict):
    # self.availability looks like: 
    # "day": [total available time, total pref time, time, time, time, time]
    # preferences: {day: number 0-6}
    pref_time = {}
    ptimearray = []
    pref_not_time = {}
    notptimearray = []
    mintime1 = float("inf")
    mintime2 = float("inf")
    for curday, timelist in availabledict.iteritems():
        totaltime = timelist.pop(0)
        totalpreftime = timelist.pop(0)
        # if there is no time in preference, order by total available time
        if totalpreftime == 0:
            pref_not_time[curday] = totaltime
            notptimearray.append(totaltime)
        # if there is a time in preference, order by total time in preference
        else:
            pref_time[curday] = totalpreftime
            ptimearray.append(totalpreftime)

    # rank the days
    ptimearray = sorted(ptimearray, reverse=True)
    for rank in xrange(len(ptimearray)):
        for day, num in pref_time.iteritems():
            if ptimearray[rank] == num:
                pref_time[day] = rank
                break

    # rank the days
    notptimearray = sorted(notptimearray, reverse=True)
    for rank in xrange(len(notptimearray)):
        for day, num in pref_not_time.iteritems():
            if notptimearray[rank] == num:
                pref_not_time[day] = rank
                break

    #now you have:
    #pref_time = {sunday: 1, tuesday: 2, wednesday: 0} 
    #pref_not_time = {monday: 1, thursday: 2, friday: 0, saturday: 4, sunday: 3}
    #now combine lists together so fix preferences of pref_not_time

    for day, pref in pref_not_time.iteritems():
        pref_not_time[day] = pref + len(pref_time)

    pref_time.update(pref_not_time)
    all_pref = pref_time

    # make availabilitydict into a tuple with (pref, times)
    prefavailability = {}
    for day, timelist in availabledict.iteritems():
        prefavailability[day] = (all_pref[day], timelist)

    # looks like: {sunday: (1, [times]), monday: (6, [times])}
    return prefavailability

# make a time from the available times for them to work out
def generateTime():
    # this is a number
    for _ in desired_days:
        pref = 0
        for day, (p, times) in self.availability.iteritems():
            if p == pref:
                pref += 1
                # pick a random time in times that fits with how long they wanted to workout
                # getWorkout manipulates the self.workout dictionary 
                generateWorkout(time)

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