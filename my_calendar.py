
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
import csv
import random
import numpy as np
import copy

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
    sleep = {'wakeup': '08:00:00', 'bedtime': '23:59:59'}
    time_preferences = ['morning', 'afternoon', 'evening']
    workout_goals = ['lose weight', 'gain muscle', 'increase endurance', 'new skills']



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
        end = event['end'].get('dateTime', event['end'].get('date'))
        ed, et = end.split("T")
        last_end = end

    personal_avail = conflict_dict

    gym_sun = {
        "Mac" : [('9:00:00', '11:59:59'), ('12:00:00', '13:00:00'), None], 
        "Hemenway" : [None, ('14:00:00', '16:59:59'), ('17:00:00', '23:00:00')],
        "Murr" : [('9:00:00', '11:59:59'), ('12:00:00', '16:59:59'), None],
        "QRAC" : [None, None, None]
    }
    gym_mon = {
        "Mac" : [('6:00:00', '11:59:59'), ('12:00:00', '16:59:59'), ('17:00:00', '22:00:00')], 
        "Hemenway" : [('6:00:00', '11:59:59'), ('12:00:00', '16:59:59'), ('17:00:00', '23:00:00')],
        "Murr" : [('7:00:00', '11:59:59'), ('12:00:00', '16:59:59'), ('17:00:00', '23:00:00')],
        "QRAC" : [('8:00:00', '11:59:59'), ('12:00:00', '16:59:59'), ('17:00:00', '23:00:00')]
    }
    gym_tue = {
        "Mac" : [('6:00:00', '11:59:59'), ('12:00:00', '16:59:59'), ('17:00:00', '22:00:00')], 
        "Hemenway" : [('6:00:00', '11:59:59'), ('12:00:00', '16:59:59'), ('17:00:00', '23:00:00')],
        "Murr" : [('7:00:00', '11:59:59'), ('12:00:00', '16:59:59'), ('17:00:00', '23:00:00')],
        "QRAC" : [('8:00:00', '11:59:59'), ('12:00:00', '16:59:59'), ('17:00:00', '23:00:00')]
    }
    gym_wed = {
        "Mac" : [('6:00:00', '11:59:59'), ('12:00:00', '16:59:59'), ('17:00:00', '22:00:00')], 
        "Hemenway" : [('6:00:00', '11:59:59'), ('12:00:00', '16:59:59'), ('17:00:00', '23:00:00')],
        "Murr" : [('7:00:00', '11:59:59'), ('12:00:00', '16:59:59'), ('17:00:00', '23:00:00')],
        "QRAC" : [('8:00:00', '11:59:59'), ('12:00:00', '16:59:59'), ('17:00:00', '23:00:00')]
    }
    gym_th = {
        "Mac" : [('6:00:00', '11:59:59'), ('12:00:00', '16:59:59'), ('17:00:00', '22:00:00')], 
        "Hemenway" : [('6:00:00', '11:59:59'), ('12:00:00', '16:59:59'), ('17:00:00', '23:00:00')],
        "Murr" : [('7:00:00', '11:59:59'), ('12:00:00', '16:59:59'), ('17:00:00', '23:00:00')],
        "QRAC" : [('8:00:00', '11:59:59'), ('12:00:00', '16:59:59'), ('17:00:00', '23:00:00')]
    }
    gym_fri = {
        "Mac" : [('6:00:00', '11:59:59'), ('12:00:00', '16:59:59'), ('17:00:00', '19:00:00')], 
        "Hemenway" : [('6:00:00', '11:59:59'), ('12:00:00', '16:59:59'), ('17:00:00', '20:00:00')],
        "Murr" : [('7:00:00', '11:59:59'), ('12:00:00', '16:59:59'), ('17:00:00', '22:30:00')],
        "QRAC" : [('8:00:00', '11:59:59'), ('12:00:00', '16:59:59'), ('17:00:00', '21:00:00')]
    }
    gym_sat = {
        "Mac" : [('9:00:00', '11:59:59'), ('12:00:00', '16:59:59'), None], 
        "Hemenway" : [('10:00:00', '11:59:59'), ('12:00:00', '16:59:59'), ('17:00:00', '20:00:00')],
        "Murr" : [('8:00:00', '11:59:59'), ('12:00:00', '16:59:59'), ('17:00:00', '20:00:00')],
        "QRAC" : [None, ('12:00:00', '16:59:59'), ('17:00:00', '21:00:00')]
    }

    all_days = {
        'sunday': gym_sun,
        'monday': gym_mon,
        'tuesday': gym_tue,
        'wednesday': gym_wed,
        'thursday': gym_th,
        'friday': gym_fri,
        'saturday': gym_sat
    }

    # assign the time preference (morning, afternoon, evening)
    # fwd check the personal availability schedule
    update_pers_avail = updateTimesPreference(personal_avail, 'morning')
    if update_pers_avail == None:
        print ("Your schedule does not allow for workouts in the indicated time preference (morning) due to Personal availability-- break")
    #print (update_pers_avail)
    # fwd check the gym hours schedule
    update_gym_avail = updateGymHoursPreference(all_days, 'morning')
    if update_gym_avail == None:
        print ("Your schedule does not allow for workouts in the indicated time preference (morning) due to Gym availability -- break")
    #print (update_gym_avail)
    # assign the time you'd like to work out for
    # fwd check the personal availability schedule
    update_pers_avail = updateTimesLimit(update_pers_avail, 60)
    if update_pers_avail == None:
        print ("Your schedule does not allow for workouts in the indicated workout time due to Personal availability-- break")
    #print ("sort of updated")
    #print (update_pers_avail)
    # fwd check the gym's hours schedule
    update_gym_avail = updateGymHoursLimit(update_gym_avail, 60)
    if update_pers_avail == None:
        print ("Your schedule does not allow for workouts in the indicated workout time due to Gym availability-- break")
    #print ("most updated")
    #print (update_pers_avail)
    # assign the day 
    assigned_pers = assignPersTime(update_pers_avail, 60)
    (day, start, end) = assigned_pers
    if assigned_pers == None:
        print ("Problem with interval")
    day = weekday(day)
    ee = updateTimesGymHours(day, start, end, update_gym_avail)
    print (ee)

    # you have your preferences (time) assigned
    # fwd check: eliminate all times in the personal calendar's domain that aren't consistent
    # fwd check: eliminate all times in the gym hours domain that aren't consistent
    # assign a day to workout
    # fwd check: eliminate all times that don't fit with the gym's hours that day
    # assign a workout time 
    """
    week_days = []
    for day, _ in personal_avail.iteritems():
        week_days.append(day)

    no_sched = False
    time_lst = []
    num_days = 0
    des_days = 3
    timelimit = 60

    while num_days != des_days:
        day = pickDay(week_days)
        week_days.remove(day)
        # if somehow all the days don't have available slots
        if week_days == []:
            no_sched = True
            break
        time = pickTime(personal_avail, timelimit, day)
        # if no time works on that specific day, don't increment num_days, otherwise do
        if time != None:
            # check to make sure that it works with time preference
            print(checkPreference(time, 'afternoon'))
            print(checkGymHours(time))
            time_lst.append(time)
            num_days += 1

    #print (time_lst)

    if no_sched:
        print ("You don't have enough available time to schedule your goals")
    """
