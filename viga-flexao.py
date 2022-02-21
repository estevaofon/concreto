#!/home/estevao/Documentos/projetos-python/concreto/env/bin/python3
import math
import designer
import os
# Entrada de dados
# dimensoes -> mm
bw = 160
h = 500
d = h*0.9
#d = 590

dt = 5 # diametro do estribo
bitola = 8
cobrimento = 25
d = h - bitola/2 - cobrimento - dt
# classe de agressividade
print(f"d:{d}")
caa = 2
brita = 1

# Mk -> kN.m
Mk = 17.54
Msd = 1.4*Mk
Vsk = 32.39
Vsd = 1.4*Vsk
# fck -> MPa
fck = 30
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
Vsd = Vsd*10**3  # N
Vsk = Vsk*10**3  # N

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


def steel_area(Msd, d, fyd, kz):
    As = Msd/(kz*d*fyd)
    return As


def steel_area_d(Msd, d, d2, sigmad):
    As = Msd/((d-d2)*sigmad)
    return As


def linha_neutra(d, Msd, bw, fcd, sigmac, lambdac):
    a = math.sqrt(d**2-2*(Msd/(bw*fcd*sigmac)))
    x1 = (d + a)/lambdac
    x2 = (d - a)/lambdac
    return x1, x2


def dmin(Msd, bw, fcd):
    fcd50 = (50*10**6)/1.4
    if fcd <= fcd50:
        kxlim = 0.45
    else:
        kxlim = .35
    d = math.sqrt(Msd/(bw*fcd*(0.68*kxlim-0.272*kxlim**2)))
    return d

# deformacao ultima do concreto
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
    return n_dominio


def teste_tutilidade(fck, kx):
    fck = fck/10**6
    if fck <= 50 and kx <= 0.45:
        print("dutilidade OK")
    elif fck > 50 and kx <= 0.35:
        print("dutilidade OK")
    else:
        print("Fora do limite de dutilidade")


def teste_armadura_dupla(fck, kx):
        sigmac, lambdac = sigma_lambda_calc(fck)
        kmd = kmd_from_kx(kx, sigmac=sigmac, lambdac=lambdac)
        if armadura_dupla_viavel(kmd):
            print("Armadura é viavel")
        else:
            print("Armadura dupla nao é viavel")


def desbitolagem(As, bitola):
    # As_cm = As * 10**4
    bitolas = [5, 6.3, 8, 10, 12.5, 16, 20, 22.0, 25.0, 32, 40]
    bitolas_m = [bmm*10**-3 for bmm in bitolas]
    nbarras = {}
    nbarras_puro = {}
    area_por_bitola = {5: 0.20, 6.3: 0.31, 8: 0.50, 10: 0.79, 12.5: 1.23, 16: 2.01, 20: 3.14,
    22.0: 3.8, 25: 4.91, 32: 8.04, 40: 12.6}
    for bmm in bitolas_m:
        area = math.pi*(bmm**2)/4
        nbarras[str(bmm*10**3)] = As/area
    for bit in bitolas:
        nbarras[str(bit)] = As/(area_por_bitola[bit]*10**-4)
    barras_por_bitola = []
    qt_barras = nbarras[str(bitola*10**3)]
    """
    value = qt_barras
    decimal = abs(value - int(value))
    if decimal <= 0.3 and value >= 1:
        qt_barras = math.floor(value)
    else:
        qt_barras = math.ceil(value)
    """
    porcentagem = math.floor(qt_barras)*area_por_bitola[bitola*10**3]/(As*10**4)
    print("Diferenca de porcentagem:")
    print(f"-------> {porcentagem}")
    value = qt_barras
    # Tolerancia de diferença de áreas
    if porcentagem >= 0.9:
        qt_barras = math.floor(value)
    else:
        qt_barras = math.ceil(value)
    barras_por_bitola = [(bitola, qt_barras)]
    return nbarras, barras_por_bitola


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


