"""
bin labeler
for Physical Computing lab in IDeATe, Carnegie Mellon University
by Robert Zacharias

v 0.1 6-12-17
    starting to play with reading a CSV and using its contents to assemble an image for printing
    currently is able to read the CSV, opening an image in the same folder if it finds it

    my CSV looks like this:
    
        num,name    
        4988,A4988 stepper motor driver

    and in the same directory as the CSV is an image file called 4988.jpgw
    
"""

import csv
import os.path
from PIL import Image

with open('try.csv') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in spamreader:
##        print (', '.join(row))
        fname = row[0] + '.jpg'
        if os.path.isfile(fname):
            print (fname + " found")
            image = Image.open(fname)
            image.show()
        else:
            print (fname + " not found")
