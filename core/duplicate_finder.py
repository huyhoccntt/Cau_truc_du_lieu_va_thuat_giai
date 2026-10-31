"""Điều phối tìm file trùng lặp."""
import os
import time
from collections import defaultdict

from core.hash_table import HashTable
from core.hasher import calculate_sha256, files_equal
from core.scanner import scan_files


def find_duplicates(root, progress=None, on_error=None, should_cancel=None):
    """Trả về dict kết quả và số liệu.

    Quy trình: quét -> nhóm kích thước -> SHA-256 -> xác minh byte-for-byte.
    Mỗi nhóm kết quả gồm ít nhất hai đường dẫn có cùng nội dung đã xác minh.
    """
    started = time.perf_counter()
    all_files = []
    errors = []
    def report_error(message):
        errors.append(message)
        if on_error:
            on_error(message)

    for record in scan_files(root, report_error, should_cancel):
        all_files.append(record)
        if progress:
            progress("scan", len(all_files), None, record[0])

    if should_cancel and should_cancel():
        return {"groups": [], "stats": _stats(started, all_files, [], errors, True)}

    by_size = defaultdict(list)
    for record in all_files:
        by_size[record[1]].append(record)

    candidates = [r for group in by_size.values() if len(group) > 1 for r in group]
    hash_table = HashTable()
    hashed = 0
    for path, size, mtime_ns in candidates:
        if should_cancel and should_cancel():
            return {"groups": [], "stats": _stats(started, all_files, candidates, errors, True, hashed, hash_table)}
        try:
            # Tránh chấp nhận hash nếu file đổi trong lúc đọc.
            before = os.stat(path)
            digest = calculate_sha256(path)
            after = os.stat(path)
            if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                report_error(f"File thay đổi trong lúc quét, đã bỏ qua: {path}")
                continue
            bucket = hash_table.get_or_create((size, digest))
            bucket.append(path)
            hashed += 1
            if progress:
                progress("hash", hashed, len(candidates), path)
        except OSError as exc:
            report_error(f"Không thể băm {path}: {exc}")

    # Xác minh byte-for-byte. Với hash bucket hiếm có va chạm SHA-256,
    # tách các nhóm nội dung thực sự khác nhau.
    groups = []
    for (size, digest), paths in hash_table.items():
        if len(paths) < 2:
            continue
        verified_groups = []
        for path in paths:
            placed = False
            for group in verified_groups:
                if files_equal(path, group[0]):
                    group.append(path)
                    placed = True
                    break
            if not placed:
                verified_groups.append([path])
        for group in verified_groups:
            if len(group) >= 2:
                groups.append({
                    "size": size,
                    "sha256": digest,
                    "paths": sorted(group, key=str.casefold),
                })

    groups.sort(key=lambda g: (-g["size"] * (len(g["paths"]) - 1), g["paths"][0].casefold()))
    return {"groups": groups, "stats": _stats(started, all_files, candidates, errors, False, hashed, hash_table)}


def _stats(started, all_files, candidates, errors, cancelled, hashed=0, table=None):
    duplicate_files = 0
    return {
        "files_scanned": len(all_files),
        "total_bytes": sum(r[1] for r in all_files),
        "candidate_files": len(candidates),
        "files_hashed": hashed,
        "groups": 0,
        "duplicate_copies": duplicate_files,
        "reclaimable_bytes": 0,
        "elapsed_seconds": time.perf_counter() - started,
        "errors": len(errors),
        "error_messages": errors[:100],
        "cancelled": cancelled,
        "hash_table_collisions": table.collisions if table else 0,
        "hash_table_capacity": table.capacity if table else 0,
    }