def returnDate(day, conf):
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    for k,v in conf.iteritems():
        k = getDateTimeFromISO8601String(k)
        if days[k.weekday()] == day:
            k = str(k)
            k,_ = k.split(" ")
            return k

def weekday(day):
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    return days[getDateTimeFromISO8601String(day).weekday()]

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

# timepref is always assigned because the user chose that 
# forward check: eliminate all times that aren't consistent with the timepref
def updateTimesPreference(availabledict, timepref):
    # https://stackoverflow.com/questions/3096953/how-to-calculate-the-time-interval-between-two-time-strings
    from datetime import datetime

    #### if any of the days have 0 time preferences, then 
    # you should you should make note not to pick those days aka eliminate from domain
    #print ("start")
    #print (availabledict)
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
            # within parameters, append it
            if scutoff <= startdate and enddate <= ecutoff:
                sorttimes.append((start, end)) 
        availabledict[day] = sorttimes
    
    # eliminate all days that do not have any valid times
    temp_dic = copy.deepcopy(availabledict)
    for day, timelist in temp_dic.iteritems():
        if not timelist:
            availabledict.pop(day, None)

    # if entire dictionary is empty, then that means there are no valid assignments
    # therefore you need to pick a different preference (return None)
    if not availabledict:
        return None

    return availabledict

