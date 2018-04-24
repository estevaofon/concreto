#!/usr/bin/python
from PIL import Image, ImageFont, ImageDraw

width, height = 800, 600
im = Image.new('RGBA', (width, height), 'white')
dr = ImageDraw.Draw(im)

ft = 6/10
x1 = width/2 - 70
y1 = height/2 - 200
h = y1+int(600*ft)
bw = x1+int(150*ft)
dr.rectangle(((x1, y1),(bw, h)), fill= (235, 235, 235, 255), outline = "black")




def round_corner(radius, fill, background):
    """Draw a round corner"""
    corner = Image.new('RGBA', (radius, radius), background)
    draw = ImageDraw.Draw(corner)
    draw.pieslice((0, 0, radius * 2, radius * 2), 180, 270, fill=fill)
    return corner
 
def round_rectangle(size, radius, fill, background):
    """Draw a rounded rectangle"""
    width, height = size
    rectangle = Image.new('RGBA', size, fill)
    corner = round_corner(radius, fill,background)
    rectangle.paste(corner, (0, 0))
    rectangle.paste(corner.rotate(90), (0, height - radius)) # Rotate the corner and paste it
    rectangle.paste(corner.rotate(180), (width - radius, height - radius))
    rectangle.paste(corner.rotate(270), (width - radius, 0))
    return rectangle
 
background = (235, 235, 235, 255)
img = round_rectangle((70, 340), 10, "gray", background)
im.paste(img, (340,110))

background = (235, 235, 235, 255)
img = round_rectangle((60, 323), 10, background, "gray")
im.paste(img, (345,120))

x = x1+18
y = h - 20
r = 12.5*ft
x0 =  x
for i in range(3):
    dr.ellipse((x-r, y-r, x+r, y+r), fill="blue")
    x += 27

x = x0
y = y1 +24
r = 6.5*ft
for i in range(2):
    dr.ellipse((x-r, y-r, x+r, y+r), fill="purple")
    x += 56

im.save("viga.png")

