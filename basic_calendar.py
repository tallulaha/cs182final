
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
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'


musclegroups= [('legs',True), ('arms',True),('back',True),('abdominals',True)]

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

def returnDate(day, conf):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for k,v in conf.iteritems():
        k = getDateTimeFromISO8601String(k)
        if days[k.weekday()] == day:
            k = str(k)
            k,_ = k.split(" ")
            return k

def weekday(day):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    return days[getDateTimeFromISO8601String(day).weekday()]



def main(wake, bed, dayprwk, avgwkt, wktprf,exrgl, startd):
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    # update to sleep = {'wakeup': wake, 'bedtime': bed}
    # where wake and sleep are military time

    sleep = {'wakeup': '08:00:00', 'bedtime': '23:59:59'}
    time_preferences = ['morning', 'afternoon', 'evening']
    workout_goals = ['lose weight', 'gain muscle', 'increase endurance', 'new skills']

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

    conflict_dict = orderTimes(conflict_dict, wktprf)
    conflict_dict = orderDays(conflict_dict)
    generateTime(conflict_dict, dayprwk, avgwkt)

def breakTime(start,end,day,dic):
    if (end >= '12:00:00') and (start < '12:00:00'):
        dic[day].append((start, '11:59:59-05:00'))
        if end >= '17:00:00':
            dic[day].append(('12:00:00-05:00', '16:59:59-05:00'))
            dic[day].append(('17:00:00-05:00', end))
        else:
            dic[day].append(('12:00:00-05:00', end))
    elif (end >='17:00:00') and (start < '17:00:00') and (start >= '12:00:00'):
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
# gives you back an array of times for the entire week
# eg gives you back (mon, 1, 3) (tue, 4, 5)
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
        workoutdescrip = generateWorkout(time_min)
        formatted_description = ""
        for (_, name, time) in workoutdescrip:
            formatted_description += name + ", " + str(time) + " min;"
        calWorkout = createEvent(day[0], (day[1], day[2]), ("Workout", formatted_description), "MAC")
        addWorkout(calWorkout)
        print ("addedWorkout")

   

"""
getWorkout:
Fill it until the time is filled

self.workout = {day: (time, muscle group, [list of exercises])}
self.musclegroup = {muscle_group: True, legs: False} 6 muscle groups (muscle groups hard coded)
musclegroups = [all the muscle groups] also hard coded
if the muscle_group is true, you can use it, if false, then it means you have already done it
"""

# **** this does not need the csv but we need to define muscle groups
# **** this could be [legs, arms, shoulders, back, abdominals]???
# generateWorkout: This function allows us to check constraints for existing muscle groups ensuring that the workouts cover a different span of muscles during the week.
def generateWorkout(time):

    # musclegroups= [('legs',True), ('arms',True),('back',True),('abdominals',True)]

    # generate a random muscle group to work on
    rand_int = random.randint(0,len(musclegroups)-1)
    rand_musc = musclegroups[rand_int][0]
    # keep picking new muscle group until you get one that is True
    # not 100% this is doing it correctly
    while not musclegroups[rand_int][1]:
        rand_int = random.randint(0,len(musclegroups)-1)
        rand_musc = musclegroups[rand_int][0]
    # now you have a valid muscle group to pick exercises from
    # set it to False so you don't choose it on next iteration
    musclegroups[rand_int] = (rand_musc,False)
    #print (musclegroups)
    # iterate through dataset to find appropriate exercises w/in time limits
    # use simulated annealing to find the optimal bag of exercises
    workout = fillTime(rand_musc, time)
    print (workout)
    return workout

#this needs to read in things from the data file but generally should work fine
#since not dependent on the time or anything
#timelimit should be in minutes



def fillTime(muscgroup, timelimit):
    #print ("selected muscle", muscgroup)
    num_exercises = 0
    time_exercises = []
    name_exercises = []
    muscles = {'legs':['Quadriceps','Hamstrings'],'arms':['Biceps','Triceps','Forearms'],'back':['Lats'],'abdominals':['Abdominals']}
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

# simulated_annealing: This function allows us to optimize the number of workouts in a gym session. This ensures that the user maximizes their time at the gym. 
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
"""
def randItem(bag, num_exercises, time_exercises, name_exercises):
  rand_ind = np.random.randint(0, num_exercises)
  # continue generating random index until you get one not in bag
  while rand_ind in indexList(bag):
    rand_ind = np.random.randint(0, num_exercises)
  return (rand_ind, name_exercises[rand_ind], time_exercises[rand_ind])
"""

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
    main('8:00:00', '11:59:59', 3, 60, 'afternoon', 'strength', '17-12-08')