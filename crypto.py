# app/crypto.py
"""
Encryption, decryption and hashing utilities.
Safe handling for Fernet keys (str or bytes).
"""
from cryptography.fernet import Fernet, InvalidToken
import hashlib
import json

def generate_fernet_key():
    """Generate a new Fernet key (bytes)."""
    return Fernet.generate_key()

def load_fernet(key):
    """
    Load a Fernet instance from a key.
    Accepts either a bytes key or a base64 str key.
    Raises RuntimeError with a clear message if invalid.
    """
    if key is None:
        raise RuntimeError("FERNET key is None. Set FERNET_KEY environment variable to a valid Fernet key.")
    # If user provided a str, convert to bytes
    if isinstance(key, str):
        key_bytes = key.encode('utf-8')
    else:
        key_bytes = key
    try:
        return Fernet(key_bytes)
    except (TypeError, ValueError) as e:
        raise RuntimeError("Invalid Fernet key. Generate one using Fernet.generate_key() and set it as FERNET_KEY. Original error: " + str(e))

def encrypt_payload(fernet, payload_dict):
    """
    Encrypt a payload dictionary using Fernet symmetric encryption.
    Returns ciphertext bytes.
    """
    plaintext = json.dumps(payload_dict, sort_keys=True).encode('utf-8')
    ciphertext = fernet.encrypt(plaintext)
    return ciphertext

def decrypt_payload(fernet, ciphertext):
    """
    Decrypt ciphertext bytes back to a payload dictionary.
    Raises RuntimeError on invalid token.
    """
    try:
        plaintext = fernet.decrypt(ciphertext)
    except InvalidToken as e:
        raise RuntimeError("Invalid token during decryption: " + str(e))
    return json.loads(plaintext.decode('utf-8'))

def compute_sha256(payload_dict):
    """
    Compute canonical SHA-256 hex digest for a payload dict.
    Sorting keys ensures canonical representation.
    """
    canonical = json.dumps(payload_dict, sort_keys=True).encode('utf-8')
    return hashlib.sha256(canonical).hexdigest()

def compute_sha256_bytes(data_bytes):
    """Compute SHA256 hex digest of raw bytes."""
    return hashlib.sha256(data_bytes).hexdigest()

def verify_hash(payload_dict, expected_hash):
    """Return True if computed hash matches expected_hash."""
    return compute_sha256(payload_dict) == expected_hash

class CryptoManager:
    """
    Convenience wrapper around Fernet + hashing operations.
    Instantiate with a Fernet key (bytes or base64 string).
    """
    def __init__(self, fernet_key):
        # load_fernet will validate and raise a descriptive error if bad
        self.fernet = load_fernet(fernet_key)

    def encrypt(self, payload_dict):
        """
        Encrypts and returns (ciphertext_bytes, payload_hash_hex)
        """
        payload_hash = compute_sha256(payload_dict)
        ciphertext = encrypt_payload(self.fernet, payload_dict)
        return ciphertext, payload_hash

    def decrypt(self, ciphertext):
        """Return decrypted payload dict from ciphertext bytes."""
        return decrypt_payload(self.fernet, ciphertext)

    def verify(self, payload_dict, expected_hash):
        """Return True if payload matches expected hash."""
        return verify_hash(payload_dict, expected_hash)
