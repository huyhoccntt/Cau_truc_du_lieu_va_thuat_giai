# Duplicate File Finder (Python + Tkinter)

Công cụ tìm tập tin trùng lặp trên Windows 10 bằng:
- Duyệt thư mục và thư mục con.
- Lọc ứng viên theo kích thước.
- SHA-256 theo từng khối 1 MiB.
- Bảng băm tự cài đặt bằng Separate Chaining.
- Xác minh nội dung byte-for-byte trước khi kết luận.
- Giao diện Tkinter, tiến trình, thống kê và xuất CSV.

## Yêu cầu
- Windows 10
- Python 3.10 trở lên (khuyến nghị Python 3.11 hoặc 3.12)
- Không cần cài thư viện ngoài.

## Chạy ứng dụng
1. Giải nén thư mục dự án.
2. Mở thư mục `DuplicateFileFinder`.
3. Nhấp vào thanh địa chỉ File Explorer, gõ `cmd`, nhấn Enter.
4. Chạy:

```bat
py --version
py main.py
```

Nếu lệnh `py` không có, thử:

```bat
python --version
python main.py
```

## Cách sử dụng
1. Nhấn **Chọn thư mục**.
2. Chọn thư mục cần quét.
3. Nhấn **Bắt đầu quét**.
4. Nhấp đúp vào một nhóm để xem các đường dẫn trong nhóm.
5. Chọn **Xuất CSV** để lưu báo cáo.

Ứng dụng chỉ tìm và báo cáo, không tự xóa tập tin.

## Chạy kiểm thử
Mở CMD tại thư mục dự án và chạy:

```bat
py -m unittest discover -s tests -v
```

## Ghi chú
- Chỉ các tập tin có cùng kích thước mới được tính SHA-256; điều này không bỏ sót bản sao chính xác vì bản sao phải có cùng kích thước.
- Các file cùng hash được xác minh nội dung byte-for-byte.
- Symlink bị bỏ qua để tránh quét vòng lặp hoặc ngoài phạm vi.
- File không đọc được sẽ được bỏ qua và ghi nhận trong số lỗi.
- Thời gian và kết quả phụ thuộc ổ đĩa, dung lượng file, cache hệ điều hành và các ứng dụng đang chạy.
