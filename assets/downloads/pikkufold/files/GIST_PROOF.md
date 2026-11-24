# A zero-slot concentration in PikkuFold's 50-bit challenge sampler

**Scope.** This note concerns the 50-bit implementation parameters in §6.2 and Table 6 of *PikkuFold: Efficient Folding in a Few Kilobytes* (ePrint 2026/1809), together with Heuristic 1 (§5.3), Definition 11, Figure 2, and Theorem 1. It does **not** claim that Theorem 1 is false when instantiated with the actual sampling error, nor that a complete Fiat–Shamir forgery has been found against SHAKE. The counting certificate and test sources are included in the accompanying archive.

## Result

For the published 50-bit parameters, we found and certified at least **4,337,664 different challenges** in the accepted fixed-weight, operator-norm-rejected set that vanish in the same quadratic CRT slot. Consequently, the probability of this event under the specified uniform rejection sampler is at least **2^-84.4637244**. This is approximately **742.5 times** the slotwise error scale predicted by Heuristic 1 (`64/q^2`, or about `2^-94`). Fixing any one challenge in that zero-slot set also gives the same order of lower bound on the *pointwise non-unit difference probability* `epsilon_C` from Definition 11.

There is a matching folding strategy. It starts with a public input that has **no short opening for any commitment key**, uses the public first-layer JL matrix to construct a non-short *formal* witness with zero projection, and computes a genuine RingSC proof for that formal witness. When the final fresh-input challenge vanishes in the selected CRT slot, the **actual zero output witness** satisfies the folded relation. Under the independent public-coin model and a full-rank condition for the public JL matrix, the attack succeeds on the certified challenge event.

We tested the construction in the original Rust verification path at `m = 2^18`, `n = 12`, and **40 sumcheck rounds**. `verify_fold()` accepted the nonzero adversarial sumcheck transcript under the normal SHAKE path. A separate **test-only final-challenge override** made `verify_fold()` and `verify_output()` accept the zero output witness for a supported zero-slot challenge; a supported non-zero-slot challenge was rejected at `verify_output()`. The normal SHAKE challenge rejected the zero witness in our run. No hash grinding or unmodified-SHAKE complete forgery was observed.

## 1. The ring and a one-slot idempotent

Use the implementation parameters

- `q = 2^50 - 2687 = 1125899906839937`, `R_q = F_q[X]/(X^128 + 1)`;
- `k = 2` fresh inputs, three JL layers, and `m = 2^18` ring elements per input (Table 6);
- challenge weight `s = 23`, coefficients in `{0,+1,-1}`, and operator-norm rejection threshold `gamma = 8.357`.

Let `beta = 739582794740178 (mod q)`. Exact modular checks give `beta^64 = -1`, `beta^128 = 1`, and `beta^((q-1)/2) = -1`. The primality and order checks, including a primality certificate for `q`, are in `round9/verify_round9.py`. Thus `beta` is a nonsquare 128-th root of unity and `X^2 - beta` is one of the 64 irreducible quadratic CRT factors of `X^128 + 1` modulo `q`.

Put `Y = X^2` and define the idempotent

```text
Lambda(X) = (1/64) * sum_{j=0}^{63} beta^(-j) X^(2j)  (mod q).
```

The roots of `Y^64 + 1` are `beta^(2i+1)`, `0 <= i < 64`. Evaluating the geometric sum shows that `Lambda` equals `1` in the factor `X^2-beta` and `0` in every other factor. Hence `Lambda^2 = Lambda != 0`, and for every `z in R_q`,

```text
z * Lambda = 0  if and only if  z = 0 in the CRT factor X^2-beta.
```

For an even polynomial `z(X) = sum_j z_j X^(2j)`, the last condition is exactly `sum_j z_j beta^j = 0 (mod q)`. The certificate verifies all 64 CRT values, not only the selected one.

An important consequence concerns the coefficient bound. Since `q = 1 (mod 64)`, the centered representative of the constant coefficient `1/64 (mod q)` of `Lambda` is `-(q-1)/64`, of absolute value **17,592,186,044,374**.

## 2. A certified lower bound for the accepted challenge distribution

Let `C` be the exact accepted set of weight-23 ternary polynomials after operator-norm rejection at `gamma = 8.357`. The pre-rejection set has precisely

