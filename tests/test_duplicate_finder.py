"""Kiểm thử việc tìm nhóm file giống nội dung và loại file chỉ cùng kích thước."""

import os
import tempfile
import unittest
from core.duplicate_finder import find_duplicates


class DuplicateFinderTests(unittest.TestCase):
    """Các ca kiểm thử tích hợp cho quy trình tìm file trùng."""

    def test_finds_only_identical_content(self):
        """Nhận diện file giống byte, gồm cả file rỗng, không chỉ cùng kích thước."""
        with tempfile.TemporaryDirectory() as root:
            a = os.path.join(root, "a.txt")
            b = os.path.join(root, "renamed.txt")
            c = os.path.join(root, "same_size_different.txt")
            empty1 = os.path.join(root, "empty1")
            empty2 = os.path.join(root, "empty2")
            with open(a, "wb") as f:
                f.write(b"same content")
            with open(b, "wb") as f:
                f.write(b"same content")
            with open(c, "wb") as f:
                f.write(b"other conten")  # same byte length
            open(empty1, "wb").close()
            open(empty2, "wb").close()

            result = find_duplicates(root)
            path_groups = [set(g["paths"]) for g in result["groups"]]
            self.assertIn({a, b}, path_groups)
            self.assertIn({empty1, empty2}, path_groups)
            self.assertFalse(any(c in group for group in path_groups))


if __name__ == "__main__":
    unittest.main()
