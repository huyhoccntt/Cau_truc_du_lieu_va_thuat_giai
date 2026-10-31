"""Bảng băm tự cài đặt bằng Separate Chaining.

Lưu ý: Python hash() chỉ dùng để ánh xạ khóa vào bucket trong lần chạy hiện tại.
Khóa nhận từ ứng dụng là chuỗi SHA-256; không dùng hash() thay cho SHA-256.
"""


class HashTable:
    def __init__(self, capacity=1024):
        if capacity < 1:
            raise ValueError("capacity phải >= 1")
        self.capacity = capacity
        self.buckets = [[] for _ in range(capacity)]
        self.size = 0
        self.collisions = 0

    def _index(self, key):
        return hash(key) % self.capacity

    def get(self, key, default=None):
        bucket = self.buckets[self._index(key)]
        for stored_key, value in bucket:
            if stored_key == key:
                return value
        return default

    def set(self, key, value):
        bucket = self.buckets[self._index(key)]
        for i, (stored_key, _) in enumerate(bucket):
            if stored_key == key:
                bucket[i] = (key, value)
                return
        if bucket:
            self.collisions += 1
        bucket.append((key, value))
        self.size += 1
        if self.size / self.capacity > 0.75:
            self._resize()

    def _resize(self):
        old_items = [(key, value) for bucket in self.buckets for key, value in bucket]
        self.capacity *= 2
        self.buckets = [[] for _ in range(self.capacity)]
        self.size = 0
        for key, value in old_items:
            self.set(key, value)

    def get_or_create(self, key, factory=list):
        value = self.get(key)
        if value is None:
            value = factory()
            self.set(key, value)
        return value

    def items(self):
        for bucket in self.buckets:
            yield from bucket
