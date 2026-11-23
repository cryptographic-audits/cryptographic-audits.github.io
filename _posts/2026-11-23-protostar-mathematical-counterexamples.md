---
title: "Mathematical Errors and Counterexamples in ProtoStar"
description: "Explicit folding counterexamples and accounting gaps in the December 6, 2023 version of ProtoStar (ePrint 2023/620)."
date: 2026-11-23 22:19:21 +0800
categories: [Audits, Folding Schemes]
tags: [protostar, folding, accumulation, plonkup, lookups, counterexamples]
math: true
---

> **Scope.** This audit addresses the December 6, 2023 manuscript version as written. It does not claim that every later revision or every ProtoStar-like construction inherits the same issues.
{: .prompt-info }

[View the original Gist](https://gist.github.com/cxcx52/bc6d699eff3eb5be5812af0ffce975cb) · [Open the paper](https://eprint.iacr.org/2023/620)

**Paper:** *Protostar: Generic Efficient Accumulation/Folding for Special-sound Protocols*\
**Authors:** Benedikt Bünz and Binyi Chen\
**Version examined:** December 6, 2023 (57 pages)\
**Reference:** [https://eprint.iacr.org/2023/620](https://eprint.iacr.org/2023/620)

## Overview

ProtoStar proposes a generic accumulation framework for special-sound protocols and instantiates it with a non-uniform Plonkup construction supporting high-degree custom gates, circuit selection, and lookups.

Section 6 combines circuit selection, lookup arguments, compressed verification (CV), and high-low-degree accumulation. Corollary 1 claims that the resulting construction supports these features with a recursive circuit dominated by three group scalar multiplications (3G), while maintaining the stated prover complexity and final proof size.

**The central mathematical error is that the circuit-selected lookup constraint in Section 6 has algebraic degree 3, while page 44 classifies all non-gate constraints as degree 2 or lower and allocates only one cross-error vector to them.**

This discrepancy directly affects the folding construction.

We give explicit counterexamples involving two valid source proofs whose folded accumulator fails verification. We also identify additional problems involving vector lookups, duplicate table entries, recursive group-operation counts, and final proof-size accounting.

## 1. The Circuit-Selected Lookup Constraint Has Degree 3, Not Degree 2

### 1.1 The original constraint

Step 8 of protocol Π_mplkup on page 42 checks:

`Σⱼ bⱼ · hᵢ · (wⱼ,Lⱼ[i] + r) = 1`

where:

- `bⱼ` is the circuit-selection variable.
- `hᵢ` is the lookup inverse variable.
- `wⱼ,Lⱼ[i]` is the witness value in branch j.
- `r` is the lookup challenge.

Expanding the expression produces the monomial:

`bⱼ · hᵢ · wⱼ,Lⱼ[i]`

Its total algebraic degree is **3**.

Although b is a one-hot vector in an ordinary valid proof, it is not a fixed selector during accumulation.

After folding, b is replaced by a linear combination of two selection vectors. The accumulated selection vector is generally not one-hot.

Consequently, the selector variable cannot be removed when determining the degree of the accumulated polynomial.

### 1.2 The conflicting degree classification

Page 44 states that only the gate checks have high degree, while the remaining checks have degree at most 2.

The proposed high-low-degree accumulation therefore uses:

1. Scalar cross-error terms for the high-degree gate check.
2. A single long cross-error vector for all remaining checks.

Appendix A, pages 49–50, describes this single-vector approach for degree-2 verification equations.

A degree-3 constraint generally requires two intermediate cross-error coefficients:

`e₁X + e₂X²`

The circuit-selected lookup constraint does not satisfy the degree assumption of the low-degree accumulation component.

This is a mismatch between the actual verification polynomial and the accumulation construction used in Corollary 1.

## 2. Explicit Counterexample: Two Valid Proofs Produce an Invalid Fold

We construct two completely valid source proofs and show that the stated low-degree folding procedure rejects their combination.

### 2.1 Configuration

Work over a prime field 𝔽ₚ with characteristic greater than 3.

Use two branch circuits and a fixed lookup table:

`t = (1, 2)`

Each branch performs one lookup.

The remaining gate constraints can be chosen to be identically zero, and the permutation can be the identity. Public-input coordinates are bound to the corresponding selected branch as required by the protocol.

We focus on the coordinates relevant to the lookup constraint.

### 2.2 Two valid source proofs

| Component                 | Proof A  | Proof B  |
| ------------------------- | -------- | -------- |
| Program counter           | 1        | 2        |
| Selection vector b        | (1, 0)   | (0, 1)   |
| Branch lookup coordinates | (1, 0)   | (0, 2)   |
| Lookup challenge r        | 1        | 1        |
| Multiplicity vector m     | (1, 0)   | (0, 1)   |
| Inverse h                 | 1/2      | 1/3      |
| Table inverse g           | (1/2, 0) | (0, 1/3) |
| Relaxation parameter μ    | 1        | 1        |

Both source proofs satisfy the original lookup constraints.

For proof A:

`(1/2) · (1 + 1) = 1`

For proof B:

`(1/3) · (2 + 1) = 1`

The table-side inverse equations and sum equality also hold.

Both proofs have zero verification error.

Thus, A is a valid old accumulator and B is a valid new proof for the accumulation procedure.

### 2.3 Folding the two proofs

Introduce a formal folding variable X and form:

`A + XB`

The folded coordinates are:

`μ(X) = 1 + X`

`b(X) = (1, X)`

`w(X) = (1, 2X)`

`r(X) = 1 + X`

`h(X) = 1/2 + X/3`

The correctly homogenized degree-3 lookup constraint is:

`F(X) = h(X) · Σⱼ bⱼ(X)(wⱼ(X) + r(X)) − μ(X)³`

Substituting the folded coordinates gives:

`F(X) = (1/2 + X/3)(2 + 2X + 3X²) − (1 + X)³`

Expanding:

`F(X) = −(4/3)X − (5/6)X²`

Therefore:

`e₁ = −4/3`

`e₂ = −5/6 ≠ 0`

The constant coefficient is zero because A is valid.

The coefficient of X³ is zero because B is valid.

However, the intermediate coefficient of X² is nonzero.

This is precisely the coefficient omitted when a degree-3 lookup constraint is handled using the degree-2 accumulation procedure.

### 2.4 Failure of the single-cross-error construction

Under the low-degree error allocation described on page 44, only the first cross-error coefficient is retained:

`e₁ = −4/3`

After sampling the folding challenge α, the decider must compare the actual folded verification error with the accumulated error.

Their difference is:

`F(α) − αe₁ = −(5/6)α²`

For every nonzero α:

`F(α) − αe₁ ≠ 0`

Therefore, the folded accumulator fails the decider check.

**Two valid source proofs produce a folded accumulator that is rejected for every nonzero folding challenge.**

The failure is caused by the omitted second-order cross-error coefficient.

### 2.5 Exhaustive verification over GF(101)

In 𝔽₁₀₁:

`−4/3 = 66`

`−5/6 = 16`

Hence:

`F(X) = 66X + 16X²`

Exhaustively evaluating all 101 possible folding challenges gives:

| Test                                                | Result |
| --------------------------------------------------- | ------ |
| Valid source proofs                                 | 2/2    |
| Folding challenges tested                           | 101    |
| Accepted with one cross-error coefficient           | 1      |
| Incorrectly rejected                                | 100    |
| Accepted with both correct cross-error coefficients | 101    |

The only challenge accepted by the incomplete error construction is:

`α = 0`

The rejection probability is:

`100/101 ≈ 99.01%`

This is an explicit failure of perfect completeness for the stated low-degree error allocation.

## 3. The Failure Occurs for General Lookup Challenges

The previous example uses `rA = rB = 1`.

We now analyze arbitrary valid source challenges.

Let:

`hA = 1/(1 + rA)`

`hB = 1/(2 + rB)`

where:

`1 + rA ≠ 0`

`2 + rB ≠ 0`

The two source proofs retain the same branch-selection vectors, witness coordinates, and table values.

After folding, the second-order cross-error coefficient becomes:

`e₂ = (2 + rB)/(1 + rA) + (rA + rB)/(2 + rB) − 3`

Introduce:

`a = 1 + rA`

`b = 2 + rB`

Then:

`e₂ = [(b − a)² − 3a]/(ab)`

Therefore:

`e₂ = 0`

if and only if:

`(b − a)² = 3a`

For a prime field with p > 3, there are exactly `p − 2` solutions among the `(p − 1)²` valid non-pole challenge pairs.

The probability that the omitted second-order coefficient is nonzero is consequently:

`Pr[e₂ ≠ 0] = 1 − (p − 2)/(p − 1)²`

The fold is incorrectly rejected whenever:

`e₂ ≠ 0` and `α ≠ 0`

Thus, for uniformly sampled independent challenges:

`P_fail = (p² − 3p + 3) / [p(p − 1)]`

As p grows:

`lim(p → ∞) P_fail = 1`

The problem therefore becomes more pronounced in large prime fields.

### Exhaustive test over GF(101)

We enumerated all valid source-challenge pairs and all folding challenges.

| Quantity                          | Result       |
| --------------------------------- | ------------ |
| Valid pairs (rA, rB)              | 10,000       |
| Pairs with nonzero e₂             | 9,901        |
| Total tested folding combinations | 1,010,000    |
| Incorrectly rejected combinations | 990,100      |
| Incorrect rejection rate          | **98.0297%** |

The missing cross-error term is not a rare algebraic corner case.

It appears with overwhelming probability for ordinary source challenges.

## 4. Combining Non-Uniform Circuit Selection with Vector Lookups Produces Degree-4 Constraints

Section 4.4 introduces vector-valued lookups.

For a vector witness, compression uses:

`wᵢ(β) = Σₛ wᵢ,ₛ βₛ`

Section 6 independently introduces non-uniform circuit selection through variables bⱼ.

The direct combination yields a lookup check of the form:

`hᵢ · Σⱼ bⱼ(Σₛ wⱼ,ᵢ,ₛ βₛ + r) = 1`

This contains the monomial:

`bⱼ · hᵢ · wⱼ,ᵢ,ₛ · βₛ`

Its total degree is **4**.

Accordingly, a correctly homogenized degree-4 relation generally requires three intermediate cross-error coefficients:

`e₁X + e₂X² + e₃X³`

The single degree-2 error vector described on page 44 cannot represent these terms.

### 4.1 Explicit vector-lookup example

Use the fixed vector lookup table:

`t = ((1,0), (0,2))`

Construct two valid source proofs.

Proof A:

- Selects branch 1.
- Uses lookup vector `(1,0)`.
- Uses vector-compression challenge `βA = 0`.
- Uses lookup challenge `rA = 1`.
- Uses inverse `hA = 1/2`.

Proof B:

- Selects branch 2.
- Uses lookup vector `(0,2)`.
- Uses vector-compression challenge `βB = 1`.
- Uses lookup challenge `rB = 1`.
- Uses inverse `hB = 1/3`.

The multiplicity vectors and table inverses are assigned consistently with the selected entries.

Both endpoint proofs satisfy their vector-lookup checks.

Under the direct composition of the two protocols, the correctly homogenized degree-4 folding residual expands to:

`F_vec(X) = −(4/3)X − (19/6)X² − (3/2)X³`

In particular:

`e₃ = −3/2 ≠ 0`

Consequently, adding only the missing X² term from the scalar lookup case is still insufficient for this direct vector-lookup composition.

The construction needs a complete degree-4 error treatment or a different auxiliary-variable formulation.

This degree issue follows directly from combining the verification relations in Sections 4.4 and 6.

## 5. Duplicate Lookup Table Entries Break the Specified Honest Prover

Definition 12 on page 33 allows a lookup table:

`t ∈ 𝔽ᵀ`

It does not require table entries to be distinct.

However, the honest prover algorithm on page 34 computes multiplicities independently for every table position:

`mᵢ = Σⱼ 1[wⱼ = tᵢ]`

Consider the valid lookup instance:

`t = (0,0)`

`w = (0)`

The witness value appears in the table, so the lookup relation is satisfied.

Following the specified honest prover algorithm gives:

`m = (1,1)`

For every nonzero challenge r:

`h = 1/r`

`g = (1/r, 1/r)`

The verifier checks:

`Σh = Σg`

But:

`Σh = 1/r`

`Σg = 2/r`

Therefore:

`Σh ≠ Σg`

The honest prover fails on a valid lookup instance.

The issue arises because one lookup occurrence is counted once for each duplicate table position.

A correct multiplicity assignment must either require distinct table entries or choose a canonical representative for each distinct table value.

For example:

`m = (1,0)`

resolves this particular instance.

The same duplicate-counting issue also invalidates the claimed sparsity bound for the multiplicity vector when duplicate entries are unrestricted.

## 6. The Claimed 3G Recursive Cost Is Not Derived by Theorem 3

Theorem 3 on page 28 gives the recursive group scalar multiplication cost of the CV construction as:

`k + 2`

where k is the number of prover messages in the underlying `(2k − 1)`-move protocol.

The lookup protocol in Section 6 has three messages:

`k = 2`

Direct substitution gives:

`k + 2 = 4G`

However, Corollary 1 on page 44 claims:

`3G`

The proof of Corollary 1 invokes Theorem 3 without specifying an additional transformation that reduces the count from 4G to 3G.

Under the described high-low accumulator representation, the verifier must account for the prover-message commitment updates and the low-degree error commitment update.

An additional optimization may reduce the number of group operations, but that optimization requires an explicit construction and corresponding correctness and security analysis.

The stated 3G result does not follow directly from the cited theorem.

Furthermore, repairing the incorrect degree classification of the lookup constraints changes the cross-error structure and therefore requires revisiting the claimed operation count.

## 7. Final Proof Size Omits the Dependence on the Number of Branch Circuits

Step 4 of protocol Π_mplkup on page 42 defines the prover-message vector as:

`w* ∈ 𝔽^(Icn)`

This vector concatenates I branch blocks, each containing cn field elements.

A new proof activates only one branch, so the newly submitted vector is sparse.

This permits efficient per-step updates.

However, after accumulating executions from different branches, the accumulated witness can contain nonzero values in multiple branch blocks.

For branch j, the accumulated block has the form:

`acc.w⁽ʲ⁾ = Σₜ:pcₜ=j αₜwₜ`

After sufficiently many steps, all I branch blocks may become nonzero.

Therefore, the following two statements are not equivalent:

**Per-step update complexity:**

`O(cn)`

**Worst-case accumulated witness length:**

`O(Icn)`

The decider described on page 22 verifies openings of the accumulated message commitments.

Corollary 1 nevertheless reports a final proof size of:

`O(cn + T + ℓ_lk)`

without an I factor for the concatenated branch witnesses.

Under the explicitly described accumulator-witness representation, the worst-case final opening includes an `Icn`-sized component.

The distinction between sparse incremental updates and the size of the accumulated witness is essential.

Appendix C contains a related accounting discrepancy for non-uniform CCS witnesses.

## 8. Implications for Corollary 1

The relevant construction chain is:

`Special-sound protocol → CV → Fiat–Shamir + commitments → Accumulation → IVC`

The generic accumulation theorem assumes that the verification equations have been assigned their correct algebraic degrees and that the corresponding cross-error terms are maintained.

In the concrete construction of Section 6:

1. The selected scalar lookup is degree 3.
2. Page 44 assigns it to the degree-2 component.
3. The resulting error representation omits a generally nonzero X² coefficient.
4. Two valid source proofs can consequently produce a folded accumulator rejected by the decider.
5. The direct composition with vector lookups introduces degree-4 constraints.
6. The stated recursive and final-proof complexity bounds contain additional accounting gaps.

The central issue is not merely that an argument has been omitted from the proof.

**The explicit verification equations do not satisfy the degree assumptions of the high-low accumulator used to establish Corollary 1.**

The counterexamples demonstrate that this mismatch has an observable consequence: valid source proofs are not preserved by the stated folding procedure.

Repairing the construction requires changing the actual constraint representation or the cross-error allocation.

It also requires re-establishing the associated complexity bounds.

## 9. Minimal Reproduction

The following Python 3 program reproduces the scalar lookup folding counterexample.

No third-party dependencies are required.

```python
p = 101
inv = lambda x: pow(x % p, -1, p)

# Two valid source proofs.
hA = inv(2)
hB = inv(3)

# Correct cross-error coefficients.
e1 = (-4 * inv(3)) % p
e2 = (-5 * inv(6)) % p

def folded_lookup_residual(x):
    mu = 1 + x
    r = 1 + x
    h = hA + x * hB
    b1, b2 = 1, x
    w1, w2 = 1, 2 * x

    selected_lookup = b1 * (w1 + r) + b2 * (w2 + r)
    return (h * selected_lookup - mu**3) % p

# Both endpoints are valid.
assert folded_lookup_residual(0) == 0

incomplete = sum(
    folded_lookup_residual(x) == x * e1 % p
    for x in range(p)
)
correct = sum(
    folded_lookup_residual(x) == (x * e1 + x * x * e2) % p
    for x in range(p)
)

print(f"Field: GF({p})")
print(f"e1 = {e1}")
print(f"e2 = {e2}")
print(f"Accepted with incomplete error: {incomplete} / {p}")
print(f"Rejected with incomplete error: {p - incomplete} / {p}")
print(f"Accepted with correct error: {correct} / {p}")
```

Expected output:

```
Field: GF(101)
e1 = 66
e2 = 16
Accepted with incomplete error: 1 / 101
Rejected with incomplete error: 100 / 101
Accepted with correct error: 101 / 101
```

## 10. Conclusion

The December 6, 2023 version of ProtoStar contains a substantive inconsistency between the algebraic degree of its circuit-selected lookup constraints and the high-low accumulation construction used in Corollary 1.

The scalar lookup constraint has degree 3, while the concrete construction allocates it only one degree-2 cross-error vector.

An explicit pair of valid source proofs produces a nonzero second-order cross-error coefficient. Omitting that coefficient causes the resulting fold to fail verification for almost every folding challenge.

For independently sampled lookup challenges, the incorrect rejection probability approaches 1 as the field size increases.

The direct combination of non-uniform circuit selection with vector-valued lookups produces degree-4 constraints, introducing further missing cross-error coefficients.

Additional discrepancies concern duplicate lookup table entries, the claimed 3G recursive cost, and the final proof-size dependence on the number of branch circuits.

**The optimized ProtoStar construction described in Corollary 1 is therefore not established by the protocol and proofs given in this version of the paper. Its stated perfect completeness and efficiency claims require substantive corrections to the construction and a revised analysis.**

### Relevant locations in the paper

- **Section 4.3, pp. 33–35:** Scalar lookup protocol and multiplicity handling.
- **Section 4.4, pp. 36–38:** Vector-valued lookup protocol.
- **Section 6, pp. 41–45:** Non-uniform Plonkup, selected lookup checks, and Corollary 1.
- **Theorem 3, pp. 28–30:** General IVC compiler and operation counts.
- **Appendix A, pp. 49–50:** High-low-degree accumulation.
- **Appendix C, pp. 54–57:** Non-uniform CCS construction.

**Paper:** [https://eprint.iacr.org/2023/620](https://eprint.iacr.org/2023/620)

---

## License and Attribution

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

© 2026 cxcx52. All rights reserved except as expressly licensed below.

This technical report is licensed under the [Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

You are free to share, reproduce, redistribute, adapt, and build upon this work, including for commercial purposes, provided that appropriate attribution is given, a link to the original work and license is included, and any modifications are clearly indicated.

When referencing or extending the mathematical counterexamples presented here, please cite the original report.

### Collaboration

Researchers interested in extending these findings, developing stronger counterexamples, or conducting further security analyses of ProtoStar are welcome to contact me for collaboration.

