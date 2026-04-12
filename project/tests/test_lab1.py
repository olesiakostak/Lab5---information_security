import unittest
from math import pi as math_pi
from services.lcg import LCG
from services.cesaro import cesaro_test
#python -m unittest discover -s tests

class TestLab1(unittest.TestCase):
    
    def setUp(self):
        self.m = (2**13) - 1
        self.a = 5**5
        self.c = 3
        self.x0 = 16
        self.lcg = LCG(m=self.m, a=self.a, c=self.c, seed=self.x0)

    def test_generation(self):
        result = self.lcg.generate(5)
        expected = [857, 7862, 3944, 5739, 4279]
        self.assertEqual(result, expected)

    def test_analysis(self):
        nums = self.lcg.generate(1000)
        pi_val, err = cesaro_test(nums)
        
        req_pi = 3.10086836473
        req_err = abs(math_pi - req_pi)
        
        error_1 = abs(pi_val - req_pi)
        error_2 = abs(err - req_err)
        
        x = error_1 <= 0.00001 and error_2 <= 0.00001
        self.assertTrue(x)

    def test_period(self):
        period = self.lcg.calculatePeriod(self.m)
        self.assertEqual(period, 273)

if __name__ == '__main__':
    unittest.main()