import numpy as np
import math
import json
import sys
def isRotationMatrix(R) :
    Rt = np.transpose(R)
    shouldBeIdentity = np.dot(Rt, R)
    I = np.identity(3, dtype = R.dtype)
    n = np.linalg.norm(I - shouldBeIdentity)
    return n < 1e-6

def rotationMatrixToEulerAngles(R) :
    assert(isRotationMatrix(R))
    sy = math.sqrt(R[0,0] * R[0,0] +  R[1,0] * R[1,0])
    singular = sy < 1e-6
    if  not singular :
        x = math.atan2(R[2,1] , R[2,2])
        y = math.atan2(-R[2,0], sy)
        z = math.atan2(R[1,0], R[0,0])
    else :
        x = math.atan2(-R[1,2], R[1,1])
        y = math.atan2(-R[2,0], sy)
        z = 0
    return np.array([x, y, z])
with open("Get_real_angle/aaa.json",'r') as jsonfile:
    data=dict(json.load(jsonfile)["c2ws"])
    for key,value in data.items():
        position=np.array(value)[0:3,-1].squeeze()
        distance=np.linalg.norm(position)
        theta=np.arccos(position[2]/distance) 
        
        
        phi=np.arctan(position[1]/position[0]) if position[0]>0 else np.arctan(position[1]/position[0])+np.pi
        if phi<0:phi+=2*np.pi
            
        
        theta=float(theta*180/np.pi)
        phi=float(phi*180/np.pi)
        
        
        print("name:",key,"distance=",distance,'\ttheta=',theta,'\tphi',phi)
    
        
