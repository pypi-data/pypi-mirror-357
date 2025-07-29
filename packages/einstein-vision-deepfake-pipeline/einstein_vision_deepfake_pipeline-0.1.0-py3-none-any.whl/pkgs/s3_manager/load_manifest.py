import json
from .load_files import load_s3_file_bytes

def load_manifest_jsonline_file(client, path):
    file_bytes = load_s3_file_bytes(client, path)
    return bytes_to_manifest_jsonlines(file_bytes)

def bytes_to_manifest_jsonlines(byte_data):
    lines = byte_data.decode('utf-8').splitlines()
    result = []
    for i, line in enumerate(lines):
        try:
            result.append(json.loads(line))
        except json.JSONDecodeError as e:
            print(f"Failed to parse line {i+1}: {e}")
            # Optionally: continue or raise
    return result