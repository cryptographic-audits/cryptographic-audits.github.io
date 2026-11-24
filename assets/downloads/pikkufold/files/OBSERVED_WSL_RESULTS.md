# User-reported native Rust verification results

The text below is extracted from the user's terminal messages in this conversation. These are not independently captured or re-executed Rust logs in the deliverable environment.

## Round 10, `PIKKU_ATTACK_LOG_M=18`

```text
PASS exact transcript-derived J0 kernel: 256 rows, 513 coefficients
Generating true adversarial sumcheck for m=2^18 (not a zero transcript)
PASS: real original verify_fold accepted 40 malicious sumcheck rounds, rank=12
CRITICAL SCOPE: zero-slot challenge is a separate conditional algebra check;
normal SHAKE/Fiat-Shamir fold challenge was NOT overridden and not claimed favorable.
test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 34 filtered out; finished in 1.98s
TEST_EXIT_CODE=0
```

## Round 11, `PIKKU_ATTACK_LOG_M=18`

```text
PASS input relation has NO short opening: |centered Lambda[0]|=17592186044374 > input_bound=5931641.601516
PASS exact transcript-derived J0 kernel: 256 rows, 513 coefficients
FS_ZERO_SLOT_EVENT_OBSERVED=false; normal SHAKE output correctly rejected zero witness
CONDITIONAL_GOOD_CHALLENGE_OUTPUT_ACCEPTED=true
CONDITIONAL_BAD_CHALLENGE_OUTPUT_REJECTED=true
PASS: original verify_fold 40 rounds, full rank 12, original verify_output challenge separation
SCOPE: one conditional post-folding experiment; no forced SHAKE or practical FS forgery
test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 35 filtered out; finished in 25.65s
```

## Round 12, `PIKKU_ATTACK_LOG_M=18`

```text
PASS exact transcript-derived J0 kernel: 256 rows, 513 coefficients
R12_NORMAL_FS_ZERO_SLOT=false; NORMAL_FS_ZERO_WITNESS_REJECTED=true
R12_GOOD_CHALLENGE_WEIGHT=23; SPECTRAL_NORM=8.117973728; LIMIT=8.357
R12_BAD_CHALLENGE_WEIGHT=23; SPECTRAL_NORM=8.117973728; LIMIT=8.357
R12_GOOD_ORIGINAL_VERIFY_FOLD_AND_OUTPUT_ACCEPTED=true
R12_BAD_ORIGINAL_VERIFY_FOLD_ACCEPTED_OUTPUT_REJECTED=true
R12_FS_STATE_RESTORED_IDENTICALLY=true
R12_PASS m=2^18, rounds=40, rank=12
R12_SCOPE: conditional public-coin verification; NOT a SHAKE forgery
test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 36 filtered out; finished in 27.55s
```

## Scope and limitations

The Round 12 test uses `--features conditional-fold-audit`, which replaces the *last challenge sampling* in a controlled test scope. It does not demonstrate an unmodified SHAKE forgery. A separate portable test back end avoids AVX-512 instructions; the zero-witness commitment case uses exact linearity `Commit(0)=0` without producing a full derived CRS.
