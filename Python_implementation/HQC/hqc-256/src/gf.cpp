/**
 * @file gf.cpp
 * @brief Galois field implementation with multiplication using the pclmulqdq instruction
 */

#include "gf.h"
#include "parameters.h"
#include <stdint.h>
#include <stdio.h>

static uint16_t gf_reduce(uint64_t x, size_t deg_x);
void gf_carryless_mul(uint8_t *c, uint8_t a, uint8_t b);
uint16_t trailing_zero_bits_count(uint16_t a);

/**
 * @brief Generates exp and log lookup tables of GF(2^m).
 *
 * The logarithm of 0 is defined as 2^PARAM_M by convention. <br>
 * The last two elements of the exp table are needed by the gf_mul function from gf_lutmul.cpp
 * (for example if both elements to multiply are zero).
 * @param[out] exp Array of size 2^PARAM_M + 2 receiving the powers of the primitive element
 * @param[out] log Array of size 2^PARAM_M receiving the logarithms of the elements of GF(2^m)
 * @param[in] m Parameter of Galois field GF(2^m)
 */
void gf_generate(uint16_t *exp, uint16_t *log, const int16_t m) {
    uint16_t elt = 1;
    uint16_t alpha = 2; // primitive element of GF(2^PARAM_M)
    uint16_t gf_poly = PARAM_GF_POLY;

    for (size_t i = 0 ; i < (1U << m) - 1 ; ++i){
        exp[i] = elt;
        log[elt] = i;

        elt *= alpha;
        if(elt >= 1 << m)
            elt ^= gf_poly;
    }

    exp[(1 << m) - 1] = 1;
    exp[1 << m] = 2;
    exp[(1 << m) + 1] = 4;
    log[0] = 0; // by convention
}



/**
 * @brief Computes the number of trailing zero bits.
 *
 * @returns The number of trailing zero bits in a.
 * @param[in] a An operand
 */
uint16_t trailing_zero_bits_count(uint16_t a) {
    uint16_t tmp = 0;
    uint16_t mask = 0xFFFF;
    for (int i = 0; i < 14; ++i) {
        tmp += ((1 - ((a >> i) & 0x0001)) & mask);
        mask &= - (1 - ((a >> i) & 0x0001));
    }
    return tmp;
}



/**
 * Reduces polynomial x modulo primitive polynomial GF_POLY.
 * @returns x mod GF_POLY
 * @param[in] x Polynomial of degree less than 64
 * @param[in] deg_x The degree of polynomial x
 */
static uint16_t gf_reduce(uint64_t x, size_t deg_x) {
    uint16_t z1, z2, rmdr, dist;
    uint64_t mod;
    size_t steps, i, j;

    // Deduce the number of steps of reduction
    steps = CEIL_DIVIDE(deg_x - (PARAM_M - 1), PARAM_GF_POLY_M2);

    // Reduce
    for (i = 0; i < steps; ++i) {
        mod = x >> PARAM_M;
        x &= (1 << PARAM_M) - 1;
        x ^= mod;

        z1 = 0;
        rmdr = PARAM_GF_POLY ^ 1;
        for (j = PARAM_GF_POLY_WT - 2; j; --j) {
            z2 = trailing_zero_bits_count(rmdr);
            dist = (uint16_t) (z2 - z1);
            mod <<= dist;
            x ^= mod;
            rmdr ^= 1 << z2;
            z1 = z2;
        }
    }

    return x;
}



/**
 * Carryless multiplication of two polynomials a and b.
 * 
 * Implementation of the algorithm mul1 in https://hal.inria.fr/inria-00188261v4/document
 * with s = 2 and w = 8
 * 
 * @param[out] The polynomial c = a * b
 * @param[in] a The first polynomial
 * @param[in] b The second polynomial
 */
void gf_carryless_mul(uint8_t *c, uint8_t a, uint8_t b) {
  uint16_t       h = 0, l = 0, g, u[4];
  u[0] = 0;
  u[1] = b & ((1UL << 7) - 1UL);
  u[2] = u[1] << 1;
  u[3] = u[2] ^ u[1];

  g = 0;
  uint16_t tmp1 = a & 3;

  for(int i =0; i < 4; i++) {
    uint32_t tmp2 = tmp1 - i;
    g ^= (u[i] & -(1 - ((tmp2 | -tmp2) >> 31)));
  }

  l = g;
  h = 0;

  for (uint8_t i = 2; i < 8; i+=2) {
    g = 0;
    uint16_t tmp1 = (a >> i) & 3;
    for (int j = 0; j < 4; ++j) {
      uint32_t tmp2 = tmp1 - j;
      g ^= (u[j] & -(1 - ((tmp2 | -tmp2) >> 31)));
    }
    
    l ^= g << i;
    h ^= g >> (8 - i);
  }

  uint16_t mask = (-((b >> 7) & 1));
  l ^= ((a << 7) & mask);
  h ^= ((a >> (1)) & mask);

  c[0] = l;
  c[1] = h;
}



/**
 * Multiplies two elements of GF(2^GF_M).
 * @returns the product a*b
 * @param[in] a Element of GF(2^GF_M)
 * @param[in] b Element of GF(2^GF_M)
 */
uint16_t gf_mul(uint16_t a, uint16_t b) {
    uint8_t c[2] = {0};
    gf_carryless_mul(c, (uint8_t) a, (uint8_t) b);
    uint16_t tmp = (uint16_t) (c[0] ^ (c[1] << 8));
    return gf_reduce(tmp, 2*(PARAM_M-1));
}



/**
 * Squares an element of GF(2^GF_M).
 * @returns a^2
 * @param[in] a Element of GF(2^GF_M)
 */
uint16_t gf_square(uint16_t a) {
    uint32_t b = a;
    uint32_t s = b & 1;     
    for (size_t i = 1; i < PARAM_M; ++i) {
        b <<= 1;
        s ^= b & (1 << 2 * i);
    }

    return gf_reduce(s, 2 * (PARAM_M - 1));
}



/**
 * Computes the inverse of an element of GF(2^8),
 * using the addition chain 1 2 3 4 7 11 15 30 60 120 127 254
 * @returns the inverse of a
 * @param[in] a Element of GF(2^GF_M)
 */
uint16_t gf_inverse(uint16_t a) {
    uint16_t inv = a;
    uint16_t tmp1, tmp2;

    inv = gf_square(a); /* a^2 */
    tmp1 = gf_mul(inv, a); /* a^3 */
    inv = gf_square(inv); /* a^4 */
    tmp2 = gf_mul(inv, tmp1); /* a^7 */
    tmp1 = gf_mul(inv, tmp2); /* a^11 */
    inv = gf_mul(tmp1, inv); /* a^15 */
    inv = gf_square(inv); /* a^30 */
    inv = gf_square(inv); /* a^60 */
    inv = gf_square(inv); /* a^120 */
    inv = gf_mul(inv, tmp2); /* a^127 */
    inv = gf_square(inv); /* a^254 */
    return inv;
}



/**
 * Returns i modulo 2^GF_M-1.
 * i must be less than 2*(2^GF_M-1).
 * Therefore, the return value is either i or i-2^GF_M+1.
 * @returns i mod (2^GF_M-1)
 * @param[in] i The integer whose modulo is taken
 */
uint16_t gf_mod(uint16_t i) {
    uint16_t tmp = i - PARAM_GF_MUL_ORDER;

    // mask = 0xffff if (i < GF_MUL_ORDER)
    int16_t mask = -(tmp >> 15);

    return tmp + (mask & PARAM_GF_MUL_ORDER);
}
