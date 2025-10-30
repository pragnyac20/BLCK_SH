import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))

from crypto import (
    generate_fernet_key,
    load_fernet,
    encrypt_payload,
    decrypt_payload,
    compute_sha256,
    verify_hash,
    CryptoManager
)

class TestCrypto(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_key = generate_fernet_key()
        self.fernet = load_fernet(self.test_key)
        self.test_payload = {
            'course': 'CS301',
            'grade': 'A',
            'semester': '2024-2',
            'student_id': 'S12345'
        }
    
    def test_encryption_decryption(self):
        """Test that encryption and decryption work correctly"""
        ciphertext = encrypt_payload(self.fernet, self.test_payload)
        
        # Verify ciphertext is different from plaintext
        self.assertIsInstance(ciphertext, bytes)
        
        # Decrypt and verify
        decrypted = decrypt_payload(self.fernet, ciphertext)
        self.assertEqual(decrypted, self.test_payload)
    
    def test_hashing(self):
        """Test SHA-256 hashing"""
        hash1 = compute_sha256(self.test_payload)
        
        # Verify hash is 64 characters (256 bits in hex)
        self.assertEqual(len(hash1), 64)
        
        # Same input should produce same hash
        hash2 = compute_sha256(self.test_payload)
        self.assertEqual(hash1, hash2)
        
        # Different input should produce different hash
        different_payload = self.test_payload.copy()
        different_payload['grade'] = 'B'
        hash3 = compute_sha256(different_payload)
        self.assertNotEqual(hash1, hash3)
    
    def test_hash_verification(self):
        """Test hash verification"""
        payload_hash = compute_sha256(self.test_payload)
        
        # Correct hash should verify
        self.assertTrue(verify_hash(self.test_payload, payload_hash))
        
        # Wrong hash should not verify
        self.assertFalse(verify_hash(self.test_payload, 'wrong_hash'))
    
    def test_crypto_manager(self):
        """Test CryptoManager class"""
        manager = CryptoManager(self.test_key)
        
        # Test encrypt
        ciphertext, payload_hash = manager.encrypt(self.test_payload)
        self.assertIsInstance(ciphertext, bytes)
        self.assertEqual(len(payload_hash), 64)
        
        # Test decrypt
        decrypted = manager.decrypt(ciphertext)
        self.assertEqual(decrypted, self.test_payload)
        
        # Test verify
        self.assertTrue(manager.verify(self.test_payload, payload_hash))
    
    def test_deterministic_hashing(self):
        """Test that hashing is deterministic"""
        # Same data should always produce same hash
        hashes = [compute_sha256(self.test_payload) for _ in range(10)]
        self.assertEqual(len(set(hashes)), 1)
    
    def test_key_isolation(self):
        """Test that different keys produce different ciphertexts"""
        key1 = generate_fernet_key()
        key2 = generate_fernet_key()
        
        fernet1 = load_fernet(key1)
        fernet2 = load_fernet(key2)
        
        cipher1 = encrypt_payload(fernet1, self.test_payload)
        cipher2 = encrypt_payload(fernet2, self.test_payload)
        
        # Different keys should produce different ciphertexts
        self.assertNotEqual(cipher1, cipher2)
        
        # Cannot decrypt with wrong key
        with self.assertRaises(Exception):
            decrypt_payload(fernet1, cipher2)

if __name__ == '__main__':
    unittest.main()