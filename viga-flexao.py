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
print(fyd)

# Conversoes
bw = bw*10**-2  # metros
d = d*10**-2
M = M*10**3  # N.m
fck = fck*10**6  # Pa
fyd = fyd*10**6

# Calculos
fcd = fck/1.4
Msd = 1.4*M
kmd = Msd/(bw*(d**2)*fcd)
print("kmd: {:.3f}".format(kmd))
sigmac = 0.85
lambdac = 0.8

# fck > 50MPa
if fck > 50*10**6:
    fck = fck/(10**6)
    sigmac = 0.85*(1-(fck-50)/200)
    lambdac = 0.8 - (fck - 50)/400

kx = (1 - (1 - 2*kmd/sigmac)**0.5)/lambdac
kz = 1 - 0.5*lambdac*kx
print("kx: {:.3f}".format(kx))
print("kz: {:.3f}".format(kz))

As = Msd/(kz*d*fyd)
As_cm = As * 10**4
print("As: {:.3f} cm2".format(As_cm))
