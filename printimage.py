#!/usr/bin/env python3


from PIL import Image, ImageChops
import array
import sys
import os


printerdevice=sys.argv[2]

img = Image.open( sys.argv[1])
img = ImageChops.invert(img)
img = img.convert('1')
'''Pixels are lost on the sides. It can print 575 pixels wide, 1 pixel row lost to the left, a bunch to the right.'''
'''The max pixel width can be set and read somehow. Coming soon i guess.'''
if img.width > 550:
    img.thumbnail(size=(550,2048))  # max height is here.
                                    # The max height using the bitimage mode is virtually unlimited. 
                                    # Increase at will



LF=b"\n" # 0x0a
CR=b"\x0d"
FF=b"\x0c"
ESC=b"\x1b"
GS=b"\x1d"
HT=b"\t" # 0x09

print("Found image: " + str(img.width) + "x" + str(img.height))

def getPrintableImage(image):
    ''' Image must be a multiple of twentyfour, so rounding up to nearest '''
    height  = (24-(image.height % 24)) + image.height

    printerimage  = Image.new( mode='1', size=(640, height), color='Black' )
    printerimage.paste(image, (1,1))
    ImageChops.invert(printerimage).save('printing.png')
    ''' Now we have a picture we can print '''

    return printerimage


def bitModeImage(image):
    data = b''
    img = image.transpose(Image.FLIP_LEFT_RIGHT)
    height = img.height
    width = img.width
    for y in range(0, height, 24):
        yRemain = height -y
        if (yRemain > 24):
            ybk = 24
        else:
            ybk = yRemain

        data += b"\x1b" + b"*" + bytes([33]) # ESC * mode 33 - Bit Image Command
        # Width of image, low byte first
        data += bytes([(width - (width >> 8 << 8))]) # n1
        data += bytes([(width >> 8 )])               # n2
        data += img.crop((0,y,width,y+ybk)).transpose(Image.ROTATE_90).tobytes()
        data += b"\x1bJ\x00" # ESC J n - Printing and feeding paper in minimum pitch
    return data




printerInitializeCommand = ESC + b"@"
startPageCommand=ESC + b"2"
endPageCommand= FF
endJobCommand= GS + b"r1"
pageCutCommand= GS + b"VA" + b"\x00" # Can also use ESC + "I"
BuzzerCommand=ESC + b"\x1e"         # Beep!

printimage = getPrintableImage(img)

fd = os.open( printerdevice, os.O_RDWR)
print("Trying to print image, resized to\n","height:",printimage.height,"\nwidth:",printimage.width,"\n")
os.write(fd, printerInitializeCommand)
os.write(fd, bitModeImage(printimage))

'''There is a physical space of about four newlines between the printer head and the paper cutter'''
os.write(fd, b"\n\n\n\n")
os.write(fd, pageCutCommand)


