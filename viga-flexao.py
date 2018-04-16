import math
# Entrada de dados
# bw h d -> mm
bw = 150
L = 6000  
h = L/(10)
d = 0.9*h  
# com d inicial
d = 400 

# espacamento -> mm
cnom = 25
dbrita = 25
dt = 5  # diametro do estribo
bitola = 10

# Mk -> kN.m
M = 50
# fck -> MPa
fck = 20
fy = 500
fyd = fy/1.15

# Conversoes
bw = bw*10**-3  # metros
d = d*10**-3
M = M*10**3  # N.m
fck = fck*10**6  # Pa
fyd = fyd*10**6
cnom = cnom*10**-3
dbrita = dbrita*10**-3
dt = dt*10**-3
bitola = bitola*10**-3

# Calculos
fcd = fck/1.4
Msd = 1.4*M


def kmd_calc(Msd, bw, d, fcd):
    kmd = Msd/(bw*(d**2)*fcd)
    return kmd


def kz_calc(lambdac, kx):
    kz = 1 - 0.5*lambdac*kx
    return kz


def kx_calc(kmd, sigmac, lambdac):
    kx = (1 - (1 - 2*kmd/sigmac)**0.5)/lambdac
    return kx


def sigma_lambda_calc(fck):
    # fck <= 50MPa
    if fck <= 50*10**6:
        sigmac = 0.85
        lambdac = 0.8
    if fck > 50*10**6:
        fck = fck/(10**6)
        sigmac = 0.85*(1-(fck-50)/200)
        lambdac = 0.8 - (fck - 50)/400
    return sigmac, lambdac


def steel_area(Msd, d, fyd):
    As = Msd/(kz*d*fyd)
    return As


def linha_neutra(d, Msd, bw, fcd):
    a = math.sqrt((0.68*d)**2-4*0.272*(Msd/(bw*fcd)))
    x1 = (0.68*d + a)/0.544
    x2 = (0.68*d - a)/0.544
    return x1, x2


def dmin(Msd, bw, fcd):
    d = 2.0*math.sqrt(Msd/(bw*fcd))
    return d


def dominio(kx):
    if kx > 0.259 and kx <= 0.45:
        n_dominio = 3
    elif kx <= 0.259 and kx >= 0.02:
        n_dominio = 2
    else:
        print("Fora do dominio 2 e 3")
        n_dominio = 0
    return n_dominio


def desbitolagem(As):
    As_cm = As * 10**4
    nbarras = {}
    nbarras['10.0'] = As_cm/0.79
    nbarras['12.5'] = As_cm/1.23
    nbarras['16.0'] = As_cm/2.01
    for key, value in nbarras.items():
        decimal = value - int(value)
        if decimal <= 0.3:
            nbarras[key] = math.floor(value)
        else:
            nbarras[key] = math.ceil(value)
    return nbarras


def bwmin(dbitola, dt, dbrita, nbarras, cnom):
    a = 20*10**-3
    if 1.2*dbrita >= 20*10**-3:
        a = 1.2*dbrita
    if dbitola >= a:
        a = dbitola
    bs = nbarras*dbitola + (nbarras-1)*a
    bwm = bs + 2*(dt + cnom)
    return bwm


def distribuicao_max2(bw, nbarras, bitola, dt, dbrita, cnom):
    # maximo de barra por camada
    bitola_str = str(bitola*10**3)
    bwm = bwmin(bitola, dt, dbrita, nbarras[bitola_str], cnom)
    layers = 1
    barra_unica = 0
    camadabarra = {}
    while bwm >= bw:
        layers += 1
        n = nbarras[bitola_str]/layers
        if n % 2:
            barra_unica = 1
            if n < 2:
                n = 2
            else:
                n = int(n)
                layers += 1
            camadabarra[str(layers)] = 1
        bwm = bwmin(12.5*10**-3, dt, dbrita, n, cnom)
        print(f"novo bwmin {bwm}")
        print(f"numero de barra por camada: {n}")
        print(f"numero de camadas: {layers}")

    print(f"Camada-barra {camadabarra}")


def distribuicao_max(bw, nbarras, bitola, dt, dbrita, cnom):
    # maximo de barra por camada
    bitola_str = str(bitola*10**3)
    bwm = bwmin(bitola, dt, dbrita, nbarras[bitola_str], cnom)
    layers = 0
    barra_unica = 0
    camadas = []
    n = nbarras[bitola_str]
    print(f"{bwm}")
    barra_max = 0
    while bwm >= bw:
        n -= 1
        layers += 1
        bwm = bwmin(12.5*10**-3, dt, dbrita, n, cnom)
        if bwm <= bw:
            barra_max = n
        print(f"{bwm}")
    nb = nbarras[bitola_str]
    while nb > 0:
        if (nb - barra_max) >= 0:
            camadas.append(barra_max)
            nb -= barra_max
        elif nb > 0:
            camadas.append(nb)
            nb = 0
    return(camadas)


kmd = kmd_calc(Msd, bw, d, fcd)
sigmac, lambdac = sigma_lambda_calc(fck)
kx = kx_calc(kmd, sigmac, lambdac)
kz = kz_calc(lambdac, kx)
As = steel_area(Msd, d, fyd)
As_cm = As * 10**4
x1, x2 = linha_neutra(d, Msd, bw, fcd)
x1_cm = x1 * 100
x2_cm = x2 * 100
dminimo = dmin(Msd, bw, fcd)
dminimo = dminimo*100
dom = dominio(kx)
nbarras = desbitolagem(As)
camadas = distribuicao_max(bw, nbarras, bitola, dt, dbrita, cnom)
print(f"kmd: {kmd:.3f}")
print("kx: {:.3f}".format(kx))
print("kz: {:.3f}".format(kz))
print(f"x1:{x1_cm:.2f}; x2:{x2_cm:.2f}")
print(f"dmin:{dminimo:.2f}")
print(f"Dominio {dom}")
print("As: {:.2f} cm2".format(As_cm))
print(nbarras)
print(f"Bitola:{str(bitola*10**3)}")
print(f"camadas:{camadas}")
