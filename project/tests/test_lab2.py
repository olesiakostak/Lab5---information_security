import unittest
from services.md5_custom import get_md5_hash, count_different_bits

class TestLab2(unittest.TestCase):
    
    def test_md5_vectors(self):
        hash_empty = get_md5_hash(b"")
        self.assertEqual(hash_empty, "d41d8cd98f00b204e9800998ecf8427e")
        
        hash_a = get_md5_hash(b"a")
        self.assertEqual(hash_a, "0cc175b9c0f1b6a831c399e269772661")
        
        hash_abc = get_md5_hash(b"abc")
        self.assertEqual(hash_abc, "900150983cd24fb0d6963f7d28e17f72")
        
        hash_msg = get_md5_hash(b"message digest")
        self.assertEqual(hash_msg, "f96b697d7cb7938d525a2f31aaf161d0")

        hash_alphabet_lower = get_md5_hash(b"abcdefghijklmnopqrstuvwxyz")
        self.assertEqual(hash_alphabet_lower, "c3fcd3d76192e4007dfb496cca67e13b")
        
        hash_alphanumeric = get_md5_hash(b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789")
        self.assertEqual(hash_alphanumeric, "d174ab98d277d9f5a5611c2c9f419d9f")
        
        long_string = b"12345678901234567890123456789012345678901234567890123456789012345678901234567890"
        hash_long_nums = get_md5_hash(long_string)
        self.assertEqual(hash_long_nums, "57edf4a22be3c955ac49da2e2107b67a")

if __name__ == '__main__':
    unittest.main()