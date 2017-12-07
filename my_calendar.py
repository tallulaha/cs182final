
from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import logging

logging.getLogger('googleapicliet.discovery_cache').setLevel(logging.ERROR)

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
SCOPES = 'https://www.googleapis.com/auth/calendar'
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


def main(wake, bed, des_days, timelim, timepref,exrgl, startd, neigh):
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    sleep = {'wakeup': wake, 'bedtime': bed}
    print ("sleep", sleep)
    print ("tp", timepref)
    #sleep = {'wakeup': '08:00:00', 'bedtime': '23:59:59'}
    #time_preferences = ['morning', 'afternoon', 'evening']
    #workout_goals = ['lose weight', 'gain muscle', 'increase endurance', 'new skills']



    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    #print(datetime.timedelta(days=7))
    now = datetime.datetime.utcnow().isoformat() # 'Z' indicates UTC time
    #todaydate = datetime.datetime.strptime(now,"%Y-%m-%d")
    now, nowtime = now.split("T")
    todaydate = getDateTimeFromISO8601String(now)
    oneweek = datetime.timedelta(days=7)
    oneday = datetime.timedelta(days=1)

    startdate = str(todaydate + oneday)
    startdate, sp = startdate.split(" ")
    stopdate = getDateTimeFromISO8601String(startdate) + oneweek
    stopdate = stopdate.isoformat()
    stopdate, time2 = stopdate.split("T")
    stopdate = stopdate + 'T' + sleep['wakeup'] + 'Z'
    start = str(startdate) + 'T' + sleep['wakeup'] + 'Z'

    print('Getting the upcoming weeks events')
    # need to think about if there are multiple calendars 
    eventsResult = service.events().list(
       calendarId='primary', timeMin=start, timeMax=stopdate, singleEvents=True,
       orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    conflict_dict = {}
    last_end = sleep['wakeup']
    ed = None
    et = None

    weekdays = []
    for i in range(7):
        newD = (getDateTimeFromISO8601String(startdate) + datetime.timedelta(days=i)).isoformat()
        newD, randTime = newD.split("T")
        weekdays.append(newD)

    if not events:
        print('No upcoming events found.')
    else: 
        for event in events:
            #print(event)
            start = event['start'].get('dateTime', event['start'].get('date'))
            day, time = start.split("T")
            # want to get free time until bedtime
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
            last_end = end
        breakTime(et, sleep['bedtime'], day, conflict_dict)
        #print ("this is the available time calendar")
    #print (conflict_dict)
    for day in weekdays:
        if day not in conflict_dict:
            print ("len", len(conflict_dict), day)
            conflict_dict[day] = []
            breakTime(sleep['wakeup']+ '-05:00', sleep['bedtime']+ '-05:00', day, conflict_dict)
            print("len", len(conflict_dict))
    print (conflict_dict)

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

    # commented out because now passed in as argument
    #timepref = 'afternoon'
    #timelim = 90


    # do all this preprocessing that does not have to be in a loop
    # assign the time preference (morning, afternoon, evening)
    # fwd check the personal availability schedule
    print ("PA", personal_avail)
    update_pers_avail = updateTimesPreference(personal_avail, timepref)
    if update_pers_avail == None:
        print ("Your schedule does not allow for workouts in the indicated time preference (morning) due to Personal availability-- break")
    #print (update_pers_avail)
    # fwd check the gym hours schedule
    update_gym_avail = updateGymHoursPreference(all_days, timepref)
    if update_gym_avail == None:
        print ("Your schedule does not allow for workouts in the indicated time preference (morning) due to Gym availability -- break")
    #print (update_gym_avail)
    # assign the time you'd like to work out for
    # fwd check the personal availability schedule
    update_pers_avail = updateTimesLimit(update_pers_avail, timelim)
    if update_pers_avail == None:
        print ("Your schedule does not allow for workouts in the indicated workout time due to Personal availability-- break")
    #print ("sort of updated")
    #print (update_pers_avail)
    # fwd check the gym's hours schedule
    update_gym_avail = updateGymHoursLimit(update_gym_avail, timelim)
    if update_pers_avail == None:
        print ("Your schedule does not allow for workouts in the indicated workout time due to Gym availability-- break")
    #print ("most updated")
    #print (update_pers_avail)

    # commented out because now a parameter argument
    #des_days = 3
    workout = []
    for _ in xrange(des_days):
        assign = runCSP(update_pers_avail, update_gym_avail, timelim)
        if assign == None:
            break
        else:
            # remove the assigned day so you don't pick it again
            (gym, wkday, ivl, start, end) = assign
            update_gym_avail.pop(wkday, None)
            timeToCalendarForm(start)
            day = returnDate(wkday, update_pers_avail)
            update_pers_avail.pop(day, None)
            workout.append((gym, wkday, day, timeToCalendarForm(start), timeToCalendarForm(end)))
    if len(workout) < des_days:
        print ("Given your preferences, we were only able to schedule", len(workout), "workout(s) this week")
    print (workout)

    #print (generateWorkout(timelim))
    for day in workout:
        # not sure if this will give minutes

        FMT = '%H:%M:%S'
        if day[4].endswith('-05:00'):
            end = day[4][:-6]
        if day[3].endswith('-05:00'):
            start = day[3][:-6]
        time_min = strp(end,start, FMT)
        # need to convert to minutes
        #print ("amt of time", amt_time)
        #print (day[0])
        # https://stackoverflow.com/questions/14190045/how-to-convert-datetime-timedelta-to-minutes-hours-in-python

        #print ("amt min", time_min)

        workoutdescrip = generateWorkout(time_min)
        formatted_description = ""
        print ("descr", workoutdescrip)
        for (_, name,_, time) in workoutdescrip:
            formatted_description += name + ", " + str(time) + " min;"
        calWorkout = createEvent(day[2], (day[3], day[4]), ("Workout", formatted_description), day[0])
        addWorkout(calWorkout)
        print ("addedWorkout")

def strp(end,start,FMT):
    from datetime import datetime
    amt = datetime.strptime(end,FMT) - datetime.strptime(start,FMT)  
    seconds = amt.total_seconds()
        #print (seconds)
    time_min = int(seconds / 60.)  
    return time_min    

def timeToCalendarForm(time):
    hr = int(time.hour)
    if hr < 10:
        hr = "0" + str(hr)
    else:
        hr = str(hr)
    mn = int(time.minute)
    if mn < 10:
        mn = "0" + str(mn)
    else:
        mn = str(mn)
    time = hr + ":" + mn + ":00-05:00"
    return time

def runCSP(pers_avail, gym_avail, des_time=60, delta=0):
    day_timeivl = selectTimeInterval(pers_avail)
    # base case
    if day_timeivl == None:
        return None
    else:
        day, time_ivl = day_timeivl
        wkt_ivl = selectTimeInInterval(time_ivl, des_time, delta)
        # if it comes back with None, means that this time_ivl is no good
        if wkt_ivl == None:
            pers_avail[day].remove(time_ivl)
            # need to rerun from the top to get a new interval with no delta to start with
            runCSP(pers_avail, gym_avail, des_time, 0)
        (startwkt, endwkt) = wkt_ivl
        wkday = weekday(day)
        new_gym_avail = updateTimesGymHours(wkday, startwkt, endwkt, gym_avail)
        # rerun with new delta if None (will always choose same day bc still least constrained)
        # hopefully get a new interval to keep trying
        # run on the same gym availability
        if new_gym_avail == None:
            delta += 15
            runCSP(pers_avail, gym_avail, des_time, delta)
        return assignGymAndTime(new_gym_avail)

    # you have your preferences (time) assigned
    # fwd check: eliminate all times in the personal calendar's domain that aren't consistent
    # fwd check: eliminate all times in the gym hours domain that aren't consistent
    # assign a day to workout
    # fwd check: eliminate all times that don't fit with the gym's hours that day
    # assign a workout time 

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

def selectTimeInterval(availabledict):

    max_duration = -float("inf")
    max_day = None

    if not availabledict:
        return None

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

    return (max_day, max_ivl)

def selectTimeInInterval(max_ivl, des_time, delta):
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
        return (starttime.time(), endtime.time())
    else:
        return None

def withinInterval(start, end, testst, testen):
    from datetime import datetime 
    # test is (date, start time, end time)
    #start = datetime.strptime(start[0:8], '%H:%M:%S')
    #end = datetime.strptime(end[0:8], '%H:%M:%S')
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
        if start.time() <= startwork and endwork <= end.time():
        #withinInterval(start, end, startwork, endwork):
            possible[gym] = (day, times, startwork, endwork)
            spec_gym = gym

    if not possible:
        return None
    return possible

# pick the first time interval that works
def assignGymAndTime (availabledict):
    for gym, vals in availabledict.iteritems():
        (day, times, startwork, endwork) = vals
        return (gym, day, times, startwork, endwork)

"""
getWorkout:
Fill it until the time is filled

self.workout = {day: (time, muscle group, [list of exercises])}
self.musclegroup = {muscle_group: True, legs: False} 6 muscle groups (muscle groups hard coded)
musclegroups = [all the muscle groups] also hard coded
if the muscle_group is true, you can use it, if false, then it means you have already done it
"""

# 4 big muscle groups
# if True, that muscle group has not been assigned to a workout yet, so can be chosen
# if False, that muscle group has been assigned to a workout, so cannot be chosen again
musclegroups = [('legs',True), ('arms',True), ('back',True),('abdominals',True)]
## this is where we can make conditional about certain strength or cardio activities
def generateWorkout(timelimit, goal='strength'):

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
    workout = fillTime(rand_musc, timelimit, goal)
    return workout

def fillTime(muscgroup, timelimit, goal):
    #print ("selected muscle", muscgroup)
    num_exercises = 0
    time_exercises = []
    name_exercises = []
    lvl_exercises = []
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
            lvl = int(row[6])
            tpe = row[0]
            # if that exercise is within that musclegroup
            if musclegroup in muscles[muscgroup] and goal == tpe.strip():
                num_exercises += 1
                # compile the number of exercises in that group, the time they take, and their names
                time_exercises.append(time)
                name_exercises.append(name)
                lvl_exercises.append(lvl)
        # if that exercise is within that musclegroup

    return simulated_annealing(timelimit, num_exercises, time_exercises, lvl_exercises, name_exercises)


#this should all be in working order
def simulated_annealing(timelimit, num_exercises, time_exercises, lvl_exercises, name_exercises):
    cur_bag = initSolution(timelimit, num_exercises, time_exercises, lvl_exercises, name_exercises)
    #values = [valTotal(cur_bag)]

    #for i in xrange(60000):
    ## CHANGED THIS FOR TESTING
    for i in xrange(2):
      temp = 1. / np.math.log10(i + 2)
      temp_bag = copy.deepcopy(cur_bag)
      new_bag = genNeighbor(temp_bag, timelimit, num_exercises, time_exercises, lvl_exercises, name_exercises)
      old_total = valTotal(cur_bag)
      new_total = valTotal(new_bag)
      prob = acceptProb(new_total, old_total, temp)
      if new_total > old_total or np.random.random() <= prob:
        cur_bag = new_bag
      #total = valTotal(cur_bag)
      #values.append(total)
    print (timeTotal(cur_bag))
    return cur_bag

def initSolution(timelimit, num_exercises, time_exercises, lvl_exercises, name_exercises):
    cur_time = 0
    bag = []
    #print ("timeL", timelimit)
    while cur_time < timelimit:
        rand_ind = np.random.randint(0, num_exercises)
        rand_item = (rand_ind, name_exercises[rand_ind], lvl_exercises[rand_ind], time_exercises[rand_ind])
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
    for (_, _, lvl, _) in bag:
        total += lvl
    return total

def timeTotal(bag):
    total = 0
    for (_, _, _, time) in bag:
        total += time
    return total

def indexList(bag):
    indexes = []
    for (i, _, _, _) in bag:
        indexes.append(i)
    return indexes

def acceptProb(new_total, old_total, temp):
  # if the new state is better, accept it
    prob = np.exp((new_total - old_total) / temp)
    return prob

def genNeighbor(bag, timelimit, num_exercises, time_exercises, lvl_exercises, name_exercises):
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
        rand_item = (rand_ind, name_exercises[rand_ind], lvl_exercises[rand_ind], time_exercises[rand_ind])
        if not rand_item in bag and not rand_item in popped_off:
            bag.append(rand_item)
        cur_time = timeTotal(bag)
    if cur_time > timelimit:
        bag.pop()
    return bag



def createEvent(day, time, descrip, loc):
    event = {
        'summary': descrip[0],
        'location': loc,
        'description': descrip[1],
        'start': {
            'dateTime': day+"T"+time[0],
            'timeZone': 'America/New_York',
        },
        'end': {
            'dateTime': day+"T"+time[1],
            'timeZone': 'America/New_York',
        },
        'reminders':{
            'useDefault': True,
        }
    }
    # add invitees
    return event


def addWorkout(event):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    event = service.events().insert(calendarId='primary', body=event).execute()
    print ('Event created: %s' % (event.get('htmlLink')))

if __name__ == '__main__':
    main('08:00:00', '11:59:59', 3, 60, 'afternoon', 'strength', '17-12-08', 'river')