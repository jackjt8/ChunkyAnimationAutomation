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
import sys
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
    
def main():
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
    
    t2 = 10.0
    x2 = 5.0
    y2 = 6.0
    z2 = 5.0
    roll2 = 0.0
    yaw2 = 50.0
    pitch2 = 5.0
    fov2 = 100
    dof2 = 200.0
    focal2 = 1.0
    
    #%%
    framerate = 24.0
    
    keyscenes = []
    
    #                [scene_fname, time_stamp]
    #keyscenes.append(['Skyrim0.json', -0.5]) # all time stamps pre 0.0 ignored post interp/convolution
    keyscenes.append(['Skyrim1.json', 0.0]) # used as template for saving
    #keyscenes.append(['Skyrim2.json', 1.0])
    #keyscenes.append(['Skyrim3.json', 2.0])
    #keyscenes.append(['Skyrim4.json', 3.0]) # all time stamps post 3.0 ignored post interp/convolution
    #keyscenes.append(['Skyrim5.json', 3.5]) 
    
    json_interp = json_interpT(framerate)
    setup_return = json_interp.keyscene_setup(keyscenes)

    if setup_return == 0:
        print('ERROR - Need at least one keyscene')
    elif setup_return == 1:
        # ASK for point 2 / B details.
        t2 = 10.0 # ASK
        x2 = 5.0 # ASK
        y2 = 6.0 # ASK
        z2 = 5.0 # ASK
        roll2 = 0.0 # ASK
        yaw2 = 50.0 # ASK
        pitch2 = 5.0 # ASK
        fov2 = 100 # ASK
        dof2 = 200.0 # ASK
        focal2 = 1.0 # ASK
        
        #pass point 2 / B
        json_interp.point2_setup([t2, x2, y2, z2, roll2, pitch2, yaw2, fov2, dof2, focal2])
        
        # run linear interp
        json_interp.do_interpT('slinear')
        
    elif setup_return == 2:
        # run linear interp
        json_interp.do_interpT('slinear')
        
    elif setup_return == 3 or setup_return == 4:
        # smoothing == 1 (off) OR smoothing > 1 (on/strength)
        json_interp.do_interpT('slinear')
    else:
        """ASK if they want to use:
        slinear
        quad
        cubic
        ---
        smoothing == 1 (off) OR smoothing > 1 (on/strength)
        """
        kind = 'cubic' # ASK
        json_interp.do_interpT(kind)
        
        pass
    
    json_interp

    
