#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
if (( $# != 1 )); then
  echo "Usage: bash $0 /absolute/path/to/pikku-main/pikku-fold-schemelet" >&2
  exit 2
fi
CRATE=$(realpath "$1")
if [[ ! -f "$CRATE/src/prover.rs" || ! -f "$CRATE/Cargo.toml" ]]; then
  echo "Not a PikkuFold schemelet crate: $CRATE" >&2; exit 2
fi
cd "$CRATE"
python3 "$ROOT/portable/install_pikkufold_scalar_output_probe.py" \
  --module "$ROOT/portable/pikkufold_output_semantics_probe.rs"
python3 "$ROOT/portable/patch_pikkufold_portable_mle.py"
python3 "$ROOT/folding-proof-reproduction/install_folding_proof_test.py" \
  --test-module "$ROOT/folding-proof-reproduction/adversarial_attack_tests.rs"
# Fix the missing import in the original Folding-proof reproduction generator. This is exactly
# the one-line fix verified by the user prior to the successful Rust tests.
python3 - <<'PY'
from pathlib import Path
p=Path('src/adversarial_attack.rs')
s=p.read_text()
before='use crate::config::{FRESH_SELECTOR_VARS, PROJECTION_BATCH_POINTS, PROJECTION_LAYERS};'
after='use crate::config::{FRESH_INPUTS, FRESH_SELECTOR_VARS, PROJECTION_BATCH_POINTS, PROJECTION_LAYERS};'
if before in s and s.count(before)==1:
    p.write_text(s.replace(before,after,1))
    print('Applied verified Folding-proof reproduction FRESH_INPUTS import fix')
elif s.count(after)==1:
    print('Folding-proof reproduction FRESH_INPUTS import already present')
else:
    raise SystemExit('Unexpected adversarial_attack.rs import; refuse to modify')
PY
python3 "$ROOT/output-challenge-check/install_output_challenge_test.py" \
  --append "$ROOT/output-challenge-check/output_challenge_test_append.rs"
python3 "$ROOT/conditional-verifier-replay/install_conditional_replay.py" \
  --append "$ROOT/conditional-verifier-replay/conditional_replay_test_append.rs"
printf '\nInstalled. Compile and run (with RUSTFLAGS="-C target-cpu=x86-64-v3"):\n'
echo 'cargo +nightly test --locked --features conditional-fold-audit --no-run'
echo 'PIKKU_ATTACK_LOG_M=18 cargo +nightly test --locked --features conditional-fold-audit adversarial_attack_tests::test_conditional_original_verifier_replay -- --exact --nocapture --test-threads=1'
