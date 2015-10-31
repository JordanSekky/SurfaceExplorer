
from math import *
from visual import *
# from time import sleep
from random import uniform
import os, sys, inspect, thread, time

sys.path.insert(0, "/Users/jordan/Downloads/LeapDeveloperKit_2.3.1+31549_mac/LeapSDK/lib/")

import Leap, sys, thread, time
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture

# arrow(axis=vector(1,0,0))
# text(text="x",pos=vector(1,0,0),height=0.4)
# arrow(axis=vector(0,1,0))
# text(text="y",pos=vector(0,1,0),height=0.4)
# arrow(axis=vector(0,0,1))
# text(text="z",pos=vector(0,0,1),height=0.4)

class SampleListener(Leap.Listener):
    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
    state_names = ['STATE_INVALID', 'STATE_START', 'STATE_UPDATE', 'STATE_END']

    def on_init(self, controller):
        print "Initialized"

    def on_connect(self, controller):
        print "Connected"

        # Enable gestures
        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE);
        controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE);

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "Disconnected"

    def on_exit(self, controller):
        print "Exited"

    def on_frame(self, controller):
        # Get the most recent frame and report some basic information
        frame = controller.frame()

        # Get hands
        results = []
        for hand in frame.hands:

            handType = "Left hand" if hand.is_left else "Right hand"

            # Get the hand's normal vector and direction
            normal = hand.palm_normal
            direction = hand.direction
            
            # Get the hand's grab strength (fist or not)
            strength = hand.grab_strength # Fist closed if strength >= 0.6

            # Get the hand's 
            pitch = hand.direction.pitch
            yaw = hand.direction.yaw
            roll = hand.palm_normal.roll

            r,p = 0,0

           # print "pitch = ", pitch

           # print "roll = ", roll

            #Roll data
            if (roll>-0.17 and roll<-0.09): #Within wiggle room
                r = 0
            else:
                if roll > -0.09:
                    if roll < 0.2:
                        r = -1
                    elif roll < 0.45:
                        r = -2
                    else:
                        r = -3
                elif roll < -0.17:
                    if roll > -0.35:
                        r = 1
                    elif roll > -0.50:
                        r = 2
                    else:
                        r = 3

            #Pitch data
            if (pitch>0.15 and pitch<0.23): # Within wiggle room
                p = 0
            else:
                if pitch > 0.23:            # Left direction
                    if pitch < 0.4:         
                        p = -1
                    elif pitch < 0.6:
                        p = -2
                    else:
                        p = -3
                elif pitch < 0.15:
                    if pitch > 0.05:
                        p = 1
                    elif pitch > -0.25:
                        p = 2
                    else:
                        p = 3

            if strength >= 0.6: #Fist closed
                normal = vector(0,0,0)

            results.append(normal)
            # print "Roll: ", r, " Pitch: ", p
            # results.append([r,p])
        return results


    def state_string(self, state):
        if state == Leap.Gesture.STATE_START:
            return "STATE_START"

        if state == Leap.Gesture.STATE_UPDATE:
            return "STATE_UPDATE"

        if state == Leap.Gesture.STATE_STOP:
            return "STATE_STOP"

        if state == Leap.Gesture.STATE_INVALID:
            return "STATE_INVALID"

class surface():
    def __init__(self,x,y,z,uRng,vRng):
        self.x=x
        self.y=y
        self.z=z
        self.uRng=uRng
        self.vRng=vRng
        self.fList=[]
        self.flg = None
        self.bll = None
        self.follow = None
        u=uRng[0]
        while(u<uRng[1]):
            v=vRng[0]
            while(v<vRng[1]):
                self.fList += [self.posn(u,v),self.posn(u+uRng[2],v),self.posn(u,v+vRng[2])]
                self.fList += [self.posn(u+uRng[2],v),self.posn(u,v+vRng[2]),self.posn(u+uRng[2],v+vRng[2])]
                curve(pos=[self.posn(u+uRng[2],v),self.posn(u,v),self.posn(u,v+vRng[2])], radius=0.03,color=color.blue)
                v+=vRng[2]
            u+=uRng[2]
        s = faces(pos=self.fList)
        s.make_twosided()
        s.smooth()


    def posn(self,u,v):
        x=self.x
        y=self.y
        z=self.z
        return vector(x(u,v),y(u,v),z(u,v))

    def normal(self,u,v):
        x=self.x
        y=self.y
        z=self.z
        n1=norm(deriv(lambda k: self.posn(k,v))(u))
        n2=norm(deriv(lambda k: self.posn(u,k))(v))
        n=norm(cross(n1,n2))
        #arrow(pos=self.posn(u,v),axis=n1)
        #arrow(pos=self.posn(u,v),axis=n2)
        #arrow(pos=self.posn(u,v),axis=n,color=color.blue)
        return n
    def placeFlagRandom(self,r,h,f):
        flag(self,uniform(self.uRng[0],self.uRng[1]),uniform(self.vRng[0],self.vRng[1]),r,h,f)