```text
N0 = 2^23 * binom(128, 23)
   = 115709895676468761711877501747200
```

members. The certificate includes a finite, explicit set of 130,629 candidate polynomials supported at even powers of `X`. Every candidate is checked exactly at `Y = beta` over `F_q`, and the operator norm is decided using an integer/rational trigonometric enclosure with no unresolved borderline cases. Of these candidates, 17,317 are certified accepted. Their signed negacyclic rotation classes reduce to 16,944 distinct classes. Each has 256 distinct signed `X` rotations: multiplication by `X` preserves both operator norm and the zero-slot condition, and the odd Hamming weight rules out a nontrivial rotational stabilizer. Rotations from different canonical classes are disjoint.

Therefore the finite certificate exhibits at least `M = 16944 * 256 = 4337664` different elements of `C` satisfying `z*Lambda = 0`. The exact program output is:

```text
source candidates             130629
certified accepted candidates  17317
canonical rotation classes     16944
accepted zero-slot challenges 4337664
unclassified norm checks           0
```

This is a **lower bound obtained from explicitly checked elements**, not an estimate from a random sample or an assertion that the fiber has been completely enumerated. Since `|C| <= N0`, uniform rejection sampling immediately yields

```text
Pr[z * Lambda = 0 | z uniform in C] = |{z in C: z*Lambda=0}| / |C|
                                  >= M / N0
                                  = 2^-84.46372441347683 (approximately).
```

Definition 11 asks for a pointwise bound on non-unit differences from a **fixed** anchor. Fix any `c0` among the certified zero-slot challenges. For every other certified `c`, the difference `c-c0` is zero in the same CRT factor and is therefore a non-unit of `R_q`. Excluding `c=c0` gives

```text
epsilon_C >= (M-1)/|C| >= 4337663/N0.
```

Heuristic 1 predicts `epsilon_C approximately phi/(e*q^e) = 64/q^2`, approximately `2^-94`, so the **certified lower bound** is about **742.5 times larger** than that nominal estimate. The conjecture also has the premise `|C| >= q^2`. We do not claim to have independently certified that cardinality condition. If it fails, the heuristic is inapplicable; if it holds, its prediction is inconsistent with the certified pointwise lower bound. Importantly, neither the counting result nor the actual zero-slot probability bound requires that cardinality premise.

The norm certificate uses rational bounds on trigonometric values: a rational enclosure for `pi`, truncated Taylor series with explicit remainders, a `2^24` fixed-point unit-root table, and one-unit component enclosures. For each weight-23 candidate, the code computes an integer upper and lower enclosure for the maximum squared Fourier magnitude, then compares them against the integer representation of `gamma^2`. There are **zero ambiguous candidates**. Signed monomial rotations preserve the exact canonical operator norm. `round9/verify_many_orbits.py` reproduces the counts; `round9/reproduce_enumeration.py` constructs the enclosures.

## 3. A public instance with no admissible short witness

Choose a commitment key `F` of the original shape (rank 12 for `m = 2^18`), but the argument below does **not** depend on its entries. Give the verifier three complete public input/accumulator slots, with every commitment equal to zero. Set the first fresh input's multilinear-evaluation point to the Boolean all-zero vector, and its claimed evaluation to `Lambda`. Give the second fresh input and the accumulator zero evaluation claims.

At the all-zero Boolean point, multilinear evaluation returns the first entry. Therefore any valid opening `w_0` of the first input must have its first ring element congruent to `Lambda` modulo `q`. Its centered coefficient vector already has one coefficient with magnitude `(q-1)/64 = 17592186044374`. The implementation's entire fresh-input norm bound at `m=2^18` is only about `5931641.60`. Thus **the input relation has no short opening for any `F`**, even before enforcing the commitment equation `Fw=0`.

This also holds against the larger extraction input cap used in Theorem 1. For completeness, any integral lift `u` of `Lambda` has 63 vanishing quadratic CRT components modulo `q`. Its nonzero algebraic norm, computed as the resultant against `X^128+1`, is divisible by `q^126`. The norm is nonzero since `X^128+1` is irreducible over `Q` and `u` is nonzero in `R_q`. Parseval's identity followed by AM–GM over the 128 complex embeddings gives `|Norm(u)| <= ||u||_2^128`; hence `||u||_2 >= q^(63/64) > 2^48`. `round9/verify_round9.py` checks the paper's extraction caps at all three Table 6 witness sizes and establishes they are below `2^31` for the parameters used in that audit.

