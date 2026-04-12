import unittest
from services.rsa import generate_rsa_keys, rsa_encrypt_file, rsa_decrypt_file

class TestLab4(unittest.TestCase):
    def setUp(self):
        self.key_size = 2048
        self.priv_pem, self.pub_pem = generate_rsa_keys(self.key_size)
        self.short_message = b"Olesia's secret RSA message"
        self.large_message = b"Hello RSA! " * 50

    def test_key_generation(self):
        self.assertIsNotNone(self.priv_pem)
        self.assertIsNotNone(self.pub_pem)
        
        self.assertIn(b"BEGIN RSA PRIVATE KEY", self.priv_pem)
        self.assertIn(b"BEGIN PUBLIC KEY", self.pub_pem)

    def test_single_block_workflow(self):
        encrypted = rsa_encrypt_file(self.short_message, self.pub_pem, self.key_size)

        self.assertNotEqual(self.short_message, encrypted)
        self.assertEqual(len(encrypted), 256)

        decrypted = rsa_decrypt_file(encrypted, self.priv_pem, self.key_size)
        self.assertEqual(self.short_message, decrypted)

    def test_large_message_workflow(self):
        encrypted = rsa_encrypt_file(self.large_message, self.pub_pem, self.key_size)
        self.assertNotEqual(self.large_message, encrypted)

        self.assertTrue(len(encrypted) % 256 == 0)
        self.assertTrue(len(encrypted) > 256)
        
        decrypted = rsa_decrypt_file(encrypted, self.priv_pem, self.key_size)
        self.assertEqual(self.large_message, decrypted)

    def test_wrong_private_key_raises_error(self):
        encrypted = rsa_encrypt_file(self.short_message, self.pub_pem, self.key_size)
        
        wrong_priv_pem, _ = generate_rsa_keys(self.key_size)
        
        with self.assertRaises(ValueError):
            rsa_decrypt_file(encrypted, wrong_priv_pem, self.key_size)

if __name__ == '__main__':
    unittest.main()