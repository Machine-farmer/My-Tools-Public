#!/usr/bin/env python3
"""
Safe file generator for storage-abuse testing.
- Expands ~ and resolves absolute paths so files are created where you expect.
- Supports jpg, png, pdf, txt, bin with appropriate header bytes.
- Chunked writes to avoid OOM for large files.
"""

import os
import sys

FILE_SIGNATURES = {
    "jpg": bytes.fromhex("FFD8FFE0") + b"\x00\x10JFIF\x00",  # simple JPEG/JFIF start
    "png": bytes.fromhex("89504E470D0A1A0A"),               # PNG signature
    "pdf": b"%PDF-1.4\n",                                   # PDF header
    "txt": b"",                                             # no signature
    "bin": b""                                              # raw binary
}

CHUNK_SIZE_DEFAULT = 4 * 1024 * 1024  # 4 MiB

def get_size_in_bytes(size_value, unit):
    unit = unit.strip().lower()
    mult = {"b":1, "bytes":1,
            "kb":1024, "kilobytes":1024,
            "mb":1024**2, "megabytes":1024**2,
            "gb":1024**3, "gigabytes":1024**3}
    if unit not in mult:
        raise ValueError("Unknown unit: " + unit)
    return int(float(size_value) * mult[unit])

def safe_makedirs(path):
    """Create the directory if it doesn't exist (path must be absolute or relative resolved)."""
    try:
        os.makedirs(path, exist_ok=True)
    except Exception as e:
        raise RuntimeError(f"Unable to create directory {path}: {e}")

def generate_file(filepath, extension, size_bytes, content_type="random", chunk_size=CHUNK_SIZE_DEFAULT):
    header = FILE_SIGNATURES.get(extension, b"")
    header_len = len(header)
    if size_bytes < header_len:
        raise ValueError(f"Requested size {size_bytes} bytes is smaller than header length {header_len} bytes")

    remaining = size_bytes - header_len

    with open(filepath, "wb") as f:
        # write header
        if header:
            f.write(header)

        # write rest in chunks
        if content_type == "random":
            while remaining > 0:
                write_len = min(chunk_size, remaining)
                f.write(os.urandom(write_len))
                remaining -= write_len
        elif content_type == "zeros":
            zero_chunk = b"\x00" * min(chunk_size, remaining)
            while remaining > 0:
                write_len = min(len(zero_chunk), remaining)
                f.write(zero_chunk[:write_len])
                remaining -= write_len
        elif content_type == "pattern":
            pattern = b"ABCD0123"
            # build a buffer from the pattern to write
            buf = pattern * (max(1, min(chunk_size, remaining) // len(pattern)))
            while remaining > 0:
                write_len = min(len(buf), remaining)
                f.write(buf[:write_len])
                remaining -= write_len
        else:
            raise ValueError("Unsupported content type: " + content_type)

    print(f"[+] Generated: {filepath} ({size_bytes} bytes)")

def main():
    try:
        print("=== Safe File Generator ===")
        print("Available extensions: " + ", ".join(FILE_SIGNATURES.keys()))
        ext = input("Choose file extension: ").strip().lower()
        if ext not in FILE_SIGNATURES:
            print("Unsupported extension. Exiting.")
            return

        unit = input("Choose size unit [B, KB, MB, GB]: ").strip() or "MB"
        size_val = input(f"Enter file size in {unit} (e.g. 10 or 0.5): ").strip()
        if not size_val:
            print("No size provided. Exiting.")
            return
        size_bytes = get_size_in_bytes(size_val, unit)

        print("Content types: random, zeros, pattern")
        content_type = input("Choose content type: ").strip().lower() or "random"
        if content_type not in ("random", "zeros", "pattern"):
            print("Unsupported content type. Exiting.")
            return

        save_dir_input = input("Enter directory path to save file (absolute or ~-path). Leave blank to use current directory: ").strip()
        if not save_dir_input:
            save_dir = os.getcwd()
        else:
            # Important: expand ~ and produce absolute path BEFORE creating directories
            save_dir = os.path.abspath(os.path.expanduser(save_dir_input))

        # If the user gave a path that looks like a file (ends with an extension), ask them to provide a dir.
        # We won't prompt — instead, handle both: if exists and is file, use its directory; if not exists but looks like file, create parent dir.
        # But to keep it simple: if path ends with a path separator or exists as dir, treat as dir. Otherwise if it has an extension, treat it as dir too.
        # We'll create the directory if needed (at the resolved location).
        if os.path.exists(save_dir) and not os.path.isdir(save_dir):
            # if it's an existing file, use its directory
            save_dir = os.path.dirname(save_dir) or os.getcwd()

        # Create directory at the resolved path (this is what fixes the "~" problem)
        safe_makedirs(save_dir)

        # filename selection
        default_name = f"testfile.{ext}"
        filename = input(f"Enter filename (default: {default_name}): ").strip() or default_name
        # ensure correct extension
        if not filename.lower().endswith("." + ext):
            filename = filename + "." + ext

        filepath = os.path.join(save_dir, filename)

        # prevent accidental overwrite by default: ask user to confirm if file exists
        if os.path.exists(filepath):
            resp = input(f"File {filepath} already exists. Overwrite? [y/N]: ").strip().lower()
            if resp != "y":
                print("Aborted by user.")
                return

        generate_file(filepath, ext, size_bytes, content_type)

    except KeyboardInterrupt:
        print("\nCancelled by user.")
    except Exception as e:
        print("Error:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