#%%  
class json_interpT():
    def __init__(self, framerate):
        self.camX = []
        self.camY = []
        self.camZ = []
        self.camRoll = []
        self.camPitch = []
        self.camYaw = []

        self.camFoV = []
        self.camDoF = []
        self.camfocalOffset = []

        self.source_fname = []      
        self.source_times = []
        self.source_scenes = []
        
        self.tframe = []
        self.nframe = []
        self.frametime = 1.0 / framerate
     
    #%%
    def keyscene_setup(self, keyscenes):
        # Unpack (for easier use)
        self.source_fname = [i[0] for i in keyscenes]
        self.source_times = [i[1] for i in keyscenes]
        
        # load scenes
        for fname in self.source_fname:
            self.source_scenes.append(jsonload(fname))
        
        # Check how many scenes we have and decide actions.
        if len(self.source_scenes) == 0:
            sys.exit('ERROR - Need at least one keyscene')
            return 0

        elif len(self.source_scenes) == 1:
            """ If you recieve '1' back from this function
                ask user for details on point2 / B
                then call point2_setup([t2, x2, y2, z2, roll2, pitch2, yaw2, fov2, dof2, focal2])
            """
            sys.exit('todo: Line 123 - read comment!')
            return 1
        
        elif len(self.source_scenes) == 2:
            # AB
            # disable smoothing + trim
            print('2')
        
        elif len(self.source_scenes) == 3 or len(self.source_scenes) == 4:
            # probably fall back to AB
            print('3')
        else:
            # use smoothing + trim with padding.
            print('else')
        return
    
    #%%
    def point2_setup(self, t2, x2, y2, z2, roll2, pitch2, yaw2, fov2, dof2, focal2):    
        # use source_scenes[0] as template
        self.source_scenes.append(self.source_scenes[0])
        # Ask users for point2 details...
        self.source_times.append(t2) # ASK
        self.source_scenes[1]['camera']['position']['x'] = x2 # ASK
        self.source_scenes[1]['camera']['position']['y'] = y2 # ASK
        self.source_scenes[1]['camera']['position']['z'] = z2 # ASK
        self.source_scenes[1]['camera']['orientation']['roll'] = roll2 # ASK
        self.source_scenes[1]['camera']['orientation']['pitch'] = pitch2 # ASK
        self.source_scenes[1]['camera']['orientation']['yaw'] = yaw2 # ASK
        
        self.source_scenes[1]['camera']['fov'] = fov2 # ASK
        self.source_scenes[1]['camera']['dof'] = dof2 # ASK
        self.source_scenes[1]['camera']['focalOffset'] = focal2 # ASK
            
    #%%
    def do_interpT(self, interp_mode):
        # Fill the lists with data (at least what we want)
        for scene in self.source_scenes:
            self.camX.append(scene['camera']['position']['x'])
            self.camY.append(scene['camera']['position']['y'])
            self.camZ.append(scene['camera']['position']['z'])
            self.camRoll.append(scene['camera']['orientation']['roll'])
            self.camPitch.append(scene['camera']['orientation']['pitch'])
            self.camYaw.append(scene['camera']['orientation']['yaw'])
            
            self.camFoV.append(scene['camera']['fov'])
            self.camDoF.append(scene['camera']['dof'])
            self.camDoF = [999999 if x=='Infinity' else x for x in self.camDoF] # Might need to use a higher value.
            self.camfocalOffset.append(scene['camera']['focalOffset'])
        
        
        self.nframe = (self.source_times[-1] - self.source_times[0]) / self.frametime #number of frames between first and last scene
        self.tframe = np.linspace(self.source_times[0], self.source_times[-1], int(self.nframe)) #time of each frame
        
        # interp data...
        self.new_camX = interpT(self.source_times, self.tframe, self.camX, interp_mode)
        self.new_camY = interpT(self.source_times, self.tframe, self.camY, interp_mode)
        self.new_camZ = interpT(self.source_times, self.tframe, self.camZ, interp_mode)
        self.new_camRoll = interpT(self.source_times, self.tframe, self.camRoll, interp_mode)
        self.new_camPitch = interpT(self.source_times, self.tframe, self.camPitch, interp_mode)
        self.new_camYaw = interpT(self.source_times, self.tframe, self.camYaw, interp_mode)
        
        self.new_camFoV = interpT(self.source_times, self.tframe, self.camFoV, interp_mode) # might go negative
        self.new_camDoF = interpT(self.source_times, self.tframe, self.camDoF, interp_mode) # might go negative
        self.new_camfocalOffset = interpT(self.source_times, self.tframe, self.camfocalOffset, interp_mode) # might go negative
    
    #%%    
    def post_interpT_smooth(self, smoothing_var):
        #Data smoothing
        self.new_camX = smooth(self.new_camX,smoothing_var)
        self.new_camY = smooth(self.new_camY,smoothing_var)
        self.new_camZ = smooth(self.new_camZ,smoothing_var)
        self.new_camRoll = smooth(self.new_camRoll,smoothing_var)
        self.new_camPitch = smooth(self.new_camPitch,smoothing_var)
        self.new_camYaw = smooth(self.new_camYaw,smoothing_var)
        
        self.new_camFoV = smooth(self.new_camFoV,smoothing_var)
        self.new_camDoF = smooth(self.new_camDoF,smoothing_var)
        self.new_camfocalOffset = smooth(self.new_camfocalOffset,smoothing_var)
        
    #%%
#%%
    

# Used for triming scene padding later.
#trim_idx = np.where( (tframe>source_times[1]) * (tframe<source_times[-2]) )[0]
#trim_tframe = [tframe[i] for i in trim_idx]

#%%



#%%




sys.exit(0)

#%%



#%%


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

if __name__ == '__main__':
    print("interp - tldr blame jackjt8")
    main()