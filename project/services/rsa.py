from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization

def generate_rsa_keys(key_size=2048):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
    )
    public_key = private_key.public_key()

    priv_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )

    pub_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return priv_pem, pub_pem


def rsa_encrypt_file(data, pub_pem, key_size=2048):
    public_key = serialization.load_pem_public_key(pub_pem)
    
    max_chunk_size = (key_size // 8) - 2 * hashes.SHA256().digest_size - 2
    
    encrypted_data = bytearray()
    
    for i in range(0, len(data), max_chunk_size):
        chunk = data[i:i + max_chunk_size]
        enc_chunk = public_key.encrypt(
            chunk,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        encrypted_data.extend(enc_chunk)
        
    return bytes(encrypted_data)

def rsa_decrypt_file(enc_data, priv_pem, key_size=2048):
    private_key = serialization.load_pem_private_key(priv_pem, password=None)
 
    chunk_size = key_size // 8
    
    decrypted_data = bytearray()
    
    for i in range(0, len(enc_data), chunk_size):
        chunk = enc_data[i:i + chunk_size]
        dec_chunk = private_key.decrypt(
            chunk,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        decrypted_data.extend(dec_chunk)
        
    return bytes(decrypted_data)