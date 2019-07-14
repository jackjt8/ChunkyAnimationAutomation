from __future__ import division
import json
import os
from easygui import *
# Progress bar, and other utilities
from py_clui import Spinner
from py_clui import gauge
from progress.bar import IncrementalBar
from tqdm import tqdm


# Command Line Wrapper
from sultan.api import Sultan
s = Sultan()

def clear_console():
    os.system('cls' if os.name=='nt' else 'clear')

# colored text
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
# Multi-processing
from multiprocessing import Pool
import subprocess
import sys


msgbox('Render script - Final steps before rendering')
system_load = []
system_load = multenterbox('Enter resource allocation', 'Resource allocation', ['Threads per scene', 'Scenes to process in parallel'])
threads = int(system_load[0])
parallel = int(system_load[1])
log('Rendering ' + str(parallel) + ' scenes in parallel on ' + str(threads) + ' threads each')

log('Grabbing details...')
with open('info.json') as json_file:
    data = json.load(json_file)
    scene_name = data['details'][0]['scene_name']
    chunky_directory = data['details'][0]['chunky_directory']
    json_file.close()


log('Grabbing number of frames...')
# Get the number of frames, reads, then deletes.
file = open('frames.txt', 'r')
frames = int(file.read())
file.close()
os.remove('frames.txt')
msgbox('Rendering is about to start -- Check console for progress bar. It only updates when a scene completes, so please be patient. Click OK to begin.')
warn('Starting rendering...')
def f(i):
    to_render  = scene_name + str(i)
    subprocess.call('java -jar ChunkyLauncher.jar -render ' + to_render + ' -threads ' + str(threads), shell=True, stdout=open(os.devnull, 'wb'))

if __name__ == '__main__':
    p = Pool(int(parallel))
    for _ in tqdm(p.imap_unordered(f, range(frames)), total=len(range(frames))):
        pass
    p.close()
    p.join()


inform('Rendering complete.')
inform('Renaming files...')

log('Getting SPP target')
file = open('target.txt', 'r')
target = int(file.read())
file.close()
with IncrementalBar('Renaming files...', max=frames, suffix='%(percent).1f%% - %(eta)ds') as bar:
    for i in range(frames):
        file_to_rename = chunky_directory + '/scenes/' + scene_name + str(i) + '-' + str(target) + '.png'
        os.rename(file_to_rename, file_to_rename.replace('-' + str(target), ''))
        bar.next()

log('File renaming complete')
msgbox('Everything is done! Check your scene folder, and grab all the .png files.')
log('Exiting...')
