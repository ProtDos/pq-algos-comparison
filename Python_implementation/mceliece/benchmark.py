import time
import numpy as np
from mceliece.mceliececipher import McElieceCipher

# Parameters for the McEliece Cipher
M = 10   # Galois field parameter (example)
N = 1024 # Code length (example)
T = 50   # Error-correcting capability (example)

# Generate random input data for encryption
input_data = np.random.randint(0, 2, N, dtype=np.uint8)

# Benchmark key generation
def benchmark_key_gen():
    start_time = time.time()
    mceliece = McElieceCipher(M, N, T)
    mceliece.generate_random_keys()
    end_time = time.time()
    return end_time - start_time

# Benchmark encryption
def benchmark_encryption(mceliece, input_data):
    start_time = time.time()
    encrypted = mceliece.encrypt(input_data)
    end_time = time.time()
    return end_time - start_time, encrypted

# Benchmark decryption
def benchmark_decryption(mceliece, encrypted_data):
    start_time = time.time()
    decrypted = mceliece.decrypt(encrypted_data)
    end_time = time.time()
    return end_time - start_time, decrypted

# Run multiple tests and calculate averages
def run_benchmarks(num_tests=10):
    keygen_times = []
    enc_times = []
    dec_times = []

    for _ in range(num_tests):
        # Key generation
        mceliece = McElieceCipher(M, N, T)
        keygen_time = benchmark_key_gen()
        keygen_times.append(keygen_time)

        # Prepare cipher with generated keys
        mceliece.generate_random_keys()

        # Encryption
        enc_time, encrypted_data = benchmark_encryption(mceliece, input_data)
        enc_times.append(enc_time)

        # Decryption
        dec_time, decrypted_data = benchmark_decryption(mceliece, encrypted_data)
        dec_times.append(dec_time)

        # Verify correctness
        if not np.array_equal(input_data, decrypted_data):
            raise ValueError("Decryption failed: Input does not match decrypted output.")

    avg_keygen_time = np.mean(keygen_times)
    avg_enc_time = np.mean(enc_times)
    avg_dec_time = np.mean(dec_times)

    return avg_keygen_time, avg_enc_time, avg_dec_time

# Main benchmarking process
if __name__ == "__main__":
    num_tests = 1
    avg_keygen_time, avg_enc_time, avg_dec_time = run_benchmarks(num_tests)

    print("| Params      | Keygen  | Keygen/s | Encap  | Encap/s | Decap  | Decap/s |")
    print("|-------------|---------|----------|--------|---------|--------|---------|")
    print(f"| McEliece    | {avg_keygen_time*1000:.2f}ms | {1/(avg_keygen_time):.2f}   | {avg_enc_time*1000:.2f}ms | {1/(avg_enc_time):.2f}  | {avg_dec_time*1000:.2f}ms | {1/(avg_dec_time):.2f}  |")
