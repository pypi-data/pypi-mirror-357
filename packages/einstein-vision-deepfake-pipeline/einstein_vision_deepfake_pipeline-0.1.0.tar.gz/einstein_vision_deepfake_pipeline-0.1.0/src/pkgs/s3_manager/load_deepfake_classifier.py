from pathlib import Path, PurePosixPath
from urllib.parse import urlparse
from .load_files import download_s3_file, upload_file_to_s3

def download_deepfake_classifier(client, s3_model_folder: str, local_folder: str):
    REQUIRED_FILES = ["model.safetensors", "config.json", "preprocessor_config.json"]
    
    parsed = urlparse(s3_model_folder)
    if parsed.scheme != "s3":
        raise ValueError("s3_model_folder must be a valid s3:// URI")

    bucket = parsed.netloc
    prefix = parsed.path.lstrip("/")

    for filename in REQUIRED_FILES:
        s3_key = str(PurePosixPath(prefix) / filename)
        s3_uri = f"s3://{bucket}/{s3_key}"
        local_path = (Path(local_folder) / filename).as_posix()
        download_s3_file(client, s3_uri, local_path)
        

def upload_deepfake_classifier(client, local_folder: str, s3_model_folder: str):
    REQUIRED_FILES = ["model.safetensors", "config.json", "preprocessor_config.json"]

    parsed = urlparse(s3_model_folder)
    if parsed.scheme != "s3":
        raise ValueError("s3_model_folder must be a valid s3:// URI")

    bucket = parsed.netloc
    prefix = parsed.path.lstrip("/")

    for filename in REQUIRED_FILES:
        local_path = Path(local_folder) / filename
        if not local_path.is_file():
            raise FileNotFoundError(f"Local file not found: {local_path}")
        
        s3_key = str(PurePosixPath(prefix) / filename)
        s3_uri = f"s3://{bucket}/{s3_key}"
        upload_file_to_s3(client, str(local_path), s3_uri)
