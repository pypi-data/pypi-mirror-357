import json


def s3_download_file(s3_client, bucket, key, dest_path):
    """Download a file from S3.
    Args:
        s3_client: The S3 client.
        bucket (str): The name of the S3 bucket.
        key (str): The S3 object key.
        dest_path (Path): The destination path to save the downloaded file.
    Returns:
        bool: True if the download was successful, False otherwise.
    """
    try:
        s3_client.download_file(bucket, key, str(dest_path))
        print(f"Successfully downloaded {key} to {dest_path}")
        return True
    except Exception as e:
        print(f"Error downloading file from S3: {e}")
        return False

def s3_upload_file(s3_client, src_path, bucket, key):
    """Upload a file to S3.
    Args:
        s3_client: The S3 client.
        src_path (Path): The source path of the file to upload.
        bucket (str): The name of the S3 bucket.
        key (str): The S3 object key.
    Returns:
        bool: True if the upload was successful, False otherwise.
    """
    try:
        s3_client.upload_file(str(src_path), bucket, key)
        print(f"Successfully uploaded {key} to S3 bucket {bucket}")
        return True
    except Exception as e:
        print(f"Error uploading file to S3: {e}")
        return False

def load_json_file(path):
    """Load JSON from a file.
    Args:
        path (Path): The path to the JSON file.
    Returns:
        dict: The loaded JSON data, or None if an error occurred.
    """
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return None

def write_json_file(path, data):
    """Write JSON to a file.
    Args:
        path (Path): The path to the JSON file.
        data (dict): The data to write to the file.
    Returns:
        bool: True if the write was successful, False otherwise.
    """
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Wrote merged metadata to {path}")
        return True
    except Exception as e:
        print(f"Failed to write {path}: {e}")
        return False


def validate_metadata_config(config, source_name):
    """
    Validate that the configuration is properly formatted for MCP servers.
    
    args:
        config: The loaded configuration object to validate
        source_name: Name of the source (file path or URL) for error messages
    
    returns:
        bool: True if configuration is valid, False otherwise
    """
    # Verify that config is a valid dictionary/JSON object
    if not isinstance(config, dict):
        print(f"Invalid configuration format: Expected a JSON object in {source_name}")
        return False
    
    # Check if the file has the mcpServers key 
    if "mcpServers" not in config:
        print(f"Invalid configuration file: 'mcpServers' key not found in {source_name}")
        return False
        
    # Also verify that mcpServers is a dictionary
    if not isinstance(config["mcpServers"], dict):
        print(f"Invalid configuration format: 'mcpServers' must be a JSON object")
        return False
        
    # If all the checks pass, return True
    return True
