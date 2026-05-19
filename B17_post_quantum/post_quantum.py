# salt = os.urandom(32) 
# #HMAC key derivation function
# def hmac_key_derivation(shared_secret: bytes, info: str, salt: bytes = None): 
#     # this function derive one time session key for encryption
#     if salt is None:
#         salt = os.urandom(32)  

#     # generate a Pseudo-Random Key using hash 
#     # extract
#     key = hmac.new(salt, shared_secret, hashlib.sha256).digest() 
   
#     # expand 
#     one_time_session_key = hmac.new(key, info.encode() + b"\x01",hashlib.sha256).digest() 
    
#     return one_time_session_key 
# encryption_key = hmac_key_derivation(shared_secret, "kyber:encryption", salt).hex()
# user_key = hmac_key_derivation(shared_secret, "kyber:user", salt)
# print(f"enc_key: {encryption_key}") 
# print(f"mac_key: {user_key}")

import os
import hashlib
import hmac
from kyber_py.kyber import Kyber768
from kyber_py.ml_kem import ML_KEM_768
from cryptography.hazmat.primitives.kdf.hkdf import HKDF 
from cryptography.hazmat.primitives import hashes
from dilithium_py.dilithium import Dilithium3
from dilithium_py.ml_dsa import ML_DSA_65
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

#hashing
def structured_hashing(*data): 
    h = hashlib.sha256() 
    for i in data: 
        # find the length of the data and include it into the hash for indicating the length of hashed data clearly
        h.update(len(i).to_bytes(4,'big')) 
        h.update(i) 
    return h.digest()


# Alice
# create keys and salt(for later salted hash)
signature_public_key_alice, signature_private_key_alice = ML_DSA_65.keygen()
public_key_Alice, private_key_Alice = ML_KEM_768.keygen()
salt = os.urandom(32) 

# sign the key and salt
# hashed_info = hashlib.sha256(public_key_Alice + salt).digest()
hashed_info_alice = structured_hashing(public_key_Alice, salt)
signature = ML_DSA_65.sign(signature_private_key_alice, hashed_info_alice)

#Alice transmit:
"""public_key_Alice, salt, signature, signature_public_key_alice"""

print(f"Public key : {len(public_key_Alice)} bytes") 
print(f"Private key : {len(private_key_Alice)} bytes")


# Bob
# Bob received:
"""public_key_Alice, salt, signature, signature_public_key_alice"""
#verify the signature
hashed_info_bob = structured_hashing(public_key_Alice,salt)
valid_info = ML_DSA_65.verify(signature_public_key_alice, hashed_info_bob, signature)
if not valid_info:
    print(valid_info)
    raise ValueError("signature not matching")

# encapulation
shared_secret, ciphertext = ML_KEM_768.encaps(public_key_Alice)

#create keys
# Assume Bob's public key is pre-shared / trusted
signature_public_key_bob, signature_private_key_bob = ML_DSA_65.keygen()
public_key_bob, private_key_bob = ML_KEM_768.keygen()


transcript = structured_hashing(public_key_Alice, salt, ciphertext)

signed_cipher = ML_DSA_65.sign(signature_private_key_bob,transcript)
# print(f"The ciphertext Bob obtain: {ciphertext_bob}")
# Bob transmitted:
"""public_key_Alice, salt, ciphertext, signed_cipher, signature_public_key_bob"""

# Alice
# Alice received:
"""public_key_Alice, salt, ciphertext, signed_cipher, signature_public_key_bob"""
transcript = structured_hashing(public_key_Alice, salt, ciphertext)

vaild_cipher = ML_DSA_65.verify(signature_public_key_bob, transcript, signed_cipher)
if not vaild_cipher:
    raise ValueError("signature not matching")

# decapsulation
recover_shared_secret = ML_KEM_768.decaps(private_key_Alice,ciphertext)
print(f"The shared secret that Alice obtain: {recover_shared_secret}")

assert recover_shared_secret == shared_secret

# ====encryption key creation====
    
def key_derivation_HKDF(shared_secret, info:bytes, transcript, salt):

    hkdf = HKDF(algorithm=hashes.SHA256(), length=32, salt=salt, info=info + transcript)
    
    return hkdf.derive(shared_secret)

# print(ciphertext)
# Note: Alice is server, and Bob is client
#  destination and key type is corresponding  
encryption_key_alice_server = key_derivation_HKDF(recover_shared_secret, b"server", transcript, salt)
encryption_key_alice_client = key_derivation_HKDF(recover_shared_secret, b"client", transcript, salt)

encryption_key_bob_client = key_derivation_HKDF(shared_secret, b"client", transcript, salt)
encryption_key_bob_server = key_derivation_HKDF(shared_secret, b"server", transcript, salt)

assert encryption_key_alice_server == encryption_key_bob_server
assert encryption_key_alice_client == encryption_key_bob_client

print(f"Alice enc_key: {encryption_key_alice_server.hex()}") 
print(f"Bob enc_key: {encryption_key_bob_client.hex()}") 

# === communication ===

# Alice
cipher_Alice = ChaCha20Poly1305(encryption_key_alice_client)
nonce = os.urandom(12)
data = b"Transmitted: Go to School"
ChaCha20_ciphertext = cipher_Alice.encrypt(nonce, data, transcript)

#Bob
cipher_Bob = ChaCha20Poly1305(encryption_key_bob_client)
decrypted_data = cipher_Bob.decrypt(nonce, ChaCha20_ciphertext, transcript)
print(decrypted_data)

assert data == decrypted_data