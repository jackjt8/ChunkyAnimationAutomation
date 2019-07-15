import json
import os
from os import path
from easygui import *
# Progress bar, and other utilities
#from py_clui import Spinner
#from py_clui import gauge
#from py_clui import Progress

# Command Line Wrapper
from sultan.api import Sultan
s = Sultan()

def clear_console():
    os.system('cls' if os.name=='nt' else 'clear')

# Isn't even needed anymore tbqh
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

# Startup information
clear_console()
msgbox('Chunky Rendering Automation \nPlease setup your scene inside of Chunky with the lighting you want, the selected chunks, camera location, etc. \nThen give the scene a unique and memorable name and save the scene. \n \nIf you turn on Dump every X frames, **DO NOT SAVE SNAPSHOT FOR EVERY DUMP**. It will get messy very fast, and make it a pain to stitch together the images. \nMake sure the scene name does not contain any spaces!\n\n\nClick OK once you have done this.')
while path.exists('ChunkyLauncher.jar') == False:
    msgbox('The ChunkyLauncher.jar does not seem to be in this folder. Please place a copy of it in the same folder as this script. \n \nIf you need to download it, visit here: http://chunkyupdate2.llbit.se/ChunkyLauncher.jar')


scene_list = run_and_return('list-scenes')
scene_name = None

while scene_name == None:
    scene_name = choicebox('What scene would you like to render?', 'Select a scene', scene_list[2:]).replace('\t', '')
    if scene_name == None:
        msgbox('Please select a scene!')

chunky_folder = None
while chunky_folder == None:
    msgbox('Please open your Chunky Directory in the following file browser window.')
    chunky_folder = diropenbox()

# Check to see if the Chunky directory is actually where the user set it
while (os.path.exists(chunky_folder + '/chunky.json') != True):
    msgbox('That seems to be the incorrect folder! Please try again.')
    chunky_folder = diropenbox()

# Save this to a file for other processes to read
log('Writing info to file...')
info_to_write = {}
info_to_write['details'] = []
info_to_write['details'].append({
    'chunky_directory': chunky_folder,
    'scene_name': scene_name
})
print(scene_name)
with open('info.json', 'w') as outfile:
    json.dump(info_to_write, outfile)
    outfile.close()

# Select action
action = choicebox('What would you like to do?', 'Select render type', ['Rotation on the spot', 'Another mysterious thing'])
if (action == 'Rotation on the spot'):
    log('Rotation on the spot selected')
    log('Handing over to spot_rotate.py ...')
    from spot_rotate import execute_spot_rotate
    execute_spot_rotate()
else:
    print('Not yet implemented. This will come Soon. (tm)')
    sys.exit()
os.system('python rendering.py')
