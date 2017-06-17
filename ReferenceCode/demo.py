import math
import pygame
from pygame.locals import *
import random
import copy
from PIL import Image
from pygame import Color
import os, os.path


RED = (199, 0, 57)
YELLOW = (255, 195, 0)
WHITE = (255,255,255)
BLACK = (0,0,0)
SUN = (94,89,74)
SHADE = (48,45,38)
#MUSIC Song is from Youtube:
#https://www.youtube.com/watch?v=Ceuny0VVlNE
pygame.mixer.pre_init(44100,16,2,4096)
pygame.init()
pygame.mixer.music.load('music.mp3')
pygame.mixer.music.set_volume(0.02)
pygame.mixer.music.play(-1)

def size(x0,y0,x1,y1): #distance function
    return ((x0-x1)**2+(y0-y1)**2)**0.5

class branch(object):   #main tree making class

    def __init__(self,x0,y0,x1,y1,theta=90,maxL= 50,lv=0, grow=True,flowerC=.9965,cut = False):
        self.x0 = x0
        self.y0 = y0    #starting point
        self.parent = None #if it grows from another branch
        self.x1 = x1
        self.y1 = y1    #end point
        self.theta = theta #angle of branch
        self.maxL = maxL #max growth length
        self.lv = lv    #current 'recursion' level
        self.grow = grow    # if it's growing or not
        self.flowerC = flowerC  #chance for a flower to grow
        self.children = []
        self.length = 0     #current length
        self.fallingSpeed = 0   #used for falling branches
        self.flower = False     #keeps track if the branch has a flower
        self.cut = cut      #determines if the brach was cut or not
        self.width = 1      #this allows for the tree to 'grow' in width
        self.disease = 0

    def newBr(self,data):   #function for initilizing new branches
        if data.wind == -1:
            lowerB = -10
            upperB = 45
        elif data.wind == 1:
            lowerB = -45
            upperB = 10
        else:
            lowerB = -45
            upperB = 45
        angle = random.randint(lowerB,upperB) + self.theta #creates a new angle
        theta = math.pi*(angle)/180
        r = .7*abs(random.random()) #alters the max length
        new = branch(self.x1,self.y1, #actually creates the branch
                                    self.x1+int(math.cos(theta)),
                                    self.y1+int(math.cos(theta)),
                                    angle,self.maxL/(1+r),
                                    self.lv+1)
        new.parent = self           #gives it a parent
        data.branches.append(new)
        self.children.append(new)

    def increase(self,distance,data): #this deals with the growth of branches
        angle = self.theta*math.pi/180
        if self.parent == None:     #changes final pt in relation to tree growth
            self.x1 = math.cos(angle)*self.length+self.x0
            self.y1 = -math.sin(angle)*self.length+self.y0
        else:
            self.x1 = math.cos(angle)*self.length+self.parent.x1
            self.y1 = -math.sin(angle)*self.length+self.parent.y1

        if self.lv <= data.maximum and self.children == []:
            self.grow = True

        if data.treeLength > data.maximumLength:
            if self.lv >= data.maximum-2 and self.flower == False:
                self.flowering(data)

        elif self.grow and (not self.cut): #if growing and hasnt been cut
            self.length += distance
            if self.length > self.maxL:     #its done growing and should split
                if self.lv <= data.maximum and self.children == []: #2nd part prevents extra growth from spliting again
                    self.grow = False
                    counter = random.randint(1,2)   #chooses how many branches
                    while counter >= 0:
                        self.newBr(data)
                        counter -= 1
                else:
                    self.grow = False #if it cant split, set its growth to false
        else:
            if (not self.cut):
                self.stillgrowing(data,distance)

    def stillgrowing(self,data,distance): #final growth after initial finishes
        if self.lv >= data.maximum-2 and self.flower == False:
            self.flowering(data)

        if data.treeLength < data.maximumLength:
            #if size(self.x0,self.y0,self.x1,self.y1) > 2*self.maxL: #final growth done
            self.length += distance*0.25        #increases the length
            angle = self.theta*math.pi/180
            if self.parent == None: #changes final pt in relation to tree growth
                self.x1 = math.cos(angle)*self.length+self.x0
                self.y1 = -math.sin(angle)*self.length+self.y0
            else:
                self.x1 = math.cos(angle)*self.length+self.parent.x1
                self.y1 = -math.sin(angle)*self.length+self.parent.y1

    def flowering(self,data): #creates a flower for the branch
        if len(data.flowers) < data.win:    # if flowers can still be made
            rand = random.random()
            if rand > self.flowerC:
                if data.rgbImage.getpixel((self.x1,self.y1)) == SUN:
                    if data.flowers == []:
                        angle = self.theta*math.pi/180
                        f = flower(self)            # initalizes the flower
                        data.flowers.append(f)      # adds it to the list
                        self.flower = f           # tells the branch it has a flower
                        for star in data.stars:
                            if not star.filled:
                                star.filled = True
                                star.flower = f
                                f.star = star
                                break
                    else:
                        for flow in data.flowers:
                            if size(self.x1,self.y1,flow.parent.x1,flow.parent.y1) > 20:
                                angle = self.theta*math.pi/180
                                f = flower(self)            # initalizes the flower
                                data.flowers.append(f)      # adds it to the list
                                self.flower = f           # tells the branch it has a flower
                                for star in data.stars:
                                    if not star.filled:
                                        star.filled = True
                                        star.flower = f
                                        f.star = star
                                        break
                            break


        else:
            data.winLv = True

    def line(self,data,x = 0): # givves the y from the line(branch)
        slope = (self.y1-self.y0)/(self.x1-self.x0)
        return slope*x - slope*self.x0 - self.y0

