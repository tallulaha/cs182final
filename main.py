# import the library
from appJar import gui
import input_cal

# handle button events
def press(button):
    if button == "Cancel":
        app.stop()
    else:
        wakeTime = app.getEntry("wakeTime")
        sleepTime = app.getEntry("sleepTime")
        neighborhood = app.getOptionBox("neighborhood")
        sessionPeriod = app.getOptionBox("sessionPeriod")
        sessionGoal = app.getOptionBox("sessionGoal")
        sessionTime = int(app.getEntry("sessionTime"))
        sessionCount = int(app.getEntry("sessionCount"))
       	dateStart = app.getDatePicker("dateStart")
       	wakeTime += ":00"
       	sleepTime += ":00"


       	# def main(wake, bed, dayprwk, avgwkt, wktprf,exrgl, startd):
       	input_cal.main(wakeTime,sleepTime,sessionCount,sessionTime,sessionPeriod,sessionGoal,dateStart)

        print(wakeTime, sleepTime, neighborhood,sessionPeriod,sessionGoal,sessionTime,sessionCount,dateStart)

def showDate(btn):
    print(app.getDatePicker("dp"))

# create a GUI variable called app
app = gui("Login Window", "600x700")
#app.setBg("white")
app.setFont(18)

# add & configure widgets - widgets get a name, to help referencing them later
app.addLabel("title", "Welcome to When2Werk")
#app.setLabelBg("title", "white")
app.setLabelFg("title", "Black")

app.setFont(12)
app.addMessage("mess", """Please select your workout preferences for the week you'd like to schedule.""")

app.addLabel("wake", "Wake Time (hh:mm)")
app.addEntry("wakeTime")

app.addLabel("sleep", "Sleep Time (hh:mm)")
app.addEntry("sleepTime")

app.addLabelOptionBox("neighborhood", ["Yard", "River", "Quad"])

app.addLabelOptionBox("sessionPeriod", ["Mornings - Wake to Noon", "Afternoons - Noon to 5pm", "Evenings - 5pm to Bed"])

app.addLabelOptionBox("sessionGoal", ["Strength Training", "Cardio"])

app.addLabel("sTime", "Average Session Length (min)")
app.addNumericEntry("sessionTime")

app.addLabel("sCount", "Desired Sessions per Week")
app.addNumericEntry("sessionCount")


app.addDatePicker("dateStart")
#app.addButton("GET", showDate)
app.setDatePickerRange("dateStart", 1900, 2100)
app.setDatePicker("dateStart")

# link the buttons to the function called press
app.addButtons(["Submit", "Cancel"], press)


# start the GUI
app.go()