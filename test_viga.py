import unittest
from elementoViga import Viga


class TestViga(unittest.TestCase):
    """Testes da Viga"""
    def setUp(self):
        self.viga1 = Viga(bw=150, h=440, fck=20, fyk=500, Msk=50, Vsk=0,
        cobrimento=25, brita=1, dt=5, bitola=10, teta=30, Tsk=0)
        self.viga1.dimensionar_viga()
    
    def test_as_longitudinal_pura(self) -> None:
        """
        Teste da armadura longitudinal pura
        """
        As = float(f"{self.viga1.As*10**4:.2f}")
        self.assertEqual(As, 4.6)

    def test_dominio(self) -> None:
        """Testa o domínio da viga"""
        self.assertEqual(int(self.viga1.dominio()), 3)
    
    def test_kx(self) -> None:
        """Testa o valor de kx"""
        self.assertEqual(f"{self.viga1.kx:.2f}", "0.34")
    
    def test_asmin_longitudinal(self) -> None:
        """Testa a armadura minima"""
        self.assertEqual(self.viga1.test_min_steelarea(), "OK")



if __name__ == '__main__':
    unittest.main()