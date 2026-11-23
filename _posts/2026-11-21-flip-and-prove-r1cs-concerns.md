---
title: "Technical Concerns on FLIP-and-Prove R1CS"
description: "Correctness counterexamples, interface gaps, and incomplete security accounting in the current IACR ePrint version of FLIP-and-Prove R1CS."
date: 2026-11-21 23:28:23 +0800
categories: [Audits, Proof Systems]
tags: [flip-and-prove, r1cs, folding, groth16, kzg, knowledge-soundness]
math: true
---

> **Scope.** This report has been updated against the current latest version available from IACR ePrint. It distinguishes concrete failures in printed equations from broader questions that would require additional argument.
{: .prompt-info }

[View the original Gist](https://gist.github.com/cxcx52/55a6c56ab3cd91edf214079a8016a3f6) · [Open the paper](https://eprint.iacr.org/2024/1364)

## The Printed Protocol Fails Basic Correctness Checks, and Its End-to-End Security Claims Remain Unsubstantiated

**Paper under examination:** Anca Nitulescu, Nikitas Paslis, and Carla Ràfols, FLIP-and-Prove R1CS, IACR ePrint 2024/1364.

**Status:** Updated against the current latest version available from IACR ePrint.

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

**Printed invariant.** FLIP folds the witness and updates the two-tier commitment as

$$
\begin{aligned}
w'[i] &= w[i]+\alpha\,w[i+\nu/2],\\
W' &= W+\alpha^{-1}W_{LR}+\alpha W_{RL}.
\end{aligned}
$$

Consistency requires the commitment key to fold as

$$
q'[i]=q[i]+\alpha^{-1}q[i+\nu/2].
$$

Figure 3 instead prints

$$
q'[i]=q[i]+\alpha^{-1}q[i+\nu/2-1].
$$

The final “− 1” is wrong.

This is not a harmless formatting issue. The printed formula fails on the smallest nontrivial input.

### Explicit counterexample

**Proof.** Work over $\mathbb F_{101}$ and represent pairing-group elements by their scalar exponents. Choose

$$
\alpha=2,
\qquad
(w_0,w_1)=(1,2),
\qquad
(q_0,q_1)=(3,5).
$$

The target-group update required by the commitment invariant is

$$
\begin{aligned}
W'
&=w_0q_0+w_1q_1+\alpha^{-1}w_0q_1+\alpha w_1q_0\\
&=78\pmod{101}.
\end{aligned}
$$

The folded witness is $w'=w_0+\alpha w_1=5$. The printed key update instead gives

$$
\begin{aligned}
q'_{\mathrm{printed}}
  &=q_0+\alpha^{-1}q_0=55\pmod{101},\\
w'q'_{\mathrm{printed}}
  &=5\cdot55=73\pmod{101}.
\end{aligned}
$$

Thus $w'q'_{\mathrm{printed}}=73\ne78=W'$.

The supposed commitment invariant fails.

Using the correct right-half index gives

$$
q'_{\mathrm{correct}}=q_0+\alpha^{-1}q_1=56,
\qquad
w'q'_{\mathrm{correct}}=5\cdot56=78\pmod{101},
$$

as required. $\square$

The manuscript also refers to cross terms with inconsistent or undefined indices in the same protocol figure.

A protocol figure that cannot preserve its central commitment invariant is not a correct executable specification.

Correcting the indexing may be straightforward. That does not change the fact that the printed protocol is incorrect.

## 3. The KZG Opening Proof Is Incorrect as Printed

**Location:** Page 10, Figure 2.

**Printed quotient.** The manuscript defines

$$
\Pi(X)
=\frac{g(X)-g(r)}{X-r}
+\xi\frac{g'(X)-g'(r)}{X-r}.
$$

Its commitment formula, however, starts at index $1$:

$$
[\Pi]_2=\sum_{i=1}^{k-1}\Pi_i[y^i]_2.
$$

Under the usual convention

$$
\Pi(X)=\Pi_0+\Pi_1X+\Pi_2X^2+\cdots,
$$

this formula omits the constant coefficient Π₀.

That omission is fatal in the simplest case.

### Explicit counterexample

**Proof.** For $k=2$, let

$$
g(X)=1+\alpha^{-2}X,
\qquad
g'(X)=1+\alpha^{-1}X.
$$

The quotient combination is constant:

$$
\Pi(X)=\alpha^{-2}+\xi\alpha^{-1}.
$$

Over $\mathbb F_{101}$, choose $\alpha=2$, $\xi=5$, $y=7$, and $r=3$. Then

$$
\Pi(X)=28,
\qquad
(y-r)\Pi(y)=4\cdot28=11\pmod{101}.
$$

But the printed commitment formula begins at index 1. For this constant quotient polynomial, it produces the zero commitment.

The resulting verification equation is therefore $11\ne0$.

Thus the printed algorithm rejects an honestly generated opening. $\square$

A corrected formula must include the constant coefficient, unless the authors intended a nonstandard coefficient-index convention that they failed to define.

Either way, the algorithm as specified does not establish its advertised correctness.

## 4. The r-Groth Simulator Has the Wrong Sign

**Location:** Page 17, Figures 4 and 5.

**Sign calculation.** In additive exponent notation, the pairing verification equation is

$$
AB-\delta C-S-\psi u^{-1}E+\phi\rho W
=u\alpha_G\beta_G,
$$

where S denotes the public-input contribution and α_G, β_G are the Groth16 setup scalars.

Solving for $C$ gives

$$
\delta C
=AB-S-\psi u^{-1}E+\phi\rho W-u\alpha_G\beta_G.
$$

The witness-commitment term therefore has sign $+\phi\rho W$.

Figure 5 instead uses the negative sign.

Substituting the printed simulator into the verifier leaves the residual $2\phi\rho W$.

Unless that residual happens to vanish, the simulated proof is rejected.

### Explicit counterexample

**Proof.** Over $\mathbb F_{101}$, choose

$$
u=1,
\quad
AB=u\alpha_G\beta_G=2,
\quad
S=E=0,
\quad
\delta=1,
\quad
\phi\rho=3,
\quad
W=4.
$$

The printed simulator produces $C=-12\pmod{101}$. The verifier then computes

$$
\begin{aligned}
AB-\delta C+\phi\rho W
&=2-(-12)+12\\
&=26\pmod{101}.
\end{aligned}
$$

The required right-hand side is $2$, so $26\ne2$. $\square$

The simulator's own output does not satisfy the verifier's equation.

This demonstrates a failure of the printed simulation algorithm. It does not, by itself, prove that an appropriately corrected scheme cannot be zero knowledge.

Nevertheless, a zero-knowledge argument cannot simply cite a simulator whose output fails verification.

## 5. FLIP and r-Groth Do Not Use the Same Relaxed-R1CS Representation

**Locations:** Pages 7–8 and 17.

This problem is more serious than a misplaced index.

**Interface mismatch.** FLIP defines the relaxed witness and relation as

$$
\mathbf z=(u,\mathbf x,\mathbf w),
\qquad
A\mathbf z\circ B\mathbf z=uC\mathbf z+\mathbf e.
$$

In particular, $z_0=u$, and folding changes this coordinate according to

$$
u'=u_1+\alpha u_2.
$$

Figure 4, by contrast, describes the r-Groth prover and verifier under the explicit convention $z_0=1$.

These are different representations.

They agree for an ordinary, unrelaxed R1CS instance with $u=1$.

They do not agree for a generic folded instance.

### A valid folded instance rejected by the printed interface

**Proof.** Take

$$
A=B=C=
\begin{pmatrix}
1&0\\
0&0
\end{pmatrix}.
$$

Let

$$
\mathbf z_1=\mathbf z_2=(1,0),
\qquad
u_1=u_2=1,
\qquad
\mathbf e_1=\mathbf e_2=\mathbf0.
$$

Both initial instances are valid.

Their cross term is zero.

Choose $\alpha=1$. FLIP produces

$$
u'=2,
\qquad
\mathbf z'=(2,0),
\qquad
\mathbf e'=\mathbf0.
$$

The relaxed relation is satisfied because

$$
A\mathbf z'\circ B\mathbf z'=(4,0)
=u'C\mathbf z'.
$$

Thus the folded instance is perfectly valid.

Imposing the r-Groth convention $z_0=1$, however, changes the first constraint to $1=2$.

This is false.

Consequently, the quotient polynomial constructed by the printed r-Groth prover does not satisfy the required divisibility condition.

The advertised composition fails on an ordinary, honestly generated folded instance. $\square$

This is not a negligible-probability corner case.

The conflict occurs whenever u′ differs from 1.

One possible repair is to normalize the folded instance when $u'\ne0$ and transform the corresponding witness, error, and commitments consistently.

But that transformation is not supplied as the complete interface in the printed construction.

There is also a separate domain problem: FLIP samples challenges from $\mathbb F$ while using $\alpha^{-1}$, and r-Groth uses $u^{-1}$ even though the relaxed relation permits $u=0$.

Perfect completeness cannot be claimed over a domain on which the honest prover algorithm is undefined.

## 6. The Verifier Does Not Authenticate the Original Commitments It Purports to Fold

**Locations:** Pages 8–11, Section 3 and Figure 3.

This is the most consequential issue for the paper's stated committed-input functionality.

Section 3 describes folding the committed statements

$$
(x_i,[w_i]_1),
\qquad i=0,\ldots,k-1.
$$

If these commitments are externally prescribed, a correct folding protocol must establish that the folded output corresponds to those specific commitments.

Figure 3 instead gives the verifier the batch state

$$
\Phi=\bigl(W_T,E_T,\{(u_i,x_i)\}_i\bigr),
\qquad
W_T=\sum_i e([w_i]_1,[q_i]_2).
$$

The individual original commitments appear in the prover's witness state.

The printed verification procedure does not check that the supplied W_T was actually computed from an externally specified list of original commitments.

That is a missing authentication boundary.

### A commitment-substitution counterexample

**Proof.** Consider the deterministic commitment $\operatorname{Com}(w)=wP_1$ and the relaxed constraint

$$
wu=ux+e.
$$

For ordinary R1CS inputs with $u=1$ and $e=0$, this requires $w=x$.

Suppose two externally prescribed committed statements satisfy

$$
x_0=x_1=0,
\qquad
[w_0]_1=[w_1]_1=P_1.
$$

These commitments fix $w_0=w_1=1$.

Neither original committed statement satisfies the relation, because each requires $w_i=0$.

Now let the prover disregard the original commitments and internally choose

$$
w_0=w_1=0,
\qquad
W_T=E_T=0,
$$

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

It does imply that the stronger committed-input functionality is not established by the displayed verifier interface. $\square$

## 7. A Security Assumption Is Trivially False as Defined

**Location:** Page 25, Definitions 3 and 4.

The manuscript's kernel assumptions define success through

$$
\sum_i e([w_i]_1,[y_i]_2)=0.
$$

However, the printed success condition does not require the output vector to be nonzero.

An adversary can therefore output $[w_i]_1=0$ for every $i$.

The equation holds with probability 1.

The same issue applies when the attacker supplies zero opening coefficients.

A hardness assumption that accepts the zero vector as a successful kernel solution is trivially false.

The natural correction is to require a nonzero kernel vector.

This is probably a repairable definitional omission.

But a security theorem cannot derive meaningful protection from an assumption that is false under its own stated success experiment.

The corrected assumption must be stated and its applicability justified.

## 8. The End-to-End Knowledge-Soundness Argument Is Not Closed

The paper needs to establish the complete implication

$$
\begin{aligned}
\text{accepted final proof}
&\Longrightarrow \text{extractable opening of the folded instance}\\
&\Longrightarrow \text{extractable original witnesses}\\
&\Longrightarrow \text{all original statements satisfy the relation}.
\end{aligned}
$$

That implication cannot be obtained merely by putting a folding theorem next to a final-proof soundness theorem.

The interfaces have to match.

Several issues remain.

### 8.1 Membership soundness is not the required extraction guarantee

Theorem 2 is stated primarily as computational soundness against acceptance of a statement outside a committed relaxed-R1CS language.

But the folding composition needs knowledge soundness: an efficient extractor must recover the necessary witness openings.

This matters particularly for relaxed R1CS with unrestricted error witnesses and randomized commitments.

Given $u$, $\mathbf x$, and a freely chosen $\mathbf w$, the error can always be defined as

$$
\mathbf e=A\mathbf z\circ B\mathbf z-uC\mathbf z.
$$

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

- the initial input-binding relation;
- the two-tier commitment keys;
- the independent setup assumptions;
- the extended r-Groth commitment keys;
- the Fiat–Shamir transcript and challenge binding; and
- the composition's extraction probability and runtime.

An extractor for one relation is not automatically an extractor for a different relation.

### 8.3 The printed interpolation proof contains an impossible condition

**Location:** Page 13, after Equation (4).

**Linear system.** The proof introduces coefficients $\nu_i$ satisfying

$$
\sum_{i=1}^{3}\nu_i\alpha_i^{\gamma}=0
\qquad
\text{for every }\gamma\in\{-1,0,1\}.
$$

For three distinct nonzero challenges, these are three independent homogeneous linear equations in three unknowns.

Generically, the only solution is $\nu_1=\nu_2=\nu_3=0$.

For challenges $1,2,3$ over $\mathbb F_{101}$, the corresponding generalized Vandermonde system is nonsingular:

$$
\det
\begin{pmatrix}
1&1&1\\
1&2&3\\
1&2^{-1}&3^{-1}
\end{pmatrix}
=34\ne0
\pmod{101}.
$$

Yet the proof uses these coefficients to extract a nonzero constant commitment term.

That inference does not follow.

To isolate the constant coefficient, the $\gamma=0$ condition needs a different normalization rather than the same zero right-hand side.

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

For $k$ public-input vectors of dimension $\ell$, the displayed algorithm performs $k-1$ vector-folding operations and therefore entails $\Theta(k\ell)$ field arithmetic under the literal procedure.

The paper acknowledges that its logarithmic bound excludes public-input processing.

That qualification is important.

The defensible claim is logarithmic folding-proof communication and associated cryptographic verification work, excluding the input-dependent component.

It is not unconditional $O(\log k)$ total verification work for arbitrarily large public statements.

### 9.3 The folding prover is not free

For $k$ original instances, Figure 3 computes $k-1$ cross-term vectors.

Each cross term is associated with an R1CS relation of size n.

The prover must compute those terms and generate corresponding commitments.

At the very least, the cost model must include:

- the $k$ initial witness commitments;
- the $k-1$ cross-term computations and commitments;
- the two-tier commitment operations;
- the final r-Groth proof; and
- the associated memory footprint.

For the paper's illustrative parameters $k=1024$ and $n=65{,}536$, the cross-term commitments alone involve

$$
(k-1)n
=1023\cdot65{,}536
=67{,}043{,}328
$$

coefficient-base inputs before accounting for MSM optimization.

This number is not a count of independent scalar multiplications. Efficient MSM algorithms can share substantial work.

But the underlying work is not negligible merely because the final communication is logarithmic.

### 9.4 Avoiding 1023 Groth16 proofs does not establish net speedup

The correct comparison is

$$
\begin{aligned}
T_{\mathrm{baseline}}
  &=k\,T_{\mathrm{Groth16}}+T_{\mathrm{aggregation}},\\
T_{\mathrm{FLIP}}
  &=T_{\mathrm{initial\ commitments}}
    +T_{\mathrm{folding}}
    +T_{r\text{-}\mathrm{Groth}}.
\end{aligned}
$$

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