class flower(object): #class for flowers

    def __init__(self,stick):
        self.radius = 3
        self.parent = stick
        self.star = None

class Fertile(object):

    def __init__(self,x0,y0,x1,y1):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1

class star(object):

    def __init__(self,maxH,maxW,flower = None):
        self.y = random.randint(maxH//10,maxH//3)
        self.x = random.randint(maxW//10,9*maxW//10)
        self.filled = False
        self.flower = flower

class leaf(object):

    def __init__(self,wind):
        self.wind = wind
        if self.wind == -1:
            self.x = random.randint(800,800+100)
        else:
            self.x = random.randint(-100,0)
        self.y = random.randint(0,800)
        self.speed = random.random()*3*self.wind+self.wind

#This next part is for finding line intercept positions

def slope(p1,p2): #gets the slope given two points
    x0,y0 = p1[0],p1[1]
    x1,y1 = p2[0],p2[1]
    if x0 != x1:
        m = (y1-y0)/(x1-x0)
        return m
    return None

def intersectAxis(p,m): #finds the y intercept
    return p[1] - m*p[0]

def getPoint(p1,p2,p3,p4): #gets the actual point
    m1 = slope(p1,p2)
    m2 = slope(p3,p4)
    if m1 == m2:            # get rid of parallel lines
        return False

    elif m1 == None:        # one line is vertical
        b = intersectAxis(p3, m2)

        x = p1[0]
        y = (m2 * x) + b

    elif m2 == None:        # other line is vertical
        b = intersectAxis(p1, m1)
        x = p3[0]
        y = (m1 * x) + b

    else:                   # both lines non vertical
        b1 = intersectAxis(p1, m1)
        b2 = intersectAxis(p3, m2)
        x = (b1 - b2)/(m2 - m1)
        y = m1 * x + b1

    return (x,y)

#Intersection finding Done

def findLofChild(data,branch,l = 0): #Will tell how much to grow the tree
    l += branch.length
    for child in branch.children:
        l += findLofChild(data,child,l) #recursive call
    return l

def cut(data):  #cuts branches and mkaes them fall
    branches = copy.copy(data.branches)    # prevents looping over modified list
    for stick in branches:
        for i in range(len(data.points)-1): #checks each line with each branch
            p1 = data.points[i]
            p2 = data.points[i+1]
            p3 = (stick.x0,stick.y0)
            p4 = (stick.x1,stick.y1)
            if getPoint(p1,p2,p3,p4) != False:
                intX,intY = getPoint(p1,p2,p3,p4) #all the possibilities in X
                if ((p1[0] <= intX <= p2[0] and p3[0] <= intX <= p4[0]) or
                    (p1[0] >= intX >= p2[0] and p3[0] >= intX >= p4[0]) or
                    (p1[0] <= intX <= p2[0] and p3[0] >= intX >= p4[0]) or
                    (p1[0] >= intX >= p2[0] and p3[0] <= intX <= p4[0])):
                    #all the possibilities in Y
                    if ((p1[1] <= intY <= p2[1] and p3[1] <= intY <= p4[1]) or
                        (p1[1] >= intY >= p2[1] and p3[1] >= intY >= p4[1]) or
                        (p1[1] <= intY <= p2[1] and p3[1] >= intY >= p4[1]) or
                        (p1[1] >= intY >= p2[1] and p3[1] <= intY <= p4[1])):

                        if stick in data.branches:#branch hasnt already been cut
                            if data.counter < 3:
                                L = findLofChild(data,stick)
                                data.treeLength -= L
                                data.cutLength += L
                            if data.cutLength > data.maximumLength//10 and data.counter < 3:
                                data.cutLength = 0
                                data.maximum += 1
                                data.counter += 1
                            #increases max size of tree based on branch lv

                            newB = branch(stick.x0,stick.y0,intX,intY,
                                         stick.theta,stick.maxL,stick.lv,True,stick.flower,
                                         True)
                            newFall = branch(intX,intY,stick.x1,stick.y1)
                            #ceates two new branches

                            newFall.width = stick.width

                            data.falling.append(newFall)
                            for child in stick.children:   #gets rid of children
                                if child not in data.branches:
                                    continue
                                remove(data,child)

                            if stick.flower != False and intX != None:
                                if intX < stick.x1:
                                    stick.flower.parent = newB
                                    newB.flower = stick.flower
                                else:
                                    stick.flower.parent = newFall
                                    newFall.flower = stick.flower
                            #places flowers on the corect new branch

                            newB.length = size(newB.x0,newB.y0,intX,intY)
                            newB.parent = stick.parent
                            newB.width = stick.width
                            if newB.parent != None:
                                newB.parent.children.append(newB)

                            data.branches.append(newB)
                            data.branches.remove(stick)

    for remaining in data.branches:
        if data.increase == 0:
            break
        remaining.maxL += data.increase
        remaining.grow = True
    data.increase = 0
                            #(self,x0,y0,x1,y1,theta=90,maxL= 50,lv=0, grow=True,flowerC=.9995,cut = False)

def remove(data, branch): #removes branch and its children
    if branch.children == []:
        data.branches.remove(branch)
        data.falling.append(branch)
    else:
        for child in branch.children:
            if child in data.branches:
                remove(data,child)      #recursive call
        data.branches.remove(branch)
        data.falling.append(branch)

def startingLocal(data,x,y):
    if data.fertile[0].x0 > x or x > data.fertile[0].x1:
        pass
    else:
        if data.start == -1:
            data.start = x

        data.endStart = x
        data.startY = y

def startTree(data):
    if not data.isDead:
        pass
    if data.startTheta > 120:
        data.startTheta = 120
    elif data.startTheta < 60:
        data.startTheta = 60
    if data.fertile[0].x0-1 < data.start < data.fertile[0].x1+1:
        new = branch(data.start,data.fertile[0].y0,data.endStart,data.startH,data.startTheta)
        data.branches.append(new)
        data.isDead = False
        data.inRangeF = False

def getPOS(data):
    if data.start > data.endStart:
        x1,y0 = max(data.endStart, data.start-25),data.fertile[0].y0
        x0,y1 = data.start, max(data.fertile[0].y1,data.startY)
        opp = y1-y0
        adj = x1-x0

        if adj == 0:
            data.startTheta = 90
        else:
            data.startTheta = 90 - (math.atan(opp/adj)*180/math.pi) + 90
    else:
        x1,y0 = min(data.endStart,data.start+25),data.fertile[0].y0
        x0,y1 = data.start, max(data.fertile[0].y1,data.startY)
        opp = y1-y0
        adj = x0-x1

        if adj == 0:
            data.startTheta = 90
        else:
            data.startTheta = math.atan(opp/adj)*180/math.pi

    data.startH = y1
    return x0,y0,x1,y1

def spreadDisease(data,branch):
    if branch.disease > 0.5:
        for child in branch.children:
            child.disease  = min(1,child.disease+0.01)
        if branch.parent != None:
            parent = branch.parent
            parent.disease = min(1,parent.disease+.01*branch.disease)

def createStars(data):
    l = []
    for i in range(data.win):
        l.append(star(data.height,data.width))
    return l

def resetLV(data):
    if data.start != -1 and data.isDead:
        if data.branches != []:
            remove(data,data.branches[0])
        data.maximum = data.originalMax
        data.treeLength = 0
        data.cutLength = 0
        data.counterB = 0
        startTree(data)
    if data.points != []:
        cut(data)
        data.points = []

def findStart(data):
    start = False
    for y in range(data.height//4,data.height):
        for x in range(data.width):
            if start == False and data.rgbImage.getpixel((x,y)) == (1,1,1):
                start = True
                Y0 = y
                X0 = x
            elif data.rgbImage.getpixel((x,y)) != (1,1,1) and start == True:
                start = 'Done'
                X1 = x
                Y1 = y
    return Fertile(X0,Y0,X1,Y0-50)

def moveStart(data,x,y):
    data.drawStuff[-1] = (['start',x,y,x+200,y+25])

def makeShadow(data):
    func = data.drawStuff[-1][0]
    dat = data.drawStuff[-1][1:]
    length = 800
    theta = math.pi*(data.drawAngle)/180
    if func == 'circ':
        x,y,color,rad = dat
        x0,y0 = x-rad*math.cos(theta+math.pi/2),y+rad*math.sin(theta+math.pi/2)
        x1,y1 = x+rad*math.cos(theta+math.pi/2),y-rad*math.sin(theta+math.pi/2)
        x2,y2 = x1-length*math.cos(theta),y1+length*math.sin(theta)
        x3,y3 = x0-length*math.cos(theta),y0+length*math.sin(theta)
        data.shadows.append([(x0,y0),(x1,y1),(x2,y2),(x3,y3)])

    if func == 'start':
        x0,y0,x1,y1 = dat
        x2,y2 = x1-length*math.cos(theta),y1+length*math.sin(theta)
        x3,y3 = x0-length*math.cos(theta),y0+length*math.sin(theta)
        data.shadows.append([(x0,y0),(x1,y1),(x2,y2),(x3,y3)])

    if func == 'free':
        length = 1600
        new = []
        l = 1
        dat = dat[:-1]
        while l < length:
            new = []
            for (x,y) in dat:
                x1,y1 = x-l*math.cos(theta),y+l*math.sin(theta)
                new.append((x1,y1))
            l += 1
            data.shadows.append(new)

def findLevels(data):
    count = 0
    path = 'Levels'
    for filename in os.listdir(path):
        count += 1
    return count

def applyWind(data):
    if data.branches != []:
        if data.newAngle == -1:
            if data.wind == 1:
                r = random.randint(-15,0)
            else:
                r = random.randint(0,15)
            data.newAngle = data.startTheta + r

        if data.windApplied:
            if int(data.branches[0].theta) == data.newAngle:
                data.windApplied = False
            else:
                diff = data.newAngle-data.branches[0].theta
                if diff > 0:
                    data.branches[0].theta += 0.1
                else:
                    data.branches[0].theta -= 0.1
        else:
            if int(data.branches[0].theta) == data.startTheta:
                data.windApplied = True
                if data.wind == 1:
                    r = random.randint(-15,5)
                else:
                    r = random.randint(-5,15)
                data.newAngle = data.startTheta + r
            else:
                diff = data.branches[0].theta - data.startTheta
                if diff > 0:
                    data.branches[0].theta -= 0.1
                else:
                    data.branches[0].theta += 0.1

def createLeafs(data):
    l = []
    for i in range(20):
        l.append(leaf(data.wind))
    return l


################################################################################
                                #Draw functions#
################################################################################
def drawFertile(data,screen):
    for fertile in data.fertile:
        x0,y0 = fertile.x0,fertile.y0
        x1,y1 = fertile.x1,fertile.y1
        pygame.draw.rect(screen,(SHADE[0]+25,SHADE[1]+25,SHADE[2]+25),(x0,y0,x1-x0,y1-y0))

    if data.start != -1:
        x0,y0,x1,y1 = getPOS(data)
        pygame.draw.line(screen,BLACK,(x0,y0),(x1,y1),5)

def drawStars(data,screen):
    for star in data.stars:
        x0,y0 = star.x-10,star.y
        x1,y1 = star.x,star.y+10
        x2,y2 = star.x+10,star.y
        x3,y3 = star.x,star.y-10
        if star.filled:
            width = 0
        else:
            width = 2
        points = [(x0,y0),(x1,y1),(x2,y2),(x3,y3)]

        pygame.draw.polygon(screen,WHITE,points,width)

def drawFallingBranches(data,screen):
    for branch in data.falling:
        x0,y0 = branch.x0,branch.y0
        x1,y1 = branch.x1,branch.y1

        R1 = int(BLACK[0]+(RED[0]-BLACK[0])*branch.disease)
        G1 = int(BLACK[1]+(RED[1]-BLACK[1])*branch.disease)
        B1 = int(BLACK[2]+(RED[2]-BLACK[2])*branch.disease)

        R = min(int(R1+branch.fallingSpeed*(WHITE[0] - R1)/data.maxSpeed),255)
        G = min(int(G1+branch.fallingSpeed*(WHITE[1] - G1)/data.maxSpeed),255)
        B = min(int(B1+branch.fallingSpeed*(WHITE[2] - B1)/data.maxSpeed),255)

        #width = int((data.maximum-branch.lv)*1.25)+1
        pygame.draw.line(screen, (R,G,B),(x0,y0), (x1,y1),int(branch.width))

def drawBranches(data,screen):
    for arm in data.branches:
        if not arm.grow:
            pass
        x0,y0 = arm.x0,arm.y0
        x1,y1 = arm.x1,arm.y1
        #width = int((data.maximum-arm.lv)*1.25)+2
        R = int(BLACK[0]+arm.disease*(RED[0]-BLACK[0]))
        G = int(BLACK[1]+arm.disease*(RED[1]-BLACK[1]))
        B = int(BLACK[2]+arm.disease*(RED[2]-BLACK[2]))
        pygame.draw.line(screen,(R,G,B),(x0,y0), (x1,y1),int(arm.width))

def drawFlowers(data,screen):
    for flower in data.flowers:
        pygame.draw.circle(screen, (WHITE),
                           (int(flower.parent.x1),int(flower.parent.y1)),
                           flower.radius)

    for flower in data.fallingFlower:
        pygame.draw.circle(screen, (WHITE),
                          (int(flower.parent.x1),int(flower.parent.y1)),
                          flower.radius)

def drawCutter(data,screen):
    if len(data.points) > 1:
        pygame.draw.lines(screen,(BLACK),0,data.points,7)
        pygame.draw.lines(screen,(WHITE),0,data.points,5)

def drawMenu(data,screen):
    myfont = pygame.font.SysFont("monospace", 75)
    x,y = data.nameX,data.nameY
    R = int(BLACK[0]+len(data.flowers)*(WHITE[0]-BLACK[0])//data.win)
    G = int(BLACK[1]+len(data.flowers)*(WHITE[1]-BLACK[1])//data.win)
    B = int(BLACK[2]+len(data.flowers)*(WHITE[2]-BLACK[2])//data.win)
    text = myfont.render("Pruned", 0, (R,G,B))
    text_rect = text.get_rect(center = (x, y))
    screen.blit(text, text_rect)

    w,h = data.w,data.h
    x,y = data.startX-w/2,data.startY-h/2
    pygame.draw.rect(screen,BLACK,(x,y,w,h))
    pygame.draw.rect(screen,RED,(x+5,y+5,w-10,h-10))
    myfont = pygame.font.SysFont("monospace", 25)
    myfont.set_italic(1)
    text = myfont.render("Start", 0, (R,G,B))
    text_rect = text.get_rect(center = (data.startX,data.startY))
    screen.blit(text, text_rect)

    x,y = data.startX-w/2,data.startY-h/2+data.height//8
    pygame.draw.rect(screen,BLACK,(x,y,w,h))
    pygame.draw.rect(screen,RED,(x+5,y+5,w-10,h-10))
    text = myfont.render("Help", 0, (R,G,B))
    text_rect = text.get_rect(center = (data.startX,data.startY+data.height//8))
    screen.blit(text, text_rect)

    x,y = data.startX-w/2,data.startY-h/2+data.height//4
    pygame.draw.rect(screen,BLACK,(x,y,w,h))
    pygame.draw.rect(screen,RED,(x+5,y+5,w-10,h-10))
    text = myfont.render("Editor", 0, (R,G,B))
    text_rect = text.get_rect(center = (data.startX,data.startY+data.height//4))
    screen.blit(text, text_rect)

    x,y = data.startX-w/2,data.startY-h/2+3*data.height//8
    pygame.draw.rect(screen,BLACK,(x,y,w,h))
    pygame.draw.rect(screen,RED,(x+5,y+5,w-10,h-10))
    text = myfont.render("Levels", 0, (R,G,B))
    text_rect = text.get_rect(center = (data.startX,data.startY+3*data.height//8))
    screen.blit(text, text_rect)

def drawHelp(data,screen):
    x,y = data.width/2-data.w/2,10
    pygame.draw.rect(screen,BLACK,(x,y,data.w,data.h))
    pygame.draw.rect(screen,RED,(x+5,y+5,data.w-10,data.h-10))
    myfont = pygame.font.SysFont("monospace", 30)
    myfont.set_italic(1)
    text = myfont.render("Menu", 0, (BLACK))
    text_rect = text.get_rect(center = (data.width//2,y+data.h/2))
    screen.blit(text, text_rect)

def drawNext(data,screen):
    pygame.draw.circle(screen,WHITE,(data.width//2,data.height//2), 100,5)
    arrow = [(data.width//2-100//3,data.height//2+100//2),
             (data.width//2+100//3,data.height//2),
             (data.width//2-100//3,data.height//2-100//2),]
    pygame.draw.lines(screen,WHITE,0,arrow,5)

def drawOptions(data,screen):
    if data.dColor == RED:
        color = BLACK
    else:
        color = WHITE
    pygame.draw.rect(screen,color,(0,0,215,255))
    pygame.draw.rect(screen,data.dColor,(5,5,205,245))
    pygame.draw.line(screen,color,(215//2,0),(215//2,50),5)
    pygame.draw.rect(screen,RED,(5,5,200/2,45))
    pygame.draw.rect(screen,BLACK,(220//2,5,200/2,45))
    myfont = pygame.font.SysFont("monospace", 30)
    myfont.set_italic(1)
    words = ['Starting','Circle',"FreeDraw",'Angle: %d'%data.drawAngle]
    for i in range(1,5):
        pygame.draw.line(screen,color,(0,i*50),(210,i*50),5)
        if i-1 < len(words):
            text = myfont.render(words[i-1], 0, (color))
            text_rect = text.get_rect(center = (210//2,i*50+50//2))
            screen.blit(text, text_rect)

def drawMap(data,screen):
    for l in data.drawStuff:
        if l != []:
            func = l[0]
            dat = l[1:]
            if func == 'circ':
                x,y,color,rad = dat
                pygame.draw.circle(screen,color,(x,y),rad)
            elif func == 'free':
                color = dat[-1]
                points = dat[:-1]
                if len(points) > 2:
                    pygame.draw.polygon(screen,color,points)
            elif func == 'start':
                x0,y0,x1,y1 = dat
                w = x1-x0
                h = y1-y0
                if w != 0 and h != 0:
                    pygame.draw.rect(screen,BLACK,(x0,y0,w,h))
                    pygame.draw.line(screen,(1,1,1),(x0,y0-1),(x1,y0-1),1)

def drawShadows(data,screen):
    if data.shadows == []:
        for thing in data.drawStuff:
            func = thing[0]
            dat = thing[1:]
            length = 1000
            theta = math.pi*(data.drawAngle)/180
            if func == 'circ':
                x,y,color,rad = dat
                x0,y0 = x-rad*math.cos(theta+math.pi/2),y+rad*math.sin(theta+math.pi/2)
                x1,y1 = x+rad*math.cos(theta+math.pi/2),y-rad*math.sin(theta+math.pi/2)
                x2,y2 = x1-length*math.cos(theta),y1+length*math.sin(theta)
                x3,y3 = x0-length*math.cos(theta),y0+length*math.sin(theta)
                data.shadows.append([(x0,y0),(x1,y1),(x2,y2),(x3,y3)])

            if func == 'start':
                x0,y0,x1,y1 = dat
                x2,y2 = x1-length*math.cos(theta),y1+length*math.sin(theta)
                x3,y3 = x0-length*math.cos(theta),y0+length*math.sin(theta)
                data.shadows.append([(x0,y0),(x1,y1),(x2,y2),(x3,y3)])

            if func == 'free':
                new = []
                l = 1
                dat = dat[:-1]
                while l < length:
                    new = []
                    for (x,y) in dat:
                        x1,y1 = x-l*math.cos(theta),y+l*math.sin(theta)
                        new.append((x1,y1))
                    l += 1
                    data.shadows.append(new)
    for shadow in data.shadows:
        if len(shadow) > 2:
            pygame.draw.polygon(screen,SHADE,shadow)

def drawWin(data,screen):
    myfont = pygame.font.SysFont("monospace", 60)
    myfont.set_italic(1)
    words = 'All Levels Complete'
    text = myfont.render(words, 0, BLACK)
    text_rect = text.get_rect(center = (data.width//2,data.height//2))
    screen.blit(text, text_rect)

def drawLevels(data,screen):
    count = 0
    path = 'Levels'
    for filename in os.listdir(path):
        X = 50*((count)%5+1) + 100*((count)%5)
        Y = 200+50*((count)//5)+100*(count//5)
        level = pygame.image.load(path +'/'+ filename)
        pygame.draw.rect(screen,BLACK,(X-5, Y-5,110,110))
        level = pygame.transform.scale(level, (100, 100))
        screen.blit(level, (X, Y))
        count += 1

def drawLeaf(data,screen):
    if data.wind != 0 and data.leafs != []:
        for leaf in data.leafs:
            pygame.draw.circle(screen,(	78, 63, 64), (int(leaf.x),int(leaf.y)),5)

################################################################################
                            #Mouse Pressed#
################################################################################

def mouseStart(data,x,y):
    if  data.startX-data.w/2 < x < data.startX+data.w:
        if data.startY-data.h/2 < y < data.startY + data.h:
            data.splash = False
            data.branches, data.flowers = [],[]
            data.stars = createStars(data)
            data.isDead = True
            data.start = -1
            data.inRangeF = True
            data.wind = random.randint(-1,1)
            if data.wind != 0:
                data.leafs = createLeafs(data)

        elif data.startY-data.h/2+data.height//8 < y < data.startY+data.h+data.height//8:
            data.splash = 'help'
            data.branches, data.flowers = [],[]
            data.stars = createStars(data)
            data.stars[0].filled = True
            data.stars[1].filled = True
            data.stars[2].filled = True
            data.isDead = True
            data.start = -1
            data.inRangeF = True

        elif data.startY-data.h/2+data.height//4 < y < data.startY + data.h+data.height//4:
            if data.numLevs < 15:
                data.splash = 'preEdit'

        elif data.startY-data.h/2+3*data.height//8 < y < data.startY + data.h+3*data.height//8:
            data.splash = 'levels'

def mouseEdit(data,x,y):
    if not data.drawing:
        if data.width/2-data.w/2 < x < data.width/2+data.w:
            if  10 < y < 10 + data.h:
                init(data)
        elif 0 < x < 200:
            if y < 50:
                if x < 125:
                    data.dColor = RED
                else:
                    data.dColor = BLACK
            elif 50 < y < 100:
                data.hasStart = False
                for elem in data.drawStuff:
                    if elem[0] == 'start':
                        data.hasStart = True
                        break
                if not data.hasStart:
                    data.drawing = 'start'
                    data.drawStuff.append([])
                    data.redoStuff = []
            elif 100 < y < 150:
                data.drawing = 'circ'
                data.drawStuff.append([])
                data.redoStuff = []
            elif 150 < y < 200:
                data.drawing = 'free'
                data.drawStuff.append(['free',data.dColor])
                data.redoStuff = []
    elif data.drawing == 'start':
        data.drawing = False

def mouseLev(data,x,y):
    if data.width/2-data.w/2 < x < data.width/2+data.w:
        if  10 < y < 10 + data.h:
            data.splash = 'start'
    levs = []
    path = 'Levels'
    for filename in os.listdir(path):
        levs.append(filename)

    for i in range(1,16):
        X = 50*(i%6) + 100*((i-1)%5)
        Y = 200+50*((i-1)//6)+100*(i//6)
        path = "%d.png" %data.currentLv
        if X < x < X+100:
            if Y < y < Y+100:
                if path in levs:
                    init(data)
                    data.currentLv = i-1
                    imageInit(data)
                    data.fertile = [findStart(data)]
                    data.splash = False
                    data.branches, data.flowers = [],[]
                    data.stars = createStars(data)
                    data.isDead = True
                    data.start = -1
                    data.inRangeF = True
                    data.wind = random.randint(-1,1)
                    break

def mouseWin(data,x,y):
    if size(x,y,data.width//2,data.height//2) < 100:
        data.currentLv += 1
        string = "Levels/%d.png" %data.currentLv
        try:
            image = Image.open(string)
            data.image = pygame.image.load(string)
            data.rgbImage = image.convert('RGB')
            data.branches,data.flowers,data.stars = [],[],createStars(data)
            data.cutLength = 0
            data.maximum = data.originalMax
            data.fertile = [findStart(data)]
            data.wind = random.randint(-1,1)
            if data.wind != 0:
                data.leafs = createLeafs(data)
        except:
            init(data)
            data.splash = 'win'
################################################################################
                        #Timer Fired functions#
################################################################################

def timerStart(data):
    for branch in data.branches:
        if (branch.x0 < 0 or branch.x0 > data.width or
            branch.x1 < 0 or branch.x1 > data.width or
            branch.y0 < 0 or branch.y0 > data.height or
            branch.y1 < 0 or branch.y1 > data.height):
            remove(data,branch)

    for arm in data.branches:
        if arm.width < int((data.maximum-arm.lv)*1.25)+2:
            arm.width += 0.1
        if arm.parent != None:
            arm.x0 = arm.parent.x1
            arm.y0 = arm.parent.y1
        arm.increase(data.growth,data)

def gameTimer(data):
    test = False
    for branch in data.branches:
        if not branch.cut:
            if branch.children != []:
                continue
            data.isDead = False
            test = True
            break
    if test == False and len(data.branches) != 0 and not data.isDead:
        data.isDead = True
        data.inRangeF = True
        data.start = -1

    data.treeLength = 0
    diseased = True
    for branch in data.branches:
        data.treeLength += branch.length
        if branch.disease < 1:
            diseased = False

    if diseased and not data.isDead:
        data.isDead = True
        data.inRangeF = True
        data.start = -1
        data.maximum = data.originalMax
        data.treeLength = 0
        data.cutLength = 0
        data.counterB = 0

    for arm in data.branches:
        if arm.width < int((data.maximum-arm.lv)*1.25)+2:
            arm.width += 0.1
        if arm.parent != None:
            arm.x0 = arm.parent.x1
            arm.y0 = arm.parent.y1
        arm.increase(data.growth,data)

def AlwaysTimer(data):
    if len(data.points) > 50:
        data.points.pop(0)

    if len(data.flowers) < data.win:
        data.winLv = False

    if data.wind != 0:
        applyWind(data)
        for mleaf in data.leafs:
            mleaf.x += mleaf.speed
            mleaf.y += random.random()*2
            if mleaf.x < 0 or mleaf.x > data.width:
                data.leafs.remove(mleaf)
                data.leafs.append(leaf(data.wind))

    for arm in data.branches:
        angle = arm.theta*math.pi/180
        if arm.parent == None:
            arm.x1 = math.cos(angle)*arm.length+arm.x0
            arm.y1 = -math.sin(angle)*arm.length+arm.y0
        else:
            arm.x0 = arm.parent.x1
            arm.y0 = arm.parent.y1
            arm.x1 = math.cos(angle)*arm.length+arm.x0
            arm.y1 = -math.sin(angle)*arm.length+arm.y0


    for branch in data.falling:
        if branch.fallingSpeed < data.maxSpeed:

            branch.fallingSpeed += 0.05
        branch.y0 += branch.fallingSpeed
        branch.y1 += branch.fallingSpeed
        if (branch.y0 and branch.y1) > data.height:
            data.falling.remove(branch)

    for flower in data.flowers:
        if flower.parent in data.falling and flower in data.flowers:
            if flower.star != None:
                flower.star.filled = False
                flower.star.flower = None
            data.fallingFlower.append(flower)
            data.flowers.remove(flower)
        if flower.parent.disease > 0.5:
            if flower.star != None:
                flower.star.filled = False
                flower.star.flower = None
            if flower in data.flowers:
                data.flowers.remove(flower)

    for branch in data.branches:
        if data.splash == False:
            if (branch.x0 < 0 or branch.x0 > data.width or
                branch.x1 < 0 or branch.x1 > data.width or
                branch.y0 < 0 or branch.y0 > data.height or
                branch.y1 < 0 or branch.y1 > data.height):
                remove(data,branch)
            elif (data.rgbImage.getpixel((branch.x0,branch.y0)) == BLACK or
                  data.rgbImage.getpixel((int(branch.x1),int(branch.y1))) == BLACK):
                  remove(data,branch)
            else:
                if (data.rgbImage.getpixel((branch.x0,branch.y0)) == RED or
                    data.rgbImage.getpixel((int(branch.x1),int(branch.y1))) == RED):
                    if branch.disease < 1:
                        branch.disease += 0.01
                        spreadDisease(data,branch)
                if branch.disease > 0.25:
                    if branch.disease < 1:
                        branch.disease += 0.01
                    spreadDisease(data,branch)

    for flower in data.fallingFlower:
        if flower.parent.y1 > data.height-10:
            data.fallingFlower.remove(flower)

##(structure derived from eventsexample.py and Lukas Perana's pygame structure)

def init(data):
    data.currentLv = 0
    data.width = 800
    data.height = 800
    data.splash = 'start'
    data.fps = 45
    data.playing = True
    data.falling = []
    data.flowers = []
    data.points = []
    data.maxSpeed = 15
    data.increase = 0
    data.isDead = False
    data.inRangeF = False
    data.wind = random.randint(-1,1)
    data.windApplied = False
    data.newAngle = -1
    data.numLevs = findLevels(data)

    data.done = False
    data.drawing = False
    data.startedD = False
    data.drawAngle = 45
    data.lastDraw = None
    data.dColor = BLACK
    data.drawStuff = []
    data.redoStuff = []
    data.hasStart = False
    data.shadows = []
    data.preview = False

    imageInit(data)

    #From level Data
    data.branches = [branch(data.width//4,data.height-2,data.width//4,data.height-2,90,60)]
    data.maximumLength = 7500
    data.maximum = 5
    data.win = 30
    data.growth = 0.5
    data.fertile = [findStart(data)]

    data.start = -1
    data.endStart = -1
    data.startY = -1
    data.startTheta = 90
    data.startH = -1
    data.originalMax = data.maximum
    data.treeLength = 0
    data.cutLength = 0
    data.counter = 0
    data.winLv = False
    data.fallingFlower = []
    data.stars = createStars(data)
    if data.wind != 0:
        data.leafs = createLeafs(data)
    menuInit(data)
    #passing = True

def imageInit(data):
    imagePath = "Levels/%d.png" %data.currentLv
    image = Image.open(imagePath)
    data.image = pygame.image.load(imagePath)
    data.rgbImage = image.convert('RGB')

def menuInit(data):
    x = 3*data.width//4
    data.nameX,data.nameY = x,data.height//6
    data.startX,data.startY = x,data.height//3
    data.helpY = data.height//2
    data.w,data.h = data.width//6,data.height//16

def redrawAll(data, screen):

    if data.inRangeF:
        drawFertile(data,screen)

    drawStars(data,screen)

    drawLeaf(data,screen)

    drawFallingBranches(data,screen)

    drawBranches(data,screen)

    drawFlowers(data,screen)

    drawCutter(data,screen)

    drawHelp(data,screen)

    if data.winLv:
        drawNext(data,screen)

def timerFired(data):
    if data.winLv:
        pass
    elif data.splash != False:
        timerStart(data)
    elif not data.winLv and not data.isDead:
        gameTimer(data)
    AlwaysTimer(data)

def mousePressed(data, x, y):
    if data.splash != False:
        if data.splash == 'start':
            mouseStart(data,x,y)

        elif data.splash == 'edit' and (not data.done):
            mouseEdit(data,x,y)

        elif data.splash == 'help':
            if data.width/2-data.w/2 < x < data.width/2+data.w:
                if  10 < y < 10 + data.h:
                    init(data)

        elif data.splash == 'preEdit':
            data.splash = 'edit'

        elif data.splash == 'win':
            if data.width/2-data.w/2 < x < data.width/2+data.w:
                if  10 < y < 10 + data.h:
                    init(data)

        elif data.splash == 'levels':
            mouseLev(data,x,y)

    else:
        if data.width/2-data.w/2 < x < data.width/2+data.w:
            if  10 < y < 10 + data.h:
                init(data)

        if data.winLv:
            mouseWin(data,x,y)

def mouseDrag(data,x,y):
    if data.splash == False:
        data.points.append((x,y))
    elif data.splash == 'edit' and (data.drawing == 'free'):
        data.startedD = True
        data.drawStuff[-1].pop()
        data.drawStuff[-1].append((x,y))
        data.drawStuff[-1].append(data.dColor)

    elif data.splash == 'edit' and data.drawing == 'circ':
        if data.startedD:
            func,x0,y0,color,rad = data.drawStuff[-1]
            rad = max(abs(x-x0),abs(y-y0))
            data.drawStuff[-1] = ['circ',x0,y0,color,rad]
        else:
             data.startedD = True
             data.drawStuff[-1] = ['circ',x,y,data.dColor,1]

def keyPressed(screen, data, key):
    if data.splash == 'edit':
        if key == pygame.K_p:
            if data.preview:
                data.preview = False
                data.shadows = []
            else:
                data.preview = True
        if key == pygame.K_h:
            data.splash = 'preEdit'

        if key == pygame.K_UP and data.drawAngle < 135:
            data.drawAngle += 1
        elif key == pygame.K_DOWN and data.drawAngle > 45:
            data.drawAngle -= 1

        if len(data.drawStuff) > 0:
            if key == pygame.K_u:
                data.redoStuff.append(data.drawStuff.pop())

        if len(data.redoStuff) > 0:
            if key == pygame.K_r:
                data.drawStuff.append(data.redoStuff.pop())

        data.hasStart = False
        for elem in data.drawStuff:
            if elem[0] == 'start':
                data.hasStart = True
                break

        if key == pygame.K_d and data.hasStart:
            data.done = True

##########

def redrawAllSplash(data, screen):
    if data.splash == 'start':
        drawLeaf(data,screen)
        drawBranches(data,screen)
        drawFlowers(data,screen)
        drawMenu(data,screen)
    elif data.splash == 'help':
        redrawAllHelp(data,screen)
    elif data.splash == 'edit':
        redrawAllEdit(data,screen)
    elif data.splash == 'levels':
        redrawAllLevels(data,screen)
    elif data.splash == 'win':
        redrawAllWin(data,screen)

def redrawAllHelp(data,screen):
    drawStars(data,screen)
    drawHelp(data,screen)

def redrawAllEdit(data,screen):
    drawMap(data,screen)
    if (not data.done):
        if not data.preview:
            drawHelp(data,screen)
            if not data.drawing:
                drawOptions(data,screen)
        else:
            drawShadows(data,screen)
            drawMap(data,screen)
    else:
        drawShadows(data,screen)
        drawMap(data,screen)
        pygame.image.save(screen,"Levels/%d.png" %data.numLevs)
        init(data)

def redrawAllWin(data,screen):
    drawHelp(data,screen)
    drawWin(data,screen)

def redrawAllLevels(data,screen):
    drawHelp(data,screen)
    drawLevels(data,screen)
    myfont = pygame.font.SysFont("monospace", 30)
    myfont.set_italic(1)
    words = 'Click on Level to Load, May Take a Second'
    text = myfont.render(words, 0, BLACK)
    text_rect = text.get_rect(center = (data.width//2,data.height-50))
    screen.blit(text, text_rect)

def keyPressedSplash(data, key):
    pass

def run():
    class Struct(object): pass
    data = Struct()
    init(data)
    pygame.init()
    clock = pygame.time.Clock()

    screen = pygame.display.set_mode((data.width, data.height))

    while data.playing:
        time = clock.tick(data.fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                data.playing = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mousePressed(data, *event.pos)
            elif (event.type == pygame.MOUSEMOTION and event.buttons[0] == 1):
                if data.inRangeF:
                    startingLocal(data,*event.pos)
                else:
                    mouseDrag(data, *event.pos)
            elif (event.type == pygame.MOUSEMOTION and event.buttons[0] != 1):
                if data.drawing != False:
                    if data.startedD:
                        data.drawing = False
                        data.startedD = False
                    elif data.drawing == 'start':
                        moveStart(data,*event.pos)
                else:
                    resetLV(data)

            elif event.type == pygame.KEYDOWN:
                keyPressed(screen, data, event.key)
        if data.splash != False:
            screen.fill(SUN)
            if data.splash == 'help':
                helpLV = pygame.image.load("HelpScreen.png")
                screen.blit(helpLV, (0, 0))
            elif data.splash == 'preEdit':
                preEdit = pygame.image.load("PreEdit.png")
                screen.blit(preEdit, (0, 0))
            redrawAllSplash(data,screen)
        else:
            screen.blit(data.image, (0, 0))
            redrawAll(data, screen)
        timerFired(data)
        pygame.display.flip()
    pygame.quit()

run()
