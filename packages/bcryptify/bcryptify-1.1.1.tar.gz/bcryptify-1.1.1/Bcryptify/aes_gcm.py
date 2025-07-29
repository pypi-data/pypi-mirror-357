from .ISymmetricCipher import ISymmetricCipher
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag
import os

# ajouter tag et mieux géré les nonce

class AesGcmCipher(ISymmetricCipher):
    def __init__(self, key: bytes):
        if len(key) not in (16, 24, 32):
            raise ValueError("The key must be 128, 192 or 256 bits")
        self.key = key
        self.aesgcm = AESGCM(key)


    # faille reporter 
    # y a pas assez d'entropie dans 12 bytes pour assurer qu'un nonce random sera garanti unique
    def encrypt(self, plaintext: bytes, tag: bytes) -> bytes:
        nonce = os.urandom(12)  # 96-bit nonce recommended
        ciphertext = self.aesgcm.encrypt(nonce, plaintext, tag)
        return nonce + ciphertext 

    def decrypt(self, ciphertext: bytes, tag:bytes) -> bytes:
        if len(ciphertext) < 12 + 16: 
            raise ValueError("Encrypted data is too short to contain a nonce and a valid GCM tag.")

        nonce = ciphertext[:12]
        actual_ct = ciphertext[12:]
        return self.aesgcm.decrypt(nonce, actual_ct, tag)
