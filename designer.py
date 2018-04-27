#!/usr/bin/python
from PIL import Image, ImageFont, ImageDraw



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
 
def draw_beam(bw, h, bitola):
    width, height = 600, 500
    im = Image.new('RGBA', (width, height), 'white')
    dr = ImageDraw.Draw(im)

    ft = 6/10
    bw = int(bw*ft)
    h = int(h*ft)
    x0 = int(width/2 - bw/2)
    y0 = 50
    x1 = x0 + bw
    y1 = y0 + h
    dr.rectangle(((x0, y0),(x1, y1)), fill= (235, 235, 235, 255), outline = "black")

    x0_est = x0 + 10
    y0_est = y0 + 10
    h_est = h - 20
    bw_est = bw - 20
    background = (235, 235, 235, 255)
    img = round_rectangle((bw_est, h_est), 10, "gray", background)
    im.paste(img, (x0_est, y0_est))

    background = (235, 235, 235, 255)
    img = round_rectangle((bw_est-10, h_est-20), 10, background, "gray")
    im.paste(img, (x0_est+5,y0_est+10))

    def desenha_camada(x, y, bitola, n_barras, x0, y0, ft):
        r = bitola*ft
        cnom = x0_est - x0
        bs1 = bw -4*cnom
        print("bs1", bs1*1/ft)
        x0 = x
        if n_barras == 1:
            dr.ellipse((x-r, y-r, x+r, y+r), fill="blue")
        else:
            eh = bs1/(n_barras-1)
            for i in range(n_barras):
                dr.ellipse((x-r, y-r, x+r, y+r), fill="blue")
                x += eh

        x = x0
        y = y0 +24
        r = 6.5*ft
        eh = int(bw-70*ft)
        for i in range(2):
            dr.ellipse((x-r, y-r, x+r, y+r), fill="purple")
            x += eh
            print(x)


    x = x0+20
    y = h+23
    camadas = [(16,2), (16, 2), (16,1)]
    ev = 0
    for c in camadas:
        if c[0] > ev:
            ev = c[0]

    for camada in camadas:
        desenha_camada(x, y, camada[0], camada[1], x0, y0, ft)
        y -= ev*2
    im.save("viga.png")

draw_beam(150, 750, 10)