def distribuicao_max(bw, bitola, dt, dbrita, cnom, barras_por_bitola):
    # maximo de barra por camada
    camadas_tuple = []
    for bpb in barras_por_bitola:
        #bitola_str = str(bitola*10**3)
        bitola = bpb[0]
        n = bpb[1]
        barra_max = n
        bitola_str = str(bitola*10**3)
        #bwm = bwmin(bitola, dt, dbrita, nbarras[bitola_str], cnom)
        bwm = bwmin(bitola, dt, dbrita, n, cnom)
        layers = 0
        camadas = []
        #n = nbarras[bitola_str]
        barra_max = 0
        if bwm <= bw:
            camadas.append(n)
            camadas_tuple.append((bitola, n))
            #return(camadas, camadas_tuple)
        # numero max de barra por camada
        else:
            while bwm > bw:
                # reduz uma barra em cada loop
                n -= 1
                layers += 1
                bwm = bwmin(bitola, dt, dbrita, n, cnom)
                if bwm <= bw:
                    barra_max = n
            #nb = nbarras[bitola_str]
            nb = bpb[1]
            # distribuicao das barras
            while nb > 0:
                if (nb - barra_max) >= 0:
                    camadas.append(barra_max)
                    camadas_tuple.append((bitola, barra_max))
                    nb -= barra_max
                else:
                    camadas.append(nb)
                    camadas_tuple.append((bitola, nb))
                    nb = 0
    return camadas_tuple


def yc_calc(camadas_tuple):
    soma = 0
    area_total = 0
    for i, camada in enumerate(camadas_tuple):
        bitola = camada[0]
        barras = camada[1]
        a = ev_min(bitola, dbrita)
        abitola = math.pi*(bitola/2)**2
        soma += barras*abitola*((bitola/2)+a*i+bitola*i)
        area_total += barras*abitola
    yc = soma/area_total
    return yc


def d1_real(cnom, dt, camadas_tuple):
    yc = yc_calc(camadas_tuple)
    d1 = cnom + dt + yc
    return d1


def d_real(d1, h):
    return h-d1


def d_test(d1_est, d1_real):
    c = d1_real/d1_est
    if c <= 1.10:
        print("d1real/dest <= 1.10 OK => {:.3f}".format(c))
        return 1
    else:
        print("Difereca maior que 1.10 => {:.3f}".format(c))
        return 0


def eh_por_camada(camadas_tuple, dt, cnom, bw):
    eh_list = []
    a = 0
    for camada in camadas_tuple:
        bitola = camada[0]
        n = camada[1]
        print("Imprimento o NNNNN", n)
        if n > 1:
            a = (bw-2*cnom-2*dt-n*bitola)/(n-1)
        elif n == 1:
            a = bw - 2*cnom-2*dt-bitola
        elif n < 1:
            continue
        eh_list.append(a)
    return eh_list


def delta_teste(cnom, dt, h, camadas_tuple):
    yc = yc_calc(camadas_tuple)
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
    "Retorna a quantidade de barra com o valor inteiro"
    decimal = abs(value - int(value))
    if decimal <= 0.15 and value >= 1:
        value = math.floor(value)
    else:
        value = math.ceil(value)
    return value


def as_pele(bw, h, dt, ev, cnom, camadas_tuple):
    """
    Calcula a armadura de pele
    e o espacamento entre elas
    """
    n_c = len(camadas_tuple)
    n_ev = n_c - 1
    soma_bitola = 0
    for camada in camadas_tuple:
        bitola = camada[0]
        soma_bitola += bitola
    espaco_armadura = soma_bitola+n_ev*ev
    J = h - 2*cnom - 2*dt - espaco_armadura
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
            print(f"O t {t}")
            print(f"bitola *15 {bitola*15}")
            print("t não OK")

    else:
        print("Não precisa de As de pele")
    return(n, t)

def kmd_from_kx(kx, sigmac=0.85, lambdac=0.8):
    kmd =-(sigmac/2)*((kx*lambdac-1)**2-1)
    return kmd


def msd1_calc(bw, d, fcd, kmdlim=0.251):
    """Msd1 da armadura dupla"""
    msd1 = kmdlim*bw*(d**2)*fcd
    return msd1


def msd2_calc(Msd, msd1):
    """Msd1 da armadura dupla"""
    msd2 = Msd - msd1
    return msd2


