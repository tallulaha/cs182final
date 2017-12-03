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
	
	self.availability = prefavailability

def generateTime

"""
Iterate through the dictionary for the number of days they wanted to workout
Pick a time within the available times for specific duration and send to getWorkout
-- is this a peak hour?
---- add time to finish workout (don’t put in as many workouts so that you stay under time limit)
"""

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

"""
self.workout = {day: (time, muscle group, [list of exercises])}
self.musclegroup = {muscle_group: (True, [list of muscles]), legs: (False, [quadriceps, hamstrings])}
def getWorkout(time):








































