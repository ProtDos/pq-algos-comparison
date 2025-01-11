import time
import numpy as np
from logger import logger
from NTRUencrypt import NTRUencrypt
from NTRUdecrypt import NTRUdecrypt
from utils import factor_int
import base64


# Constants for N, p, q, df, dg, d parameter sets
PARAM_SETS = {
    "moderate": {"N": 107, "p": 3, "q": 64, "df": 15, "dg": 12, "d": 5},  # the key generation for this takes around 0.5sec
    "high": {"N": 167, "p": 3, "q": 128, "df": 61, "dg": 20, "d": 18},  # the key generation for this takes around 1.4sec
    "highest": {"N": 503, "p": 3, "q": 256, "df": 216, "dg": 72, "d": 55},  # the key generation for this takes around 15sec

    "dead": {"N": 701, "p": 3, "q": 8192, "df": 216, "dg": 72, "d": 55},  # the key generation for this takes around 50sec
    "dead2": {"N": 821, "p": 3, "q": 4096, "df": 216, "dg": 72, "d": 55},  # the key generation for this takes around 64sec

    "ntru128_hps": {"N": 509, "p": 3, "q": 2048, "df": 146, "dg": 72, "d": 50},  # 128-bit security margin (NTRU-HPS)
    "ntru192_hps": {"N": 677, "p": 3, "q": 2048, "df": 200, "dg": 112, "d": 70},  # 192-bit security margin (NTRU-HPS)
    "ntru256_hps": {"N": 821, "p": 3, "q": 4096, "df": 216, "dg": 120, "d": 80},  # 256-bit security margin (NTRU-HPS)
    "ntru256_hrss": {"N": 701, "p": 3, "q": 8192, "df": 216, "dg": 72, "d": 55},  # 256-bit security margin (NTRU-HRSS)

}
"""
where:
- N is the order of the polynomial ring, 
- p is the modulus of the polynomial f (which has df 1 coefficients and df-1 -1 coefficients), 
- q is the modulus of the polynomial g (which has dg 1 and -1 coefficients),
- d is the number of 1 and -1 coefficients in the obfuscating polynomial.
"""

"""
This is from Wikipedia: https://en.wikipedia.org/wiki/NTRUEncrypt#Table_1:_Parameters
+-------------------------------------+-----+------+---+
|                                     | N   | q    | p |
+-------------------------------------+-----+------+---+
| 128 bit security margin (NTRU-HPS)  | 509 | 2048 | 3 |
+-------------------------------------+-----+------+---+
| 192 bit security margin (NTRU-HPS)  | 677 | 2048 | 3 |
+-------------------------------------+-----+------+---+
| 256 bit security margin (NTRU-HPS)  | 821 | 4096 | 3 |
+-------------------------------------+-----+------+---+
| 256 bit security margin (NTRU-HRSS) | 701 | 8192 | 3 |
+-------------------------------------+-----+------+---+
"""


def generate_keys(name: str = "key", mode: str = "highest", skip_check: bool = False, debug: bool = False,
                  check_time: bool = False) -> None:
    """
    Generate a pair of public and private keys using NTRU encryption.

    :param name: name of the key file to output
    :param mode: the security mode to use - "moderate", "high", or "highest"
    :param skip_check: whether to skip the security factor check
    :param debug: whether to enable verbose logger
    :param check_time: whether to log the duration of each step
    """
    if mode not in PARAM_SETS:
        raise ValueError("Mode unknown.")

    params = PARAM_SETS[mode]
    if debug:
        logger.info("Starting key generation in %s mode", mode)

    N1 = NTRUdecrypt(logger, debug=debug, check_time=check_time)
    N1.setNpq(**params)

    start_time = time.time() if check_time else None
    step_start = time.time() if check_time else None
    logger.info("Generating public and private keys")
    N1.genPubPriv(name)
    if check_time:
        elapsed = time.time() - step_start
        logger.info(f"Key generation took {elapsed:.4f} seconds")

    if skip_check:
        logger.info("Skipping security check")
    else:
        logger.info("Performing security check on generated keys")
        step_start = time.time() if check_time else None
        if security_check(N1):
            logger.info("Security check passed")
            if check_time:
                elapsed = time.time() - step_start
                logger.info(f"Security check took {elapsed:.4f} seconds")
        else:
            logger.warning("Security check failed!")

        if attack_simulation(N1):
            logger.info("Security 2 check passed")
            if check_time:
                elapsed = time.time() - step_start
                logger.info(f"Security check 2 took {elapsed:.4f} seconds")
        else:
            logger.warning("Security check 2 failed!")

    if check_time:
        total_elapsed = time.time() - start_time
        logger.info(f"Total key generation process took {total_elapsed:.4f} seconds")


