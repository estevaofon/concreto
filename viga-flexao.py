import math
# Entrada de dados
# bw h d -> mm
bw = 150
L = 6000
# h = L/(10)
# d = 0.9*h
# com d inicial
# d = 400
h = 650
d = 590

# espacamento -> mm
cnom = 30
dbrita = 19
dt = 6.3  # diametro do estribo
bitola = 20

# Mk -> kN.m
M = 58.4
# fck -> MPa
fck = 30
fy = 500
fyd = fy/1.15

# Conversoes
h = h*10**-3  # metros
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
# Msd = 1.4*M
Msd = 247
Msd = Msd*10**3  # N.m
d1_est = h-d


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
    # As_cm = As * 10**4
    bitolas = [5, 6.3, 8, 10, 12.5, 16, 20, 22.0, 25.0, 32, 40]
    bitolas_m = [bmm*10**-3 for bmm in bitolas]
    nbarras = {}
    for bmm in bitolas_m:
        area = math.pi*(bmm**2)/4
        nbarras[str(bmm*10**3)] = As/area
    for key, value in nbarras.items():
        decimal = value - int(value)
        if decimal <= 0.3 and value >= 1:
            nbarras[key] = math.floor(value)
        else:
            nbarras[key] = math.ceil(value)
    return nbarras


def ev_min(bitola, dbrita):
    ev = 20 * 10**-3
    if bitola > ev:
        ev = bitola
    elif 0.5*dbrita > ev:
        ev = 0.5*dbrita
    return ev


def eh_min(bitola, dbrita):
    eh = 20 * 10**-3
    if bitola > eh:
        eh = bitola
    elif 1.2*dbrita > eh:
        eh = 1.2*dbrita
    return eh


def bwmin(dbitola, dt, dbrita, nbarras, cnom):
    a = eh_min(dbitola, dbrita)
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
    barra_max = 0
    while bwm >= bw:
        n -= 1
        layers += 1
        bwm = bwmin(12.5*10**-3, dt, dbrita, n, cnom)
        if bwm <= bw:
            barra_max = n
    nb = nbarras[bitola_str]
    while nb > 0:
        if (nb - barra_max) >= 0:
            camadas.append(barra_max)
            nb -= barra_max
        elif nb > 0:
            camadas.append(nb)
            nb = 0
    return(camadas)


def d1_real(cnom, dt, bitola, camadas):
    a = ev_min(bitola, dbrita)
    abitola = math.pi*(bitola/2)**2
    soma = 0
    for i, barras in enumerate(camadas):
        soma += barras*abitola*((bitola/2)+a*i+bitola*i)
    bitola_str = str(bitola*10**3)
    yc = soma/(nbarras[bitola_str]*abitola)
    d1 = cnom + dt + yc
    return d1


def d_real(d1, h):
    return h-d1


def d_test(d1_est, d1_real):
    c = d1_real/d1_est
    if c <= 1.10:
        print("d esta ok")
        return 1
    else:
        print("Difereca maior que 1.10 => {:.3f}".format(c))
        return 0


def eh_por_camada(camadas, bitola, dt, cnom, bw):
    eh_list = []
    for n in camadas:
        if n > 1:
            a = (bw-2*cnom-2*dt-n*bitola)/(n-1)
        elif n == 1:
            a = bw - 2*cnom-2*dt-bitola
        eh_list.append(a)
    return eh_list


def delta_teste(cnom, dt, bitola, camadas, h):
    a = ev_min(bitola, dbrita)
    abitola = math.pi*(bitola/2)**2
    soma = 0
    for i, barras in enumerate(camadas):
        soma += barras*abitola*((bitola/2)+a*i+bitola*i)
    bitola_str = str(bitola*10**3)
    yc = soma/(nbarras[bitola_str]*abitola)
    if yc <= 0.1*h:
        print("Passou no teste de tensao centrada no cg")
    else:
        print("Não passou no delta teste")
    return 1