class ball():
    def __init__(self,rad,surf,u,v):
        self.rad=rad
        self.surf=surf
        self.surf.bll = self
        self.u=u
        self.v=v
        self.drawn=sphere(radius=rad,pos=surf.posn(u,v)+rad*surf.normal(u,v))

    def move(self,du,dv):
        surf=self.surf
        self.u+=du/(surf.uRng[1]-surf.uRng[0])
        self.v+=dv/(surf.vRng[1]-surf.vRng[0])
        if(self.u<surf.uRng[0]):
            if(surf.uRng[3]):
                self.u+=surf.uRng[1]-surf.uRng[0]
            else:
                self.u=surf.uRng[0]
        if(self.u>surf.uRng[1]):
            if(surf.uRng[3]):
                self.u-=surf.uRng[1]-surf.uRng[0]
            else:
                self.u=surf.uRng[1] 
        if(self.v<surf.vRng[0]):
            if(surf.vRng[3]):
                self.v+=surf.vRng[1]-surf.vRng[0]
            else:
                self.v=surf.vRng[0]
        if(self.v>surf.vRng[1]):
            if(surf.vRng[3]):
                self.v-=surf.vRng[1]-surf.vRng[0]
            else:
                self.v=surf.vRng[1] 
        self.drawn.pos=surf.posn(self.u,self.v)+self.rad*surf.normal(self.u,self.v)

    def distToFlag(self):
        return sqrt((self.u - self.surf.flg.u)**2+(self.v - self.surf.flg.v)**2)
        
class flag():
    def __init__(self,surf,u,v,r,h,f):
        self.surf=surf
        self.u=u
        self.v=v
        self.r=r
        self.h=h
        self.f=f
        surf.flg=self
        pos=surf.posn(u,v)
        n=surf.normal(u,v)
        cylinder(pos=pos,axis=h*n,radius=r)
        faces(pos=[pos+n*h,pos+n*(h-f),pos+n*(h-f/2)+f*norm(deriv(lambda k: surf.posn(k,v))(u))],color=color.yellow).make_twosided()
    


def deriv(f):
    h=0.00001
    return lambda x: (f(x+h)-f(x))/h

def createGame(levelnum):
    global baller, won, helparr, myscene
    levels = [
    [lambda u,v: u,lambda u,v: v,lambda u,v: 0,[-5,5,1,False],[-5,5,1,False],0,0,True],
    [lambda u,v: u,lambda u,v: v,lambda u,v: -u**2,[-5,5,1,False],[-5,5,1,False],0,0,True],
    [lambda u,v: v,lambda u,v: u,lambda u,v: (u**2-v**2)/3,[-5,5,1,False],[-5,5,1,False,True],0,0,True],
    [lambda u,v: 5*cos(u) ,lambda u,v:v ,lambda u,v: -sin(u),[0,2*pi,pi/8,True],[-5,5,1,False],0,0,True],
    [lambda u,v: v*cos(u) ,lambda u,v: v*sin(u) ,lambda u,v: 0,[0,2*pi,pi/8,True],[0.1,5,1,False],0,2.5,True],
    [lambda u,v:v*cos(u) ,lambda u,v: v*sin(u) ,lambda u,v: (v-2)**2,[0,2*pi,pi/8,True],[1,3,0.5,False],0,2,True],
    # [lambda u,v:v*cos(pi/4*u) ,lambda u,v:u ,lambda u,v: v*sin(pi/4*u),[-8,8,0.5,False],[-8,8,1,False],0,0,False],
    [lambda u,v:cos(u)*(2+cos(v)) ,lambda u,v: sin(u)*(2+cos(v)) ,lambda u,v: sin(v),[0,2*pi,pi/8,True],[0,2*pi,pi/8,True],0,0,True],
    [lambda u,v: cos(u)*(2+v*cos(u/2)),lambda u,v: sin(u)*(2+v*cos(u/2)),lambda u,v: v*sin(u/2),[0,4*pi,pi/8,True],[-1,1,0.25,False],0,0,True],
    # [lambda u,v: cos(u)*(2+cos(u/2)+0.25*cos(v)),lambda u,v: sin(u)*(2+v*cos(u/2)+0.25*cos(v)),lambda u,v: sin(u/2)+0.25*sin(v),[0,4*pi,pi/8,True],[-1,1,0.25,False],0,0,True],
             []]
    if levelnum == 0:
        scene.title = "Surface Explorer"
        scene.width = 1280
        scene.height = 720
    myscene = display.get_selected()
    if levelnum > 0:
        myscene.delete()
        myscene = display(title="Surface Explorer", width=1280, height=720)
        myscene.title = "Surface Explorer"
        myscene.select()
    if levels[levelnum] == []:
        won = True
        text(text="You Win!",pos=vector(-1,0,0),height=0.4)
        return
    surfer = surface(levels[levelnum][0], levels[levelnum][1], levels[levelnum][2], levels[levelnum][3], levels[levelnum][4], )
    surfer.follow = levels[levelnum][7]
    baller = ball(0.3, surfer, levels[levelnum][5], levels[levelnum][6])
    surfer.placeFlagRandom(0.03,1.5, 0.5)
    # helparr = arrow(pos=(0,0,2))


def main():
    global baller, won, helparr, myscene
    contr = Leap.Controller()
    liste = SampleListener()
    
    levelnumber = 0
    createGame(levelnumber)

    # THE GAME -- YOU HAVE LOST IT

    won = False

    while True:
        rate(30)
        if won == True:
            continue
        # print(liste.on_frame(contr))
        norma = liste.on_frame(contr)
        if len(norma) > 0:
            baller.move(3*-norma[0].x, 3*norma[0].z)
            if baller.surf.follow:
                myscene.center = baller.surf.posn(baller.u, baller.v) + baller.rad*baller.surf.normal(baller.u, baller.v)
                if baller.surf.normal(baller.u, baller.v) != (0,0,0):
                    myscene.forward = -1*baller.surf.normal(baller.u, baller.v)
            # helparr.axis = norm(vector(baller.surf.flg.u - baller.u, baller.surf.flg.v - baller.v, 0))
            # helparr.pos = baller.surf.posn(baller.u, baller.v) + baller.rad*baller.surf.normal(baller.u, baller.v)
            if baller.distToFlag() < baller.rad:
                levelnumber += 1
                createGame(levelnumber)

            # print([norm[0].x, norm[0].y, norm[0].z])


if __name__ == "__main__":
    main()
