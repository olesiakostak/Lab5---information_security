import struct
import math

def rotate_left(x, amount):
    x &= 0xFFFFFFFF
    return ((x << amount) | (x >> (32 - amount))) & 0xFFFFFFFF 

def get_md5_hash(message: bytes):
    message = bytearray(message)
    orig_len_bits = (8 * len(message)) & 0xFFFFFFFFFFFFFFFF 
    
    #Крок 1: додавання доповнення 
    message.append(0x80)
    while len(message) % 64 != 56: 
        message.append(0)
        
    #Крок 2: Додавання значення довжини
    message += struct.pack('<Q', orig_len_bits)

    #Крок 3: ініціалізація MD-буфера
    A, B, C, D = 0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476
    
    T = []
    for i in range(64):
        T.append(int((1 << 32) * abs(math.sin(i + 1))) & 0xFFFFFFFF)

    S = [7, 12, 17, 22] * 4 + [5, 9, 14, 20] * 4 + [4, 11, 16, 23] * 4 + [6, 10, 15, 21] * 4

    #Крок 4: обробка повідомлення блоками по 512 бітів (16-слів)
    for i in range(0, len(message), 64):

        chunk = message[i:i+64]
        M = list(struct.unpack('<16I', chunk))
        a, b, c, d = A, B, C, D

        #функція стисненння
        for j in range(64):
            if 0 <= j <= 15:
                F = (b & c) | (~b & d)
                g = j
            elif 16 <= j <= 31:
                F = (d & b) | (~d & c)
                g = (5 * j + 1) % 16
            elif 32 <= j <= 47:
                F = b ^ c ^ d
                g = (3 * j + 5) % 16
            elif 48 <= j <= 63:
                F = c ^ (b | ~d)
                g = (7 * j) % 16
            
            F = (a + F + T[j] + M[g]) & 0xFFFFFFFF #0xFFFFFFFF - ((1 << 32) - 1)
            a, d, c = d, c, b
            b = (b + rotate_left(F, S[j])) & 0xFFFFFFFF

        A = (A + a) & 0xFFFFFFFF
        B = (B + b) & 0xFFFFFFFF
        C = (C + c) & 0xFFFFFFFF
        D = (D + d) & 0xFFFFFFFF

    res = struct.pack('<4I', A, B, C, D) 
    return res.hex()

def count_different_bits(hash1, hash2):
    h1_int = int(hash1, 16)
    h2_int = int(hash2, 16)
    xor_res = h1_int ^ h2_int
    return bin(xor_res).count('1')