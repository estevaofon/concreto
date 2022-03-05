import unittest
from elementoViga import Viga


class TestViga(unittest.TestCase):
    """Testes da Viga"""
    def setUp(self):
        pass
    
    def test_as_longitudinal_pura(self):
        """
        Teste da armadura longitudinal pura
        """
        viga = Viga(bw=150, h=440, fck=20, fyk=500, Msk=50, Vsk=0,
        cobrimento=25, brita=1, dt=5, bitola=10, teta=30, Tsk=0)
        viga.dimensionar_viga()
        As = float(f"{viga.As*10**4:.2f}")
        self.assertEqual(As, 4.6)

if __name__ == '__main__':
    unittest.main()