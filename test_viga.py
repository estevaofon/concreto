import unittest
from elementoViga import Viga


class TestViga(unittest.TestCase):
    """Testes da Viga"""
    def setUp(self):
        # Viga 1 testa a armadura longitudinal
        # Exemplo do Teatini
        self.viga1 = Viga(bw=150, h=440, fck=20, fyk=500, Msk=50, Vsk=0,
        cobrimento=25, brita=1, dt=5, bitola=10, teta=30, Tsk=0)
        self.viga1.dimensionar_viga()
        # Viga 2 testa a armadura longitudinal
        # Exemplo do chust
        self.viga2 = Viga(bw=120, h=330, fck=20, fyk=500, Msk=12.2, Vsk=0,
        cobrimento=25, brita=1, dt=5, bitola=8, teta=30, Tsk=0)
        self.viga2.dimensionar_viga()
        #Viga 3 testa a armadura transveral
        self.viga3 = Viga(bw=200, h=600, fck=20, fyk=500, Msk=90, Vsk=60,
        cobrimento=25, brita=1, dt=5, bitola=16, teta=30, Tsk=0)
        self.viga3.dimensionar_viga()
        #Viga 4 testa a armadura transveral
        self.viga4 = Viga(bw=200, h=600, fck=20, fyk=500, Msk=189, Vsk=126,
        cobrimento=25, brita=1, dt=5, bitola=20, teta=30, Tsk=0)
        self.viga4.dimensionar_viga()
    
    def test_as_longitudinal_pura(self) -> None:
        """
        Teste da armadura longitudinal pura
        """
        As = float(f"{self.viga1.As*10**4:.2f}")
        self.assertEqual(As, 4.6)

        As2 = float(f"{self.viga2.As*10**4:.2f}")
        self.assertEqual(As2, 1.43)

    def test_dominio(self) -> None:
        """Testa o domínio da viga"""
        self.assertEqual(int(self.viga1.dominio()), 3)
        self.assertEqual(int(self.viga2.dominio()), 2)
    
    def test_kx(self) -> None:
        """Testa o valor de kx"""
        self.assertEqual(f"{self.viga1.kx:.2f}", "0.34")
        self.assertEqual(f"{self.viga2.kx:.2f}", "0.18")
    
    def test_asmin_longitudinal(self) -> None:
        """Testa a armadura minima"""
        self.assertEqual(self.viga1.test_min_steelarea(), "OK")
        self.assertEqual(self.viga2.test_min_steelarea(), "OK")
    
    # Testes da armadura Transversal

    def test_Vrd2(self) -> None:
        """Testa o valor de Vrd2"""
        self.assertEqual(f"{self.viga3.VRd2:.0f}", "345422")
    
    def test_conferir_aswmin(self) -> None:
        """Testa o método conferir aswmin"""
        self.assertEqual(self.viga3.conferir_aswmin(), "Pode ser adotada")

    def test_Aswmin(self) -> None:
        """Testa o valor aswmin"""
        self.assertEqual(f"{self.viga3.Aswmin:.2f}", "1.77")
    
    def test_Vc(self) -> None:
        """Testa o valor do Vc"""
        self.assertEqual(f"{self.viga4.Vc:.0f}", "46169")

    def test_asw90(self) -> None:
        """Testa o valor do asw90"""
        self.assertEqual(f"{self.viga4.asw90:.2f}", "3.43")

    def test_bielac_comprimida_transversal(self) -> None:
        """Testa o valor do asw90"""
        self.assertEqual(self.viga4.verificar_bielas_transversal(), "OK")

if __name__ == '__main__':
    unittest.main()