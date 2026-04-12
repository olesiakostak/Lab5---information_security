import time
from services.lcg import LCG

class RC5:
    def __init__(self, w, r, key_bytes):
        self.w = w
        self.r = r
        self.b = len(key_bytes)
        self.key = key_bytes
        self.u = self.w // 8
        self.mod = 1 << self.w
        self.mask = self.mod - 1

        if self.w == 16:
            self.P = 0xB7E1
            self.Q = 0x9E37
        else:
            raise ValueError("Ця реалізація оптимізована під w=16")

        self.S = self.key_expansion()

    def rotate_left(self, val, shift):
        shift = shift & (self.w - 1)
        return ((val << shift) | (val >> (self.w - shift))) & self.mask

    def rotate_right(self, val, shift):
        shift = shift & (self.w - 1)
        return ((val >> shift) | (val << (self.w - shift))) & self.mask

    def key_expansion(self):
        aligned_b = ((self.b + self.u - 1) // self.u) * self.u
        padded_key = self.key.ljust(aligned_b, b'\x00')
        c = aligned_b // self.u
        if c == 0:
            c = 1
            padded_key = b'\x00' * self.u

        L = [0] * c
        for i in range(c):
            chunk = padded_key[i*self.u : (i+1)*self.u]
            L[i] = int.from_bytes(chunk, byteorder='little')

        t = 2 * self.r + 2
        S = [0] * t
        S[0] = self.P
        for i in range(1, t):
            S[i] = (S[i-1] + self.Q) & self.mask

        i = j = A = B = 0
        for _ in range(3 * max(c, t)):
            A = S[i] = self.rotate_left((S[i] + A + B) & self.mask, 3)
            B = L[j] = self.rotate_left((L[j] + A + B) & self.mask, A + B)
            i = (i + 1) % t
            j = (j + 1) % c
        return S

    def encrypt_block(self, data):
        A = int.from_bytes(data[:self.u], byteorder='little')
        B = int.from_bytes(data[self.u:], byteorder='little')

        A = (A + self.S[0]) & self.mask
        B = (B + self.S[1]) & self.mask

        for i in range(1, self.r + 1):
            A = (self.rotate_left(A ^ B, B) + self.S[2 * i]) & self.mask
            B = (self.rotate_left(B ^ A, A) + self.S[2 * i + 1]) & self.mask

        return A.to_bytes(self.u, byteorder='little') + B.to_bytes(self.u, byteorder='little')

    def decrypt_block(self, data):
        A = int.from_bytes(data[:self.u], byteorder='little')
        B = int.from_bytes(data[self.u:], byteorder='little')

        for i in range(self.r, 0, -1):
            B = self.rotate_right((B - self.S[2 * i + 1]) & self.mask, A) ^ A
            A = self.rotate_right((A - self.S[2 * i]) & self.mask, B) ^ B

        B = (B - self.S[1]) & self.mask
        A = (A - self.S[0]) & self.mask

        return A.to_bytes(self.u, byteorder='little') + B.to_bytes(self.u, byteorder='little')


def pad(data, block_size):
    pad_len = block_size - (len(data) % block_size)
    return data + bytes([pad_len] * pad_len)

def unpad(data, block_size):
    pad_len = data[-1]
    if pad_len < 1 or pad_len > block_size:
        raise ValueError("Maybe password is wrong or file is damaged.")
    return data[:-pad_len]

def generate_iv_lcg(block_size):
    import time
    from services.lcg import LCG
    
    m = (2**13) - 1
    a = 5**5
    c = 3
    seed = int(time.time() * 1000) % m
    gen = LCG(m=m, a=a, c=c, seed=seed)
    
    nums = gen.generate(3)
    val = (nums[0] << 26) | (nums[1] << 13) | nums[2]
    
    mask = (1 << (block_size * 8)) - 1
    val = val & mask
    
    return val.to_bytes(block_size, byteorder='little')

def rc5_cbc_pad_encrypt(data, key_bytes, w, r):
    rc5 = RC5(w, r, key_bytes)
    block_size = (2 * w) // 8
    
    iv = generate_iv_lcg(block_size)
    enc_iv = rc5.encrypt_block(iv) 
    
    result = bytearray(enc_iv) 
    padded_data = pad(data, block_size)
    
    prev_block = iv
    for i in range(0, len(padded_data), block_size):
        block = padded_data[i:i+block_size]
        xored_block = bytes(a ^ b for a, b in zip(block, prev_block))
        enc_block = rc5.encrypt_block(xored_block)
        result.extend(enc_block)
        prev_block = enc_block
        
    return bytes(result)

def rc5_cbc_pad_decrypt(data, key_bytes, w, r):
    rc5 = RC5(w, r, key_bytes)
    block_size = (2 * w) // 8
    
    if len(data) < block_size * 2:
        raise ValueError("File is too short!")
        
    enc_iv = data[:block_size]
    iv = rc5.decrypt_block(enc_iv)
    
    result = bytearray()
    prev_block = iv
    
    for i in range(block_size, len(data), block_size):
        enc_block = data[i:i+block_size]
        dec_block = rc5.decrypt_block(enc_block)
        xored_block = bytes(a ^ b for a, b in zip(dec_block, prev_block))
        result.extend(xored_block)
        prev_block = enc_block
        
    return unpad(bytes(result), block_size)