## 4. A malicious formal witness constructed after the public JL coins

The first coarse JL matrix `J0` is sampled **publicly before** the prover transmits the projection messages. It has 256 rows. Select its first column `j0` and a set of additional columns that spans `F_q^256`. Solve `J0*a=0` over `F_q` with `a[0]=1`, e.g., by solving `J_extra*a_extra=-j0`. Embed these field coefficients as scalar ring elements and define the *formal* first-input witness entries by `w_tilde[j] = a[j]*Lambda` over the chosen columns; all remaining entries of all three witness slots are zero.

The formal witness has the required all-zero-point MLE value, because `a[0]=1`. It is not a short opening, and it is **not** required to satisfy `F*w_tilde=0`. That is precisely the source-relation inconsistency the verifier should ultimately detect. Its first coarse projection nevertheless equals zero, because `J0*a=0`; the same `J0` is used in the corresponding repeated coarse blocks. All later projection levels are zero as well. Consequently, the prover can supply zero final projection image and zero batched projection values, satisfying the projection norm, trace, and batching checks.

The projection and evaluation identities formed from this formal witness are genuine polynomial identities over the ring. The prover computes the full RingSC transcript from them, including the real nonzero round polynomials and the terminal evaluations. Sumcheck's perfect completeness therefore gives acceptance of the entire stage; no false sumcheck polynomial is asserted. Because all first-input formal witness entries lie in the ideal `Lambda*R_q`, the first-input terminal evaluation `t0'` also lies in that ideal. The other terminal values are zero.

There are two distinct rank statements:

1. **Finite Rust test:** the tested transcript-derived `J0` had enough rank in its first **512 additional columns**. The test explicitly solved for 513 coefficients (`a[0]=1`) and checked all 256 residuals, then generated a true 40-round proof. This is a reproducible *sample-specific* certificate, not by itself a bound for every random JL draw.
2. **High-probability attack algorithm:** allow the solver to inspect **2048 additional columns** (available at `m=2^18`). In the ideal biased-ternary independent-column model, every new column leaves a given proper subspace with conditional probability at least `1/2`: choose a nonzero linear form annihilating the subspace; one coordinate of the independent ternary column has maximum atom probability `1/2`. A monotone coupling bounds the probability of fewer than 256 rank increments in 2048 trials by `2^-2048 * sum_{j=0}^{255} binom(2048,j)`, which is **less than `2^-942`** by exact integer comparison. This is the rank guarantee for the *2048-column* mathematical attack, not for the 512-column Rust fixture.

The calculation assumes the independent biased-ternary public-coin distribution analyzed by the scheme. The concrete SHAKE/AES transcript expander is deterministic after the seed; the Rust tests check the realized matrix rather than statistically proving an expander bound.

## 5. The favorable final challenge gives a real zero output witness

Only after the 40-round sumcheck and terminal claims are fixed does the verifier obtain the fresh folding challenges `(z0,z1)`. The formal witness yields a first terminal evaluation `t0' in Lambda*R_q`; the other two terminal evaluations are zero. All public commitments are zero. Therefore the folded public statement has commitment zero and claimed evaluation `z0*t0'`.

For **every** final challenge with `z0*Lambda=0`, we have `z0*t0'=0`. The actual **zero vector** then satisfies all parts of the folded output relation: its commitment is zero, its MLE at the verifier's terminal point is zero, and its norm is zero. In contrast, a non-zero-slot challenge usually leaves a nonzero folded evaluation; a zero output witness is rejected, which is the observed negative control.

The sampling certificate supplies at least `M` supported values of `z0` that cause this event; `z1` is unrestricted. The count is independent of the terminal points. Under the interactive public-coin experiment, the first-layer JL coins and the final fold challenge are independent. Combining the 2048-column rank bound with the challenge lower bound gives the **conservative** success-probability guarantee

```text
p_success >= (1 - 2^-942) * 4337664 / (2^23 * binom(128,23))
          = approximately 2^-84.464.
```

