from utils.constants import CONSTANTS_FIRE_SABER
from utils.algorithms import randombytes
from Crypto.Cipher import AES
import time
from kem import KEM

kem = KEM(**CONSTANTS_FIRE_SABER)
a = time.time()
pk, sk = kem.KeyGen()
print(f"Key generation took: {round(time.time()-a,2)}s")
b = time.time()
session_key_alice, ciphertext = kem.Encaps(pk)
print(f"Encapsulation took: {round(time.time()-b,2)}s")
c = time.time()
session_key_eve = kem.Encaps(pk)
print(f"Decapsulation took: {round(time.time()-c,2)}s")

assert session_key_alice != session_key_eve, "Eavesdropping Eve has compromised the session key!"
print("Session key is secure!")

session_key_bob = kem.Decaps(ciphertext, sk)

assert session_key_alice == session_key_bob, "Wrong session key!"

iv = randombytes(16)

aes_A = AES.new(session_key_alice, AES.MODE_CBC, iv)

data = 'Hi Bob! Our communication is now resilient for quantum atacks!'.encode('utf-8')
data = data + b"\x00" * (16 - len(data) % 16)  # Padding (if needed)
aes_encrypted= aes_A.encrypt(data)

aes_B = AES.new(session_key_bob, AES.MODE_CBC, iv)

decrypted_data = aes_B.decrypt(aes_encrypted)

print(f"Original data:  {data}")
print(f"Decrypted data: {decrypted_data}")

assert data == decrypted_data, "Decryption failed!"
print("Decryption successful!")