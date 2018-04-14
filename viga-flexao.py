import math
# Entrada de dados
# bw h d -> cm
bw = 15

# Sem d inicial
L = 6  # m
h = 6/10
d = 0.9*h*100
# com d inicial
# d = 40  # cm

# espacamento -> mm
cnom = 30
dbrita = 25
dt = 6.3  # diametro do estribo

# M -> kN.m
M = 58.4
# fck -> MPa
fck = 25
fy = 500
fyd = fy/1.15

# Conversoes
bw = bw*10**-2  # metros
d = d*10**-2
M = M*10**3  # N.m
fck = fck*10**6  # Pa
fyd = fyd*10**6
cnom = cnom*10**-3
dbrita = dbrita*10**-3
dt = dt*10**-3

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
        print("Dominio 3")
    elif kx <= 0.259 and kx >= 0.02:
        n_dominio = 2
        print("Dominio 2")
    else:
        print("Fora do dominio 2 e 3")
        n_dominio = 0
    return n_dominio


def desbitolagem(As):
    As_cm = As * 10**4
    nbarras = {}
    nbarras['10'] = As_cm/0.79
    nbarras['12.5'] = As_cm/1.23
    nbarras['16'] = As_cm/2.01
    for key, value in nbarras.items():
        decimal = value - int(value)
        if decimal <= 0.3:
            nbarras[key] = math.floor(value)
        else:
            nbarras[key] = math.ceil(value)
    # nbarras = {key: math.ceil(value) for (key, value) in nbarras.items()}
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
dominio(kx)
nbarras = desbitolagem(As)
bitola = '12.5'
bwm = bwmin(12.5*10**-3, dt, dbrita, nbarras[bitola], cnom)

layers = 1
barra_unica = 0
print(nbarras)
while bwm >= bw:
    layers += 1
    n = nbarras[bitola]/layers
    if n < 2:
        n = 2
        barra_unica = 1
    bwm = bwmin(12.5*10**-3, dt, dbrita, n, cnom)
    print(f"novo bwmin {bwm}")
    if barra_unica:
        print(f"Ultima camada com uma barra só")
    print(f"numero de barra por camada: {n}")
    print(f"numero de camadas: {layers}")


print(f"kmd: {kmd:.3f}")
print("kx: {:.3f}".format(kx))
print("kz: {:.3f}".format(kz))
print("As: {:.3f} cm2".format(As_cm))
print(f"x1:{x1_cm:.2f}; x2:{x2_cm:.2f}")
print(f"dmin:{dminimo:.2f}")
print(nbarras)
print(bwm)
print(bw)