This is a single-shot **probability over the verifier's public randomness**, not a claim that we have efficiently found an actual SHAKE transcript with that final challenge. In the ideal random-oracle interpretation, this corresponds to a very small success probability for a one-attempt prover, not a practical preimage attack. The proof uses the abstract challenge law; any exact byte-level distribution statement about SHAKE plus the implementation's rejection sampler requires a separate encoding/distribution audit.

## 6. Relationship to the paper's security statements

Definition 11 and Theorem 1 *already contain* the term `epsilon_C` to pay for non-unit differences. The results here do not contradict the abstract theorem when it uses the **true** `epsilon_C`; they show that the *concrete estimate inserted for the implemented sampler* is too small. In §6.2 the implementation reports a knowledge error around `2^-90`. The certified favorable-challenge event alone has probability at least about `2^-84.46`, a factor of about **46.4** above that nominal error.

For reference, under the paper's **heuristic** substitution `epsilon_C=64/q^2` and its assumed cardinality `|C|>=q^2`, the audited Theorem 1 parameters give `kappa_main <= 276/q^2 + kappa_proj`, with `kappa_proj = 4225*2^-128`; the Appendix A strategy gives `kappa_AppendixA <= 406/q^2 + kappa_proj`. The attack lower bound is respectively about **172.18** and **117.05** times these *nominal* bounds. These comparisons are conditional on the claimed numerical sampling assumptions and are not claims about a theorem instantiated with the actual `epsilon_C`.

The original knowledge-soundness statement also permits an extractor to output a same-key SIS solution. Our input-relation impossibility is **unconditional** on the key, but exclusion of the alternative SIS-break outcome for the random rank-12 key still rests on the paper's SIS hardness assumption. The optional identity-key construction discussed in the Round 9 report removes that alternative for a different, non-benchmark key; it is not used in the Rust result described here.

## 7. Rust verification: what was executed

The provided code is a test-only adversarial prover. It derives the real projection matrices and sumcheck challenges from the original statement transcript, solves the first-layer kernel, computes scalar witness rounds for general mod-`q` coefficients, and calls the original `verify_fold()` and `verify_output()` routines. A portable arithmetic feature was necessary because the original prover's AVX-512 routines cannot run on the tested CPU. The verifier's equations and round-check logic were left unchanged.

The user-reported runs on WSL2/x86-64 (Rust nightly, pinned Rokoko dependency) were:

```text
Round 10, m=2^18:
  PASS exact transcript-derived J0 kernel: 256 rows, 513 coefficients
  PASS: real original verify_fold accepted 40 malicious sumcheck rounds, rank=12
  test result: ok. 1 passed; 0 failed

Round 11, m=2^18:
  PASS input relation has NO short opening
  FS_ZERO_SLOT_EVENT_OBSERVED=false; normal SHAKE output correctly rejected zero witness
  CONDITIONAL_GOOD_CHALLENGE_OUTPUT_ACCEPTED=true
  CONDITIONAL_BAD_CHALLENGE_OUTPUT_REJECTED=true
  PASS: original verify_fold 40 rounds, full rank 12, original verify_output challenge separation

Round 12, m=2^18:
  R12_NORMAL_FS_ZERO_SLOT=false; NORMAL_FS_ZERO_WITNESS_REJECTED=true
  R12_GOOD_CHALLENGE_WEIGHT=23; SPECTRAL_NORM=8.117973728; LIMIT=8.357
  R12_BAD_CHALLENGE_WEIGHT=23; SPECTRAL_NORM=8.117973728; LIMIT=8.357
  R12_GOOD_ORIGINAL_VERIFY_FOLD_AND_OUTPUT_ACCEPTED=true
  R12_BAD_ORIGINAL_VERIFY_FOLD_ACCEPTED_OUTPUT_REJECTED=true
  R12_FS_STATE_RESTORED_IDENTICALLY=true
  R12_PASS m=2^18, rounds=40, rank=12
  test result: ok. 1 passed; 0 failed
```

The **Round 12 controlled replay** replaces **only the final folding-challenge sampling** while an explicit test-feature guard is in scope. It checks that both supplied challenges belong to the original sampler's support (weight 23, operator norm approximately 8.118), calls the unchanged `verify_fold()` checking logic with that final public coin, then passes its returned statement directly to `verify_output()`. The negative control rejects and the guard restores normal SHAKE results exactly. This is a genuine *conditional public-coin verification trace*, **not** an acceptance trace produced by the unmodified SHAKE challenge generator. The additional `derived-key` test path uses the exact identity `Commit(0)=0` to avoid generating a huge public key; it is not a general independent implementation of nonzero commitments.

