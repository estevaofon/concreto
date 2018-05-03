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
    corner = round_corner(radius, fill, background)
    rectangle.paste(corner, (0, 0))
    # Rotate the corner and paste it
    rectangle.paste(corner.rotate(90), (0, height - radius))
    rectangle.paste(corner.rotate(180), (width - radius, height - radius))
    rectangle.paste(corner.rotate(270), (width - radius, 0))
    return rectangle


def desenha_camada(dr, x0, y0, bitola, n_barras, ft, x0_est, bw):
    r = bitola*ft
    cnom = x0_est - (x0-20)
    bs1 = bw-4*cnom
    if bitola >= 16:
        bs1 = bw-4*cnom-(bitola/5)
    if n_barras == 1:
        dr.ellipse((x0-r, y0-r, x0+r, y0+r), fill="blue")
    else:
        eh = bs1/(n_barras-1)
        for i in range(n_barras):
            dr.ellipse((x0-r, y0-r, x0+r, y0+r), fill="blue")
            x0 += eh


def desenha_camadas(dr, x0, y0, ft, x0_est, bw, h, camadas):
    x0 = x0+20
    y0 = h+23
    ev = 0
    for c in camadas:
        if c[0] > ev:
            ev = c[0]
            print(ev)

    for camada in camadas:
        desenha_camada(dr, x0, y0, camada[0], camada[1], ft, x0_est, bw)
        y0 -= ev*2


def desenha_porta_estribo(dr, x0, y0, ft, bw):
    x = x0+20
    y = y0+24
    r = 6.5*ft
    eh = int(bw-65*ft)
    for i in range(2):
        dr.ellipse((x-r, y-r, x+r, y+r), fill="purple")
        x += eh


def desenha_pele(dr, x0, y0, ft, bw, h, n, camadas):
    y1 = h+23
    ev = camadas[0][0]
    n += 1
    for camada in camadas:
        y1 -= ev*2
    inc = (y1-y0)/(n)
    for i in range(n):
        desenha_porta_estribo(dr, x0, y0, ft, bw)
        y0 += inc

def draw_beam(bw, h, camadas, n_pele=0):
    """
    Desenha um viga de armadura simples
    camadas = [(bitola, numero_barras), ...]
    """
    width, height = h+50, h
    im = Image.new('RGBA', (width, height), 'white')
    dr = ImageDraw.Draw(im)

    ft = 6/10  # fator de reducao do desenho
    bw = int(bw*ft)
    h = int(h*ft)
    x0 = int(width/2 - bw/2)
    y0 = 50
    x1 = x0 + bw
    y1 = y0 + h
    dr.rectangle(((x0, y0), (x1, y1)), fill=(235, 235, 235, 255),
                 outline="black")

    # Desenha o estribo
    # est -> estribo
    x0_est = x0 + 10
    y0_est = y0 + 10
    h_est = h - 20
    bw_est = bw - 20
    background = (235, 235, 235, 255)
    img = round_rectangle((bw_est, h_est), 10, "gray", background)
    im.paste(img, (x0_est, y0_est))
    background = (235, 235, 235, 255)
    img = round_rectangle((bw_est-10, h_est-20), 10, background, "gray")
    im.paste(img, (x0_est+5, y0_est+10))

    if not n_pele:
        desenha_porta_estribo(dr, x0, y0, ft, bw)
    else:
        desenha_pele(dr, x0, y0, ft, bw, h, n_pele, camadas)
    desenha_camadas(dr, x0, y0, ft, x0_est, bw, h, camadas)
    im.save("viga.png")


if __name__ == "__main__":
    camadas = [(20, 2), (10, 2), (12.5, 2)]
    draw_beam(150, 750, camadas, 0)
