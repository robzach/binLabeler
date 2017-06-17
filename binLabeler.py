#!  /home/jakezimmer/anaconda3/envs/py35/bin/python
# coding: utf-8

"""
bin labeler
for Physical Computing lab in IDeATe, Carnegie Mellon University
by Jake Zimmer

v 0.3 6-17-17
    able to generate tags with pygame and save them under the 'Tags' folder
    must close program with ctr-c for now

    important changes:
        fname is now just the file name without an extension
        picName is the picture of the item
        qrName is the qr code
        debug flags added: printErrors, printMessages, showStuff, autoQuit

"""
import pip

pip.main(['install', 'pyscreenshot'])
pip.main(['install', 'pillow'])
pip.main(['install', 'qrcode'])
pip.main(['install', 'pygame'])


import csv
import os.path
from tkinter import *
import pyscreenshot
from PIL import Image, ImageTk
import qrcode
from qrcode.image.pure import PymagingImage
import pygame
from pygame.locals import *
import time


printErrors = True
printMessages = False   #set to true if you want program to print to console
showStuff = False; #for debugging only
makeQR = True;
autoQuit = True #change this if you need to debug

website = 'shrtco.de/'

#these are the tag dimensions in pixels
tagWidth = 400
tagHeight = 200



def generate(fname):
    picName = fname+".jpg"
    if os.path.isfile(picName):
        if printMessages: print (picName + " found")
        if showStuff:
            image = Image.open(picName)
            image.show()

        if makeQR:
            url = website + fname
            qr = qrcode.make(url)
            if printMessages: print ('made qr code pointing to: ' + url)
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=35,
                border=1,
            )
            qr.add_data(url)
            qr.make(fit=True)

            pngout = qr.make_image()
            pngout.save(fname+".png")  #saves a png of the qr code
            if showStuff: pngout.show()

    else:
        if printMessages or printErrors: print (fname + " not found")

def getImage(imgName):
    image = pygame.image.load(imgName)
    image = pygame.transform.scale(image, (tagWidth//4,tagWidth//4))
    return image

def makeTag(window,fname,descriptor):
    qrName = fname+'.png'
    picName = fname+'.jpg'
    #display the qr code
    if os.path.isfile(qrName):
        window.blit(getImage(qrName),
        (tagWidth//(1/0.3)-tagWidth//8,
        tagHeight//(1/0.2)) )
    #display the item picture
    if os.path.isfile(picName):
        window.blit(getImage(picName),
        (tagWidth//(1/0.7)-tagWidth//8,
        tagHeight//(1/0.2)) )
    #display the description
    text = pygame.font.SysFont("arial",24)
    text = text.render(descriptor, True, (0,0,0))
    window.blit(text, (tagWidth//2-text.get_width()//2, tagHeight*0.8))
    #update the screen
    pygame.display.flip()


def run():
    pygame.init()
    window = pygame.display.set_mode((tagWidth,tagHeight))
    window.fill((255,255,255))
    with open('try.csv') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            if printMessages: print (', '.join(row))
            fname = row[0]
            descriptor = row[1]
            generate(fname) #generate qr code
            makeTag(window, fname, descriptor)  #place all the images
            pygame.image.save(window, 'Tags/'+fname+"Tag.jpeg") #save the window
            if printMessages: print("saved Tag " +fname+"Tag.jpeg")
            window.fill((255,255,255))  #clear the window

    while not autoQuit:
        time.sleep(5)

    print("DONE! Labels should be in 'Tags' subfolder")

run()
