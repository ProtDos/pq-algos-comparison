/**
 * \file gf2x.cpp
 * \brief Implementation of multiplication of two polynomials
 */

#include "gf2x.h"
using namespace NTL;

GF2XModulus init_modulo();

/**
 * \fn GF2XModulus init_modulo()
 * \brief This function build the modulus \f$ X^n - 1\f$
 * \return the modulus as an GF2XModulus object
 */
GF2XModulus init_modulo() {
  GF2XModulus P;
  GF2X tmp;
  SetCoeff(tmp, PARAM_N, 1);
  SetCoeff(tmp, 0, 1);
  build(P, tmp);
  return P;
}



/** 
 * \fn void vect_mul(uint64_t *o, const uint64_t *v1, const uint64_t *v2)
 * \brief Multiply two vectors
 *
 * Vector multiplication is defined as polynomial multiplication performed modulo the polynomial \f$ X^n - 1\f$.
 *
 * \param[out] o Product of <b>v1</b> and <b>v2</b>
 * \param[in] v1 Pointer to the first vector
 * \param[in] v2 Pointer to the second vector
 */
void vect_mul(uint64_t *o, const uint64_t *v1, const uint64_t *v2) {
  GF2X tmp1, poly1, poly2;
  uint8_t tmp2[VEC_N_SIZE_BYTES] = {0};

  GF2XFromBytes(poly1, (uint8_t *) v1, VEC_N_SIZE_BYTES);
  GF2XFromBytes(poly2, (uint8_t *) v2, VEC_N_SIZE_BYTES);
  GF2XModulus P = init_modulo();

  MulMod(tmp1, poly1, poly2, P);

  BytesFromGF2X(tmp2, tmp1, VEC_N_SIZE_BYTES);
  memcpy(o, tmp2, VEC_N_SIZE_BYTES);
}