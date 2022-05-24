import getpass
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.padding import PKCS7
from dotenv import load_dotenv
import os

def encrypt_pass(file_str):
    digest = hashes.Hash(hashes.SHA256())
    password = getpass.getpass('Password:')
    digest.update(password.encode('ascii'))
    init_vec = bytes(b'\x9a3\x8a*\xce{Zpu\xe0W\xc0\x19i2\xc5')
    cipher = Cipher(algorithms.AES(digest.finalize()), modes.CFB(init_vec))
    encryptor = cipher.encryptor()

    file = open(file_str, "r+")
    contents = bytes(file.read(), 'ascii')
    ct = encryptor.update(contents) + encryptor.finalize()
    new_file = open("encrypted.txt", "w")
    encrypt_data = ct.hex()
    new_file.write(encrypt_data)

    new_file.close()
    file.close()
    

def decrypt_file_contents(file_str):
    # below is code for inputting a password to start the program with the wallet
    """ while True:
        try:
            digest = hashes.Hash(hashes.SHA256())
            password = getpass.getpass('Password:')
            digest.update(password.encode('ascii'))
            init_vec = bytes(b'\x9a3\x8a*\xce{Zpu\xe0W\xc0\x19i2\xc5')
            cipher = Cipher(algorithms.AES(digest.finalize()), modes.CFB(init_vec))
            decrypt_file = open(file_str, "r")
            contents = decrypt_file.read()
            decryptor = cipher.decryptor()
            return decryptor.update(bytes.fromhex(contents)).decode()
        except:
            print("Incorrect Password") """
    load_dotenv()
    password = os.getenv("PASS2")
    digest = hashes.Hash(hashes.SHA256())
    # password = getpass.getpass('Password:')
    digest.update(password.encode('ascii'))
    init_vec = bytes(b'\x9a3\x8a*\xce{Zpu\xe0W\xc0\x19i2\xc5')
    cipher = Cipher(algorithms.AES(digest.finalize()), modes.CFB(init_vec))
    decrypt_file = open(file_str, "r")
    contents = decrypt_file.read()
    decryptor = cipher.decryptor()
    return decryptor.update(bytes.fromhex(contents)).decode()