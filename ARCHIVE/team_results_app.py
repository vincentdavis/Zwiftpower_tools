import PySimpleGUI as sg

sg.theme('DarkAmber')	# Add a touch of color
# All the stuff inside your window.
layout = [  [sg.Text('Simple app to get team results and save an csv file.')],
            [sg.Text('Team ID or team zwiftpower url'), sg.InputText(key = "team_id")],
            [sg.Button('Ok'), sg.Button('Quit')] ]
# Create the Window
window = sg.Window('Window Title', layout)
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event in (None, 'Cancel'):	# if user closes window or clicks cancel
        break
    text_input = values["team_id"]
    sg.popup('You entered', text_input)

window.close()