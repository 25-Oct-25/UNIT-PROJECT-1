from cryptography.fernet import Fernet
import os

def generate_key(key_path="output/secret.key"):
    """Generate and save an AES encryption key."""
    os.makedirs(os.path.dirname(key_path), exist_ok=True)
    key = Fernet.generate_key()
    with open(key_path, "wb") as key_file:
        key_file.write(key)
    return key_path


def load_key(key_path="output/secret.key"):
    """Load an existing AES encryption key."""
    with open(key_path, "rb") as key_file:
        return key_file.read()


def encrypt_file(file_path, key_path="output/secret.key"):
    """Encrypt a JSON results file."""
    key = load_key(key_path)
    cipher = Fernet(key)

    with open(file_path, "rb") as f:
        data = f.read()

    encrypted_data = cipher.encrypt(data)
    encrypted_path = file_path.replace(".json", "_encrypted.json")

    with open(encrypted_path, "wb") as f:
        f.write(encrypted_data)

    print(f"🔒 File encrypted successfully → {encrypted_path}")
    return encrypted_path


def decrypt_file(encrypted_path, key_path="output/secret.key"):
    """Decrypt an encrypted JSON file."""
    key = load_key(key_path)
    cipher = Fernet(key)

    with open(encrypted_path, "rb") as f:
        encrypted_data = f.read()

    decrypted_data = cipher.decrypt(encrypted_data)
    decrypted_path = encrypted_path.replace("_encrypted.json", "_decrypted.json")

    with open(decrypted_path, "wb") as f:
        f.write(decrypted_data)

    print(f"🔓 File decrypted successfully → {decrypted_path}")
    return decrypted_path
