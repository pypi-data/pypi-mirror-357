import unittest
from dikshantdata.generator import generate
import pandas as pd

class TestDataGen(unittest.TestCase):
    def test_default(self):
        df = generate("students")
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 10)

    def test_custom(self):
        df = generate("employees", rows=5, columns=6)
        self.assertEqual(len(df), 5)
        self.assertEqual(df.shape[1], 6)

    def test_invalid(self):
        with self.assertRaises(Exception):
            generate("invalid_table")
    def test_students_generation():
        df = generate("students", rows=5, columns=5)
        assert not df.empty

    def test_players_generation():
        df = generate("players", rows=3, columns=4)
        assert not df.empty

    def test_movies_generation():
        df = generate("movies", rows=2, columns=5)
        assert "title" in df.columns

if __name__ == '__main__':
    unittest.main() 
