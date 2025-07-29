import re
import base64
import requests
import json
from Crypto.Cipher import AES
from Crypto.Util import Counter
from tqdm import tqdm

def mega_extract_id_and_key(url):
    # Check if the URL matches the pattern for "/file/"
    if re.match(r'.*/file/[^#]*#[^#]*', url):
        # Extract id and key from the URL when it matches the pattern
        id_part = url.split('file/')[1]
        id = id_part.split('#')[0]
        key = id_part.split('#')[1]
    else:
        # Extract id and key from the URL when it does not match the pattern
        id_part = url.split('!')[1]
        id = url.split('!')[0]
        key = id_part

    return id, key

def get_raw_hex_from_key(key):
    modified_key = key + '='  # Append '=' for padding
    modified_key = modified_key.replace('-', '+').replace('_', '/')  # Replace characters
    modified_key = modified_key.replace(',', '')  # Remove commas

    try:
        # Step 2: Decode the modified base64 key
        decoded_data = base64.b64decode(modified_key)  # decode base64
    except base64.binascii.Error:
        return None  # If base64 decoding fails, return None

    raw_hex = decoded_data.hex()

    return raw_hex

def transform_key(raw_hex):
    if len(raw_hex) < 64:
        return None

    part1 = int(raw_hex[0:16], 16)
    part2 = int(raw_hex[32:48], 16)
    part3 = int(raw_hex[16:32], 16)
    part4 = int(raw_hex[48:64], 16)

    result = (part1 ^ part2)
    result2 = (part3 ^ part4)

    hex_result = f"{result:016x}" + f"{result2:016x}"

    return hex_result

def mega_get_file_json_data(file_id):
    url = 'https://g.api.mega.co.nz/cs?id=&ak='
    payload = [{"a": "g", "g": "1", "p": file_id}]
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to get data from API, status code: {response.status_code}")
    
    return json.loads(response.text)

def decrypt_and_extract(at, hex_key):
    # Step 1: Decode the Base64 string
    # Replace '-' with '+' and '_' with '/'
    at_modified = at + '=='
    at_modified = at_modified.replace('-', '+').replace('_', '/')
    
    # Remove commas (as per the Bash `tr -d ','`)
    at_modified = at_modified.replace(',', '')

    # Base64 decode
    decrypted_data = base64.b64decode(at_modified)

    key = bytes.fromhex(hex_key)
    iv = bytes([0] * 16)
    
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_bytes = cipher.decrypt(decrypted_data)

    decrypted_bytes = decrypted_bytes.rstrip(b'\0')
    decrypted_string = decrypted_bytes.decode('utf-8')

    print(decrypted_string)

    json_str = decrypted_string.lstrip("MEGA")
    json_data = json.loads(json_str)
    file_name = json_data.get("n", "")

    return file_name


def mega_download_and_decrypt(file_url, hex_key, raw_hex, file_name):
    response = requests.get(file_url, stream=True)
    
    if response.status_code != 200:
        raise Exception(f"Failed to download the file, status code: {response.status_code}")
    
    key = bytes.fromhex(hex_key)  # Convert the hex key to bytes
    iv = bytes.fromhex(raw_hex[32:48] + "0000000000000000")  # Extract the IV from raw_hex and append zeros

    cipher = AES.new(key, AES.MODE_CTR, counter=Counter.new(128, initial_value=int.from_bytes(iv, byteorder='big')))
    
    total_size = int(response.headers.get('Content-Length', 0))  # Get the total file size from the headers
    chunk_size = 1024 * 1024  # 1MB chunks

    with open(file_name, 'wb') as file, tqdm(total=total_size, unit='B', unit_scale=True, desc="Downloading and decrypting") as pbar:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                decrypted_chunk = cipher.decrypt(chunk)
                file.write(decrypted_chunk)
                pbar.update(len(chunk))
    
    print(f"Decrypted file saved as {file_name}")

def mega_download(file_url, file_name):
    file_id, file_key = mega_extract_id_and_key(file_url)
    print(f"ID: {file_id}, Key: {file_key}")

    raw_hex = get_raw_hex_from_key(file_key)
    print(f'Raw hex: {raw_hex}')

    hex_value = transform_key(raw_hex)
    if hex_value:
        print(f"Transformed hex: {hex_value}")
    else:
        print("Base64 decoding failed.")

    json_data = mega_get_file_json_data(file_id)
    file_url = json_data[0]['g']
    file_at = json_data[0]['at']

    represent_file_name = decrypt_and_extract(file_at, hex_value)
    print(f"File name: {represent_file_name}")

    mega_download_and_decrypt(file_url, hex_value, raw_hex, file_name)