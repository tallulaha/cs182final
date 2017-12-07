# import the library
from appJar import gui

# handle button events
def press(button):
    if button == "Cancel":
        app.stop()
    else:
        print("hehe")

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

app.addLabelEntry("WakeTime")
app.addLabelEntry("SleepTime")

app.addLabelOptionBox("sessionTime", ["Mornings - Wake to Noon", "Afternoons - Noon to 5pm", "Evenings - 5pm to Bed"])



app.addRadioButton("sessionTime", "Mornings - 6am to Noon")
app.addRadioButton("sessionTime", "Afternoons - Noon to 5pm")
app.addRadioButton("sessionTime", "Evenings - 5pm to 10pm")


app.addRadioButton("sessionGoal", "Strength Training")
app.addRadioButton("sessionGoal", "Cardio")

app.addSpinBoxRange("sessionCount", 1, 7)

app.addDatePicker("dp")
#app.addButton("GET", showDate)
app.setDatePickerRange("dp", 1900, 2100)
app.setDatePicker("dp")

# link the buttons to the function called press
app.addButtons(["Submit", "Cancel"], press)


# start the GUI
app.go()