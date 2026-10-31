"""Bảng băm tự cài đặt bằng Separate Chaining.

Lưu ý: Python hash() chỉ dùng để ánh xạ khóa vào bucket trong lần chạy hiện tại.
Khóa nhận từ ứng dụng là chuỗi SHA-256; không dùng hash() thay cho SHA-256.
"""


class HashTable:
    """Bảng ánh xạ khóa-giá trị dùng danh sách liên kết trong từng bucket."""

    def __init__(self, capacity=1024):
        """Khởi tạo bảng với số bucket ban đầu và bộ đếm va chạm."""
        if capacity < 1:
            raise ValueError("capacity phải >= 1")
        self.capacity = capacity
        self.buckets = [[] for _ in range(capacity)]
        self.size = 0
        self.collisions = 0

    def _index(self, key):
        """Đổi khóa thành chỉ số bucket trong phạm vi dung lượng hiện tại."""
        return hash(key) % self.capacity

    def get(self, key, default=None):
        """Tìm khóa trong bucket tương ứng; trả về default nếu không có."""
        bucket = self.buckets[self._index(key)]
        for stored_key, value in bucket:
            if stored_key == key:
                return value
        return default

    def set(self, key, value):
        """Thêm khóa mới hoặc cập nhật giá trị của khóa đã tồn tại."""
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
        """Tăng gấp đôi số bucket và phân phối lại toàn bộ mục đang lưu."""
        old_items = [(key, value) for bucket in self.buckets for key, value in bucket]
        self.capacity *= 2
        self.buckets = [[] for _ in range(self.capacity)]
        self.size = 0
        for key, value in old_items:
            self.set(key, value)

    def get_or_create(self, key, factory=list):
        """Lấy giá trị hiện có hoặc tạo, lưu giá trị mới bằng factory."""
        value = self.get(key)
        if value is None:
            value = factory()
            self.set(key, value)
        return value

    def items(self):
        """Duyệt lần lượt các cặp khóa-giá trị được lưu trong bảng."""
        for bucket in self.buckets:
            yield from bucket
