import json
import os
import psutil
# Progress bar, and other utilities
from py_clui import Spinner
from py_clui import gauge
from py_clui import Progress

def clear_console():
    os.system('cls' if os.name=='nt' else 'clear')
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
clear_console()
inform('This is the Spot Rotation script. It is assumed that the current camera position is the location to rotate around, and will start rotating 360 from 0deg. (Facing south.) You can re-order the frames later using another program.')
inform('What direction would you like to rotate?')
inform('1 | Clockwise')
inform('2 | Anti-Clockwise')
rotation_type = ask('Enter a number: ')
frames = ask('How many frames would you like the rotation to last? Enter a number of frames. (60 frames = 2s at 30fps OR 1s at 60fps; 120 frames = 2s at 60fps OR 4s at 30fps; etc')
rotation_increment = 360 / int(frames)

if rotation_type == '1':
    log('Rotating clockwise at ' + str(rotation_increment) + ' per frame')
else:
    rotation_increment = rotation_increment * -1
    log('Rotating Anti-Clockwise at ' + str(rotation_increment) + ' per frame')
inform('Final setup before rendering!')
threads = int(ask('Enter the number of CPU threads to use'))
target = int(ask('Enter the SPP target per frame'))

# Get info
with open('info.json') as json_file:
    data = json.load(json_file)
    scene_name = data['details'][0]['scene_name']
chunky_run('set yaw 0.0 ' + scene_name)
