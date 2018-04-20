import math
# Entrada de dados
# dimensoes -> mm
bw = 150
h = 400
d = 340

dt = 5  # diametro do estribo
bitola = 20
# classe de agressividade
caa = 1
brita = 1

# Mk -> kN.m
Mk = 70
Msd = 1.4*Mk
# Msd = 109
# fck -> MPa
fck = 25
fy = 500

dic_caa = {1: 25, 2: 30, 3: 40, 4: 50}
dic_brita = {1: 19, 2: 25, 3: 50, 4: 76}
dbrita = dic_brita[brita]
cnom = dic_caa[caa]
# Conversoes para Metro
h = h*10**-3
bw = bw*10**-3
d = d*10**-3
fck = fck*10**6  # Pa
fy = fy*10**6
fyd = fy/1.15
cnom = cnom*10**-3
dbrita = dbrita*10**-3
dt = dt*10**-3
bitola = bitola*10**-3
Msd = Msd*10**3  # N.m

# Calculos
fcd = fck/1.4
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


def ecu_calc(fck):
    fck = fck/10**6  # Pa
    # 20, 50, 90
    if fck <= 50:
        ecu = 3.5
    else:
        ecu = 2.6 + 35*((90-fck)/100)**4
    return ecu


def dominio(kx, fck, fy=500*10**6):
    ecu = ecu_calc(fck)
    fy = int(fy/10**7)
    fck = fck/10**6  # Pa
    # fck ex 20, fy 500
    dic_eyd = {25: 1.035, 50: 2.070, 60: 2.484}
    eyd = dic_eyd[fy]
    if kx < 0:
        print("Dominio 1")
        n_dominio = 1
    elif kx > 0 and kx <= ecu/(ecu+10):
        print("Dominio 2")
        n_dominio = 2
    elif kx >= ecu/(ecu+10) and kx < ecu/(ecu + eyd):
        print("Dominio 3")
        n_dominio = 3
    elif kx >= ecu/(ecu+eyd) and kx <= 1:
        print("Dominio 4")
        n_dominio = 4

    if fck <= 50 and kx <= 0.45:
        print("dutilidade OK")
    elif fck > 50 and kx <= 0.35:
        print("dutilidade OK")
    else:
        print("Fora do limite de dutilidade")
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


def distribuicao_max(bw, nbarras, bitola, dt, dbrita, cnom):
    # maximo de barra por camada
    bitola_str = str(bitola*10**3)
    bwm = bwmin(bitola, dt, dbrita, nbarras[bitola_str], cnom)
    layers = 0
    barra_unica = 0
    camadas = []
    n = nbarras[bitola_str]
    barra_max = 0
    if bwm <= bw:
        camadas.append(n)
        return(camadas)
    # numero max de barra por camada
    while bwm > bw:
        # reduz uma barra em cada loop
        n -= 1
        layers += 1
        bwm = bwmin(12.5*10**-3, dt, dbrita, n, cnom)
        if bwm <= bw:
            barra_max = n
    nb = nbarras[bitola_str]
    # distribuicao das barras
    while nb > 0:
        if (nb - barra_max) >= 0:
            camadas.append(barra_max)
            nb -= barra_max
        else:
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
        print("d1real/dest <= 1.10 OK")
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
        print("tensao centrada no cg OK")
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
        print("Armadura min OK")
        return 0
    else:
        print("Menor que a area min")
        return 1


def test_max_steelarea(bw, h, fck, As):
    if As <= (4/100)*(bw*h):
        print("Armadura maxima OK")
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
            print("Nao OK, t > 20cm")
        if t > d/3:
            print("Nao OK, t > d/3")
        if t > 15*bitola:
            print("t não OK")

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
dom = dominio(kx, fck, fy)
nbarras = desbitolagem(As)
camadas = distribuicao_max(bw, nbarras, bitola, dt, dbrita, cnom)
eh_camadas = eh_por_camada(camadas, bitola, dt, cnom, bw)
d1 = d1_real(cnom, dt, bitola, camadas)
delta_teste(cnom, dt, bitola, camadas, h)
d_r = d_real(d1, h)
d_test(d1_est, d1)
ev = ev_min(bitola, dbrita)
n, t = as_pele(bw, h, bitola, dt, ev, camadas, cnom)
ecu = ecu_calc(fck)
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
print("{} As de pele de cada lado, ev: {:.2f}".format(n, t*100))
print(f"ecu {ecu}")