# randomly assign a day to go to the gym
def updateGymHoursPreference(all_days, timepref):
    from datetime import datetime 
    
    if timepref == 'morning':
        for day, gym_day in all_days.iteritems():
            # now you're looking at individuals schedules for gyms
            for gym, times in gym_day.iteritems():
                gym_day[gym] = times[0]
    elif timepref == 'afternoon':
        for day, gym_day in all_days.iteritems():
            # now you're looking at individuals schedules for gyms
            for gym, times in gym_day.iteritems():
                gym_day[gym] = times[1]
    else:
        for day, gym_day in all_days.iteritems():
            # now you're looking at individuals schedules for gyms
            for gym, times in gym_day.iteritems():
                gym_day[gym] = times[2]
    #print("FIRST")
    #print (all_days)


    # eliminate all gyms that do not have times within the parameters
    temp_days = copy.deepcopy(all_days)
    for day, gym_day in temp_days.iteritems():
        for gym, times in gym_day.iteritems():
            if times == None:
                all_days[day].pop(gym, None)
    #print("SECOND")
    #print (all_days)

    # eliminate all days that do not have times within the parameters
    temp_days2 = copy.deepcopy(all_days)
    for day, gym_day in temp_days2.iteritems():
        if not gym_day:
            all_days.pop(day, None)
    #print("THIRD")
    #print (all_days)

    # if entire dictionary is empty, then that means there are no valid assignments
    # therefore you need to pick a different preference (return None)
    if not all_days:
        return None

    return all_days

def updateTimesLimit(availabledict, timelimit):

    print (availabledict)

    # eliminate all intervals that do not have times suitable to the desired workout time
    temp_dict = copy.deepcopy(availabledict)
    for day, times in temp_dict.iteritems():
        for (start, end) in times:
            duration = calcDuration(start, end)
            # if the interval is not as long as the workout time, remove it
            if duration < timelimit:
                availabledict[day].remove((start, end))
    # eliminate all days that have empty lists
    temp_dict2 = copy.deepcopy(availabledict)
    for day, times in temp_dict2.iteritems():
        if not times:
            availabledict.pop(day)

    # if entire dictionary is empty, then that means there are no valid assignments
    # therefore you need to pick a different time limit (return None)
    if not availabledict:
        return None
    return availabledict

def updateGymHoursLimit(availabledict, timelimit):

    # eliminate all intervals that do not have times suitable to the desired workout time
    temp_dict = copy.deepcopy(availabledict)
    for day, gym_dict in temp_dict.iteritems():
        for gym, time in gym_dict.iteritems():
            (start, end) = time
            duration = calcDuration(start, end)
            # if the interval is not as long as the workout time, remove it
            if duration < timelimit:
                availabledict[day][gym] = None

    # eliminate all gyms that have empty lists 
    temp_dict2 = copy.deepcopy(availabledict)
    for day, gym_dict in temp_dict2.iteritems():
        for gym, time in gym_dict.iteritems():
            if time == None:
                availabledict[day].pop(gym, None)

    # eliminate all days that have empty lists
    temp_dict3 = copy.deepcopy(availabledict)
    for day, gym_dict in temp_dict3.iteritems():
        if not gym_dict:
            availabledict.pop(day, None)

    # if entire dictionary is empty, then that means there are no valid assignments
    # therefore you need to pick a different preference (return None)
    if not availabledict:
        return None
    return availabledict
            
def calcDuration(start, end):
    # https://stackoverflow.com/questions/3096953/how-to-calculate-the-time-interval-between-two-time-strings
    from datetime import datetime

    start = datetime.strptime(start[0:8], '%H:%M:%S')
    end = datetime.strptime(end[0:8], '%H:%M:%S')
    timediff = end - start + datetime.strptime('00:00:00', '%H:%M:%S')
    duration = calcTotalTime(timediff.hour, timediff.minute, timediff.second)
    return duration


