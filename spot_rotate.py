import json
import os
import psutil
import shutil
# Progress bar, and other utilities

from py_clui import gauge
from progress.bar import IncrementalBar

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
    print(Back.RED + text + Style.RESET_ALL)

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
inform('This is the Spot Rotation script. It is assumed that the current camera position is the location to rotate at, and will start rotating 360 from 0deg. (Facing south.) You can re-order the frames later using another program.')
inform('What direction would you like to rotate?')
inform('1 | Clockwise')
inform('2 | Anti-Clockwise')
rotation_type = ask('Enter a number: ')
frames = int(ask('How many frames would you like the rotation to last? Enter a number of frames. (60 frames = 2s at 30fps OR 1s at 60fps; 120 frames = 2s at 60fps OR 4s at 30fps; etc'))
rotation_increment = 360 / int(frames)

if rotation_type == '1':
    log('Rotating clockwise at ' + str(rotation_increment) + ' per frame')
else:
    rotation_increment = rotation_increment * -1
    log('Rotating Anti-Clockwise at ' + str(rotation_increment) + ' per frame')
target = int(ask('Enter the SPP target per frame'))

# Get info
with open('info.json') as json_file:
    data = json.load(json_file)
    scene_name = data['details'][0]['scene_name']
    chunky_directory = data['details'][0]['chunky_directory']
    json_file.close()

scene_file = chunky_directory + '/scenes/' + scene_name + '.json'

# Setting the camera in the template
count = 0

with open(scene_file, 'r') as original_scene:
    data = json.load(original_scene)
    data['camera']['orientation']['yaw'] = 0.0
    data['sppTarget'] = target
    data['name'] = scene_name + str(0)
    original_scene.close()

with open(scene_file, "w") as new_scene:
    json.dump(data, new_scene)
    new_scene.close()


with IncrementalBar('Copying JSON...', max=frames, suffix='%(percent).1f%% - %(eta)ds') as bar:
    for count in range(frames):
        shutil.copyfile(scene_file, chunky_directory + '/scenes/' + scene_name + str(count) + '.json')
        with open(scene_file, 'r') as original_scene:
            data = json.load(original_scene)
            data['camera']['orientation']['yaw'] += rotation_increment * count
            data['sppTarget'] = target
            data['name'] = scene_name + str(count)
            original_scene.close()

        with open(chunky_directory + '/scenes/' + scene_name + str(count) + '.json', "w") as new_scene:
            json.dump(data, new_scene)
            new_scene.close()
        bar.next()


# Handover below. Must be included at the end of every prep script

# Write number of frames to frames.txt
# It's incredibly hacky, fight me.
file = open('frames.txt', 'w')
file.write(str(frames))
file.close()

#Hand over to the render script
inform('Beginning rendering...')
os.system('python rendering.py')
