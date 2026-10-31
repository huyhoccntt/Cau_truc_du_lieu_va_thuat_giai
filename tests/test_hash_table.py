import unittest
from core.hash_table import HashTable


class HashTableTests(unittest.TestCase):
    def test_insert_and_get(self):
        table = HashTable(2)
        table.set("a", 1)
        table.set("b", 2)
        self.assertEqual(table.get("a"), 1)
        self.assertEqual(table.get("b"), 2)

    def test_update(self):
        table = HashTable(2)
        table.set("a", 1)
        table.set("a", 9)
        self.assertEqual(table.get("a"), 9)
        self.assertEqual(table.size, 1)

    def test_resize(self):
        table = HashTable(2)
        for i in range(100):
            table.set(f"k{i}", i)
        for i in range(100):
            self.assertEqual(table.get(f"k{i}"), i)


if __name__ == "__main__":
    unittest.main()
