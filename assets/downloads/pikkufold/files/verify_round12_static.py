#!/usr/bin/env python3
"""Independent no-dependency arithmetic sanity check for Round12 challenge fixtures."""
import cmath
import json
import math

Q = (1 << 50) - 2687
BETA = 739582794740178
POS = [1,4,5,6,9,13,16,21,22,23,24,25,33,34,35,37,41,42,48,55,58,60,62]
SIGN = [1,-1,-1,-1,1,1,1,-1,1,-1,1,1,1,-1,-1,1,1,1,-1,-1,-1,1,1]
WEIGHT = 23
CAP = 8.357


def challenge(k):
    coeffs = [0] * 64
    for p, s in zip(POS, SIGN):
        degree = (2 * p * k) % 256
        index = (degree % 128) // 2
        sign = -s if degree >= 128 else s
        assert coeffs[index] == 0, (k, index)
        coeffs[index] = sign
    assert len([v for v in coeffs if v]) == WEIGHT
    return coeffs


def slot_eval(coeffs):
    return sum(s * pow(BETA, i, Q) for i, s in enumerate(coeffs)) % Q


def spectral_norm(coeffs):
    values = []
    for j in range(64):
        angle = math.pi * (2*j + 1) / 64
        values.append(abs(sum(s * cmath.exp(1j * angle * i)
                              for i,s in enumerate(coeffs) if s)))
    return max(values)

assert pow(BETA, 64, Q) == Q - 1
assert pow(BETA, 128, Q) == 1
out = {}
for label, power in [('GOOD',1), ('BAD',3)]:
    z = challenge(power)
    norm = spectral_norm(z)
    residue = slot_eval(z)
    assert norm < CAP - 0.1
    if label == 'GOOD':
        assert residue == 0
    else:
        assert residue != 0
    out[label] = {
        'weight':sum(v!=0 for v in z),
        'slot_evaluation_mod_q':residue,
        'operator_norm':round(norm,12),
        'norm_cap':CAP,
    }
print(json.dumps(out, ensure_ascii=False, indent=2))
