import unittest
from harenpp import HAREN

class TestHAREN(unittest.TestCase):
    def test_basic_search(self):
        arr = [5, 3, 9, 1, 7]
        haren = HAREN(arr)
        for i, val in enumerate(arr):
            self.assertEqual(haren.search(val), i)

    def test_search_not_found(self):
        arr = [2, 4, 6, 8]
        haren = HAREN(arr)
        self.assertEqual(haren.search(5), -1)

if __name__ == '__main__':
    unittest.main()
