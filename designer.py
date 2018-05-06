#!/home/estevao/Documentos/projetos-python/concreto/env/bin/python3
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
    pos_bitola = []
    if bitola >= 16:
        bs1 = bw-4*cnom-(bitola/5)
    if n_barras == 1:
        dr.ellipse((x0-r, y0-r, x0+r, y0+r), fill="blue")
    else:
        eh = bs1/(n_barras-1)
        for i in range(n_barras):
            dr.ellipse((x0-r, y0-r, x0+r, y0+r), fill="blue")
            pos_bitola.append((bitola, (x0, y0)))
            x0 += eh
    return pos_bitola


def desenha_camadas(dr, x0, y0, ft, x0_est, bw, h, camadas):
    x0 = x0+20
    y0 = h+23
    ev = 0
    list_collection = []
    for c in camadas:
        if c[0] > ev:
            ev = c[0]

    for camada in camadas:
        pos_bitola = desenha_camada(dr, x0, y0, camada[0], camada[1], ft, x0_est, bw)
        list_collection.append(pos_bitola)
        y0 -= ev*2
    flat_bitola = [item for sublist in list_collection for item in sublist]
    return flat_bitola



def desenha_porta_estribo(dr, x0, y0, ft, bw):
    x = x0+20
    y = y0+24
    bitola = 6.3
    r = bitola*ft
    eh = int(bw-65*ft)
    estribo_pos_bitola = []
    for i in range(2):
        dr.ellipse((x-r, y-r, x+r, y+r), fill="purple")
        estribo_pos_bitola.append((bitola, (x,y)))
        x += eh
    return estribo_pos_bitola



def desenha_pele(dr, x0, y0, ft, bw, h, n, camadas):
    bitola = 6.3
    y1 = h+23
    ev = camadas[0][0]
    n += 1
    for camada in camadas:
        y1 -= ev*2
    inc = (y1-y0)/(n)
    list_collection = []
    for i in range(n):
        list_collection.append(desenha_porta_estribo(dr, x0, y0, ft, bw))
        y0 += inc
    pos_bitola = [item for sublist in list_collection for item in sublist]

    return pos_bitola


def guia_estribo(x0, y0, dr, estribo_pos_bitola):
    for pb in estribo_pos_bitola:
        x, y = pb[1]
        dr.line((x, y, 150,250), fill="gray", width=2)
    font = ImageFont.truetype("OpenSans-Regular.ttf", 20)
    dr.text((x0, y0), str(estribo_pos_bitola[0][0]), fill="black",font=font)

def agrupa_bitola(pos_bitola):
    bitolas = set(map(lambda x:x[0], pos_bitola))
    bitolas = sorted(bitolas)
    list_final = []
    for bitola in bitolas:
        temp = []
        for item in pos_bitola:
            if item[0] == bitola:
                temp.append(item)
        list_final.append(temp)
    return list_final


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
    estribo_pos_bitola = []
    if not n_pele:
        estribo_pos_bitola = desenha_porta_estribo(dr, x0, y0, ft, bw)
        guia_estribo(120, 250, dr, estribo_pos_bitola)
    else:
        pos_bitola = desenha_pele(dr, x0, y0, ft, bw, h, n_pele, camadas)
        guia_estribo(120, 250, dr, pos_bitola)
    pos_bitola = desenha_camadas(dr, x0, y0, ft, x0_est, bw, h, camadas)
    agrupa_bitola(pos_bitola)
    im.save("viga.png")


if __name__ == "__main__":
    camadas = [(20, 2), (16, 2), (12.5, 2)]
    draw_beam(150, 750, camadas, 3)
    import os
    os.system("xdg-open viga.png")