def calcTotalTime(hour, minute, second):
    # return in minutes
    return (hour*60 + minute + second/60.)


def assignPersTime(availabledict, des_time, delta=0):

    max_duration = -float("inf")
    max_day = None

    # pick least constrained day (one with most available time)
    for day, times in availabledict.iteritems():
        duration = 0
        for (start, end) in times:
            duration += calcDuration(start, end)
            # if the interval is not as long as the workout time, remove it
        if duration > max_duration:
            max_duration = duration
            max_day = day

    time_ivls = availabledict[max_day]
    # you know all the time intervals are long enough for desired workout
    # you know each day has at least 1 time interval because of fwd checking
    # pick the least constrained time ivl (most time)
    max_dur = -float("inf")
    max_ivl = time_ivls[0]
    for (start, end) in time_ivls:
        duration = calcDuration(start, end)
        if duration > max_duration:
            max_duration = duration
            max_ivl = (start, end)

    return selectTimeInInterval(max_day, max_ivl, des_time, delta)

def selectTimeInInterval(max_day, max_ivl, des_time, delta):
    from datetime import datetime
    import datetime as dt
    # pick a time interval within that interval 
    (start, end) = max_ivl
    starttime = datetime.strptime(start[0:8], '%H:%M:%S') + dt.timedelta(minutes=delta)
    endtime = starttime + dt.timedelta(minutes=des_time)
    start = datetime.strptime(start[0:8], '%H:%M:%S')
    end = datetime.strptime(end[0:8], '%H:%M:%S')
    if withinInterval(start, end, starttime, endtime):
        #print (max_day, starttime.time(), endtime.time())
        return (max_day, starttime.time(), endtime.time())
    else:
        return None

def withinInterval(start, end, testst, testen):
    from datetime import datetime 
    # test is (date, start time, end time)
    #start = datetime.strptime(start[0:8], '%H:%M:%S')
    #end = datetime.strptime(end[0:8], '%H:%M:%S')
    print (start, end)
    print ("HELOO")
    print (testst, testen)
    start = start.time()
    end = end.time()
    testst = testst.time()
    testen = testen.time()
    
    return (start <= testst and testen <= end)

# consider all times within an interval to make sure it works
# consider all intervals within the day to make sure it works
# consider all days within the week to make sure it works

def updateTimesGymHours (day, startwork, endwork, availabledict):
    # you know that all gym hours are continuous 
    # check if the times fit within that window
    # eliminate times that fall outside of that window
    # if the domain is empty, you need to return back None and pick a new day
    #gym_time = availabledict[day]
    from datetime import datetime 

    gym_day = availabledict[day]
    possible = {}
    spec_gym = None
    for gym, times in gym_day.iteritems():
        (start, end) = times
        start = datetime.strptime(start[0:8], '%H:%M:%S')
        end = datetime.strptime(end[0:8], '%H:%M:%S')
        if withinInterval(start, end, startwork, endwork):
            possible[gym] = times
            spec_gym = gym

    if possible: #put in gym 
        return (day, spec_gym, startwork, endwork)
    #else:
        # try a bunch of intervals until it works
        

# assign a day of the week to workout 
def assignDay(week_days, all_days):
    from datetime import datetime
    # randomly pick a day
    # week_days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
    rand_int = random.randint(0, len(week_days)-1)
    day = week_days[rand_int]
    # check to make sure you haven't done that day yet
    while day == None:
        rand_int = random.randint(0, len(week_days)-1)
        day = week_days[day]
    # choose the gym with the longest hours
    intervals = []
    maxi = -float("inf")
    max_gym = "Mac"

    #gym_dict = all_days[day]
    gym_dict = all_days['sunday']
    for gym, time in gym_dict.iteritems():
        print (time)
        start = datetime.strptime(time[0][0:8], '%H:%M:%S')
        end = datetime.strptime(time[1][0:8], '%H:%M:%S')
        timediff = end - start + datetime.strptime('00:00:00', '%H:%M:%S')
        duration = calcTotalTime(timediff.hour, timediff.minute, timediff.second)
        if duration > maxi:
            maxi = duration
            max_gym = gym
            hours = (time[0], time[1])

    return (day, max_gym, hours)






        
