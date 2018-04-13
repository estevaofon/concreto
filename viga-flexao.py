# Entrada de dados
# bw h d -> cm
bw = 15
d = 40
# M -> kN.m
M = 50
# fck -> MPa
fck = 20
fy = 500
fyd = fy/1.15

# Conversoes
bw = bw*10**-2  # metros
d = d*10**-2
M = M*10**3  # N.m
fck = fck*10**6  # Pa
fyd = fyd*10**6

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


kmd = kmd_calc(Msd, bw, d, fcd)
sigmac, lambdac = sigma_lambda_calc(fck)
kx = kx_calc(kmd, sigmac, lambdac)
kz = kz_calc(lambdac, kx)
As = steel_area(Msd, d, fyd)
As_cm = As * 10**4

print(f"kmd: {kmd:.3f}")
print("kx: {:.3f}".format(kx))
print("kz: {:.3f}".format(kz))
print("As: {:.3f} cm2".format(As_cm))
