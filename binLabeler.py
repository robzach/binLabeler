"""
bin labeler
for Physical Computing lab in IDeATe, Carnegie Mellon University
by Robert Zacharias

v 0.1 6-12-17
    starting to play with reading a CSV and using its contents to assemble an image for printing
    currently is able to read the CSV, opening an image in the same folder if it finds it

    my CSV, try.csv, looks like this:
    
        num,name    
        4988,A4988 stepper motor driver

    and in the same directory as the CSV is an image file called 4988.jpg

    also tries to generate a QR code encoding a sample short URL, but that's not working yet
    
"""

import csv
import os.path
from PIL import Image
import qrcode
from qrcode.image.pure import PymagingImage

showImage = False;
makeQR = True;

with open('try.csv') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in spamreader:
##        print (', '.join(row))
        fname = row[0] + '.jpg'
        if os.path.isfile(fname):
            print (fname + " found")
            if showImage:
                image = Image.open(fname)
                image.show()
            if makeQR:
                url = 'shrtco.de/' + row[0]
                qr = qrcode.make(url)
                print ('made qr code pointing to: ' + url)
                pngout = qrcode.make(url, image_factory=PymagingImage)
                pngout.show()
            
        else:
            print (fname + " not found")
