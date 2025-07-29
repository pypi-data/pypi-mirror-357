
# loads file in memory
def load_s3_file_bytes(client, path: str):
    bucket, key = path.replace("s3://", "").split("/", 1)
    try:
        obj = client.get_object(Bucket=bucket, Key=key)
        return obj['Body'].read()
    except client.exceptions.NoSuchKey:
        print(f"Key not found: {key}")
    except Exception as e:
        print(f"Failed to load object: {e}")

# saves directly to disk
def download_s3_file(client, s3_uri: str, local_path: str):
    bucket, key = s3_uri.replace("s3://", "").split("/", 1)
    try:
        client.download_file(bucket, key, local_path)
        print(f"Downloaded {s3_uri} to {local_path}")
    except client.exceptions.NoSuchKey:
        print(f"Key not found: {key}")
    except Exception as e:
        print(f"Failed to download {s3_uri}: {e}")

# uploads from from disk to s3
def upload_file_to_s3(client, local_path: str, s3_uri: str):
    bucket, key = s3_uri.replace("s3://", "").split("/", 1)
    try:
        client.upload_file(local_path, bucket, key)
        print(f"Uploaded {local_path} to {s3_uri}")
    except Exception as e:
        print(f"Failed to upload {local_path} to {s3_uri}: {e}")