def security_check(N1: NTRUdecrypt) -> bool:
    """
    Perform a security check by factoring NTRU parameters and verifying key strength.

    :param N1: the NTRUdecrypt object containing the parameters
    :return: True if the key passes security checks, False otherwise
    """
    factors = factor_int(N1.h[-1])
    possible_keys = (2 ** N1.df * (N1.df + 1) ** 2 *
                     2 ** N1.dg * (N1.dg + 1) *
                     2 ** N1.dr * (N1.dr + 1))

    logger.debug("Factors of the last parameter: %s", factors)
    logger.debug("Calculated possible keys: %d", possible_keys)

    return len(factors) == 0 and possible_keys > 2 ** 80


def encrypt(name: str, message: str, check_time: bool = False, encode: bool = True) -> str:
    """
    Encrypt a message using the public key.

    :param name: name of the key file
    :param message: plaintext message to encrypt
    :param check_time: whether to log the duration of the encryption process
    :return: encrypted message
    """
    logger.info("Encrypting message with key: %s", name)
    start_time = time.time()

    E = NTRUencrypt()
    E.readPub(f"{name}.pub")
    E.encryptString(message)

    if check_time:
        elapsed = time.time() - start_time
        logger.info(f"Encryption took {elapsed:.4f} seconds")

    if encode:
        return base64.b64encode(E.Me.encode()).decode()
    return E.Me


def decrypt(name: str, cipher: str, check_time: bool = False, encode: bool = True) -> str:
    """
    Decrypt a message using the private key.

    :param name: name of the key file
    :param cipher: encrypted message to decrypt
    :param check_time: whether to log the duration of the decryption process
    :return: decrypted message
    """
    logger.info("Decrypting message with key: %s", name)
    start_time = time.time()

    D = NTRUdecrypt(logger=logger)
    D.readPriv(f"{name}.priv")
    if encode:
        D.decryptString(base64.b64decode(cipher).decode())
    else:
        D.decryptString(cipher)

    if check_time:
        elapsed = time.time() - start_time
        logger.info(f"Decryption took {elapsed:.4f} seconds")

    return D.M


def check_key_sparsity(f, threshold=5):
    """
    Check if the secret key f has a sparsity that could make it vulnerable.

    :param f: The polynomial representing the secret key.
    :param threshold: The maximum number of non-zero coefficients allowed.
    :return: True if the key is vulnerable, False otherwise.
    """
    non_zero_coeffs = np.count_nonzero(f)
    return non_zero_coeffs <= threshold


def attack_simulation(N1):
    """
    Simulate an attack on the generated keys based on sparsity.

    :param N1: The NTRUdecrypt object containing the generated keys.
    """
    logger.info("Simulating attack on the generated keys...")

    # Check if the secret key f is vulnerable
    if check_key_sparsity(N1.f, threshold=5):
        logger.warning("The secret key f has too few non-zero coefficients! This key may be vulnerable to attacks.")
        return False
    else:
        logger.debug("The secret key f appears to be sufficiently dense.")

    # Check the public key h as well
    if check_key_sparsity(N1.h, threshold=5):
        logger.warning("The public key h has too few non-zero coefficients! This key may be vulnerable to attacks.")
        return False
    else:
        logger.debug("The public key h appears to be sufficiently dense.")
        return True


if __name__ == "__main__":
    n = 1  # number of tests
    modes = ["ntru128_hps", "ntru192_hps", "ntru256_hps", "ntru256_hrss"]
    results = []

    for mode in modes:
        total_gen = 0
        total_enc = 0
        total_dec = 0

        for _ in range(n):
            a = time.time()
            generate_keys("key", mode=mode, skip_check=True)
            total_gen += (time.time() - a)

            b = time.time()
            enc = encrypt("key", "test")
            total_enc += (time.time() - b)

            c = time.time()
            decrypt("key", enc)
            total_dec += (time.time() - c)

        avg_gen = (total_gen / n) * 1000  # Convert to ms
        avg_enc = (total_enc / n) * 1000
        avg_dec = (total_dec / n) * 1000

        results.append({
            "params": mode,
            "keygen": avg_gen,
            "keygen_s": 1000 / avg_gen,
            "encap": avg_enc,
            "encap_s": 1000 / avg_enc,
            "decap": avg_dec,
            "decap_s": 1000 / avg_dec,
        })

    # Print results
    print("-" * 80)
    print("   Params    |  keygen  |  keygen/s  |  encap  |  encap/s  |  decap  |  decap/s")
    print("-" * 80)
    for result in results:
        print(f"{result['params']:>10} | {result['keygen']:8.2f} | {result['keygen_s']:10.2f} | "
              f"{result['encap']:7.2f} | {result['encap_s']:9.2f} | {result['decap']:7.2f} | {result['decap_s']:9.2f} |")
    print("-" * 80)

    # generate_keys("key", mode="dead2", skip_check=False, debug=True, check_time=True)
    # enc = encrypt("key", "test", check_time=True)
    # print("Encrypted message:", enc)
    # dec = decrypt("key", enc, check_time=True)
    # print("Decrypted message:", dec)