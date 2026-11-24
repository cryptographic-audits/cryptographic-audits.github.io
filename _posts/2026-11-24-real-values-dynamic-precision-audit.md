---
title: "Technical Audit of Real-Value Hashing and Commitments with Dynamic Precision"
description: "A same-salt opening counterexample, parameter-regime analysis, and reproducible implementation checks for ePrint 2026/2962."
date: 2026-11-24 08:00:00 +0800
categories: [Audits, Commitments]
tags: [real-values, commitments, csis, clwe, dynamic-precision, counterexamples]
math: true
---

> **Scope.** This report has been checked against the current latest version available from IACR ePrint. Its central result is a counterexample to Theorem 6.4 as stated. The remaining findings separate parameter choices, proof relations, and finite-precision implementations from the paper's continuous CSIS/CLWE assumptions.
{: .prompt-info }

[Open the paper on IACR ePrint](https://eprint.iacr.org/2026/2962)

## Overview

**Paper under examination:** Binyi Chen, Yilei Chen, Zhenghao Guan, and Wenjie Li, *How to Hash and Commit Real Values with Dynamic Precision*, IACR ePrint 2026/2962. **Status:** Updated against the current latest version available from IACR ePrint.

The paper develops hashing and commitment mechanisms for real-valued messages whose verification precision can be chosen dynamically. The main constructions combine digit transformations, real-valued lattice assumptions, modular masking, and a proof-of-knowledge protocol. This audit identifies one missing hypothesis that causes a literal binding theorem to fail, then examines several parameter and implementation choices that affect how the constructions can be used.

| Finding | Location | Main consequence |
|---|---|---|
| Same-salt double opening | Theorem 6.4 | Reducing modulo one erases an integer hash difference unless the hash output is range-restricted. |
| Sparse CSIS′ solutions | Corollary 4.25 | In the suggested $m=2n$, $b=2$ regime, a random instance almost surely has no bounded solution. |
| Public relation witnesses | Theorem 8.2 | For $m\le n/2$, a witness for the printed relation can often be computed from the public statement. |
| Coordinate versus bit compression | Definitions 3.3–3.5 | Fewer real coordinates need not mean fewer representation bits. |
| Finite-precision masking | Schemes 6.2 and 6.12 | Truncated salt digits or coarse masking keys can expose message-dependent residues. |
| Numerical cost | Theorem 5.26 | A direct binary64 implementation misses the stated error target, while sufficient fixed-point precision can expand the bit representation. |

## 1. Theorem 6.4 Needs an Output-Range Hypothesis

Scheme 6.3 commits to a message $x$ by computing

$$
C(x;r,\ell)
=\bigl(h_\ell(x)+A_r r\bigr)\bmod 1.
$$

The hypotheses listed in Theorem 6.4 constrain the approximate-collision threshold $f$, the consistency error $g$, and the verification threshold $q$, but they do not constrain the range of $h_\ell$. The proof later uses the additional condition

$$
h_\ell(x)\in
\left(-\frac{1}{100n},\frac{1}{100n}\right)^n.
$$

That condition is essential. Without it, two well-separated hash outputs may differ by an integer vector, which disappears after reduction modulo one.

### A literal counterexample

**Proof.** Let

$$
M=\left\{0,\frac12\right\},
\qquad n=\lambda,
\qquad m=n+1.
$$

For $x\in M^m$, write $b_j=2x_j\in\{0,1\}$ and define

$$
h_\ell(x)=
\left(
b_1+\frac14b_{n+1},
b_2,\ldots,b_n
\right).
$$

This deterministic map is injective. Its first coordinate belongs to $\{0,1/4,1,5/4\}$, and every other input bit occupies its own coordinate. Hence distinct messages have output distance at least $1/4$, so the definitions are satisfied with

$$
f(\ell)=\frac18,
\qquad g(\ell)=0.
$$

Choose

$$
q_\lambda(\ell)=\frac{1}{200\lambda 2^\ell}.
$$

Then $f/3\ge q_\lambda>4g$ and $q_\lambda\le 1/(100\lambda)$. Now take

$$
x_0=(0,\ldots,0),
\qquad
x_1=(1/2,0,\ldots,0).
$$

Their hashes differ by the first standard basis vector:

$$
h_\ell(x_1)-h_\ell(x_0)=e_1.
$$

For every public masking matrix and every common admissible salt,

$$
\begin{aligned}
C(x_1;r,\ell)
&=\bigl(h_\ell(x_0)+e_1+A_rr\bigr)\bmod1\\
&=\bigl(h_\ell(x_0)+A_rr\bigr)\bmod1\\
&=C(x_0;r,\ell).
\end{aligned}
$$

The messages remain a distance $1/2$ apart. Thus the commitment has a same-salt double opening under the theorem's printed hypotheses. $\square$

The repair is direct: promote the small-output-range condition used in the proof to an explicit theorem hypothesis, or make the scaling step mandatory in the scheme.

### For example: a minimal exact reproduction

The core failure needs only exact rational arithmetic; no lattice solver is involved.

```python
from fractions import Fraction as F

def mod_one(x):
    return x - x.numerator // x.denominator

def h(x, n):
    bits = [int(2 * value) for value in x]
    return [F(bits[0]) + F(bits[-1], 4), *map(F, bits[1:-1])]

n, m = 16, 17
x0 = [F(0)] * m
x1 = [F(1, 2), *([F(0)] * (m - 1))]
mask = [F(37, 101)] * n  # any common mask works

c0 = [mod_one(a + b) for a, b in zip(h(x0, n), mask)]
c1 = [mod_one(a + b) for a, b in zip(h(x1, n), mask)]

assert h(x1, n)[0] - h(x0, n)[0] == 1
assert c0 == c1
```

## 2. A CSIS′ Regime with Almost No Solutions

Definition 4.18 asks for a nonzero integer vector $z$ satisfying

$$
\lVert z\rVert_2\le\beta,
\qquad
\lVert Az\rVert_\infty\le\zeta.
$$

Consider

$$
A\leftarrow U([0,1)^{n\times2n}),
\quad
\beta=2\sqrt{2n},
\quad
\zeta=\frac1{8n}.
$$

For fixed nonzero integer $z$, every row of $Az\bmod1$ is uniform on the circle, independently of the other rows. Therefore

$$
\Pr_A\!\left[\lVert Az\rVert_\infty\le\frac1{8n}\right]
\le\left(\frac1{4n}\right)^n.
$$

A Gaussian counting bound gives fewer than $10^{2n}$ integer vectors inside the permitted Euclidean ball. A union bound then yields

$$
\Pr_A[\text{a valid CSIS′ solution exists}]
<10^{2n}(4n)^{-n}
=\left(\frac{25}{n}\right)^n.
$$

At $n=128$, this upper bound is below $10^{-90.78}$. The issue is not a collision algorithm: it is that computational hardness is being invoked in a regime where the search relation is overwhelmingly empty. Parameter statements should include a solution-existence condition before treating failure to solve the instance as evidence of hardness.

## 3. Public Witnesses for the Printed Proof Relation

Section 8 writes the public matrix in row blocks as $A=(a_s;A_w)$ and defines

$$
L(s,w,e)=\gamma(a_s^Ts+A_w^Tw)+e\pmod1.
$$

The relation bounds $s$, $w$, and $e$, but it does not impose the unit-sphere condition used by the honest commitment sampler. Suppose $A_w^T\in\mathbb R^{m\times n}$ has full row rank. For any public $y$ and chosen scalar $s^*\in[-B,B]$, set

$$
\begin{aligned}
t&=\operatorname{center}(y-\gamma a_s^Ts^*),\\
w^*&=\frac1\gamma(A_w^T)^\dagger t,\\
e^*&=0.
\end{aligned}
$$

Then $L(s^*,w^*,0)=y$, and

$$
\lVert w^*\rVert_\infty
\le
\frac{\sqrt m}{2\gamma\,\sigma_{\min}(A_w^T)}.
$$

Thus the public-key condition

$$
\sigma_{\min}(A_w^T)>
\frac{\sqrt m}{2\gamma B}
$$

is sufficient to produce a valid witness for every $y$ and every selected $s^*$. For the paper's Gaussian sampling and $m\le n/2$, standard rectangular-matrix bounds make this the typical case. The formal special-soundness theorem may still extract a witness, but that witness no longer certifies knowledge of the scalar originally committed by the honest algorithm. The relation must encode the intended opening semantics if that is the application goal.

## 4. Coordinate Compression and Representation Size

Definitions 3.3–3.5 count real output coordinates. They therefore admit an unconditional digit-interleaving map: pair two input coordinates, interleave their binary digits as base-4 digits, and store the result in one real coordinate. This reduces $m$ coordinates to $\lceil m/2\rceil$ while preserving all inspected digits.

The construction satisfies the literal separation and consistency requirements, yet the precision of each output coordinate grows with the amount of encoded input. It is coordinate compression, not necessarily bit-length compression. If a short digest representation is intended, its total bit length needs an explicit definition and bound.

## 5. Finite-Precision Masking Requires Its Own Parameters

Two simple identities show why the continuous model does not automatically specify a finite implementation.

In Scheme 6.2, suppose a commitment uses $k$ base-$B$ positions but the salt supplies only $s<k$ digit positions. The final salt digit is then zero, and

$$
(B^k cm)\bmod B=A_xx^{(k)}\bmod B.
$$

The final message digit becomes publicly visible. A finite implementation therefore needs at least as many independent salt digits as the commitment precision requires.

For Scheme 6.12, suppose the public masking key lies on a grid $A_r\in Q^{-1}\mathbb Z^{n\times m_r}$ and the output denominator is $p=QL$. With integer salt,

$$
(Qcm)\bmod1
=
\left(\frac{\lfloor ph(x)\rfloor}{L}\right)\bmod1,
$$

which is independent of the salt. Public-key precision and output quantization therefore have to be chosen and analyzed together.

## 6. Numerical Precision Can Reverse the Apparent Compression

The base-shifting map in Scheme 5.22 can distinguish exact values that binary64 merges. With $B=2^{21}$,

$$
x=\frac12,
\qquad
x'=\frac9{16},
$$

the transformed values differ by $B^{-4}$, but their binary64 encodings are equal. Theorem 5.26 asks for much greater precision than ordinary binary64 provides.

For the illustrative parameters $n=128$, $m=256$, $\ell=128$, and $B=2^{21}$, a direct fixed-point implementation of the theorem's sufficient error target needs about $2723$ fractional bits per output coordinate. The input occupies $32{,}768$ bits, while the output occupies about $348{,}544$ bits. The example is representation-specific, but it makes the engineering point precise: reducing coordinate count does not guarantee a shorter serialized object.

## 7. Conclusions

Theorem 6.4 is false under its printed list of hypotheses because the commitment reduces the hash modulo one without first constraining its range. The same audit also exposes a nearly empty CSIS′ parameter regime, a proof relation with publicly constructible witnesses, and several finite-precision choices that require explicit treatment. These issues have different repairs, but they share a common lesson: real-valued cryptography needs its range, precision, serialization, and relation semantics stated as part of the construction rather than left to implementation convention.

---

## License and Attribution

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

© 2026 cxcx52. All rights reserved except as expressly licensed below.

This technical report is licensed under the [Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). You may share, reproduce, redistribute, adapt, and build upon it, including commercially, provided that appropriate attribution is given, the original work and license are linked, and modifications are indicated.

When referencing or extending these counterexamples, please cite the original report. Researchers interested in stronger counterexamples or further analysis are welcome to contact the author for collaboration.
