#!  /home/jakezimmer/anaconda3/envs/py35/bin/python
# coding: utf-8



import csv
import os.path
from tkinter import *
import pyscreenshot
from PIL import Image, ImageTk
import qrcode
from qrcode.image.pure import PymagingImage



showImage = True;
makeQR = True;



with open('try.csv') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in spamreader:
        print (', '.join(row))
        fname = row[0] + '.jpg'
        if os.path.isfile(fname):
            print (fname + " found")
            if showImage:
                image = Image.open(fname)
                #image.show()
                pass;
            if makeQR:
                url = 'shrtco.de/' + row[0]
                qr = qrcode.make(url)
                print ('made qr code pointing to: ' + url)
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=35,
                    border=1,
                )
                qr.add_data('Some data')
                qr.make(fit=True)

                pngout = qr.make_image()
                pngout.save(fname[:-4]+".png")
                #pngout.show()
        else:
            print (fname + " not found")






root = Tk()
root.configure(background='white')


#tag dimensions
w = 1000
h = 500

#qr and item dimensions
qrw = w//4
qrh = qrw

itemw = w//4
itemh = itemw

#text placement
textx = 0
texty = h*0.8

textSize = 20

text = "Testing"
subText = "wow this is a cool part that can be used to make stuff"


Frame(root,width=w,height=h, bg='white').grid(row=1,column=0)

qr = ImageTk.PhotoImage(Image.open("4988.png").resize(size=(qrw,qrh)))
qr_label = Label(image=qr)
qr_label.image = qr

qr_label.place(x=w*0.7,y=h*0.1)
qr_label.config(width=qrw, height=qrh)


item = ImageTk.PhotoImage(Image.open("4988.jpg").resize(size=(itemw,itemh)))
item_label = Label(image=item)
item_label.image = item

item_label.place(x=w*0.1,y=h*0.1)
item_label.config(width=itemw, height=itemh)


text_label = Label(text=text, font=('Verdana', 20, 'bold'), justify='center')
text_label.place(x=textx,y=texty)

subText_label = Label(text=subText, justify='center')
subText_label.place(x=textx,y=texty)


from pyscreenshot import grab

im = grab(bbox=(100, 200, 300, 400), backend='scrot')
im.show()

# img = pyscreenshot.grab(bbox=(0,0,w,h),backend='scrot')
# print(pyscreenshot.backends())
# pyscreenshot.grab_to_file("test.png")

root.mainloop()
