from __future__ import division
import json
import os
# Progress bar, and other utilities
from py_clui import Spinner
from py_clui import gauge
from tqdm import tqdm


# Command Line Wrapper
from sultan.api import Sultan
s = Sultan()

def clear_console():
    os.system('cls' if os.name=='nt' else 'clear')

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
# Multi-processing
from multiprocessing import Pool
import subprocess
import sys
clear_console()
inform('Rendering script - Render is about to begin')
threads = int(ask('Enter number of threads per scene'))
parallel = int(ask('Enter number of scenes to process in parallel'))
inform('Enter the amount of RAM per thread to allocate.')
warn('Leave Java Arguments blank by pressing enter when asked to fill out its field.')
os.system('java -jar ChunkyLauncher.jar --setup')


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
explicit_logging = ask('Explicit logging on? This replaces the progress bar with the direct output of the Chunky processes. (True / False)')
warn('Starting render...')
def f(i):
    to_render  = scene_name + str(i)
    if (explicit_logging == 'False' or explicit_logging == 'no')):
        subprocess.call('java -jar ChunkyLauncher.jar -render ' + to_render + ' -threads ' + str(threads), shell=True, stdout=open(os.devnull, 'wb'))
    else:
        subprocess.call('java -jar ChunkyLauncher.jar -render ' + to_render + ' -threads ' + str(threads), shell=True)
if __name__ == '__main__':
    p = Pool(int(parallel))
    for _ in tqdm(p.imap_unordered(f, range(frames)), total=len(range(frames))):
        pass
    p.close()
    p.join()


inform('Rendering complete.')