def test_min_steelarea(bw, h, fck, As):
    fck = str(int(fck/(10**6)))
    tx_min = {'20': 0.15, '25': 0.15, '30': 0.15, '35': 0.164, '40': 0.179,
              '45': 0.195, '50': 0.208, '55': 0.211, '60': 0.219, '65': 0.226,
              '70': 0.233, '75': 0.239, '80': 0.245, '85': 0.251, '90': 0.256}
    asmin = (tx_min[fck]/100)*bw*h
    if As >= asmin:
        print("Area min ok")
        return 0
    else:
        print("Menor que a area min")
        return 1


def test_max_steelarea(bw, h, fck, As):
    if As <= (4/100)*(bw*h):
        print("Area maxima ok")
        return 0
    else:
        print("Maior que a area maxima")
        return 1


def barra_int(value):
    decimal = value - int(value)
    if decimal <= 0.3 and value >= 1:
        value = math.floor(value)
    else:
        value = math.ceil(value)
    return value


def as_pele(bw, h, bitola, dt, ev, camadas, cnom):
    n_c = len(camadas)
    n_ev = n_c - 1
    w = cnom+dt+n_c*bitola+n_ev*ev-bitola/2
    J = h - cnom - dt - w
    n = 0
    t = 0
    if h > 0.6:
        area_pele = (0.10/100)*bw*h
        area_bitola = math.pi*(dt**2)/4
        n = area_pele/area_bitola
        n = barra_int(n)

        t = J/(n+1)
        if t > 0.2:
            print("Nao ok, t > 20cm")
        if t > d/3:
            print("Nao ok, t > d/3")
        if t > 15*bitola:
            print("t não ok")

    else:
        print("Não precisa de As de pele")
    return(n, t)


kmd = kmd_calc(Msd, bw, d, fcd)
sigmac, lambdac = sigma_lambda_calc(fck)
kx = kx_calc(kmd, sigmac, lambdac)
kz = kz_calc(lambdac, kx)
As = steel_area(Msd, d, fyd)
amin = test_min_steelarea(bw, h, fck, As)
amin = test_max_steelarea(bw, h, fck, As)
As_cm = As * 10**4
x1, x2 = linha_neutra(d, Msd, bw, fcd)
x1_cm = x1 * 100
x2_cm = x2 * 100
dminimo = dmin(Msd, bw, fcd)
dminimo = dminimo*100
dom = dominio(kx)
nbarras = desbitolagem(As)
camadas = distribuicao_max(bw, nbarras, bitola, dt, dbrita, cnom)
eh_camadas = eh_por_camada(camadas, bitola, dt, cnom, bw)
d1 = d1_real(cnom, dt, bitola, camadas)
delta_teste(cnom, dt, bitola, camadas, h)
d_r = d_real(d1, h)
d_test(d1_est, d1)
ev = ev_min(bitola, dbrita)
n, t = as_pele(bw, h, bitola, dt, ev, camadas, cnom)
print(f"dmin:{dminimo:.2f}")
print(f"d1: {d1*100:.2f} cm")
print(f"d1_est: {d1_est*100:.2f} cm")
print(f"d_real: {d_r*100:.2f} cm")
print(f"kmd: {kmd:.3f}")
print("kx: {:.3f}".format(kx))
print("kz: {:.3f}".format(kz))
print(f"x1:{x1_cm:.2f}; x2:{x2_cm:.2f}")
print(f"Dominio {dom}")
print("As: {:.2f} cm2".format(As_cm))
selecionadas = [8.0, 10.0, 12.5, 16.0, 20.0, 22.0]
dic_barras = {}
for i in selecionadas:
    dic_barras[str(i)] = nbarras[str(i)]
print(dic_barras)
print(f"Bitola:{str(bitola*10**3)}")
print(f"camadas:{camadas}")
print(f"eh:{[str(round(eh*100,2)) for eh in eh_camadas]}")
print(f"ev:{ev*100}")
print(n, str(round(t*100,2)))
