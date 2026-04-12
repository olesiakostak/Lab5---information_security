import unittest
from services.rc5 import RC5, pad, unpad, rc5_cbc_pad_encrypt, rc5_cbc_pad_decrypt
from services.md5_custom import get_md5_hash

class TestLab3(unittest.TestCase):
    def setUp(self):
        self.w = 16
        self.r = 20
        self.block_size = (2 * self.w) // 8
        
        self.passphrase = b"olesia_secret_pass"
        pass_hash_hex = get_md5_hash(self.passphrase)
        self.key_bytes = bytes.fromhex(pass_hash_hex)
        
        self.message = b"Heloooooooooooooooooooooooooooooooooooooooooooo world"

    def test_pad_and_unpad(self):
        data1 = b"123" 
        padded1 = pad(data1, self.block_size)
        self.assertEqual(padded1, b"123\x01")
        self.assertEqual(unpad(padded1, self.block_size), data1)

        data2 = b"1234" 
        padded2 = pad(data2, self.block_size)
        self.assertEqual(padded2, b"1234\x04\x04\x04\x04")
        self.assertEqual(unpad(padded2, self.block_size), data2)

    def test_single_block_encryption(self):
        rc5 = RC5(self.w, self.r, self.key_bytes)
        block = b"Test"
        
        encrypted_block = rc5.encrypt_block(block)
        self.assertNotEqual(block, encrypted_block)
        
        decrypted_block = rc5.decrypt_block(encrypted_block)
        self.assertEqual(block, decrypted_block)

    def test_full_cbc_pad_workflow(self): 
        encrypted = rc5_cbc_pad_encrypt(self.message, self.key_bytes, self.w, self.r)
        self.assertNotEqual(self.message, encrypted)
        
        decrypted = rc5_cbc_pad_decrypt(encrypted, self.key_bytes, self.w, self.r)
        self.assertEqual(self.message, decrypted)

    def test_wrong_password_raises_error(self):
        encrypted = rc5_cbc_pad_encrypt(self.message, self.key_bytes, self.w, self.r)
        
        wrong_pass_hash = get_md5_hash(b"hacker_password")
        wrong_key_bytes = bytes.fromhex(wrong_pass_hash)
        
        with self.assertRaises(ValueError):
            rc5_cbc_pad_decrypt(encrypted, wrong_key_bytes, self.w, self.r)

if __name__ == '__main__':
    unittest.main()