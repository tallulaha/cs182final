"""
getTimes: 
Input is from Google API is ?dictionary: days - keys, list of conflicts - values
Reverse the conflicts for available times (take away sleep time)
Conflicts also include gym hours
Return a dictionary: days - keys, list of available times - values

orderTimes:
Take into account the workout time specified (eg morning)
Manipulate list of available times to put the preferred workout time first
Return a dictionary: days - keys, list of available times sorted - values

orderDays:
Order the days based on which have the preferred workout time
If they have the preferred workout, move to front, otherwise, move to back
Then sort based on amount of free time you have 
Return a dictionary: days sorted- keys, list of available times sorted - values
"""