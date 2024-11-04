import os
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

class DataEncryption:
    def __init__(self, password: str, salt: bytes):
        self.password = password.encode('utf-8')
        self.salt = salt

    def derive_key(self) -> bytes:
        """Derives a cryptographic key from the provided password using PBKDF2."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(self.password)

    def encrypt_data(self, plaintext: str, associated_data: bytes) -> dict:
        """Encrypts the given plaintext using AES-GCM."""
        aesgcm = AESGCM(self.derive_key())
        nonce = os.urandom(12)  # 96-bit nonce for AES-GCM
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), associated_data)
        return {
            'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
            'nonce': base64.b64encode(nonce).decode('utf-8')
        }

    def decrypt_data(self, ciphertext: str, nonce: str, associated_data: bytes) -> str:
        """Decrypts the given ciphertext using AES-GCM."""
        try:
            aesgcm = AESGCM(self.derive_key())
            decoded_ciphertext = base64.b64decode(ciphertext)
            decoded_nonce = base64.b64decode(nonce)
            return aesgcm.decrypt(decoded_nonce, decoded_ciphertext, associated_data).decode('utf-8')
        except InvalidTag:
            raise ValueError("Invalid decryption attempt")

class KeyManager:
    def __init__(self, master_key: bytes):
        self.master_key = master_key

    def derive_encryption_key(self, salt: bytes) -> bytes:
        """Derives an encryption key using Scrypt."""
        kdf = Scrypt(
            salt=salt,
            length=32,
            n=2**14,
            r=8,
            p=1,
            backend=default_backend()
        )
        return kdf.derive(self.master_key)

    def generate_secure_key(self, length: int = 32) -> bytes:
        """Generates a secure random key."""
        return os.urandom(length)

    def key_rotation(self, current_key: bytes, new_salt: bytes) -> bytes:
        """Rotates the encryption key by deriving a new one from the current key."""
        return self.derive_encryption_key(new_salt)

class FileEncryption:
    def __init__(self, key: bytes):
        self.key = key

    def encrypt_file(self, input_file: str, output_file: str, associated_data: bytes):
        """Encrypts a file using AES-GCM."""
        with open(input_file, 'rb') as f:
            data = f.read()
        aesgcm = AESGCM(self.key)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, data, associated_data)
        with open(output_file, 'wb') as f:
            f.write(base64.b64encode(nonce + ciphertext))

    def decrypt_file(self, input_file: str, output_file: str, associated_data: bytes):
        """Decrypts a file using AES-GCM."""
        with open(input_file, 'rb') as f:
            file_data = base64.b64decode(f.read())
        nonce = file_data[:12]
        ciphertext = file_data[12:]
        aesgcm = AESGCM(self.key)
        decrypted_data = aesgcm.decrypt(nonce, ciphertext, associated_data)
        with open(output_file, 'wb') as f:
            f.write(decrypted_data)

class PasswordEncryption:
    def __init__(self, password: str):
        self.password = password.encode('utf-8')

    def hash_password(self, salt: bytes) -> bytes:
        """Hashes a password with a salt using PBKDF2."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(self.password)

    def verify_password(self, stored_password: bytes, salt: bytes) -> bool:
        """Verifies a password by comparing it to the stored hash."""
        try:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            kdf.verify(self.password, stored_password)
            return True
        except InvalidTag:
            return False

def generate_salt(length: int = 16) -> bytes:
    """Generates a random salt."""
    return os.urandom(length)

def encrypt_database_entry(data: str, encryption_key: bytes, associated_data: bytes) -> dict:
    """Encrypts sensitive database entries."""
    cipher = Cipher(algorithms.AES(encryption_key), modes.GCM(os.urandom(16)), backend=default_backend())
    encryptor = cipher.encryptor()
    encryptor.authenticate_additional_data(associated_data)
    ciphertext = encryptor.update(data.encode('utf-8')) + encryptor.finalize()
    return {
        'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
        'nonce': base64.b64encode(cipher.nonce).decode('utf-8'),
        'tag': base64.b64encode(encryptor.tag).decode('utf-8')
    }

def decrypt_database_entry(encrypted_data: dict, encryption_key: bytes, associated_data: bytes) -> str:
    """Decrypts sensitive database entries."""
    cipher = Cipher(algorithms.AES(encryption_key), modes.GCM(base64.b64decode(encrypted_data['nonce'])), backend=default_backend())
    decryptor = cipher.decryptor()
    decryptor.authenticate_additional_data(associated_data)
    decrypted_data = decryptor.update(base64.b64decode(encrypted_data['ciphertext'])) + decryptor.finalize_with_tag(base64.b64decode(encrypted_data['tag']))
    return decrypted_data.decode('utf-8')

if __name__ == "__main__":
    password = "strongpassword"
    salt = generate_salt()
    encryption = DataEncryption(password, salt)
    
    # Encrypt and decrypt text
    associated_data = b"transaction-id-1234"
    encrypted = encryption.encrypt_data("Sensitive information", associated_data)
    print("Encrypted Data:", encrypted)

    decrypted = encryption.decrypt_data(encrypted['ciphertext'], encrypted['nonce'], associated_data)
    print("Decrypted Data:", decrypted)