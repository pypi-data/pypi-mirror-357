from .ISymmetricCipher import ISymmetricCipher
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag
import os
import time

# ajouter tag et mieux géré les nonce

class AesGcmCipher(ISymmetricCipher):
    def __init__(self, key: bytes):
        if len(key) not in (16, 24, 32):
            raise ValueError("The key must be 128, 192 or 256 bits")
        self.key = key
        self.aesgcm = AESGCM(key)


    def _generate_nonce(self) -> bytes:
        xor_key = os.urandom(12)

        time.sleep(20 / 1_000_000)
        try:
            timestamp_ns = time.time_ns()
        except AttributeError:
            timestamp_ns = int(time.time() * 1_000_000_000)
        timestamp_bytes = timestamp_ns.to_bytes(8, 'big')
        random_bytes = os.urandom(4)

        base_nonce = timestamp_bytes + random_bytes

        final_nonce = bytes(b1 ^ b2 for b1, b2 in zip(base_nonce, xor_key))

        if len(final_nonce) != 12:
            raise RuntimeError("Critical error: The final nonce does not have the expected size of 12 bytes.")
        
        return final_nonce
    

    def encrypt(self, plaintext: bytes, tag: bytes) -> bytes:

        nonce = self._generate_nonce()  # 96-bit nonce recommended os.urandom(12)
        ciphertext = self.aesgcm.encrypt(nonce, plaintext, tag)
        return nonce + ciphertext

    def decrypt(self, ciphertext: bytes, tag:bytes) -> bytes:
        if len(ciphertext) < 12 + 16: 
            raise ValueError("Encrypted data is too short to contain a nonce and a valid GCM tag.")

        nonce = ciphertext[:12]
        actual_ct = ciphertext[12:]
        return self.aesgcm.decrypt(nonce, actual_ct, tag)
