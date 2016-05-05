
from transformations import concatenate_matrices, euler_matrix, euler_from_matrix
from transformations import quaternion_from_matrix, euler_from_quaternion, rotation_from_matrix, rotation_matrix
from numpy import zeros, array, dot, cross
from scipy import spatial
import math
from math import sqrt
pi = math.pi

# pick which side is 'up'
OFF_SIDE_INDEX = 4

# generate 12 points in Cartesian space, with 'spiral' method
# from http://blog.andreaskahler.com/2009/06/creating-icosphere-mesh-in-code.html
t = (1.0 + math.sqrt(5.0)) / 2.0
norm = math.sqrt(t*t + 1)

aa = zeros((12, 3))
aa[0] = (-1,  t,  0)
aa[1] = ( 1,  t,  0)
aa[2] = (-1, -t,  0)
aa[3] = ( 1, -t,  0)

aa[4] = ( 0, -1,  t)
aa[5] = ( 0,  1,  t)
aa[6] = ( 0, -1, -t)
aa[7] = ( 0,  1, -t)

aa[8] = ( t,  0, -1)
aa[9] = ( t,  0,  1)
aa[10]=(-t,  0, -1)
aa[11] = (-t,  0,  1)

# normalize to unit sphere
aa = aa / norm

# rotate above points to match one point with 0, 0, 1
a = (0,0,1)
b = aa[OFF_SIDE_INDEX]
direction = cross(a,b)
angle=math.acos(dot(a,b))
rm = rotation_matrix(angle, direction, point=None)
rm3 = rm[0:3, 0:3]
ar = zeros((12, 3))

for i in range(12):
    ar[i] = dot(aa[i], rm3)

def channel_from_euler(roll, pitch, yaw, dodeca_array=ar, verbosity = 0):
    """ Get dodecahedron side from Euler angle """
    rr = euler_matrix(roll, pitch, yaw, 'sxyz')
    rr3 = rr[0:3, 0:3]
    distance,index = spatial.KDTree(dodeca_array).query(rr3[2])
    if verbosity > 0: 
        print "{}\t{}".format(index, distance)
    return index

