/**
 * \file gf2x.h
 * \brief Header file for gf2x.cpp
 */

#ifndef GF2X_H
#define GF2X_H

#include <NTL/GF2X.h>
#include <inttypes.h>

#include "parameters.h"

using namespace NTL;

void vect_mul(uint64_t *o, const uint64_t *v1, const uint64_t *v2);

#endif