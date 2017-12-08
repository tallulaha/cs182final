
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
import matplotlib.pyplot as plt

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
    SA_trace =  generateWorkout(60, 'strength')
    plt.plot(SA_trace, label="SA")
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)
    plt.show()
    
        # {(12-03, Sunday) : [(8,10), (10-12), (12, 1)]; (12-04, Monday): [(8,10), (10-12), (12, 1)]}
        # want to split 8-3 into 8-11:59, 12-3
        # calendar.day_name[my_date.weekday()]

# if False, that muscle group has been assigned to a workout, so cannot be chosen again
musclegroups = [('legs',True), ('arms',True), ('back',True),('abdominals',True), ('chest', True), ('shoulders', True), ('glutes', True)]

## this is where we can make conditional about certain strength or cardio activities
def generateWorkout(timelimit, goal):
    print ("gen workout timelimit", timelimit)
    # 4 big muscle groups
    # if True, that muscle group has not been assigned to a workout yet, so can be chosen
    # if False, that muscle group has been assigned to a workout, so cannot be chosen again
    # generate a random muscle group to work on
    rand_int = random.randint(0,len(musclegroups)-1)
    rand_musc_group = musclegroups[rand_int][0]
    # keep picking new muscle group until you get one that is True
    while not musclegroups[rand_int][1]:
        rand_int = random.randint(0,len(musclegroups)-1)
        rand_musc_group = musclegroups[rand_int][0]
    # now you have a valid muscle group to pick exercises from
    # set it to False so you don't choose it on next iteration
    musclegroups[rand_int] = (rand_musc_group, False)
    # iterate through dataset to find musclegroup specific exercises w/in time limits
    workout = fillTime(rand_musc_group, timelimit, goal)
    return workout

def fillTime(muscgroup, timelimit, goal):
    #print ("selected muscle", muscgroup)
    print (muscgroup)
    print ("filltime timelimit", timelimit)

    num_exercises = 0
    time_exercises = []
    name_exercises = []
    lvl_exercises = []
    musc_exercises = []

    musclegroup_dict = {
    'legs':['Quadriceps','Hamstrings'],
    'arms':['Biceps','Triceps','Forearms'], 
    'back':['Upper back', 'Lower back'],
    'abdominals':['Upper abdominals', 'Lower abdominals'],
    'chest':['Pectoralis major', 'Pectoralis minor'],
    'shoulders':['Trapezius', 'Deltoid'],
    'glutes':['Gluteus maximus', 'Gluteus minimus']
    }
    # go through each row in the dataset
    #***** this is where we need to read in datafile
    workout_file = 'workout.csv'
    with open(workout_file, 'r') as work_fh:
        workout_csv = csv.reader(work_fh, delimiter=",", quotechar='"')
        next(workout_csv, None)
        for row in workout_csv:
            muscle = row[4]
            #print ("time?", row[2])
            #print (row[2])
            time = int(row[2])
            name = row[1]
            lvl = int(row[6])
            tpe = row[0]
            # if that exercise is within that musclegroup
            if muscle in musclegroup_dict[muscgroup] and goal == tpe.strip():
                num_exercises += 1
                # compile the number of exercises in that group, the time they take, and their names
                time_exercises.append(time)
                name_exercises.append(name)
                lvl_exercises.append(lvl)
                musc_exercises.append(muscle)
        print (num_exercises)
        # if that exercise is within that musclegroup

    return simulated_annealing(timelimit, num_exercises, time_exercises, lvl_exercises, name_exercises, musc_exercises)


#this should all be in working order
def simulated_annealing(timelimit, num_exercises, time_exercises, lvl_exercises, name_exercises, musc_exercises):
    #print ("sim annneal timelimit", timelimit)
    """
    cur_bag = initSolution(timelimit, num_exercises, time_exercises, lvl_exercises, name_exercises, musc_exercises)
    values = [valTotal(cur_bag)]
    for i in xrange(50):
        cur_bag = initSolution(timelimit, num_exercises, time_exercises, lvl_exercises, name_exercises, musc_exercises)
        total = valTotal(cur_bag)
        values.append(total)
    return values
    """

    cur_bag = initSolution(timelimit, num_exercises, time_exercises, lvl_exercises, name_exercises, musc_exercises)
    values = [valTotal(cur_bag)]
    #for i in xrange(60000):
    ## CHANGED THIS FOR TESTING
    for i in xrange(50):
      temp = 1. / np.math.log10(i + 2)
      temp_bag = copy.deepcopy(cur_bag)
      new_bag = genNeighbor(temp_bag, timelimit, num_exercises, time_exercises, lvl_exercises, name_exercises, musc_exercises)
      old_total = valTotal(cur_bag)
      new_total = valTotal(new_bag)
      prob = acceptProb(new_total, old_total, temp)
      if new_total > old_total or np.random.random() <= prob:
        cur_bag = new_bag
      total = valTotal(cur_bag)
      values.append(total)
    #print ("time total", timeTotal(cur_bag))
    #return cur_bag
    return values
    
def initSolution(timelimit, num_exercises, time_exercises, lvl_exercises, name_exercises, musc_exercises):
    cur_time = 0
    bag = []
    #print ("timeL", timelimit)
    print ("timelimit", timelimit)
    while cur_time < timelimit:
        rand_ind = np.random.randint(0, num_exercises)
        rand_item = (name_exercises[rand_ind], lvl_exercises[rand_ind], time_exercises[rand_ind], musc_exercises[rand_ind])
        if not rand_item in bag:
          bag.append(rand_item)
        cur_time = timeTotal(bag)
    print (bag)
    if cur_time > timelimit:
        bag.pop()
    return bag

# want to maximize time working out
# minimize free time in workout
def valTotal(bag):
    total = 0
    for (_, lvl, _, _) in bag:
        total += lvl
    return total

def timeTotal(bag):
    total = 0
    for (_, _, time, _) in bag:
        total += time
    return total

def acceptProb(new_total, old_total, temp):
  # if the new state is better, accept it
    prob = np.exp((new_total - old_total) / temp)
    return prob

def genNeighbor(bag, timelimit, num_exercises, time_exercises, lvl_exercises, name_exercises, musc_exercises):
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
        rand_item = (name_exercises[rand_ind], lvl_exercises[rand_ind], time_exercises[rand_ind], musc_exercises[rand_ind])
        if not rand_item in bag and not rand_item in popped_off:
            bag.append(rand_item)
        cur_time = timeTotal(bag)
    if cur_time > timelimit:
        bag.pop()
    return bag


if __name__ == '__main__':
    main()