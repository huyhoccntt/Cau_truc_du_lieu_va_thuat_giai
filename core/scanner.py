"""Quét thư mục bằng os.walk; ghi nhận lỗi và tiếp tục."""
import os


def scan_files(root, on_error=None, should_cancel=None):
    """Yield (absolute_path, size_bytes, mtime_ns).

    Bỏ qua symlink tới thư mục để tránh chu trình; không theo symlink file.
    """
    def handle_error(exc):
        if on_error:
            on_error(str(exc))

    for current, dirs, names in os.walk(
        root, topdown=True, onerror=handle_error, followlinks=False
    ):
        if should_cancel and should_cancel():
            return
        dirs[:] = [
            d for d in dirs
            if not os.path.islink(os.path.join(current, d))
        ]
        for name in names:
            if should_cancel and should_cancel():
                return
            path = os.path.abspath(os.path.join(current, name))
            try:
                if os.path.islink(path) or not os.path.isfile(path):
                    continue
                stat = os.stat(path, follow_symlinks=False)
                yield path, stat.st_size, stat.st_mtime_ns
            except OSError as exc:
                handle_error(exc)
