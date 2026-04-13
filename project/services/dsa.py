from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import dsa
from cryptography.exceptions import InvalidSignature


def generate_dsa_keys(key_size: int = 1024) -> tuple[bytes, bytes]:
    '''
    Generates a pair of DSA keys in PEM format
    '''
    private_key = dsa.generate_private_key(key_size=key_size)
    public_key = private_key.public_key()

    priv_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    pub_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return priv_pem, pub_pem


def dsa_sign(data: bytes, priv_key_pem: bytes) -> str:
    '''
    Creates digital Signature using Private key
    '''
    private_key = serialization.load_pem_private_key(
        priv_key_pem,
        password=None
    )
    signature = private_key.sign(data, hashes.SHA256())
    return signature.hex()


def dsa_verify(signature_hex: str, data: bytes, pub_key_pem: bytes) -> bool:
    '''
    Verifies Signature using Public key'''
    try:
        public_key = serialization.load_pem_public_key(pub_key_pem)
        signature = bytes.fromhex(signature_hex)
        public_key.verify(signature, data, hashes.SHA256())
        return True
    except InvalidSignature:
        return False
    except Exception as e:
        return False