def armadura_dupla_viavel(kmd):
    """Se for possivel o uso
    de armadura dupla retorna true"""
    if kmd <= 0.425:
        return True
    else:
        return False


def esdl(ecu, d2, d, kxlim=0.45):
    esd = ecu*(kxlim-d2/d)/kxlim
    return esd


def sigmas_calc(es, fy):
    """
    Funcao para obter a tensao
    no aco do valor da deformacao
    """
    fyd = fy/1.15
    aco = int(fy/10**7)
    eyd_dic = {25: 1.035, 50: 2.070, 60: 2.484}
    eyd = eyd_dic[aco]
    if es >= eyd and es <= 10:
        sigmas = fyd
    elif es >= 0 and es <= eyd:
        Es = 2.1*10**5
        sigmas = Es*es
    return sigmas

def VRd2(bw, d, teta, fck):
    # Valor em N
    fcd = fck/1.4
    sigma2 = 1-(fck/10**6)/250
    print(f'sigma2:{sigma2}')
    bw = bw*10**3
    d = d*10**3
    fcd = fcd/(10**6)
    return 0.27*sigma2*fcd*bw*d*math.sin(math.radians(90))

def Aswmin(bw, fck):
    """Area de aço mínima transversal"""
    # cm2/cm
    bw = bw*100
    fck = fck/(10**6)
    fctm = 0.3 * fck**(2/3)
    print(f'fctm: {fctm}')
    return 4*bw*fctm*10**(-4)*10**2

def calculo_VC(Vsd, VRd2, bw, d, fck):
    """Cálculo do VC através do Vc0
    Resultado em N
    """
    fck = fck/(10**6)
    fctm = 0.3*fck**(2/3)
    fctk = 0.7*fctm
    fctd = fctk*1.4*10**6
    #bw = bw*100
    #d = d*100
    print(f'fctd: {fctd}')
    print(f'bw: {bw}')
    print(f'd: {d}')
    Vc0 = 0.6*fctd*bw*d
    Vc0 = Vc0_tabela(fck*10**6)*bw*1000*d*1000
    if Vsd <= Vc0:
        return Vc0
    print(f'Vc0: {Vc0}')
    print(f'Vsd: {Vsd}')
    print(f'VRd2: {VRd2}')
    Vc1 = Vc0*((VRd2-Vsd)/(VRd2-Vc0))
    print(f'Vc1: {Vc1}')
    return Vc1

def Vc0_tabela(fck):
    tabela = {20: 0.66, 25: 0.77, 30: 0.87, 35: 0.96, 40: 1.05, 45: 1.14, 50: 1.22,
    50: 1.38, 60: 1.38, 70: 1.53, 75: 1.6, 80: 1.67, 85: 1.74, 90: 1.81}
    fck = int(fck/10**6)
    return tabela[fck]

def vrmin90(aswmin90, d, fyd, teta, Vc):
    """Valor em N"""
    aswmin90 = aswmin90 * 10**-2
    d = d*100
    fyd = fyd/10**5
    print(f'd: {d}')
    print(f'fyd: {fyd}')
    vmin = (1/1.4)*(0.9*aswmin90*d*fyd*(1/math.tan(math.radians(teta))) + Vc*10**-1)
    vmin = vmin*9.8
    print(f'vmin: {vmin}')
    return vmin

def conferir_aswmin(Vrmin90, Vsk):
    print(f'vrmin90: {Vrmin90}')
    print(f'Vsk: {Vsk}')
    if Vrmin90 > Vsk:
        print("Área minima pode ser adotada")
    else:
        print("Área minima não pode ser adotada")

def calcular_asw90(Vsd, Vc, d, fyd, teta):
    """Resultado em cm2/cm"""
    Vsd = Vsd * 0.1
    #Vc = Vc * 0.1
    Vsd = 1.4*10200
    Vc = 4280
    d = 0.54
    fyd = fyd/10**5
    print(f'Vsd: {Vsd}')
    print(f'Vc: {Vc}')
    asw90 = ((Vsd - Vc)/(0.9*d*fyd))*math.tan(math.radians(teta))
    print(f'aswmin90: {asw90}')
    return asw90

