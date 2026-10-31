"""Điểm khởi chạy ứng dụng tìm file trùng lặp."""

from gui.main_window import DuplicateFinderApp

if __name__ == "__main__":
    # Tạo cửa sổ chính và bắt đầu vòng lặp sự kiện của Tkinter.
    app = DuplicateFinderApp()
    app.mainloop()