The Rust execution results above are transcribed from the user's local terminal reports; this archive does not contain machine-generated Rust logs signed or captured by an independent operator. The numerical certificate is separately reproducible from the included files.

## 8. Reproduction and limitations

Run `bash round9/verify_all.sh` from the attached extracted archive to reproduce the zero-slot candidate certificates, CRT algebra, finite sample kernel and probability arithmetic. The additional checker `python3 round12/verify_round12_static.py` verifies the positive and negative challenge fixtures. The archive also contains the upstream source snapshot, compatibility patches, the original Round 10 test-only prover, and incremental Round 11/12 test installers. `README_CN.md` and `INSTALL_FROM_CLEAN.sh` specify the installation order.

**What has not been established:** an ordinary production build that accepts a complete, unmodified-SHAKE Fiat–Shamir forgery; an exact distributional bound for the byte-level SHAKE/AES sampler; a proof that the sampler satisfies Heuristic 1's cardinality premise; or a theorem-level contradiction with the actual `epsilon_C`. The mathematical public-coin lower bound uses a 2048-column rank solver, whereas the executed Rust fixture uses 512 extra columns. The 50-bit benchmark result says nothing automatically about the separate 64-bit Table 5 estimates.

**Primary references:** *PikkuFold: Efficient Folding in a Few Kilobytes*, ePrint 2026/1809, especially Definition 11, Figure 2, Theorem 1, Heuristic 1, §6.2 and Table 6; original code at `https://github.com/osdnk/pikku` (the attached snapshot is dated September 17, 2026). The Rokoko dependency is pinned in the original Cargo manifest to commit `64a9cd49d7d5281b0e174556662ec283e2eb8b3d`.

## 9. Short Rust regression excerpt

For example, after building the `instance` and `proof` from the real transcript-derived `J0` (see `round10/adversarial_attack_tests.rs`), the Round 12 test checks the verification path as follows. The helper `audit_force_fold_challenges` is compiled **only** with the `conditional-fold-audit` test feature; it does not exist in normal verifier builds.

```rust
// Baseline: no final-challenge override.
let normal = verify_fold(m, &instance, &proof).unwrap();
let normal_result = verify_output(
    &key, &zero_output_witness,
    &normal.folded_commitment, &normal.folded_claim, cap,
);
assert_ne!(normal.folded_claim.value, zero); // observed baseline run
assert!(normal_result.is_err());

// These are both in the original sampler's support: weight 23, norm < 8.357.
let good = challenge_galois(1); // good * Lambda = 0
let bad = challenge_galois(3);  // bad * Lambda != 0
round12_check_accepted_fixed_weight_challenge(&good, "GOOD");
round12_check_accepted_fixed_weight_challenge(&bad, "BAD");

// The *original verify_fold* returns the favorable folded statement itself.
let favorable = {
    let _guard = audit_force_fold_challenges(vec![
        good.clone(), bad.clone(), one.clone(),
    ]);
    verify_fold(m, &instance, &proof).unwrap()
};
assert_eq!(favorable.folded_claim.value, zero);
verify_output(
    &key, &zero_output_witness,
    &favorable.folded_commitment, &favorable.folded_claim, cap,
).unwrap();

// Swap good and bad in the first input's challenge; zero output must fail.
let unfavorable = {
    let _guard = audit_force_fold_challenges(vec![bad, good, one]);
    verify_fold(m, &instance, &proof).unwrap()
};
assert!(verify_output(
    &key, &zero_output_witness,
    &unfavorable.folded_commitment, &unfavorable.folded_claim, cap,
).is_err());

// Confirm the audit hook was removed and the SHAKE output is unchanged.
let restored = verify_fold(m, &instance, &proof).unwrap();
assert_eq!(restored.folded_claim.value, normal.folded_claim.value);
assert_eq!(restored.folded_claim.point, normal.folded_claim.point);
assert_eq!(restored.folded_commitment, normal.folded_commitment);
```

This is a readable excerpt, not a standalone Rust module. The complete definition of the fixture and the actual acceptance assertions are in `round12/round12_test_append.rs`; the count and probability certificates are in `round9/`.
