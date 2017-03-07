#!/usr/bin/env python


import Image, ImageChops
import array
import sys
import os


printerdevice=sys.argv[2]

img = Image.open( sys.argv[1])
img = ImageChops.invert(img)
img = img.convert('1')
'''Pixels are lost on the sides. It can print 575 pixels wide, 1 pixel row lost to the left, a bunch to the right.'''
'''Really strange. Maybe it's the wrong paper size? Resizing to max 566 pixels here:'''
if img.width > 575:
    img.thumbnail(size=(575,1024))


LF="\n" # 0x0a
CR="\x0d"
FF="\x0c"
ESC="\x1b"
GS="\x1d"
HT="\t" # 0x09



def getPrintableImage(image):
    ''' Image must be a multiple of eight, so rounding up to nearest eight '''
    height  = (image.height % 8) + image.height

    printerimage  = Image.new( mode='1', size=(640, height), color='Black' )
    printerimage.paste(image, (1,0))

    ''' Now we have a picture we can print '''

    return printerimage

def rasterHeader(image):
    ''' get height and width in a format the printer understands: '''
    h = image.height
    hexheight = chr(h - (h >> 8 << 8 )) + chr(h >> 8)

    w = image.width / 8
    hexwidth = chr(w - (w >> 8 << 8 )) + chr(w >> 8)
    
    return GS + "v00" + hexwidth + hexheight

printerInitializeCommand = ESC + "@"
startPageCommand=ESC + "2"
endPageCommand= FF
endJobCommand= GS + "r1"
pageCutCommand= ESC + "i"
BuzzerCommand=ESC + "\x1e"

printimage = getPrintableImage(img)

fd = os.open( printerdevice, os.O_RDWR)

os.write(fd, printerInitializeCommand)
os.write(fd, startPageCommand)
os.write(fd, rasterHeader(printimage))
os.write(fd, printimage.tobytes())
os.write(fd, endPageCommand)
os.write(fd, endJobCommand)

'''There is a physical space of about four newlines between the printer head and the paper cutter'''
os.write(fd, "\n\n\n\n")
os.write(fd, pageCutCommand)