def checkPreference(time, preference):
    from datetime import datetime 

    if preference == 'morning':
        # should be wake time
        scutoff = datetime.strptime('05:00:00', '%H:%M:%S')
        ecutoff = datetime.strptime('11:59:59', '%H:%M:%S')
    elif preference == 'afternoon':
        scutoff = datetime.strptime('12:00:00', '%H:%M:%S')
        ecutoff = datetime.strptime('16:59:59', '%H:%M:%S')
    else:
        scutoff = datetime.strptime('17:00:00', '%H:%M:%S')
        ecutoff = datetime.strptime('23:59:59', '%H:%M:%S')
    return withinInterval(scutoff, ecutoff, time)



# gone for CSP





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
# gives you back an array of times for the entire week
# eg gives you back (mon, 1, 3) (tue, 4, 5)

# randomly assign a time
# check if its in the wkt preference 
# check if its in the open gym hours
def generateTime(availabledict, num_days, des_time):
    # this is a number
    from datetime import datetime
    import datetime as dt

    pref = 0
    wkt_times = []
    for i in xrange(num_days):
        for day, (p, times) in availabledict.iteritems():
            if p == pref:
                pref += 1
                # bug to figure out later: if there isn't enough time in the first time interval
                # keep moving through that same date even if it is no longer in time preference
                # could also decide to move to a different day 
                (start, end) = times[0]
                starttime = datetime.strptime(start[0:8], '%H:%M:%S')
                endtime = starttime + dt.timedelta(minutes=des_time)
                endlimit = datetime.strptime(end[0:8], '%H:%M:%S')
                if endtime > endlimit:
                    print ("hello")
                    # need to pick another time interval
                else:
                    starttime = str(starttime.time()) + '-05:00'
                    endtime = str(endtime.time()) + '-05:00'
                    wkt_times.append((day, starttime, endtime))
                break

    #print ("workout times")
    #print ("WORKOUT TIMES", wkt_times)
    for day in wkt_times:
        # not sure if this will give minutes

        FMT = '%H:%M:%S'
        if day[2].endswith('-05:00'):
            end = day[2][:-6]
        if day[1].endswith('-05:00'):
            start = day[1][:-6]
        amt_time = datetime.strptime(end,FMT) - datetime.strptime(start,FMT)
        # need to convert to minutes
        #print ("amt of time", amt_time)
        #print (day[0])
        # https://stackoverflow.com/questions/14190045/how-to-convert-datetime-timedelta-to-minutes-hours-in-python
        seconds = amt_time.total_seconds()
        #print (seconds)
        time_min = int(seconds / 60.)
        #print ("amt min", time_min)
        generateWorkout(time_min)

         

"""
getWorkout:
Fill it until the time is filled

self.workout = {day: (time, muscle group, [list of exercises])}
self.musclegroup = {muscle_group: True, legs: False} 6 muscle groups (muscle groups hard coded)
musclegroups = [all the muscle groups] also hard coded
if the muscle_group is true, you can use it, if false, then it means you have already done it
"""


def generateWorkout(timelimit):
    # 4 big muscle groups
    # if True, that muscle group has not been assigned to a workout yet, so can be chosen
    # if False, that muscle group has been assigned to a workout, so cannot be chosen again
    musclegroups = [('legs',True), ('arms',True), ('back',True),('abdominals',True)]
    # generate a random muscle group to work on
    rand_int = random.randint(0,len(musclegroups)-1)
    rand_musc = musclegroups[rand_int][0]
    # keep picking new muscle group until you get one that is True
    while not musclegroups[rand_int][1]:
        rand_int = random.randint(0,len(musclegroups)-1)
        rand_musc = musclegroups[rand_int][0]
    # now you have a valid muscle group to pick exercises from
    # set it to False so you don't choose it on next iteration
    musclegroups[rand_int] = (rand_musc,False)
    # iterate through dataset to find musclegroup specific exercises w/in time limits
    workout = fillTime(rand_musc, timelimit)
    return workout

