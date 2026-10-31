import csv
import os
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from core.duplicate_finder import find_duplicates


def human_size(value):
    amount = float(value)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if amount < 1024 or unit == "TB":
            return f"{amount:.2f} {unit}"
        amount /= 1024
    return f"{amount:.2f} TB"


class DuplicateFinderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Duplicate File Finder — SHA-256")
        self.geometry("1050x680")
        self.minsize(800, 520)
        self.events = queue.Queue()
        self.worker = None
        self.cancel_event = threading.Event()
        self.groups = []
        self.last_stats = None
        self._build_ui()
        self.after(100, self._poll_events)

    def _build_ui(self):
        top = ttk.Frame(self, padding=12)
        top.pack(fill="x")
        ttk.Label(top, text="Thư mục cần quét:").grid(row=0, column=0, sticky="w")
        self.path_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.path_var).grid(row=0, column=1, sticky="ew", padx=8)
        ttk.Button(top, text="Chọn thư mục", command=self._choose_folder).grid(row=0, column=2)
        top.columnconfigure(1, weight=1)

        controls = ttk.Frame(self, padding=(12, 0, 12, 8))
        controls.pack(fill="x")
        self.start_btn = ttk.Button(controls, text="Bắt đầu quét", command=self._start_scan)
        self.start_btn.pack(side="left")
        self.cancel_btn = ttk.Button(controls, text="Hủy quét", command=self._cancel_scan, state="disabled")
        self.cancel_btn.pack(side="left", padx=8)
        ttk.Button(controls, text="Xuất CSV", command=self._export_csv).pack(side="left")
        ttk.Button(controls, text="Mở thư mục file", command=self._open_selected_folder).pack(side="left", padx=8)

        self.progress = ttk.Progressbar(self, mode="determinate")
        self.progress.pack(fill="x", padx=12)
        self.status_var = tk.StringVar(value="Chọn thư mục rồi nhấn Bắt đầu quét.")
        ttk.Label(self, textvariable=self.status_var, padding=(12, 6)).pack(fill="x")

        columns = ("group", "size", "copies", "saving", "path")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        headings = {
            "group": ("Nhóm", 70),
            "size": ("Dung lượng mỗi file", 150),
            "copies": ("Số file", 80),
            "saving": ("Có thể tiết kiệm", 150),
            "path": ("Đường dẫn đại diện", 560),
        }
        for key, (label, width) in headings.items():
            self.tree.heading(key, text=label)
            self.tree.column(key, width=width, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        self.tree.bind("<Double-1>", self._show_group)

        self.summary_var = tk.StringVar(value="")
        ttk.Label(self, textvariable=self.summary_var, padding=12).pack(fill="x")

    def _choose_folder(self):
        folder = filedialog.askdirectory(title="Chọn thư mục cần quét")
        if folder:
            self.path_var.set(folder)

    def _start_scan(self):
        root = self.path_var.get().strip()
        if not root or not os.path.isdir(root):
            messagebox.showerror("Thư mục không hợp lệ", "Hãy chọn một thư mục tồn tại.")
            return
        if self.worker and self.worker.is_alive():
            return
        self.groups = []
        self.last_stats = None
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.progress["value"] = 0
        self.status_var.set("Đang quét thư mục...")
        self.summary_var.set("")
        self.cancel_event.clear()
        self.start_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")
        self.worker = threading.Thread(target=self._run_scan, args=(root,), daemon=True)
        self.worker.start()

    def _run_scan(self, root):
        def progress(stage, current, total, path):
            self.events.put(("progress", stage, current, total, path))
        def on_error(message):
            self.events.put(("error", message))
        try:
            result = find_duplicates(
                root,
                progress=progress,
                on_error=on_error,
                should_cancel=self.cancel_event.is_set,
            )
            self.events.put(("done", result))
        except Exception as exc:
            self.events.put(("fatal", str(exc)))

    def _cancel_scan(self):
        self.cancel_event.set()
        self.status_var.set("Đang yêu cầu dừng...")

    def _poll_events(self):
        try:
            while True:
                event = self.events.get_nowait()
                kind = event[0]
                if kind == "progress":
                    _, stage, current, total, path = event
                    if stage == "scan":
                        self.status_var.set(f"Đang duyệt: {current} file — {path}")
                    else:
                        if total:
                            self.progress["maximum"] = total
                            self.progress["value"] = current
                        self.status_var.set(f"Đang tính SHA-256: {current}/{total} — {os.path.basename(path)}")
                elif kind == "error":
                    # Lỗi được đếm và ghi vào kết quả; tránh popup hàng loạt.
                    pass
                elif kind == "done":
                    self._show_result(event[1])
                elif kind == "fatal":
                    self._finish_controls()
                    messagebox.showerror("Lỗi", event[1])
        except queue.Empty:
            pass
        self.after(100, self._poll_events)

    def _show_result(self, result):
        self.groups = result["groups"]
        stats = result["stats"]
        # Tính thống kê từ nhóm đã xác minh.
        stats["groups"] = len(self.groups)
        stats["duplicate_copies"] = sum(len(g["paths"]) - 1 for g in self.groups)
        stats["reclaimable_bytes"] = sum((len(g["paths"]) - 1) * g["size"] for g in self.groups)
        self.last_stats = stats
        for index, group in enumerate(self.groups, 1):
            saving = (len(group["paths"]) - 1) * group["size"]
            self.tree.insert("", "end", iid=str(index - 1), values=(
                f"Nhóm {index}", human_size(group["size"]),
                len(group["paths"]), human_size(saving), group["paths"][0]
            ))
        self.progress["value"] = self.progress["maximum"] or 1
        status = "Đã hủy quét." if stats["cancelled"] else "Quét hoàn tất."
        self.status_var.set(status)
        self.summary_var.set(
            f"Đã quét: {stats['files_scanned']} file | "
            f"Ứng viên: {stats['candidate_files']} | "
            f"Đã băm: {stats['files_hashed']} | "
            f"Nhóm trùng: {stats['groups']} | "
            f"Bản sao dư: {stats['duplicate_copies']} | "
            f"Có thể tiết kiệm: {human_size(stats['reclaimable_bytes'])} | "
            f"Thời gian: {stats['elapsed_seconds']:.2f}s | Lỗi: {stats['errors']}"
        )
        self._finish_controls()
        if stats["errors"]:
            messagebox.showwarning(
                "Hoàn tất có cảnh báo",
                f"Có {stats['errors']} lỗi khi quét. Một số file có thể bị bỏ qua.\n"
                "Chi tiết tối đa 100 lỗi có thể xuất hiện trong báo cáo CSV."
            )

    def _finish_controls(self):
        self.start_btn.config(state="normal")
        self.cancel_btn.config(state="disabled")

    def _show_group(self, _event=None):
        selected = self.tree.selection()
        if not selected:
            return
        index = int(selected[0])
        group = self.groups[index]
        win = tk.Toplevel(self)
        win.title(f"Các file trong nhóm {index + 1}")
        win.geometry("800x360")
        ttk.Label(win, text=f"SHA-256: {group['sha256']}", padding=8).pack(anchor="w")
        box = tk.Listbox(win)
        box.pack(fill="both", expand=True, padx=8, pady=8)
        for path in group["paths"]:
            box.insert("end", path)

    def _open_selected_folder(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Chưa chọn", "Hãy chọn một nhóm kết quả trước.")
            return
        path = self.groups[int(selected[0])]["paths"][0]
        try:
            os.startfile(os.path.dirname(path))
        except (AttributeError, OSError) as exc:
            messagebox.showerror("Không mở được thư mục", str(exc))

    def _export_csv(self):
        if self.last_stats is None:
            messagebox.showinfo("Chưa có kết quả", "Hãy quét thư mục trước.")
            return
        destination = filedialog.asksaveasfilename(
            title="Lưu báo cáo CSV", defaultextension=".csv",
            filetypes=[("CSV", "*.csv")]
        )
        if not destination:
            return
        try:
            with open(destination, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["Group", "SHA256", "SizeBytes", "Path", "GroupFileCount", "ReclaimableBytes"])
                for i, group in enumerate(self.groups, 1):
                    saving = (len(group["paths"]) - 1) * group["size"]
                    for path in group["paths"]:
                        writer.writerow([i, group["sha256"], group["size"], path, len(group["paths"]), saving])
                writer.writerow([])
                writer.writerow(["Statistic", "Value"])
                for key, value in self.last_stats.items():
                    if key != "error_messages":
                        writer.writerow([key, value])
                for error in self.last_stats.get("error_messages", []):
                    writer.writerow(["error", error])
            messagebox.showinfo("Đã xuất", f"Đã lưu báo cáo:\n{destination}")
        except OSError as exc:
            messagebox.showerror("Lỗi ghi báo cáo", str(exc))
