import json
import os
# Progress bar, and other utilities
from py_clui import Spinner
from py_clui import gauge
from py_clui import Progress

# Command Line Wrapper
from sultan.api import Sultan
s = Sultan()

# Coloured Text
from colorama import init
init()
from colorama import Fore, Back, Style
def inform(text):
    print(Fore.CYAN + text + Style.RESET_ALL)
def log(text):
    print(Fore.BLACK + Style.BRIGHT + text + Style.RESET_ALL)
def ask(text):
    print(Fore.MAGENTA + text + Style.RESET_ALL)
    return input()
def warn(text):
    print(Fore.YELLOW + Back.RED + text + Style.RESET_ALL)

# Wrapper for the wrapper???
def run_and_return(command):
    with Sultan.load() as s:
        result = s.java('-jar ChunkyLauncher.jar -' + command).run()
        log(str(result.stdout))
        return result.stderr
def chunky_run(command):
    with Sultan.load() as s:
        result = s.java('-jar ChunkyLauncher.jar -' + command).run()
# Startup information


inform('Chunky Rendering Automation')
warn('It is reccomended to clear out your scene folder beforehand, as this can get very messy VERY FAST!')
warn('This script requires a copy of the ChunkyLauncher.jar to be placed in the directory with all these scripts.')
inform('Please setup your scene inside of Chunky with the lighting you want, the selected chunks, etc.')
warn('If you turn on Dump every X frames, **DO NOT SAVE SNAPSHOT FOR EVERY DUMP**. It will cause a lot of mess to happen.')
inform('Then give the scene a unique and memorable name and save the scene.')
warn('The name must not contain spaces!')

ask('Press Enter once you have done this.')

input()
scene_list = run_and_return('list-scenes')
for scene in scene_list:
    inform(scene)
print()
print()
scene_name = ask('What scene would you like to render? (Type it exactly!)')
chunky_folder = ask('What is your Chunky directory? eg: /home/snorlax/.chunky (Paste it here. If you cannot find it, look for the Settings loaded message above, but discard everything after ./chunky)')

# Check to see if the Chunky directory is actually where the user set it
while (os.path.exists(chunky_folder + '/chunky.json') != True):
    warn('That seems to be the incorrect folder!! Please try again.')
    chunky_folder = ask('What is your Chunky directory? eg: /home/snorlax/.chunky (Paste it here. If you cannot find it, look for the Settings loaded message above, but discard everything after ./chunky)')

# Save this to a file for other processes to read
info_to_write = {}
info_to_write['details'] = []
info_to_write['details'].append({
    'chunky_directory': chunky_folder,
    'scene_name': scene_name
})

with open('info.json', 'w') as outfile:
    json.dump(info_to_write, outfile)
    outfile.close()

# Select action
inform('What would you like to do?')
inform('1 | Rotation on spot')
inform('2 | Straight Line flythrough -- NOT YET IMPLEMENTED')
action = ask('Enter a number: ')
print(action)
if (action == '1'):
    os.system('python spot_rotate.py')
else:
    print('Not yet implemented. Exiting...')
