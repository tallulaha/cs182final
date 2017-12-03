"""
getTimes: 
Input is from Google API is ?dictionary: days - keys, list of conflicts - values
Reverse the conflicts for available times (take away sleep time)
Conflicts also include gym hours
Return a dictionary: days - keys, list of available times - values
"""
def getTimes(schedule):
	# schedule is from Google Calendar 
	# Keys: Days of the week
	# Values: Times of conflicts
	self.availability = {}
	for day, conflictlst in schedule.iteritems():
		availabletime = []
		for conflict in conflictlst:
			# populate available time with reverse of conflicts
			# if times span from morning-afternoon or afternoon-evening, split the times up (discretize)
		# take out sleep time from the available times
		self.availability[day] = availabletime
	print self.availability

"""
orderTimes:
Take into account the workout time specified (eg morning)
Manipulate list of available times to put the preferred workout time first
Return a dictionary: days - keys, list of available times sorted - values
"""
def orderTimes():
	morning = [wake, 11:59]
	afternoon = [12:00, 5:00]
	evening = [5:00, sleep]

	for day, timelist in self.availability.iteritems():
		# create a new list of sorted times
		sorttimes = []
		timeinpref = 0
		totaltime = 0
		for time in timelist:
			# add times that fit within the workout pref time to the front
			if time is within times for workout_pref:
				sorttimes.insert(0, time)
				# get the amt of time you have in your workout pref time
				timeinpref += time 
			# add remaining times to the end (don't fit workout pref time)
			else:
				sorttimes.append(time)
			totaltime += time
		sorttimes.insert(0, timeinpref)
		sorttimes.insert(0, totaltime)
		self.availability[day] = sorttimes
	print self.availability

"""
orderDays:
Order the days based on which have the preferred workout time
If they have the preferred workout, move to front, otherwise, move to back
Then sort based on amount of free time you have 
Return a dictionary: days sorted- keys, (preference, list of available times sorted) - values
"""
def orderDays():
	# self.availability looks like: 
	# "day": [total available time, total pref time, time, time, time, time]
	# preferences: {day: number 0-6}
	pref_time = {}
	pref_not_time = {}
	mintime = float("inf")
	mintime2 = float("inf")
	for curday, timelist in self.availability.iteritems():
		totaltime = timelist.pop(0)
		totalpreftime = timelist.pop(0)
		# if there is no time in preference, order by total available time
		if totalpreftime == 0:
			if totaltime < mintime1:
				mintime1 = totaltime
				pref_not_time[curday] = 0
				for day, pref in pref_not_time.iteritems():
				# increment rest of preferences
					if day != curday:
						preferences[day] = pref + 1
		# if there is a time in preference, order by total time in preference
		else:
			if totalpreftime < mintime2:
				mintime2 = totaltime
				pref_time[curday] = 0
				for day, pref in pref_not_time.iteritems():
				# increment rest of preferences
					if day != curday:
						preferences[day] = pref + 1
	"""
	now you have:
	pref_time = {sunday: 1, tuesday: 2, wednesday: 0} 
	pref_not_time = {monday: 1, thursday: 2, friday: 0, saturday: 4, sunday: 3}
	now combine lists together so fix preferences of pref_not_time
	"""
	for day, pref in pref_not_time:
		pref_not_time[day] = pref + len(pref_time)

	all_pref = pref_time + pref_not_time

	# make self.availability into a tuple with (pref, times)
	prefavailability = {}
	for day, timelist in self.availability.iteritems():
		prefavailability[day] = (all_pref[day], timelist)

	# looks like: {sunday: (1, [times]), monday: (6, [times])}
	self.availability = prefavailability


"""
Iterate through the dictionary for the number of days they wanted to workout
Pick a time within the available times for specific duration and send to getWorkout
-- is this a peak hour?
---- add time to finish workout (don’t put in as many workouts so that you stay under time limit)
"""
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

"""
getWorkout:
Already has time it should last
Existing workout dictionary: day - keys, workout - values
Existing dictionary: muscle group (legs) - keys, list of muscles in that - values
Existing dictionary: muscle group (legs) - keys, binary if you’ve done it this week - values
If strength day:
Only work on muscle group that have a 0 (you haven’t worked on)
Dive into that muscle group list to get exercises
Fill it until the time is filled

self.workout = {day: (time, muscle group, [list of exercises])}
self.musclegroup = {muscle_group: True, legs: False} 6 muscle groups
musclegroups = [all the muscle groups]
if the muscle_group is true, you can use it, if false, then it means you have already done it
"""

def generateWorkout(time):
	import random
	# generate a random muscle group to work on
	rand_int = random.randint(len(musclegroups))
	rand_musc = musclegroups[rand_int]
	# keep picking new muscle group until you get one that is True
	while not self.musclegroup[rand_musc]:
		rand_int = random.randint(len(musclegroups))
		rand_musc = musclegroups[rand_int]
	# now you have a valid muscle group to pick exercises from
	# set it to False so you don't choose it on next iteration
	self.musclegroup[rand_musc] = False
	# iterate through dataset to find appropriate exercises w/in time limits
	# use simulated annealing to find the optimal bag of exercises
	fillTime(rand_musc, time)

def fillTime(muscgroup, timelimit):
	num_exercises = 0
	time_exercises = []
	name_exercises = []
	# go through each row in the dataset
	for exercise in dataset:
		# if that exercise is within that musclegroup
		if muscgroup == exercise[musclegroup]:
			num_exercises += 1
			time_exercises.append(exercise[time])
			name_exercises.append(exercise[name])
	simulated_annealing()

def initSolution(timelimit):
	cur_time = 0
	bag = []
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

def randItem(bag):
  rand_ind = np.random.randint(0, num_exercises)
  # continue generating random index until you get one not in bag
  while rand_ind in indexList(bag):
    rand_ind = np.random.randint(0, num_exercises)
  return (rand_ind, name_exercises[rand_ind], time_exercises[rand_ind])

def genNeighbor(bag):
  popped_off = []
  for i in xrange(3):
    rand = np.random.randint(0, len(bag))
    pop = bag.pop(rand)
    popped_off.append(pop)
  cur_time = timeTotal(bag)
  while cur_time < timelimit:
    rand_ind = np.random.randint(0, num_exercises)
    rand_item = (rand_ind, name_exercises[rand_ind], time_exercises[rand_ind])
    if not rand_item in bag and not rand_item in popped_off:
      bag.append(rand_item)
    cur_time = timeTotal(bag)
  if cur_time > timelimit:
    bag.pop()
  return bag

def simulated_annealing():
    cur_bag = initSolution()
    values = [valTotal(cur_bag)]

    for i in xrange(60000):
      temp = 1. / np.math.log10(i + 2)
      temp_bag = copy.deepcopy(cur_bag)
      new_bag = genNeighbor(temp_bag)
      old_total = valTotal(cur_bag)
      new_total = valTotal(new_bag)
      prob = acceptProb(new_total, old_total, temp)
      if new_total > old_total or np.random.random() <= prob:
        cur_bag = new_bag
      #total = valTotal(cur_bag)
      #values.append(total)
    return cur_bag