def espaçamento_estribo(asw, bitola):
    bt5 = [5.61, 4.91, 4.36, 3.93, 3.57, 3.27, 3.02, 2.81, 2.62, 2.45,
     2.31, 2.18, 2.07, 1.96, 1.87, 1.79, 1.71, 1.64, 1.57, 1.51, 1.45,
      1.4, 1.35, 1.31]
    bt63 = [8.91, 7.79, 6.93, 6.23, 5.67]


kmd = kmd_calc(Msd, bw, d, fcd)
sigmac, lambdac = sigma_lambda_calc(fck)
kx = kx_calc(kmd, sigmac, lambdac)
kz = kz_calc(lambdac, kx)
As = steel_area(Msd, d, fyd, kz)
amin = test_min_steelarea(bw, h, fck, As)
amin = test_max_steelarea(bw, h, fck, As)
As_cm = As * 10**4
x1, x2 = linha_neutra(d, Msd, bw, fcd, sigmac, lambdac)
x1_cm = x1 * 100
x2_cm = x2 * 100
dminimo = dmin(Msd, bw, fcd)
dminimo = dminimo*100
dom = dominio(kx, fck, fy)
nbarras, barras_por_bitola = desbitolagem(As, bitola)
print(f"barras por bitola {barras_por_bitola}")
print(f"nbarras {nbarras}")
camadas_tuple = distribuicao_max(bw, bitola, dt, dbrita, cnom, barras_por_bitola)
camadas_tuple_mm = [(item[0]*10**3, item[1]) for item in camadas_tuple]
print(camadas_tuple_mm)
eh_camadas = eh_por_camada( camadas_tuple, dt, cnom, bw)
d1 = d1_real(cnom, dt, camadas_tuple)
delta_teste(cnom, dt, h, camadas_tuple)
d_r = d_real(d1, h)
d_test(d1_est, d1)
ev = ev_min(bitola, dbrita)
ecu = ecu_calc(fck)
msd1 = msd1_calc(bw, d, fcd)
print(f"dmin:{dminimo:.2f}")
print(f"d1_real: {d1*100:.2f} cm")
print(f"d1_est: {d1_est*100:.2f} cm")
print(f"d_real: {d_r*100:.2f} cm")
print(f"kmd: {kmd:.3f}")
print("kx: {:.3f}".format(kx))
print("kz: {:.3f}".format(kz))
print(f"x1:{x1_cm:.2f}; x2:{x2_cm:.2f}")
print("As: {:.2f} cm2".format(As_cm))
#selecionadas = [8.0, 10.0, 12.5, 16.0, 20.0, 22.0]
#dic_barras = {}
#for i in selecionadas:
#    dic_barras[str(i)] = nbarras[str(i)]
#print(dic_barras)
print(f"eh:{[str(round(eh*100,3)) for eh in eh_camadas]}")
print(f"ev:{ev*100}")
if h>0.6:
    n, t = as_pele(bw, h, dt, ev, cnom, camadas_tuple)
    print("{} As de pele de cada lado, ev: {:.2f}".format(n, t*100))
    designer.draw_beam(int(bw*10**3), int(h*10**3), camadas_tuple_mm, dt*10**3, n)
else:
    designer.draw_beam(int(bw*10**3), int(h*10**3), camadas_tuple_mm, dt*10**3)
# os.system("xdg-open viga.png")
os.system("viga.png")
print("ARMADURA TRANSVERSAL".center(30, "-"))
vrd2 = VRd2(bw, d, 30, fck)
print(f'VRd2:{vrd2}')
aswmin = Aswmin(bw, fck)
print(f'Aswmin:{aswmin}')
vc = calculo_VC(Vsd, vrd2, bw, d, fck)
vc0 = Vc0_tabela(fck)
print(f'vc0:{vc0}')
vrmin = vrmin90(aswmin, d, fyd, 30, vc)
conferir_aswmin(vrmin, Vsk)
calcular_asw90(Vsd, vc, d, fyd, 30)