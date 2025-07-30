# Bcryptify

Bcryptify is a modern and elegant Python library designed to simplify the use of cryptographic algorithms, while adhering to SOLID principles to ensure clean, extensible, and maintainable code.

---

## 📦 Installation 

You can install **Bcryptify** directly from PyPI with pip:

```bash 
pip install bcryptify
```

Bcryptify library dependent on the cryptography library

```bash
pip install cryptography
```


## 🚀 Use

Here is a simple example of using the **AesGcmCipher** class to encrypt and decrypt messages or files.


```python
import os
from Bcryptify.aes_gcm import AesGcmCipher

# 256-bit AES key (must be kept secret)
key =
b'\xcd_\x8d\xfd1E\xd4\xe3uj\xee_\x1dj\x9c\x07\xa3\x13\x95\x96\x10\xa6\xf3\rb\xc0\x08\xde\xfa\xb6\x99\xc9'

tag = b"\xcd_\x8d\xfd1E\xd4"

# Initializing the AES-GCM cipher
aes_gcm = AesGcmCipher(key)


# --- Example of file encryption/decryption ---

def read_file(filename: str) -> bytes:
    with open(filename, "rb") as f:
        return f.read()

def write_file(filename: str, data: bytes) -> None:
    with open(filename, "wb") as f:
        f.write(data)

def encrypt_file(filepath: str) -> None:
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"The file {filepath} does not exist.")
    data = read_file(filepath)
    encrypted = aes_gcm.encrypt(data, tag)
    encrypted_filepath = filepath + ".lock"
    write_file(encrypted_filepath, encrypted)
    os.remove(filepath) 
    print(f"File encrypted in {encrypted_filepath} and original file deleted.")

def decrypt_file(encrypted_filepath: str) -> None:
    if not encrypted_filepath.endswith(".lock"):
        raise ValueError("The decrypted file must have the extension '.lock'.")
    if not os.path.isfile(encrypted_filepath):
        raise FileNotFoundError(f"The file {encrypted_filepath} does not exist.")
    data = read_file(encrypted_filepath)
    decrypted = aes_gcm.decrypt(data, tag)
    original_filepath = encrypted_filepath[:-5] 
    write_file(original_filepath, decrypted)
    os.remove(encrypted_filepath)
    print(f"Decrypted file in {original_filepath} and encrypted file deleted.")

# Example of use
file_path = "l.png"

encrypt_file(file_path)
decrypt_file(file_path + ".lock")


# ----------------------------------------


# Encrypting a text message
#message = "Hello, this is a secret message.".encode('utf-8')
#encrypted_message = aes_gcm.encrypt(message, tag)
#print(f"Encrypted message : {encrypted_message}")

# Decrypting the message
#decrypted_message = aes_gcm.decrypt(encrypted_message, tag)
#print(f"Deciphered message : {decrypted_message.decode('utf-8')}")
```

<br>

## support

- RSA
- AES GCM