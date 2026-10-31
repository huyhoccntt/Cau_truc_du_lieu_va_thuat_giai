"""Tính SHA-256 theo khối, không nạp toàn bộ file vào RAM."""
import hashlib


def calculate_sha256(path, chunk_size=1024 * 1024):
    """Tính SHA-256 theo từng khối để giới hạn bộ nhớ sử dụng."""
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        while True:
            chunk = stream.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def files_equal(path_a, path_b, chunk_size=1024 * 1024):
    """So sánh kích thước rồi nội dung byte-for-byte theo từng khối."""
    try:
        import os
        # File khác kích thước không thể có nội dung giống hệt nhau.
        if os.path.getsize(path_a) != os.path.getsize(path_b):
            return False
        with open(path_a, "rb") as a, open(path_b, "rb") as b:
            while True:
                chunk_a = a.read(chunk_size)
                chunk_b = b.read(chunk_size)
                if chunk_a != chunk_b:
                    return False
                if not chunk_a:
                    return True
    except OSError:
        return False
