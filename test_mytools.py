"""
test_mytools.py
A collection of unit tests for parts of the mytools module.
"""
import unittest
import inspect
import mytools as mt
__author__ = 'cotejrp'


class MyToolTests(unittest.TestCase):

    def setUp(self):
        pass

    def test_nudir(self):
        res = mt.nudir(inspect)
        self.assertTrue(len(res) > 0)

    def test_fdir(self):
        res = mt.fdir(inspect, "code")
        self.assertTrue(len(res) > 0)

    def test_varkey(self):
        res = mt.varkey(inspect)
        self.assertTrue(len(res) > 0)

    def test_rest_call(self):
        base_url = "https://www.khanacademy.org"
        api_call = "api/v1/badges"
        res = mt.rest_call(base_url, api_call)
        self.assertTrue(len(res) > 0)

    def test_simple_send(self):
        gen = (x for x in range(5))
        send = mt.simple_send(gen)
        self.assertIsNotNone(send)
        result = send()
        self.assertIsNotNone(result)

    def test_get_randomizer(self):
        ran = mt.get_randomizer()
        self.assertIsNotNone(ran)
        ran_num = ran.choice([3, 6, 8, 9, 1])
        self.assertIsNotNone(ran_num)

    def test_extension_finder(self):
        res = mt.extension_finder(".", "py")
        self.assertIsNotNone(res)
        self.assertTrue(len(list(res)) > 0)

    def test_dump_dataset(self):
        test_data = [("here", "lies", "dragons"), ("there", "lies", "snails")]
        mt.dump_dataset(test_data)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
