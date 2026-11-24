---
title: "A Zero-Slot Concentration in PikkuFold's 50-Bit Challenge Sampler"
description: "A certified challenge concentration, a no-short-witness instance, and a verifier-path reproduction for PikkuFold."
date: 2026-11-24 08:05:00 +0800
categories: [Audits, Folding Schemes]
tags: [pikkufold, lattice, folding, challenge-sampling, sumcheck, zero-divisors]
math: true
---

> **Scope.** This report has been checked against the current latest version available from IACR ePrint. It analyzes the 50-bit implementation parameters in Section 6.2 and Table 6, together with Heuristic 1, Definition 11, Figure 2, and Theorem 1. The certified result concerns the sampler's actual non-unit probability and a conditional public-coin attack path.
{: .prompt-info }

[Open the paper on IACR ePrint](https://eprint.iacr.org/2026/1809) · [Open the upstream implementation](https://github.com/osdnk/pikku)

## Result

**Paper under examination:** Michał Osadnik, *PikkuFold: Efficient Folding in a Few Kilobytes*, IACR ePrint 2026/1809. **Status:** Updated against the current latest version available from IACR ePrint.

For the published 50-bit parameters, the accompanying certificate identifies at least **4,337,664 accepted challenges** that vanish in the same quadratic CRT slot. Under the specified uniform rejection sampler, this gives

$$
\Pr[z\Lambda=0]
\ge 2^{-84.4637244}.
$$

This lower bound is approximately **742.5 times** the slotwise scale $64/q^2\approx2^{-94}$ predicted by Heuristic 1. It also induces a folding strategy: start from a public instance with no admissible short witness, use the public first-layer Johnson–Lindenstrauss matrix to build a non-short formal witness with zero projection, and compute a genuine RingSC transcript. If the final fresh-input challenge lies in the certified zero slot, the folded statement has the real zero vector as a valid output witness.

The construction was exercised on the original Rust verification path at $m=2^{18}$, rank $12$, and $40$ sumcheck rounds. The normal SHAKE run accepted the adversarial folding transcript but rejected the zero output witness. A test-only challenge override then reproduced the favorable and unfavorable public-coin branches through the same verifier path: the supported zero-slot challenge was accepted with the zero witness, while the supported non-zero-slot challenge was rejected.

## 1. Parameters and the Selected CRT Slot

The audited configuration is

| Parameter | Value |
|---|---:|
| Modulus | $q=2^{50}-2687=1125899906839937$ |
| Ring | $R_q=\mathbb F_q[X]/(X^{128}+1)$ |
| Fresh inputs | $k=2$ |
| Witness length | $m=2^{18}$ ring elements per input |
| Challenge weight | $s=23$ |
| Coefficients | $\{0,+1,-1\}$ |
| Operator-norm threshold | $\gamma=8.357$ |

Let

$$
\beta=739582794740178\pmod q.
$$

Exact checks give $\beta^{64}=-1$, $\beta^{128}=1$, and show that $X^2-\beta$ is one of the $64$ irreducible quadratic factors of $X^{128}+1$ over $\mathbb F_q$. Define

$$
\Lambda(X)=
\frac1{64}
\sum_{j=0}^{63}\beta^{-j}X^{2j}pmod q.
$$

**Lemma.** The element $\Lambda$ is the idempotent that equals one in the factor $X^2-\beta$ and zero in every other quadratic CRT factor. Consequently,

$$
\Lambda^2=\Lambda\ne0,
\qquad
z\Lambda=0
\iff
z=0\text{ in }R_q/(X^2-\beta).
$$

**Proof.** Put $Y=X^2$. The roots of $Y^{64}+1$ are $\beta^{2i+1}$ for $0\le i<64$. Evaluating the geometric sum defining $\Lambda$ gives one at $Y=\beta$ and zero at every other root. Multiplication by $\Lambda$ therefore projects onto exactly one CRT component. $\square$

For an even polynomial $z(X)=\sum_j z_jX^{2j}$, the zero-slot condition becomes the single field equation

$$
\sum_j z_j\beta^j=0\pmod q.
$$

The centered constant coefficient of $\Lambda$ already has magnitude

$$
\left|\operatorname{center}\!\left(\frac1{64}\right)\right|
=\frac{q-1}{64}
=17{,}592{,}186{,}044{,}374.
$$

## 2. The Certified Challenge Concentration

Let $\mathcal C$ be the accepted set of weight-$23$ ternary polynomials after operator-norm rejection at $8.357$. Before rejection there are

$$
N_0
=2^{23}\binom{128}{23}
=115709895676468761711877501747200
$$

possible challenges. The certificate checks $130{,}629$ explicit candidates at the selected CRT slot and evaluates the operator norm with rational trigonometric enclosures. It finds:

```text
source candidates              130629
certified accepted candidates   17317
canonical rotation classes      16944
accepted zero-slot challenges 4337664
unclassified norm checks            0
```

Each canonical class contributes $256$ distinct signed negacyclic rotations. Rotation preserves both the exact operator norm and the zero-slot equation, and odd Hamming weight rules out a nontrivial stabilizer. Hence the certificate exhibits

$$
M=16{,}944\cdot256=4{,}337{,}664
$$

distinct accepted challenges satisfying $z\Lambda=0$. Since $|\mathcal C|\le N_0$,

$$
\begin{aligned}
\Pr[z\Lambda=0\mid z\leftarrow\mathcal C]
&=\frac{|\{z\in\mathcal C:z\Lambda=0\}|}{|\mathcal C|}\\
&\ge\frac{M}{N_0}\\
&=2^{-84.46372441347683}\text{ approximately.}
\end{aligned}
$$

Fixing one certified challenge $c_0$, every other certified challenge $c$ has $c-c_0$ equal to zero in the same CRT factor. Definition 11's pointwise non-unit-difference probability therefore satisfies

$$
\epsilon_{\mathcal C}
\ge\frac{M-1}{N_0}
=\frac{4{,}337{,}663}{N_0}.
$$

The certificate is a finite lower bound, not a statistical extrapolation. Its conclusion does not require complete enumeration of the accepted set.

## 3. A Public Instance with No Short Witness

Give the verifier three complete public input/accumulator slots with zero commitments. For the first fresh input, choose the all-zero Boolean evaluation point and claim the value $\Lambda$; use zero evaluation claims for the other fresh input and the accumulator.

At the all-zero Boolean point, multilinear evaluation returns the first witness entry. Every opening of the first input must therefore begin with a ring element congruent to $\Lambda$. That element has a centered coefficient of magnitude

$$
\frac{q-1}{64}
=17{,}592{,}186{,}044{,}374,
$$

while the implementation's entire fresh-input norm bound at $m=2^{18}$ is about $5{,}931{,}641.60$. The relation has no admissible short opening, regardless of the commitment key.

The gap also survives the larger extraction cap used in Theorem 1. Any integral lift of $\Lambda$ has $63$ zero quadratic CRT components modulo $q$, so its nonzero algebraic norm is divisible by $q^{126}$. Parseval and AM–GM then imply

$$
\lVert\Lambda\rVert_2\ge q^{63/64}>2^{48},
$$

still above the audited extraction bounds.

## 4. Constructing the Formal Witness After the Public JL Coins

The first coarse JL matrix $J_0$ is public before the prover sends the projection messages. It has $256$ rows. Take its first column $j_0$, find additional columns spanning $\mathbb F_q^{256}$, and solve

$$
J_0a=0,
\qquad
a_0=1.
$$

Embedding the coefficients as scalar ring elements, define the formal witness by

$$
\widetilde w_j=a_j\Lambda
$$

on the selected columns and zero elsewhere. It has the claimed all-zero-point evaluation because $a_0=1$, yet it is not a short opening of the public input. Its first coarse projection is zero by construction, and every later projection remains zero.

The remaining projection and evaluation claims are honest polynomial identities for this formal witness. The adversarial prover can therefore compute the real nonzero sumcheck polynomials and terminal evaluations rather than inventing a false transcript. Because the entries lie in the ideal $\Lambda R_q$, the first terminal value $t'_0$ also lies in that ideal.

The Rust fixture found a kernel using $512$ additional columns and checked all $256$ residual equations. For the mathematical attack, allowing $2048$ available columns gives a clean rank bound. In the independent biased-ternary model, the probability of fewer than $256$ rank increments is at most

$$
2^{-2048}
\sum_{j=0}^{255}\binom{2048}{j}
<2^{-942}.
$$

## 5. The Favorable Challenge Produces a Real Zero Output Witness

After the $40$ sumcheck rounds, the verifier samples fresh folding challenges $(z_0,z_1)$. All public commitments are zero, the second terminal value and accumulator terminal value are zero, and $t'_0\in\Lambda R_q$. The folded claim is therefore

$$
z_0t'_0.
$$

Whenever $z_0\Lambda=0$, this value is zero. The actual zero vector then satisfies the output relation: its commitment, terminal evaluation, and norm are all zero. Combining the rank estimate with the certified challenge count gives the conservative public-coin bound

$$
p_{\mathrm{success}}
\ge
(1-2^{-942})
\frac{4{,}337{,}664}{2^{23}\binom{128}{23}}
\approx2^{-84.464}.
$$

This is the relevant correction to the concrete error accounting. Definition 11 and Theorem 1 already include $\epsilon_{\mathcal C}$; the problem is that the heuristic value substituted for the implemented sampler is smaller than the certified lower bound. The reported 50-bit knowledge error around $2^{-90}$ is therefore below an explicitly exhibited favorable-challenge event of about $2^{-84.46}$.

## 6. What the Rust Reproduction Checks

The supplied adversarial prover derives the projection matrices and sumcheck challenges from the original statement transcript, solves the first-layer kernel, computes all $40$ RingSC rounds, and calls the original `verify_fold()` and `verify_output()` routines. The code uses a portable arithmetic path on the tested x86-64 system; the verifier equations and sumcheck round checks are unchanged.

The author-reported Ubuntu/WSL2 runs produced the following key results:

```text
Round 10, m=2^18:
  PASS exact transcript-derived J0 kernel: 256 rows, 513 coefficients
  PASS original verify_fold accepted 40 malicious sumcheck rounds, rank=12

Round 11, m=2^18:
  PASS input relation has NO short opening
  normal SHAKE output rejected the zero witness
  supported zero-slot challenge accepted the zero witness
  supported non-zero-slot challenge rejected the zero witness

Round 12, m=2^18:
  favorable challenge norm: 8.117973728 < 8.357
  original verify_fold and verify_output accepted the favorable branch
  the unfavorable branch failed at verify_output
  SHAKE state was restored identically after the guarded test
```

Round 12 places a thread-local, test-feature guard exactly at final challenge sampling. Both injected challenges belong to the original sampler's support. This reproduces the two public-coin branches through the verifier, while the normal SHAKE control remains untouched outside the guard. Accordingly, the experiment demonstrates the conditional verification path and the concrete probability discrepancy; it is not a SHAKE preimage result.

## 7. Reproduction Downloads

All source-code comments in the published modules are in English. The complete archive retains the certificate data, upstream snapshot, installation scripts, and recorded run notes.

### Individual files

- [Main proof note](/assets/downloads/pikkufold/files/GIST_PROOF.md)
- [Exact ring and parameter verifier](/assets/downloads/pikkufold/files/verify_round9.py)
- [Zero-slot orbit counter](/assets/downloads/pikkufold/files/verify_many_orbits.py)
- [Round 12 static challenge verifier](/assets/downloads/pikkufold/files/verify_round12_static.py)
- [Round 12 Rust verifier-path fixture](/assets/downloads/pikkufold/files/round12_test_append.rs)
- [Clean installation script](/assets/downloads/pikkufold/files/INSTALL_FROM_CLEAN.sh)
- [Recorded Ubuntu/WSL2 results](/assets/downloads/pikkufold/files/OBSERVED_WSL_RESULTS.md)

### Module downloads

- [Counting certificate module](/assets/downloads/pikkufold/pikkufold-counting-certificate.zip) — CRT checks, candidate certificate, orbit counting, and reference results.
- [Verifier replay module](/assets/downloads/pikkufold/pikkufold-verifier-replay.zip) — portable helpers plus the Round 10–12 adversarial prover and verifier-path tests.

### Complete package

- [Download the complete PikkuFold proof and code bundle](/assets/downloads/pikkufold/pikkufold-full-proof-and-code.zip)

The quickest certificate-only reproduction is:

```bash
bash round9/verify_all.sh
python3 round12/verify_round12_static.py
```

For the full Rust path, follow `INSTALL_FROM_CLEAN.sh` in the complete package and run the guarded tests under the feature names documented by the Round 10–12 modules.

---

## License and Attribution

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

© 2026 cxcx52. All rights reserved except as expressly licensed below.

This technical report is licensed under the [Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). You may share, reproduce, redistribute, adapt, and build upon it, including commercially, provided that appropriate attribution is given, the original work and license are linked, and modifications are indicated.

When referencing or extending this analysis, please cite the original report. Researchers interested in extending the challenge certificate, improving the attack construction, or auditing the 64-bit parameters are welcome to contact the author for collaboration.
