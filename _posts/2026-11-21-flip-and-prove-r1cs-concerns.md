---
title: "Technical Concerns on FLIP-and-Prove R1CS"
description: "Correctness counterexamples, interface gaps, and incomplete security accounting in the August 28, 2026 manuscript of FLIP-and-Prove R1CS."
date: 2026-11-21 23:28:23 +0800
categories: [Audits, Proof Systems]
tags: [flip-and-prove, r1cs, folding, groth16, kzg, knowledge-soundness]
math: true
---

> **Scope.** These findings concern the 27-page manuscript dated August 28, 2026, as written. They distinguish concrete failures in printed equations from broader questions that would require additional argument.
{: .prompt-info }

[View the original Gist](https://gist.github.com/cxcx52/55a6c56ab3cd91edf214079a8016a3f6) · [Open the paper](https://eprint.iacr.org/2024/1364)

## The Printed Protocol Fails Basic Correctness Checks, and Its End-to-End Security Claims Remain Unsubstantiated

**Paper under examination:** Anca Nitulescu, Nikitas Paslis, and Carla Ràfols, FLIP-and-Prove R1CS, IACR ePrint 2024/1364.

**Version examined:** 27-page manuscript, August 28, 2026.

---

## 1. Executive Summary
FLIP-and-Prove R1CS claims to combine logarithmic-communication folding with a Groth16-style final proof system, yielding efficient proofs for batches of R1CS instances without recursive verification circuits.

The proposal is ambitious. Unfortunately, the protocol printed in the manuscript does not satisfy several of its own fundamental correctness equations.

Our examination identifies:

- An incorrect commitment-key update in FLIP that breaks the claimed two-tier commitment invariant, even for two inputs.
- A KZG quotient-commitment formula that omits the constant coefficient and causes honest verification to fail under the standard coefficient convention.
- An incorrect sign in the r-Groth simulator, producing proofs rejected by the paper's own verification equation.
- A direct incompatibility between the relaxed-R1CS representation produced by FLIP and the representation assumed by r-Groth.
- An unauthenticated interface between externally prescribed witness commitments and the batch commitment actually verified by FLIP.
- A kernel assumption that is trivially false as literally defined because it permits the all-zero output.
- An incomplete end-to-end knowledge-extraction argument, including a defective interpolation step.
- Efficiency claims that are not supported by a sufficiently complete accounting of commitment generation, folding, input processing, and pairing costs.

These are not merely complaints about presentation quality.

Several displayed equations are mathematically false. Some honest inputs cannot be processed by the stated algorithms. And the verifier does not explicitly authenticate certain objects that the paper claims to fold.

An elegant asymptotic bound cannot compensate for an incorrect protocol specification.

We emphasize the precise scope of this criticism: the findings establish failures in the examined manuscript as written. They do not, without further argument, prove that every possible corrected FLIP-like construction is insecure or impossible.

## 2. FLIP's Commitment Update Is Wrong

**Location:** Page 11, Figure 3.

FLIP folds witnesses according to

w′[i] = w[i] + α · w[i + ν/2].

Its two-tier commitment is updated using cross terms:

W′ = W + α⁻¹W_LR + αW_RL.

For this equation to remain consistent, the corresponding commitment key must satisfy

q′[i] = q[i] + α⁻¹q[i + ν/2].

However, Figure 3 prints

q′[i] = q[i] + α⁻¹q[i + ν/2 − 1].

The final “− 1” is wrong.

This is not a harmless formatting issue. The printed formula fails on the smallest nontrivial input.

### Explicit counterexample

Work over the field 𝔽₁₀₁ and represent pairing-group elements by their scalar exponents.

Choose

α = 2,

(w₀, w₁) = (1, 2),

(q₀, q₁) = (3, 5).

The required target-group update is

W′ = w₀q₀ + w₁q₁ + α⁻¹w₀q₁ + αw₁q₀

= 78 mod 101.

Meanwhile,

w′ = w₀ + αw₁ = 5.

The printed formula gives

q′ = q₀ + α⁻¹q₀ = 55 mod 101,

and therefore

w′q′ = 5 · 55 = 73 mod 101.

Consequently,

73 ≠ 78.

The supposed commitment invariant fails.

Using the correct right-half index instead gives

q′ = q₀ + α⁻¹q₁ = 56 mod 101,

so that

w′q′ = 5 · 56 = 78 mod 101,

as required.

The manuscript also refers to cross terms with inconsistent or undefined indices in the same protocol figure.

A protocol figure that cannot preserve its central commitment invariant is not a correct executable specification.

Correcting the indexing may be straightforward. That does not change the fact that the printed protocol is incorrect.

## 3. The KZG Opening Proof Is Incorrect as Printed

**Location:** Page 10, Figure 2.

The manuscript defines a quotient polynomial of the form

Π(X) = (g(X) − g(r))/(X − r) + ξ(g′(X) − g′(r))/(X − r).

However, its commitment formula sums coefficients starting from index 1:

[Π]₂ = ∑ᵢ₌₁ᵏ⁻¹ Πᵢ[yⁱ]₂.

Under the usual polynomial convention

Π(X) = Π₀ + Π₁X + Π₂X² + ⋯,

this formula omits the constant coefficient Π₀.

That omission is fatal in the simplest case.

### Explicit counterexample

For k = 2, the relevant polynomials are

g(X) = 1 + α⁻²X,

g′(X) = 1 + α⁻¹X.

Their quotient combination is the constant polynomial

Π(X) = α⁻² + ξα⁻¹.

Choose, over 𝔽₁₀₁,

α = 2, ξ = 5, y = 7, r = 3.

Then

Π(X) = 28 mod 101.

The correct KZG verification identity requires

(y − r)Π(y) = 4 · 28 = 11 mod 101.

But the printed commitment formula begins at index 1. For this constant quotient polynomial, it produces the zero commitment.

The resulting verification equation becomes

11 ≠ 0.

Thus the printed algorithm rejects an honestly generated opening.

A corrected formula must include the constant coefficient, unless the authors intended a nonstandard coefficient-index convention that they failed to define.

Either way, the algorithm as specified does not establish its advertised correctness.

## 4. The r-Groth Simulator Has the Wrong Sign

**Location:** Page 17, Figures 4 and 5.

Write the pairing verification equation in additive exponent notation:

AB − δC − S − ψu⁻¹E + ϕρW = uα_Gβ_G,

where S denotes the public-input contribution and α_G, β_G are the Groth16 setup scalars.

Solving for C gives

δC = AB − S − ψu⁻¹E + ϕρW − uα_Gβ_G.

Notice the sign of the witness-commitment term:

+ϕρW.

Figure 5 instead uses the negative sign.

Substituting the printed simulator into the verifier leaves an unwanted residual

2ϕρW.

Unless that residual happens to vanish, the simulated proof is rejected.

### Explicit counterexample

Over 𝔽₁₀₁, choose

u = 1,

AB = uα_Gβ_G = 2,

S = E = 0,

δ = 1,

ϕρ = 3,

W = 4.

The printed simulator produces

C = −12 mod 101.

The verifier then obtains

AB − δC + ϕρW

= 2 − (−12) + 12

= 26 mod 101.

But the required right-hand side is 2.

Therefore,

26 ≠ 2.

The simulator's own output does not satisfy the verifier's equation.

This demonstrates a failure of the printed simulation algorithm. It does not, by itself, prove that an appropriately corrected scheme cannot be zero knowledge.

Nevertheless, a zero-knowledge argument cannot simply cite a simulator whose output fails verification.

## 5. FLIP and r-Groth Do Not Use the Same Relaxed-R1CS Representation

Locations: Pages 7–8 and 17.

This problem is more serious than a misplaced index.

FLIP defines the relaxed witness vector as

z = (u, x, w),

subject to

Az ∘ Bz = uCz + e.

In particular,

z₀ = u.

The folding operation changes this coordinate:

u′ = u₁ + αu₂.

But Figure 4 describes the r-Groth prover and verifier while explicitly assuming

z₀ = 1.

These are different representations.

They agree for an ordinary, unrelaxed R1CS instance with u = 1.

They do not agree for a generic folded instance.

### A valid folded instance rejected by the printed interface

Take

A = B = C = [[1, 0], [0, 0]].

Let the two initial witnesses be

z₁ = z₂ = (1, 0),

with

u₁ = u₂ = 1,

e₁ = e₂ = 0.

Both initial instances are valid.

Their cross term is zero.

Choose α = 1. FLIP produces

u′ = 2,

z′ = (2, 0),

e′ = 0.

The relaxed relation is satisfied:

Az′ ∘ Bz′ = (4, 0),

u′Cz′ = (4, 0).

Thus the folded instance is perfectly valid.

But imposing the r-Groth convention z₀ = 1 changes the first constraint to

1 = 2.

This is false.

Consequently, the quotient polynomial constructed by the printed r-Groth prover does not satisfy the required divisibility condition.

The advertised composition fails on an ordinary, honestly generated folded instance.

This is not a negligible-probability corner case.

The conflict occurs whenever u′ differs from 1.

One possible repair is to normalize the folded instance when u′ ≠ 0 and transform the corresponding witness, error, and commitments consistently.

But that transformation is not supplied as the complete interface in the printed construction.

There is also a separate domain problem: FLIP samples challenges from 𝔽 while using α⁻¹, and r-Groth uses u⁻¹ even though the relaxed relation permits u = 0.

Perfect completeness cannot be claimed over a domain on which the honest prover algorithm is undefined.

## 6. The Verifier Does Not Authenticate the Original Commitments It Purports to Fold

Locations: Pages 8–11, Section 3 and Figure 3.

This is the most consequential issue for the paper's stated committed-input functionality.

Section 3 describes folding an initial collection of committed statements:

(xᵢ, [wᵢ]₁), for i = 0, …, k − 1.

If these commitments are externally prescribed, a correct folding protocol must establish that the folded output corresponds to those specific commitments.

But Figure 3 gives the verifier a batch state of the form

Φ = (W_T, E_T, {(uᵢ, xᵢ)}ᵢ),

where

W_T = ∑ᵢ e([wᵢ]₁, [qᵢ]₂).

The individual original commitments appear in the prover's witness state.

The printed verification procedure does not check that the supplied W_T was actually computed from an externally specified list of original commitments.

That is a missing authentication boundary.

### A commitment-substitution counterexample

Consider a deliberately simple deterministic commitment:

Com(w) = wP₁.

Use the relaxed constraint

wu = ux + e.

For ordinary R1CS inputs with u = 1 and e = 0, this requires

w = x.

Suppose two externally prescribed committed statements both have

x₀ = x₁ = 0,

[w₀]₁ = [w₁]₁ = P₁.

These commitments fix w₀ = w₁ = 1.

Neither original committed statement satisfies the relation, because each requires wᵢ = 0.

Now let a prover disregard those original commitments and internally choose

w₀ = w₁ = 0.

The prover can use

W_T = 0,

E_T = 0,

with zero cross terms.

The internally selected witnesses satisfy the public-input relation, and their folded output can be valid.

But the verifier in Figure 3 does not compare this internal batch against the two externally prescribed commitments P₁.

The protocol has changed the objects being proved without authenticating that change.

This is not an attack on a weaker functionality in which the prover is free to choose the original witness commitments.

It is a counterexample to the stronger claim that the protocol folds a previously specified list of committed statements.

The distinction is fundamental.

If the intended functionality is merely

“For each public xᵢ, there exists some valid witness,”

then the authors should say so.

If the intended functionality is

“These specific committed statements are correctly folded,”

then the original commitments must be authenticated against the batch commitment.

If the batch commitment is assumed to have been authenticated beforehand, that assumption must be explicit, and the corresponding cost must not simply disappear.

A verifier cannot authenticate commitments it never receives, references through an authenticated digest, or otherwise binds to its input.

No asymptotic notation changes that fact.

This observation does not imply that every possible repair requires k separate pairing evaluations. Succinct authentication mechanisms may exist.

It does imply that the stronger committed-input functionality is not established by the displayed verifier interface.

## 7. A Security Assumption Is Trivially False as Defined

**Location:** Page 25, Definitions 3 and 4.

The manuscript's kernel assumptions define success using a pairing-kernel equation of the form

∑ᵢ e([wᵢ]₁, [yᵢ]₂) = 0.

However, the printed success condition does not require the output vector to be nonzero.

An adversary can therefore output

[wᵢ]₁ = 0 for every i.

The equation holds with probability 1.

The same issue applies when the attacker supplies zero opening coefficients.

A hardness assumption that accepts the zero vector as a successful kernel solution is trivially false.

The natural correction is to require a nonzero kernel vector.

This is probably a repairable definitional omission.

But a security theorem cannot derive meaningful protection from an assumption that is false under its own stated success experiment.

The corrected assumption must be stated and its applicability justified.

## 8. The End-to-End Knowledge-Soundness Argument Is Not Closed

The paper needs a complete implication of the following form:

Accepted final proof
⇒ extractable opening of the folded committed instance
⇒ extractable original witnesses
⇒ all original statements satisfy the intended relation.

That implication cannot be obtained merely by putting a folding theorem next to a final-proof soundness theorem.

The interfaces have to match.

Several issues remain.

### 8.1 Membership soundness is not the required extraction guarantee

Theorem 2 is stated primarily as computational soundness against acceptance of a statement outside a committed relaxed-R1CS language.

But the folding composition needs knowledge soundness: an efficient extractor must recover the necessary witness openings.

This matters particularly for relaxed R1CS with unrestricted error witnesses and randomized commitments.

Given u, x, and a freely chosen w, the error can always be defined as

e = Az ∘ Bz − uCz.

Moreover, a randomized Pedersen commitment in a prime-order cyclic group has, mathematically, an opening to any specified message under some randomness, even when computing that randomness is infeasible.

Thus bare existential membership does not provide the extraction guarantee needed by the folding reduction.

The manuscript does attempt algebraic extraction in its later proof.

The objection is not that no extraction argument is attempted.

The objection is that the required end-to-end extraction theorem, with consistent commitment relations and interfaces, is not established in the form the composition demands.

### 8.2 The final proof extracts under a different commitment key

The paper acknowledges that r-Groth's extracted openings are associated with expanded commitment keys CK and C̃K, not necessarily the original ck and c̃k.

That difference is not automatically fatal.

But the authors need to demonstrate that the extracted opening is valid for the relation expected by FLIP's extractor.

In particular, they must reconcile:

The initial input-binding relation.

The two-tier commitment keys.

The independent setup assumptions.

The extended r-Groth commitment keys.

The Fiat–Shamir transcript and challenge binding.

The composition's extraction probability and runtime.

An extractor for one relation is not automatically an extractor for a different relation.

### 8.3 The printed interpolation proof contains an impossible condition

**Location:** Page 13, after Equation (4).

The proof introduces three coefficients νᵢ satisfying

∑ᵢ₌₁³ νᵢ αᵢᵞ = 0

for every γ ∈ {−1, 0, 1}.

For three distinct nonzero challenges, these are three independent homogeneous linear equations in three unknowns.

Generically, the only solution is

ν₁ = ν₂ = ν₃ = 0.

For example, with challenges 1, 2, and 3 over 𝔽₁₀₁, the corresponding generalized Vandermonde determinant is

34 ≠ 0.

Yet the proof uses these coefficients to extract a nonzero constant commitment term.

That inference does not follow.

To isolate the constant coefficient, the γ = 0 condition should have a different normalization, rather than being zero like the others.

This may be a repairable interpolation error.

But the extraction argument printed in the manuscript does not prove what it claims at that step.

## 9. The Efficiency Claims Are Ahead of the Evidence

The paper's efficiency narrative is also less convincing than its abstract suggests.

### 9.1 Pairing counts are not reconciled

The abstract advertises two pairing checks.

The body attributes five pairings to r-Groth verification alone.

The FLIP final-opening procedure introduces additional pairing equations.

These figures may refer to different cost units, such as pairing-product checks rather than individual pairing evaluations.

But the paper must explain that accounting.

Pairing terms, Miller loops, final exponentiations, and pairing-product equations are not interchangeable metrics.

A concrete verifier-cost claim should be supported by a concrete verifier-cost accounting.

### 9.2 The logarithmic verifier claim excludes substantial input processing

For k public-input vectors of dimension ℓ, the displayed folding algorithm performs k − 1 vector-folding operations.

This entails Θ(kℓ) field arithmetic under the literal procedure.

The paper acknowledges that its logarithmic bound excludes public-input processing.

That qualification is important.

The defensible claim is logarithmic folding-proof communication and associated cryptographic verification work, excluding the input-dependent component.

It is not unconditional O(log k) total verification work for arbitrarily large public statements.

### 9.3 The folding prover is not free

For k original instances, Figure 3 computes k − 1 cross-term vectors.

Each cross term is associated with an R1CS relation of size n.

The prover must compute those terms and generate corresponding commitments.

At the very least, the cost model must reflect:

The k initial witness commitments.

The k − 1 cross-term computations.

The k − 1 cross-term commitments.

The two-tier commitment operations.

The final r-Groth proof.

The associated memory footprint.

For the paper's illustrative parameters

k = 1024 and n = 65,536,

the cross-term commitments alone involve

1023 × 65,536 = 67,043,328

coefficient–base inputs before accounting for MSM optimization.

This number is not a count of independent scalar multiplications. Efficient MSM algorithms can share substantial work.

But the underlying work is not negligible merely because the final communication is logarithmic.

### 9.4 Avoiding 1023 Groth16 proofs does not establish net speedup

The correct comparison is

T_baseline = k · T_Groth16 + T_aggregation,

against

T_FLIP = T_initial commitments + T_folding + T_r-Groth.

The paper's argument that it avoids k − 1 Groth16 proofs identifies a potentially significant saving.

It does not quantify the complete cost of the replacement protocol.

The cited runtime comparison is explicitly an analytical estimate, not a reproducible end-to-end benchmark.

Saving an expensive operation is not the same as demonstrating that its replacement is cheaper.

Without a complete cost model or corresponding measurements, the strongest prover-efficiency rhetoric remains unsubstantiated.

## 10. Conditional Setup Failures Must Not Be Confused with an Attack on the Claimed Model

The construction relies on independence between the outer two-tier commitment trapdoor and the internal r-Groth commitment trapdoors.

If those trapdoors are reused, or related through a publicly known affine transformation, incompatible error commitments may cancel in the initial target-group commitment.

This permits explicit false-batch examples under such a misconfigured setup.

That is a serious deployment hazard.

But it violates the independent-trapdoor condition assumed by the construction.

Accordingly, it is not, by itself, an attack on correctly generated independent parameters.

The distinction matters.

A rigorous criticism should not rely on weakening the scheme's stated setup assumptions and then pretending to have broken the original theorem.

The stronger criticism is that the manuscript must specify and prove its complete setup and composition requirements clearly enough for those assumptions to be checked in practice.

Similarly, a Fiat–Shamir implementation that fails to bind the complete public statement before deriving challenges may permit adaptive cancellation attacks.

The examined manuscript does not specify a complete hash transcript, so that possibility should be treated as a missing implementation specification—not as proof that the authors actually deployed such an insecure transcript.

## 11. What These Findings Establish

Let us be precise.

### Established by explicit counterexamples

The examined manuscript contains algorithmic formulas that fail their claimed correctness identities.

The printed FLIP commitment update is inconsistent.

The printed KZG quotient commitment is incomplete under the standard indexing convention.

The printed simulator does not satisfy the verification equation.

The printed FLIP-to-r-Groth interface does not accept generic valid folded instances.

The printed kernel assumption is trivially false without a nonzero-output condition.

These are concrete mathematical findings, not subjective disagreements.

### Established as a protocol-interface problem

The displayed verifier does not itself authenticate an externally prescribed list of original witness commitments against the batch commitment used for folding.

The stronger committed-input functionality therefore requires additional specification or authentication.

---

## License and Attribution

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

© 2026 cxcx52. All rights reserved except as expressly licensed below.

This technical report is licensed under the [Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

You are free to share, reproduce, redistribute, adapt, and build upon this work, including for commercial purposes, provided that appropriate attribution is given, a link to the original work and license is included, and any modifications are clearly indicated.

When referencing or extending the mathematical counterexamples presented here, please cite the original report.

### Collaboration

Researchers interested in extending these findings, developing stronger counterexamples, or conducting further security analyses of FLIP-and-Prove are welcome to contact me for collaboration.