def fillTime(muscgroup, timelimit):
    #print ("selected muscle", muscgroup)
    num_exercises = 0
    time_exercises = []
    name_exercises = []
    muscles = {'legs':['Quadriceps','Hamstrings'],'arms':['Biceps','Triceps','Forearms'], 'back':['Lats'],'abdominals':['Abdominals']}
    # go through each row in the dataset
    #***** this is where we need to read in datafile
    workout_file = 'workout.csv'
    with open(workout_file, 'r') as work_fh:
        workout_csv = csv.reader(work_fh, delimiter=",", quotechar='"')
        next(workout_csv, None)
        for row in workout_csv:
            musclegroup = row[4]
            #print ("time?", row[2])
            time = int(row[2])
            name = row[1]
            # if that exercise is within that musclegroup
            if musclegroup in muscles[muscgroup]:
                num_exercises += 1
                # compile the number of exercises in that group, the time they take, and their names
                time_exercises.append(time)
                name_exercises.append(name)
        # if that exercise is within that musclegroup

    return simulated_annealing(timelimit, num_exercises, time_exercises, name_exercises)


#this should all be in working order
def simulated_annealing(timelimit, num_exercises, time_exercises, name_exercises):
    cur_bag = initSolution(timelimit, num_exercises, time_exercises, name_exercises)
    #values = [valTotal(cur_bag)]

    #for i in xrange(60000):
    ## CHANGED THIS FOR TESTING
    for i in xrange(2):
      temp = 1. / np.math.log10(i + 2)
      temp_bag = copy.deepcopy(cur_bag)
      new_bag = genNeighbor(temp_bag, timelimit, num_exercises, time_exercises, name_exercises)
      old_total = valTotal(cur_bag)
      new_total = valTotal(new_bag)
      prob = acceptProb(new_total, old_total, temp)
      if new_total > old_total or np.random.random() <= prob:
        cur_bag = new_bag
      #total = valTotal(cur_bag)
      #values.append(total)
    print (timeTotal(cur_bag))
    return cur_bag

def initSolution(timelimit, num_exercises, time_exercises, name_exercises):
    cur_time = 0
    bag = []
    #print ("timeL", timelimit)
    while cur_time < timelimit:
        rand_ind = np.random.randint(0, num_exercises)
        rand_item = (rand_ind, name_exercises[rand_ind], time_exercises[rand_ind])
        if not rand_item in bag:
          bag.append(rand_item)
        cur_time = timeTotal(bag)
    if cur_time > timelimit:
        bag.pop()
    return bag

# want to maximize time working out
# minimize free time in workout
def valTotal(bag):
    total = 0
    for (_, _, time) in bag:
        total += time
    return total

def timeTotal(bag):
    total = 0
    for (_, _, time) in bag:
        total += time
    return total

def indexList(bag):
    indexes = []
    for (i, _, _) in bag:
        indexes.append(i)
    return indexes

def acceptProb(new_total, old_total, temp):
  # if the new state is better, accept it
    prob = np.exp((new_total - old_total) / temp)
    return prob

def genNeighbor(bag, timelimit, num_exercises, time_exercises, name_exercises):
    popped_off = []
  # this doesnt work because already empty i am guessing to change this
  #for i in xrange(3):
  # to this
    while len(bag) > 0:
        rand = np.random.randint(0, len(bag))
        pop = bag.pop(rand)
        popped_off.append(pop)
    cur_time = timeTotal(bag)
  # getting in a loop here maybe because we are not perfectly doing the exercise time
  # or maybe not working because we dont have enough examples 
    while cur_time < (timelimit):
        rand_ind = np.random.randint(0, num_exercises)
        rand_item = (rand_ind, name_exercises[rand_ind], time_exercises[rand_ind])
        if not rand_item in bag and not rand_item in popped_off:
            bag.append(rand_item)
        cur_time = timeTotal(bag)
    if cur_time > timelimit:
        bag.pop()
    return bag






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