import sys, getopt

sys.path.append('.')
import RTIMU
import os.path
import time
import math

from get_dodeca_points import channel_from_euler

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

diva_sounds = ['samples/diva01.wav',
  'samples/diva02.wav',
  'samples/diva03.wav',
  'samples/diva04.wav',
]

desert_sounds = [ 
    'samples/desertstrings1.wav',
    'samples/desertstrings2.wav',
    'samples/desertstrings3.wav',
    'samples/desertstrings4.wav']

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

start_sounds(diva_sounds)

count = 0
track = 1
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

      if chan == 7:
          print "Pausing" + str(count) 
          pm.pause()
      elif chan in [1, 3, 5, 9, 11] and track == 1 and count > 200:
           print pm.get_busy()
           if track == 1:
               pm.fadeout(3000)
               start_sounds(desert_sounds)
               track = 2
               count = 0
      elif chan in [0, 2, 4, 6, 8, 10]  and track == 2 and count > 200:
          pm.fadeout(2500)
          start_sounds(diva_sounds)
          track = 1  
          count = 0
      else:
          pm.unpause()
      
    time.sleep(poll_interval*1.0/1000.0)
    count += 1

