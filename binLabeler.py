#!  /home/jakezimmer/anaconda3/envs/py35/bin/python
# coding: utf-8

import pip

pip.main(['install', 'pyscreenshot'])
pip.main(['install', 'pillow'])
pip.main(['install', 'qrcode'])

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




showImage = True;
makeQR = True;



tagWidth = 400
tagHeight = 200




def generate(fname):
    imgName = fname+".jpg"
    if os.path.isfile(imgName):
        print (imgName + " found")
        if showImage:
            image = Image.open(imgName)
            #image.show()
            pass;
        if makeQR:
            url = 'shrtco.de/' + fname
            qr = qrcode.make(url)
            print ('made qr code pointing to: ' + url)
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=35,
                border=1,
            )
            qr.add_data(url)
            qr.make(fit=True)

            pngout = qr.make_image()
            pngout.save(fname[:-4]+".png")
            #pngout.show()
    else:
        print (fname + " not found")

def getImage(imgName):
    image = pygame.image.load(imgName)
    image = pygame.transform.scale(image, (tagWidth//4,tagWidth//4))
    return image

def makeTag(window,fname):
    qrName = fname+'.png'
    picName = fname+'.jpg'
    if os.path.isfile(qrName):
        window.blit(getImage(qrName), (tagWidth//(1/0.2),tagHeight//(1/0.2)) )
    if os.path.isfile(picName):
        window.blit(getImage(picName), (-tagWidth//(1/0.2),tagHeight//(1/0.2)) )
    pygame.display.flip()


def run():
    pygame.init()
    window = pygame.display.set_mode((tagWidth,tagHeight))
    window.fill((255,255,255))
    with open('try.csv') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            print (', '.join(row))
            fname = row[0]
            generate(fname)
            makeTag(window, fname)
    while True:
        time.sleep(5)

run()
