#!/home/estevao/Documentos/projetos-python/concreto/env/bin/python3
import math
from tkinter import W
import designer
import os

class Viga():
    """Classe Viga"""
    def __init__(self, bw, h, fck, fyk, Msk, Vsk, cobrimento, brita, dt, bitola, teta, caa=2, Tsk=0):
        self.bw = bw
        self.h = h
        self.fck = fck
        self.fyk = fyk
        self.Msk = Msk
        self.Vsk = Vsk
        self.Tsk = Tsk
        self.cobrimento = cobrimento
        self.brita = brita
        self.dt = dt
        self.bitola = bitola
        self.dic_caa = {1: 25, 2: 30, 3: 40, 4: 50}
        self.dic_brita = {1: 19, 2: 25, 3: 50, 4: 76}
        self.dbrita = self.dic_brita[brita]
        self.cnom = self.dic_caa[caa]
        self.teta = teta

    def processa_entrada(self):
        """Pre processamento"""
        self.d = self.h - self.bitola/2 - self.cobrimento - self.dt
        self.Msd = 1.4*self.Msk
        self.Vsd = 1.4*self.Vsk
        self.Tsd = 1.4*self.Tsk
        self.fcd = self.fck/1.4
        self.d1_est = self.h - self.d
    
    def conversoes_de_unidade(self):
        """Conversoes de unidades
        Padronização para as mesmas unidades
        """
        self.h = self.h*10**-3
        self.bw = self.bw*10**-3
        self.d = self.d*10**-3
        self.cobrimento = self.cobrimento*10**-3
        self.fck = self.fck*10**6  # Pa
        self.fcd = self.fcd*10**6  # Pa
        self.fyk = self.fyk*10**6
        self.fyd = self.fyk/1.15
        self.cnom = self.cnom*10**-3
        self.dbrita = self.dbrita*10**-3
        self.dt = self.dt*10**-3
        self.bitola = self.bitola*10**-3
        self.Msd = self.Msd*10**3  # N.m
        self.Vsd = self.Vsd*10**3  # N
        self.Vsk = self.Vsk*10**3  # N
        self.Tsd = self.Tsd*10**3  # N
        self.Tsk = self.Tsk*10**3  # N
        self.d1_est = self.d1_est*10**-3

    def sigma_lambda_calc(self):
        """
        Calcula o sigmac e o lambda c
        """
        # fck <= 50MPa
        fck = self.fck
        if fck <= 50*10**6:
            sigmac = 0.85
            lambdac = 0.8
        if fck > 50*10**6:
            fck = fck/(10**6)
            sigmac = 0.85*(1-(fck-50)/200)
            lambdac = 0.8 - (fck - 50)/400
        self.sigmac = sigmac
        self.lambdac = lambdac
        return sigmac, lambdac

    def kmd_calc(self):
        self.kmd = self.Msd/(self.bw*(self.d**2)*self.fcd)
        return self.kmd

    def kx_calc(self):
        self.sigmac, self.lambdac = self.sigma_lambda_calc()
        kx = (1 - (1 - 2*self.kmd/self.sigmac)**0.5)/self.lambdac
        self.kx = kx
        return self.kx 
    
    def kz_calc(self):
        kz = 1 - 0.5*self.lambdac*self.kx
        self.kz = kz
        return self.kz
    
    def steel_area(self):
        """m2"""
        As = self.Msd/(self.kz*self.d*self.fyd)
        self.As = As
        return self.As
    
    def linha_neutra(self):
        """
        Calcula a linha neutra
        """
        d, lambdac = self.d, self.lambdac
        Msd = self.Msd
        bw = self.bw
        fcd = self.fcd
        sigmac = self.sigmac
        a = math.sqrt(d**2-2*(Msd/(bw*fcd*sigmac)))
        x1 = (d + a)/lambdac
        x2 = (d - a)/lambdac
        self.x1 = x1
        self.x2 = x2
        return x1, x2
    
    def calcular_dmin(self):
        """
        Calcula o dmin necessário para viga
        """
        Msd, bw, fcd = self.Msd, self.bw, self.fcd
        fcd50 = (50*10**6)/1.4
        if fcd <= fcd50:
            kxlim = 0.45
        else:
            kxlim = .35
        d = math.sqrt(Msd/(bw*fcd*(0.68*kxlim-0.272*kxlim**2)))
        self.dmin = d
        return d

    # deformacao ultima do concreto
    def ecu_calc(self):
        fck = self.fck
        fck = fck/10**6  # Pa
        # 20, 50, 90
        if fck <= 50:
            ecu = 3.5
        else:
            ecu = 2.6 + 35*((90-fck)/100)**4
        self.ecu = ecu
        return ecu
    
    def dominio(self):
        kx, fck, fy = self.kx, self.fck, self.fyk
        ecu = self.ecu_calc()
        fy = int(fy/10**7)
        dic_eyd = {25: 1.035, 50: 2.070, 60: 2.484}
        eyd = dic_eyd[fy]
        if kx < 0:
            n_dominio = 1
        elif kx > 0 and kx <= ecu/(ecu+10):
            n_dominio = 2
        elif kx >= ecu/(ecu+10) and kx < ecu/(ecu + eyd):
            n_dominio = 3
        elif kx >= ecu/(ecu+eyd) and kx <= 1:
            n_dominio = 4
        self.n_dominio = n_dominio
        return n_dominio

    def teste_dutilidade(self) -> str:
        fck, kx = self.fck, self.kx
        fck = fck/10**6
        if fck <= 50 and kx <= 0.45:
            return "OK"
        elif fck > 50 and kx <= 0.35:
            return "OK"
        else:
            return "Não OK"

    def teste_armadura_dupla(self) -> tuple[int, str]:
        fck, kx = self.fck, self.kx
        sigmac, lambdac = self.sigma_lambda_calc()
        kmd = self.kmd_from_kx()
        if self.armadura_dupla_viavel():
            return (1, "viável")
        else:
            return (0, "não viável")

    def desbitolagem(self):
        As, bitola = self.As, self.bitola
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
        porcentagem = math.floor(qt_barras)*area_por_bitola[bitola*10**3]/(As*10**4)
        value = qt_barras
        # Tolerancia de diferença de áreas
        if porcentagem >= 0.9:
            qt_barras = math.floor(value)
        else:
            qt_barras = math.ceil(value)
        barras_por_bitola = [(bitola, qt_barras)]
        self.nbarras, self.barras_por_bitola = nbarras, barras_por_bitola
        return nbarras, barras_por_bitola

    def ev_min(self):
        bitola, dbrita = self.bitola, self.dbrita
        ev = 20 * 10**-3
        if bitola > ev:
            ev = bitola
        elif 0.5*dbrita > ev:
            ev = 0.5*dbrita
        self.ev = ev
        return ev

    def eh_min(self):
        bitola, dbrita = self.bitola, self.dbrita
        eh = 20 * 10**-3
        if bitola > eh:
            eh = bitola
        elif 1.2*dbrita > eh:
            eh = 1.2*dbrita
        self.eh = eh
        return eh


    def calcular_bwmin(self, numero_barras):
        dbitola, dt, dbrita, cnom = self.bitola, self.dt, self.dbrita, self.cnom
        a = self.eh_min()
        bs = numero_barras*dbitola + (numero_barras-1)*a
        bwmin = bs + 2*(dt + cnom)
        self.bwmin = bwmin
        return bwmin


    def distribuicao_max(self):
        bw, bitola, dt, dbrita, cnom, barras_por_bitola = self.bw, self.bitola, self.dt, self.dbrita, self.cnom, self.barras_por_bitola
        # maximo de barra por camada
        camadas_tuple = []
        for bpb in barras_por_bitola:
            #bitola_str = str(bitola*10**3)
            bitola = bpb[0]
            n = bpb[1]
            barra_max = n
            bitola_str = str(bitola*10**3)
            #bwm = bwmin(bitola, dt, dbrita, nbarras[bitola_str], cnom)
            bwm = self.calcular_bwmin(n)
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
                    bwm = self.calcular_bwmin(n)
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
        self.camadas_tuple = camadas_tuple
        return camadas_tuple

    def yc_calc(self):
        camadas_tuple = self.camadas_tuple
        soma = 0
        area_total = 0
        for i, camada in enumerate(camadas_tuple):
            bitola = camada[0]
            barras = camada[1]
            a = self.ev_min()
            abitola = math.pi*(bitola/2)**2
            soma += barras*abitola*((bitola/2)+a*i+bitola*i)
            area_total += barras*abitola
        yc = soma/area_total
        self.yc = yc
        return yc


    def calcular_d1_real(self):
        cnom, dt, camadas_tuple = self.cnom, self.dt, self.camadas_tuple
        yc = self.yc_calc()
        d1 = cnom + dt + yc
        self.d1 = d1
        self.d1_real = d1
        return d1


    def calcular_d_real(self):
        d1, h = self.d1, self.h
        self.d_real = h-d1
        return h-d1


    def d_test(self):
        d1_est, d1_real = self.d1_est, self.d1_real
        c = d1_real/d1_est
        if c <= 1.10:
            # print("d1real/dest <= 1.10 OK => {:.3f}".format(c))
            return 1
        else:
            # print("Difereca maior que 1.10 => {:.3f}".format(c))
            return 0


    def eh_por_camada(self):
        camadas_tuple, dt, cnom, bw = self.camadas_tuple, self.dt, self.cnom, self.bw
        eh_list = []
        a = 0
        for camada in camadas_tuple:
            bitola = camada[0]
            n = camada[1]
            if n > 1:
                a = (bw-2*cnom-2*dt-n*bitola)/(n-1)
            elif n == 1:
                a = bw - 2*cnom-2*dt-bitola
            elif n < 1:
                continue
            eh_list.append(a)
        self.eh_list = eh_list
        return eh_list


    def delta_teste(self) -> tuple[int, str]:
        """Verifica se a tensão é aplicada
        no cg"""
        cnom, dt, h, camadas_tuple = self.cnom, self.dt, self.h, self.camadas_tuple
        yc = self.yc_calc()
        if yc <= 0.1*h:
            # print("tensao centrada no cg OK")
            return (1, "ok")
        else:
            # print("Não passou no delta teste")
            return(0, "não ok")


    def test_min_steelarea(self) -> str:
        bw, h, fck, As = self.bw, self.h, self.fck, self.As
        fck = str(int(fck/(10**6)))
        tx_min = {'20': 0.15, '25': 0.15, '30': 0.15, '35': 0.164, '40': 0.179,
                '45': 0.195, '50': 0.208, '55': 0.211, '60': 0.219, '65': 0.226,
                '70': 0.233, '75': 0.239, '80': 0.245, '85': 0.251, '90': 0.256}
        asmin = (tx_min[fck]/100)*bw*h
        if As >= asmin:
            return "OK"
        else:
            return "Não Ok"


    def test_max_steelarea(self) -> str:
        bw, h, fck, As = self.bw, self.h, self.fck, self.As
        if As <= (4/100)*(bw*h):
            return "OK"
        else:
            return "Não OK"


    def barra_int(self, value):
        "Retorna a quantidade de barra com o valor inteiro"
        decimal = abs(value - int(value))
        if decimal <= 0.15 and value >= 1:
            value = math.floor(value)
        else:
            value = math.ceil(value)
        return value


    def as_pele(self):
        """
        Calcula a armadura de pele
        e o espacamento entre elas
        """
        bw, h, dt, ev, cnom, camadas_tuple = (self.bw, self.h, self.dt,
        self.ev, self.cnom, self.camadas_tuple)
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
            n = self.barra_int(n)

            t = J/(n+1)
            if t > 0.2:
                print("Nao OK, t > 20cm")
            if t > self.d/3:
                print("Nao OK, t > d/3")
            if t > 15*bitola:
                print(f"O t {t}")
                print(f"bitola *15 {bitola*15}")
                print("t não OK")

        else:
            print("Não precisa de As de pele")
        self.n, self.t = n, t
        return(n, t)

    def kmd_from_kx(self):
        kx, sigmac, lambdac = self.kx, self.sigmac, self.lambdac
        kmd =-(sigmac/2)*((kx*lambdac-1)**2-1)
        return kmd


    def msd1_calc(self):
        """Msd1 da armadura dupla"""
        bw, d, fcd, kmdlim = self.bw, self.d, self.fcd, 0.251
        msd1 = kmdlim*bw*(d**2)*fcd
        self.msd1 = msd1
        return msd1


    def msd2_calc(self):
        """Msd1 da armadura dupla"""
        Msd, msd1 = self.Msd, self.msd1
        msd2 = Msd - msd1
        self.msd2 = msd2
        return msd2


    def armadura_dupla_viavel(self):
        """Se for possivel o uso
        de armadura dupla retorna true"""
        kmd = self.kmd
        if kmd <= 0.425:
            return True
        else:
            return False


    def esdl(self):
        ecu, d2, d, kxlim = self.ecu, self.d2, self.d, 0.45
        esd = ecu*(kxlim-d2/d)/kxlim
        self.esd = esd
        return esd


    def sigmas_calc(self):
        """
        Funcao para obter a tensao
        no aco do valor da deformacao
        """
        es, fyk = self.es, self.fyk
        fyd = self.fyk/1.15
        aco = int(self.fyk/10**7)
        eyd_dic = {25: 1.035, 50: 2.070, 60: 2.484}
        eyd = eyd_dic[aco]
        if es >= eyd and es <= 10:
            sigmas = fyd
        elif es >= 0 and es <= eyd:
            Es = 2.1*10**5
            sigmas = Es*es
        self.sigmas = sigmas
        return sigmas
    
    # Cálculo da Armadura Transveral

    def calculo_VRd2(self):
        bw, d, fck, teta = self.bw, self.d, self.fck, self.teta
        # Valor em N
        fcd = fck/1.4
        sigma2 = 1-(fck/10**6)/250
        bw = bw*10**3
        d = d*10**3
        fcd = fcd/(10**6)
        self.VRd2 =  0.27*sigma2*fcd*bw*d*math.sin(math.radians(2*self.teta))
        return self.VRd2

    def calculo_Aswmin(self):
        """Area de aço mínima transversal"""
        # cm2/cm
        bw, fck = self.bw, self.fck
        bw = bw*100
        fck = fck/(10**6)
        fctm = 0.3 * fck**(2/3)
        self.Aswmin = 4*bw*fctm*10**(-4)*10**2
        return self.Aswmin

    def Vc0_tabela(self):
        fck = self.fck
        tabela = {20: 0.66, 25: 0.77, 30: 0.87, 35: 0.96, 40: 1.05, 45: 1.14, 50: 1.22,
        50: 1.38, 60: 1.38, 70: 1.53, 75: 1.6, 80: 1.67, 85: 1.74, 90: 1.81}
        fck = int(fck/10**6)
        return tabela[fck]

    def calcular_fctm(self) -> float:
        """N/m2"""
        # Convertendo MPa
        fck = self.fck/(10**6)
        fctm = 0.3*fck**(2/3)
        # Convertendo novamente N/m2
        self.fctm = fctm*10**6
        return self.fctm

        
    def calculo_VC(self):
        """Cálculo do VC através do Vc0
        Resultado em N
        """
        Vsd, VRd2, bw, d, fck = self.Vsd, self.VRd2, self.bw, self.d, self.fck
        fck = fck/(10**6)
        print(f'fck que quero veeeeeeeeer {fck}')
        fctm = 0.3*fck**(2/3)
        fctd = 0.7*fctm/1.4
        print(f"fctd ===========AQUI===============> {fctd}")
        bw = bw*1000
        d = d *1000
        print(f'bw: {bw}')
        print(f'd: {d}')
        print(f'fctd: {fctd}')
        Vc0 = 0.6*fctd*bw*d
        print(f"Vc0 ===========AQUI===============> {Vc0}")
        #Vc0 = self.Vc0_tabela()*bw*1000*d*1000
        if Vsd <= Vc0:
            self.Vc = Vc0
            return Vc0
        print(f'Vc0: {Vc0}')
        print(f'Vsd: {Vsd}')
        print(f'VRd2: {VRd2}')
        Vc1 = Vc0*((VRd2-Vsd)/(VRd2-Vc0))
        print(f'Vc1: {Vc1}')
        self.Vc = Vc1
        return Vc1

    
    def calculo_vrmin90(self):
        """Valor em N"""
        aswmin90, d, fyd, teta, Vc = self.Aswmin, self.d, self.fyd, self.teta, self.Vc
        aswmin90 = aswmin90 * 10**-2
        d = d*100
        fyd = fyd/10**5
        print(f'd: {d}')
        print(f'fyd: {fyd}')
        vmin = (1/1.4)*(0.9*aswmin90*d*fyd*(1/math.tan(math.radians(teta))) + Vc*10**-1)
        vmin = vmin*9.8
        print(f'vmin: {vmin}')
        self.vrmin90 = vmin
        return vmin

    def conferir_aswmin(self) -> str:
        Vrmin90, Vsk = self.vrmin90, self.Vsk
        print(f'vrmin90: {Vrmin90}')
        print(f'Vsk: {Vsk}')
        if Vrmin90 > Vsk:
            return "Pode ser adotada"
        else:
            return "não pode ser adotada"

    def calcular_asw90(self):
        Vsd, Vc, d, fyd, teta = self.Vsd, self.Vc, self.d, self.fyd, self.teta
        """Resultado em cm2/cm"""
        fyd = fyd/10**5
        Vsd = Vsd /10
        Vc = Vc /10

        print(f'Vsd: {Vsd}')
        print(f'Vc: {Vc}')
        print(f"=============> teta {self.teta}")
        asw90 = ((Vsd - Vc)/(0.9*d*fyd))*math.tan(math.radians(30))
        print(f'asw90 ==================>: {asw90}')
        self.asw90 = asw90
        return asw90

    def espaçamento_estribo(self):
        asw90, dt = self.asw90, self.dt
        bt5 = [5.61, 4.91, 4.36, 3.93, 3.57, 3.27, 3.02, 2.81, 2.62, 2.45,
        2.31, 2.18, 2.07, 1.96, 1.87, 1.79, 1.71, 1.64, 1.57, 1.51, 1.45,
        1.4, 1.35, 1.31]
        bt63 = [8.91, 7.79, 6.93, 6.23, 5.67]
    
    # Cálculo da armadura de Torção
    def calcular_area_da_viga(self):
        self.area_viga = self.bw*self.h
        return self.area_viga
    
    def calcular_perimetro_da_viga(self):
        self.u_perimetro_viga = 2*(self.bw+self.h)
        return self.u_perimetro_viga 
    
    def calcular_he(self):
        """Espessura da parede fina"""
        self.calcular_area_da_viga()
        self.calcular_perimetro_da_viga()
        he1 = self.area_viga/self.u_perimetro_viga
        print(f"Valor do cobrimento dentro de {self.cobrimento}")
        self.c1 = (self.bitola/2)+self.dt+self.cobrimento
        c1 = self.c1
        he2 = c1*2
        print(f"Valor de c1 {c1}")
        he = 0
        if he1 >= he2:
            he = he1
        else:
            h3 = self.bw - 2*c1
            print(f"Valor de h3 {h3}")
            print(f"Valor de he1 {he1}")
            if he1 <= h3:
                he = he1
            else:
                print("Espessura da casca não atende!")
        print(f"O valor de he é {he}")
        self.he = he
        return self.he
    
    def calcular_Ae(self):
        "Área interna m2"
        self.Ae = (self.bw - 2*self.c1)*(self.h-2*self.c1)
        print(f"=======> Valor de Ae {self.Ae*10**4}")
        return self.Ae
    
    def calcular_ue(self):
        """Perímetro da área equivalente"""
        self.ue = 2*((self.bw-2*self.c1)+(self.h-self.c1))
        return self.ue
    
    def calcular_TRd2(self, teta=45):
        "N.m"
        fck = self.fck
        # Valor em N
        fcd = fck/1.4
        sigma2 = 1-(fck/10**6)/250
        # fcd = fcd/(10**6)
        self.TRd2 = 0.5*sigma2*self.fcd*self.Ae*self.he*math.sin(math.radians(teta*2))
        print(f"=========> TRD2: {self.TRd2/10**3} kN.m")
        return self.TRd2
    
    def verificar_bielas(self) -> None:
        """Verifica a resistência das bielas
        de concreto"""
        v = (self.Vsd/self.VRd2) + self.Tsd/self.TRd2
        if v <= 1:
            print("Bielas na torção OK")
        else:
            print("Bielas na torção Não OK")
    
    # Cálculo das armaduras mínimas para torçao

    def calcular_Asmin_longitudinal_torcao(self) -> float:
        """Unidade: cm2/cm"""
        self.calcular_fctm()
        fy_local = self.fyk/10**7
        fctm_mpa = self.fctm/10**6

        self.Asmin_longitudinal_torcao = 20*(fctm_mpa*0.1)*self.he*100/fy_local
        print(f"ASMINLONGITUDINAL {self.Asmin_longitudinal_torcao}")
        return self.Asmin_longitudinal_torcao

    def calcular_Asmin_transveral_torcao(self) -> float:
        """Unidade: cm2/m"""
        self.calcular_fctm()
        fy_local = self.fyk/10**7
        fctm_mpa = self.fctm/10**6

        self.Asmin_transveral_torcao = 20*(fctm_mpa*0.1)*self.bw*100/fy_local
        print(f"ASMINTRANSVERAL {self.Asmin_transveral_torcao}")
        return self.Asmin_transveral_torcao

    def calcular_As_longitudinal_torcao(self) -> float:
        """cm2/cm"""
        print("As longitudinal torcao".center(100,"-"))
        Tsd_local = self.Tsd/10
        Ae_local = self.Ae*10**4
        fyd_local = self.fyd/10**7
        self.As_longitudinal_torcao = Tsd_local/(2*Ae_local*fyd_local*math.tan(math.radians(self.teta)))
        print(f"As longitudinal de torcao: {self.As_longitudinal_torcao}")
        return self.As_longitudinal_torcao
        
    def calcular_As_transversal_torcao(self) -> float:
        """cm2/cm"""
        print("As transversal torcao".center(100,"-"))
        Tsd_local = self.Tsd/10
        Ae_local = self.Ae*10**4
        fyd_local = self.fyd/10**7
        self.As_transversal_torcao = (Tsd_local/(2*Ae_local*fyd_local))*math.tan(math.radians(self.teta))
        print(f"As transversal de torcao: {self.As_transversal_torcao}")
        return self.As_transversal_torcao
    
    def verificar_Asmin_longitudinal_torcao(self):
        Aslong_cm2_m = self.As_longitudinal_torcao*100
        if Aslong_cm2_m > self.Asmin_longitudinal_torcao:
            print("Armadura minima longitudinal de torcao ok")
        else:
            print("Armadura minima longitudinal de torcao NÃO OK")

    def verificar_Asmin_transversal_torcao(self) -> None:
        """Verifica o atendimento da Asmin para armadura 
        Transversal"""
        Astrans_cm2_m = self.As_transversal_torcao*100
        if Astrans_cm2_m > self.Asmin_transveral_torcao:
            print("Armadura minima transversal de torcao OK")
        else:
            print("Armadura minima transversal de torcao NÃO OK")

    
    def calcular_Aslong_resultante_face_tracionada(self) -> float:
        """
        Calcula a Área longitudinal resultante 
        Longitunal + Torção
        Resultado em cm2
        """
        print(f"bw {self.bw*100}")
        print(f"2c1 {self.c1*2*100}")
        As_torcao = (self.bw*100 - 2 * self.c1*100)*self.As_longitudinal_torcao
        As_long = self.As*10**4
        self.Aslong_face_tracionada_total = As_torcao + As_long
        print(f"As torcao longitudinal tracionada resultante ==============================>: {self.Aslong_face_tracionada_total} cm2")
        return self.Aslong_face_tracionada_total
    
    def calcular_Aslong_resultante_face_comprimida(self) -> float:
        """
        Calcula a Área longitudinal resultante 
        Longitunal + Torção
        Resultado em cm2
        """
        As_torcao = (self.bw*100 - 2 * self.c1*100)*self.As_longitudinal_torcao
        self.Aslong_face_comprimida_total = As_torcao
        print(f"As torcao longitudinal comprimida resultante ==============================>: {self.Aslong_face_comprimida_total} cm2")
        return self.Aslong_face_comprimida_total

    def calcular_Aslong_resultante_face_lateral(self) -> float:
        """
        Calcula a Área longitudinal resultante 
        Longitunal + Torção
        Resultado em cm2
        """
        As_torcao = (self.h*100 - 2 * self.c1*100)*self.As_longitudinal_torcao
        self.Aslong_face_lateral_total = As_torcao
        print(f"As torcao longitudinal lateral resultante 1 lado ==============================>: {self.Aslong_face_lateral_total} cm2")
        return self.Aslong_face_lateral_total
    
    def calcular_As_transversal_total(self) -> float:
        """
        Calculo de estribos resultante
        Transversal + estribos de torção
        cm2/cm
        """
        if self.conferir_aswmin() == 'Pode ser adotada':
            asw_puro = self.Aswmin
            print("Foi o minimo")
        else:
            asw_puro = self.asw90
        asw_puro = asw_puro/2
        print(f'asw_puro {asw_puro}')
        print(f'torcao {self.As_transversal_torcao}')
        aswtotal = asw_puro/100 + self.As_transversal_torcao
        print(f"As torcao transversal total ==============================>: {aswtotal} cm2/cm")
        return aswtotal

       
    def calcular_torcao(self) -> None:
        self.calcular_he()
        self.calcular_Ae()
        self.calcular_ue()
        self.calcular_TRd2()
        self.verificar_bielas()
        self.calcular_Asmin_longitudinal_torcao()
        self.calcular_Asmin_transveral_torcao()
        self.calcular_As_longitudinal_torcao()
        self.calcular_As_transversal_torcao()
        self.verificar_Asmin_longitudinal_torcao()
        self.verificar_Asmin_transversal_torcao()
        self.calcular_Aslong_resultante_face_tracionada()
        self.calcular_Aslong_resultante_face_comprimida()
        self.calcular_Aslong_resultante_face_lateral()
        self.calcular_As_transversal_total()
        return

    def desenhar_viga(self) -> None:
        """Desenha a viga Resultante"""
        camadas_tuple = self.distribuicao_max()
        camadas_tuple_mm = [(item[0]*10**3, item[1]) for item in camadas_tuple]
        if self.h>0.6:
            n, t = self.as_pele()
            print("{} As de pele de cada lado, ev: {:.2f}".format(n, t*100))
            designer.draw_beam(int(self.bw*10**3), int(self.h*10**3), camadas_tuple_mm, self.dt*10**3, n)
        else:
            designer.draw_beam(int(self.bw*10**3), int(self.h*10**3), camadas_tuple_mm, self.dt*10**3)
    

    def dimensionar_viga(self):
        self.processa_entrada()
        self.conversoes_de_unidade()
        self.kmd_calc()
        self.kx_calc()
        self.kz_calc()
        self.steel_area()
        self.dominio()
        self.desbitolagem()
        self.distribuicao_max()
        self.eh_por_camada()
        self.ev_min()
        self.desenhar_viga()
        self.calculo_VRd2()
        self.calculo_Aswmin()
        self.calculo_VC()
        self.calculo_vrmin90()
        self.conferir_aswmin()
        self.calcular_asw90()
        self.calcular_torcao()
