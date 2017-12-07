#!/usr/bin/python

# Import modules for CGI handling 
import add
#import input_cal
import cgi, cgitb 


# Create instance of FieldStorage 
form = cgi.FieldStorage() 

# Get data from fields
waketime = form.getvalue('waketime')
sleeptime = form.getvalue('sleeptime')
timeRadios = form.getvalue('timeRadios')
typeRadios  = form.getvalue('typeRadios')
sessionTime  = int(form.getvalue('sessionTime'))
sessionDays  = int(form.getvalue('sessionDays'))

n = add.addition(sessionDays)
#input_cal.main()

print "Content-type:text/html\r\n\r\n"
print "<html>"
print "<head>"
print "<title>Hello - Second CGI Program</title>"
print "</head>"
print "<body>"
print "<h2>Hello TALLULAH%s %s</h2>" % (sessionDays, sleeptime)

print "<p>"
print "Wake Time: %s" % (waketime)
print "Sleep Time: %s" % (sleeptime)
print "Preferred Time of Day: %s" % (timeRadios)
print "Exercise Goals: %s" % (typeRadios)
print "Minutes per Session: %s" % (sessionTime)
print "Sessions per Week: %s" % (sessionDays)
print "Sessions Doubled: ", n
print "</p>"




print "</body>"
print "</html>"