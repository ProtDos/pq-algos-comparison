# Post-Quantum Cryptography Benchmarks

Welcome to the repository for benchmarking various post-quantum cryptographic algorithms. This document provides details on setup, execution, and performance metrics for each algorithm tested.

---

## Speed Testing - Python Implementation
The projects listed below are unofficial and programmed using python. I have tested them too, because thats what I have been using for my application.
<details>
  <summary>Click me</summary>

### Kyber

#### Overview
Kyber is a lattice-based KEM that offers strong security guarantees and high performance, making it suitable for post-quantum cryptographic applications.
- Official Website: [Crystals Project](https://pq-crystals.org/kyber/)
- Reference Implementation: [Download GitHub](https://github.com/GiacomoPope/kyber-py)
- Documentation: [Specification (PDF)](https://pq-crystals.org/kyber/data/kyber-specification-round3-20210804.pdf)

#### Testing
```bash
cd Python_implementation/kyber/src
python3 benchmark_kyber.py
```

#### Performance Metrics
The table below shows the performance for various parameter sets:

```text
--------------------------------------------------------------------------------
   Params    |  keygen  |  keygen/s  |  encap  |  encap/s  |  decap  |  decap/s
--------------------------------------------------------------------------------
 Kyber512    |   2.83ms |     353.25 |  3.92ms |    255.35 |  5.62ms |  177.84 |
 Kyber768    |   4.79ms |     208.98 |  6.05ms |    165.38 |  8.31ms |  120.34 |
 Kyber1024   |   7.21ms |     138.68 |  8.66ms |    115.54 | 11.45ms |   87.35 |
```
The `Kyber1024` parameter set is the one that we'll take to compare to the other algorithms, as it's the most secure and also [recommended one](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf) (page 39).

---

### McEliece

#### Overview
McEliece is a code-based cryptographic algorithm known for its resilience to quantum attacks. It has a long history of reliability in the cryptographic community.
- Official Website: [Project Page](https://classic.mceliece.org/)
- Reference Implementation: [Download GitHub](https://github.com/Niiklasu/mceliece)
- Documentation: [Specification (PDF)](https://classic.mceliece.org/mceliece-impl-20221023.pdf)

###  Testing
Coming soon...

#### Performance Metrics
(TODO: Include specific metrics once tests are completed.)

---

### NTRU

#### Overview
NTRU is a lattice-based cryptosystem offering efficient encryption and decryption with high security. It has been extensively studied and standardized.

#### Performance Metrics
- Official Website: [Project Page](https://www.ntru.org/)
- Reference Implementation: [Download GitHub](https://github.com/ProtDos/pq-ntru)
- Documentation: [Specification (PDF)](https://www.ntru.org/f/hps98.pdf)

#### Testing
```bash
cd Python_implementation/NTRU
python3 ntru.py
```

#### Performance Metrics
The table below shows the performance for various parameter sets:

##### [Parameter Set](https://en.wikipedia.org/wiki/NTRUEncrypt#Table_1:_Parameters)
| Security Margin                      | N   | q    | p |
|--------------------------------------|-----|------|---|
| 128 bit security margin (NTRU-HPS)  | 509 | 2048 | 3 |
| 192 bit security margin (NTRU-HPS)  | 677 | 2048 | 3 |
| 256 bit security margin (NTRU-HPS)  | 821 | 4096 | 3 |
| 256 bit security margin (NTRU-HRSS) | 701 | 8192 | 3 |


##### Performance
| Params       | Keygen  | Keygen/s | Encap   | Encap/s | Decap   | Decap/s |
|--------------|---------|----------|---------|---------|---------|---------|
| ntru128_hps  | 20.0s   | 0.05     | 656.5ms | 1.52    | 1.3s    | 0.77    |
| ntru192_hps  | 75.0s   | 0.01     | 1.2s    | 0.83    | 2.6s    | 0.39    |
| ntru256_hps  | 65.6s   | 0.02     | 2.0s    | 0.50    | 3.8s    | 0.26    |
| ntru256_hrss | 55.0s   | 0.02     | 1.5s    | 0.67    | 2.9s    | 0.34    |

</details>



## Speed Testing - Original NIST Implementation
The time analysis is in cycle counts. They result from this processor: `Intel i5-4430 (4) @ 3.200GHz`. Times may very between tests and different devices.
<details>
  <summary>Click me</summary>

### HQC (Hamming Quasi-Cyclic)

#### Overview
HQC is a post-quantum key encapsulation mechanism (KEM) designed for robustness and efficiency. It achieves security using a combination of code-based cryptography and structured lattices.

- Official Website: [HQC Project](http://pqc-hqc.org/implementation.html)
- Reference Implementation: [Download](http://pqc-hqc.org/doc/hqc-reference-implementation_2024-10-30.zip)
- Documentation: [Specification (PDF)](http://pqc-hqc.org/doc/hqc-specification_2024-10-30.pdf)

#### Configuration
Tested with HQC-256, providing a security level of 256 bits.

#### How to Run
Follow these steps to set up and measure performance:

```bash
# Change directory
cd HQC/hqc-256

# Install required dependencies
sudo dnf install ntl-devel
sudo dnf install gmp-devel
sudo dnf install gf2x-devel

# Build the implementation
make hqc-256

# Run average time script
chmod +x average_time.sh
./average_time.sh
```

#### Results
The average time for 100 runs:
- **Time per operation:** 0.0129 seconds (12.9 ms)

---

### SABER
#### Overview
SABER is an IND-CCA2 secure Key Encapsulation Mechanism (KEM) whose security relies on the hardness of the Module Learning With Rounding problem (MLWR) and remains secure even against quantum computers. 
- Official Website: [Project Page](https://www.esat.kuleuven.be/cosic/pqcrypto/saber/index.html)
- Reference Implementation: [Download GitHub](https://github.com/KULeuven-COSIC/SABER)
- Documentation: [Specification (PDF)](https://eprint.iacr.org/2018/230.pdf)

#### Testing
```bash
git clone https://github.com/KULeuven-COSIC/SABER
cd SABER/Reference_Implementation_KEM
```
Change `SABER_L` in `SABER_params.h` to `4`, so it uses the parameters for entropy of 256, same as all the other algorithms.
```bash
make clean
make all
./test/test_kex
```

#### Performance Metrics
The table below shows the performance. The values are in cycle counts and not times:


| Params      | Keygen | Keygen/s | Encap   | Encap/s | Decap  | Decap/s |
|-------------|--------|----------|---------|---------|--------|---------|
| FireSaber   | 211181 | ---      | 227181d | ---     | 227877 | ---     |




---

### Kyber

#### Overview
Kyber is an IND-CCA2-secure key encapsulation mechanism (KEM), whose security is based on the hardness of solving the learning-with-errors (LWE) problem over module lattices. Kyber is one of the finalists in the NIST post-quantum cryptography project. 
- Official Website: [Project Page](https://pq-crystals.org/kyber/index.shtml)
- Reference Implementation: [Download GitHub](https://github.com/pq-crystals/kyber.git)
- Documentation: [Specification (PDF)](https://pq-crystals.org/kyber/data/kyber-specification-round3-20210804.pdf)

#### Testing
```bash
git clone https://github.com/pq-crystals/kyber.git
cd kyber/ref && make
cd ../avx2 && make 
./test/test_speed1024
```

#### Performance Metrics
The table below shows the performance. The values are in cycle counts and not times:


| Params     | Keygen | Keygen/s | Encap  | Encap/s | Decap  | Decap/s |
|------------|--------|----------|--------|---------|--------|---------|
| Kyber-1024 | 316494 | ---      | 347092 | ---     | 425869 | ---     |



---

### Mc Eliece

#### Overview
Kyber is an IND-CCA2-secure key encapsulation mechanism (KEM), whose security is based on the hardness of solving the learning-with-errors (LWE) problem over module lattices. Kyber is one of the finalists in the NIST post-quantum cryptography project. 
- Official Website: [Project Page](https://pq-crystals.org/kyber/index.shtml)
- Reference Implementation: [Download GitHub](https://github.com/pq-crystals/kyber.git)
- Documentation: [Specification (PDF)](https://pq-crystals.org/kyber/data/kyber-specification-round3-20210804.pdf)

#### Testing
```bash
wget -m https://lib.mceliece.org/libmceliece-latest-version.txt
version=$(cat lib.mceliece.org/libmceliece-latest-version.txt)
wget -m https://lib.mceliece.org/libmceliece-$version.tar.gz
tar -xzf lib.mceliece.org/libmceliece-$version.tar.gz
cd libmceliece-$version

./configure && make -j8 install
```

#### Performance Metrics
All speed metrics are shown here: https://lib.mceliece.org/speed.html

---

### NTRU
#### Overview
NTRU is a lattice-based cryptosystem offering efficient encryption and decryption with high security. It has been extensively studied and standardized.

#### Performance Metrics
- Official Website: [Project Page](https://www.ntru.org/)
- Reference Implementation: [Download GitHub](https://github.com/ProtDos/pq-ntru)
- Documentation: [Specification (PDF)](https://www.ntru.org/f/hps98.pdf)

#### Testing
```bash
git clone https://github.com/jschanck/ntru.git
cd ref-hrss701 && make
./test/speed
```
#### Performance Metrics
The table below shows the performance. The values are in cycle counts and not times:


| Params | Keygen  | Keygen/s | Encap  | Encap/s | Decap  | Decap/s |
|--------|---------|----------|--------|---------|--------|---------|
| NTRU   | 3501672 | ---      | 114842 | ---     | 274140 | ---     |


</details>


---

## Conclusion
### NIST Implementation
| **Algorithm** | **Key Generation** | **Encryption**   | **Decryption**   |
|---------------|--------------------|------------------|------------------|
| **SABER**     | 211181 ⇒ 0.066ms   | 227181 ⇒ 0.068ms | 227877 ⇒ 0.068ms |
| **Kyber**     | 324211 ⇒ 0.101ms   | 347092 ⇒ 0.109ms | 425869 ⇒ 0.130ms |
| **McEliece**  | 24106405 ⇒ 7.54ms  | 20804 ⇒ 0.006ms  | 106097 ⇒ 0.032ms |
| **NTRU**      | 3877727 ⇒ 1.21ms   | 114842 ⇒ 0.036ms | 274140 ⇒ 0.086ms |

### Python Implementation
| **Algorithm** | **Key Generation** | **Encryption** | **Decryption** |
|---------------|--------------------|----------------|----------------|
| **Kyber**     | 7.21ms             | 8.66ms         | 1.45ms         |
| **McEliece**  | ---                | ---            | ---            |
| **NTRU**      | 55.0s              | 1.5s           | 2.9s           |

As you can see the times vary a lot between the C-Implementation and the Python-Implementation. As we all know, Python is slow.
