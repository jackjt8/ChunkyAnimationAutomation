# -*- coding: utf-8 -*-
"""
@author: jackjt8

title: Chunky JSON generator
      -  Camera interpT A-B

ver: 0.1 (2019-07-14) [Python 3.7]

Current: numpy, scipy, (matplotlib)
"""


import json
import os
import numpy as np
from scipy import interpolate

#import matplotlib.pyplot as plt

def jsonload(fname):
    return json.load(open(os.path.join('Source', fname),"r"))

def jsonsave(scene, fname):
    json.dump(scene, open(os.path.join('Output', fname),"w"), indent=2)
    #print(fname)
    return

def interpT(t, tframe, x, kindtype): # use t,x,and kindtype to create function. use tfrmae with function.
    f = interpolate.interp1d(t, x, kind=kindtype)
    return f(tframe)

def smooth(y, box_pts): # Standard convolve/moving average type of smoothing. Just added y padding to fix
    box = np.ones(box_pts)/box_pts
    y_padded = np.pad(y, (box_pts//2, box_pts-1-box_pts//2), mode='edge')
    y_smooth = np.convolve(y_padded, box, mode='valid')
    return y_smooth

#%%
# Other
decimals = 8
interp_mode = 'slinear' # SET
smoothing_var = 14 # SET
""" Compared against ‘quadratic’ & ‘cubic’ which produced curves slinear/linear does NOT have issues with overshoots.
    Meaning that for values that have boundaries, ie Sun Color Red which falls between 0.0 & 1.0 it would be
    possible for quad/cubic to overshoot and go negative or above 1.0 (which is bad). Either the keyscenes cannot
    have any significant swings in interp'ed values or more keyscenes around the turning points would be needed to
    help smooth and avoid overshoots are needed.
    
    slinear/linear, as the name implies, goes point to point in a straight line. Combined with convolution based
    smoothing and it can be a very sound alternative assuming we have enough padded data.
"""

# Render properites
framerate = 24.0 # SET (needs default value)
frametime = 1.0/framerate

SPP = 128 # SET (Optional)
RD = 5 # SET (Optional)
res_w = 1920 # SET (Optional)
res_h = 1080 # SET (Optional)

write_json = True # SET
""" It would be a good idea to make this step optional. I am considering working on some visual display for the
    interp'ed path with velocity based colours so people can see what they are getting before they commit the files.
"""

#%%
keyscenes = []

#                [scene_fname, time_stamp]
#keyscenes.append(['Skyrim0.json', -0.5]) # all time stamps pre 0.0 ignored post interp/convolution
keyscenes.append(['Skyrim1.json', 0.0]) # used as template for saving
keyscenes.append(['Skyrim2.json', 10.0])
#keyscenes.append(['Skyrim3.json', 2.0])
#keyscenes.append(['Skyrim4.json', 3.0]) # all time stamps post 3.0 ignored post interp/convolution
#keyscenes.append(['Skyrim5.json', 3.5]) 

# Unpack (for easier use)
source_fname = [i[0] for i in keyscenes]
source_times = [i[1] for i in keyscenes]
del keyscenes

#%%
source_scenes = [] # holds loaded json data as dict

for fname in source_fname:
    source_scenes.append(jsonload(fname))
    
nframe = (source_times[-1] - source_times[0]) / frametime #number of frames between first and last scene
tframe = np.linspace(source_times[0], source_times[-1], int(nframe)) #time of each frame

# Used for triming scene padding later.
trim_idx = np.where( (tframe>source_times[1]) * (tframe<source_times[-2]) )[0]
trim_tframe = [tframe[i] for i in trim_idx]

#%%
# Define lists to store data
camX = []
camY = []
camZ = []
camRoll = []
camPitch = []
camYaw = []

camFoV = []
camDoF = []
camfocalOffset = []


# Fill the lists with data (at least what we want)
for scene in source_scenes:
    camX.append(scene['camera']['position']['x'])
    camY.append(scene['camera']['position']['y'])
    camZ.append(scene['camera']['position']['z'])
    camRoll.append(scene['camera']['orientation']['roll'])
    camPitch.append(scene['camera']['orientation']['pitch'])
    camYaw.append(scene['camera']['orientation']['yaw'])
    
    camFoV.append(scene['camera']['fov'])
    camDoF.append(scene['camera']['dof'])
    camDoF = [999999 if x=='Infinity' else x for x in camDoF] # Might need to use a higher value.
    camfocalOffset.append(scene['camera']['focalOffset'])

#%%
# interp data...
new_camX = interpT(source_times, tframe, camX, interp_mode)
new_camY = interpT(source_times, tframe, camY, interp_mode)
new_camZ = interpT(source_times, tframe, camZ, interp_mode)
new_camRoll = interpT(source_times, tframe, camRoll, interp_mode)
new_camPitch = interpT(source_times, tframe, camPitch, interp_mode)
new_camYaw = interpT(source_times, tframe, camYaw, interp_mode)

new_camFoV = interpT(source_times, tframe, camFoV, interp_mode) # might go negative
new_camDoF = interpT(source_times, tframe, camDoF, interp_mode) # might go negative
new_camfocalOffset = interpT(source_times, tframe, camfocalOffset, interp_mode) # might go negative

#%%
# Data smoothing
#new_camX = smooth(new_camX,smoothing_var)
#new_camY = smooth(new_camY,smoothing_var)
#new_camZ = smooth(new_camZ,smoothing_var)
#new_camRoll = smooth(new_camRoll,smoothing_var)
#new_camPitch = smooth(new_camPitch,smoothing_var)
#new_camYaw = smooth(new_camYaw,smoothing_var)
#
#new_camFoV = smooth(new_camFoV,smoothing_var)
#new_camDoF = smooth(new_camDoF,smoothing_var)
#new_camfocalOffset = smooth(new_camfocalOffset,smoothing_var)

#%%
# Data rounding... (to avoid any issues with Chunky)
new_camX = np.round(new_camX,decimals)
new_camY = np.round(new_camY,decimals)
new_camZ = np.round(new_camZ,decimals)
new_camRoll = np.round(new_camRoll,decimals)
new_camPitch = np.round(new_camPitch,decimals)
new_camYaw = np.round(new_camYaw,decimals)

new_camFoV = np.round(new_camFoV,decimals)
new_camDoF = np.round(new_camDoF,decimals)
new_camfocalOffset = np.round(new_camfocalOffset,decimals)

#%%
# trim unusable data? This might not be an issue if using slinear/linear + smoothing
#   but I'll keep this in in case people use quad/cubic.
#new_camX = [new_camX[i] for i in trim_idx]
#new_camY = [new_camY[i] for i in trim_idx]
#new_camZ = [new_camZ[i] for i in trim_idx]
#new_camRoll = [new_camRoll[i] for i in trim_idx]
#new_camPitch = [new_camPitch[i] for i in trim_idx]
#new_camYaw = [new_camYaw[i] for i in trim_idx]
#
#new_camFoV = [new_camFoV[i] for i in trim_idx]
#new_camDoF = [new_camDoF[i] for i in trim_idx]
#new_camfocalOffset = [new_camfocalOffset[i] for i in trim_idx]

#%%
# create jsons
for i in range(len(new_camX)):
    temp_scene = source_scenes[1]
    
    temp_scene['camera']['position']['x'] = new_camX[i]
    temp_scene['camera']['position']['y'] = new_camY[i]
    temp_scene['camera']['position']['z'] = new_camZ[i]
    temp_scene['camera']['orientation']['roll'] = new_camRoll[i]
    temp_scene['camera']['orientation']['pitch'] = new_camPitch[i]
    temp_scene['camera']['orientation']['yaw'] = new_camYaw[i]
    
    temp_scene['camera']['fov'] = new_camFoV[i]
    temp_scene['camera']['dof'] = new_camDoF[i]
    temp_scene['camera']['focalOffset'] = new_camfocalOffset[i]
    
    temp_scene['spp'] = SPP
    temp_scene['rayDepth'] = RD
    temp_scene['width'] = res_w
    temp_scene['heigh'] = res_h
    
    name = 'interp_' + str(i).zfill( len(str(int(nframe))) ) # insure padding in file explorer
    temp_scene['name'] = name
    
    fname = name + '.json'
    jsonsave(temp_scene, fname)

print('done')