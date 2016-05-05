import sys, getopt

sys.path.append('.')
import RTIMU
import os.path
import time
import math

from get_dodeca_points import channel_from_euler
from channel_config import sound_files

OFF_CHANNEL = 7

SETTINGS_FILE = "RTIMULib"

print("Using settings file " + SETTINGS_FILE + ".ini")
if not os.path.exists(SETTINGS_FILE + ".ini"):
  print("Settings file does not exist, will be created")

s = RTIMU.Settings(SETTINGS_FILE)
imu = RTIMU.RTIMU(s)

print("IMU Name: " + imu.IMUName())

if (not imu.IMUInit()):
    print("IMU Init Failed")
    sys.exit(1)
else:
    print("IMU Init Succeeded")

# this is a good time to set any fusion parameters

imu.setSlerpPower(0.02)
imu.setGyroEnable(True)
imu.setAccelEnable(True)
imu.setCompassEnable(True)

poll_interval = imu.IMUGetPollInterval()
print("Recommended Poll Interval: %dmS\n" % poll_interval)


import pygame
import pygame.mixer as pm
pm.init()
pm.pre_init(44100, -16, 1, 4096)

def start_sounds(sound_list):
    """ start list of sound files with PyGame  
    """
    loops = []
    for sound in sound_list:
        loop = pygame.mixer.Sound(sound)
        loops.append(loop)

    for loop in loops:
        loop.play(-1)

    return

def is_rotating(data, threshold = 0.01):
    dg = data['gyro']
    
    magnitude = (dg[0]*dg[0] + dg[1]*dg[1] + dg[2]*dg[2])
    if magnitude > threshold:
        return True
    else:
        return False


count = 0
cur_chan = OFF_CHANNEL
while True:
  if imu.IMURead():
    # x, y, z = imu.getFusionData()
    # print("%f %f %f" % (x,y,z))
    data = imu.getIMUData()
    
    fusionPose = data["fusionPose"]
    if not (count % 8):
      
      #roll = math.degrees(fusionPose[0])
      #pitch = math.degrees(fusionPose[1])
      #yaw = math.degrees(fusionPose[2])
      #print("r: %f p: %f y: %f" % (math.degrees(fusionPose[0]), 
      #  math.degrees(fusionPose[1]), math.degrees(fusionPose[2])))

      roll_rad = fusionPose[0]
      pitch_rad = fusionPose[1]
      yaw_rad = fusionPose[2]
      chan = channel_from_euler(roll_rad, pitch_rad, yaw_rad, verbosity=1)

      rotating = is_rotating(data)

      if chan == OFF_CHANNEL and not rotating:
          if cur_chan != OFF_CHANNEL:
              print "Pausing" 
              pm.fadeout(1000)
              cur_chan = OFF_CHANNEL
          count = 0

      elif chan != cur_chan and not rotating:
          print "Switching to channel {}".format(chan)
          pm.fadeout(2500)
          start_sounds(sound_files[chan])
          cur_chan = chan
          count = 0
      
    time.sleep(poll_interval*1.0/1000.0)
    count += 1

