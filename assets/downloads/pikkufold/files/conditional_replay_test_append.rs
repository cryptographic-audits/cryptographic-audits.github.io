// CONDITIONAL_VERIFIER_REPLAY_BEGIN
// Stronger than Output-challenge check's post-verification relation substitution:
// The SAME original verify_fold() is executed with the final public-coin
// challenges injected at its ONLY call to fold_challenges(). The same
// original verify_output() then consumes the returned VerifierMessage.
// This is a controlled-public-coin unit test, NOT a SHAKE preimage attack.
#[cfg(feature = "conditional-fold-audit")]
fn check_accepted_fixed_weight_challenge(
    z: &RingElement,
    label: &str,
) -> f64 {
    use crate::config::{FOLD_CHALLENGE_OP_NORM_BOUND, FOLD_CHALLENGE_WEIGHT};
    let mut coefficients = z.clone();
    coefficients.from_incomplete_ntt_to_even_odd_coefficients();
    assert_eq!(coefficients.v.len(), 128);
    let mut terms = Vec::<(usize, i8)>::new();
    for (index, &value) in coefficients.v[..64].iter().enumerate() {
        let sign = if value == 0 { 0 } else if value == 1 { 1 }
            else if value == Q - 1 { -1 }
            else { panic!("{label}: coefficient outside {{-1,0,1}} at even index {index}"); };
        if sign != 0 { terms.push((index, sign)); }
    }
    assert!(coefficients.v[64..].iter().all(|&x| x == 0),
        "{label}: expected only even powers of X");
    assert_eq!(terms.len(), FOLD_CHALLENGE_WEIGHT,
        "{label}: invalid challenge Hamming weight");

    // Negacyclic ring R = Z[X]/(X^128+1). For even-power z = p(X^2),
    // the canonical operator norm is the maximum of |p(Y)| at the 64 roots
    // Y = exp(i*pi*(2j+1)/64) of Y^64+1. All arithmetic here is independent
    // of the short-challenge rejection sampler and runs only in a TEST.
    let mut spectral_max = 0.0f64;
    for j in 0..64 {
        let theta = std::f64::consts::PI * (2 * j + 1) as f64 / 64.0;
        let (mut re, mut im) = (0.0f64, 0.0f64);
        for &(exponent, sign) in &terms {
            let angle = theta * (exponent as f64);
            re += (sign as f64) * angle.cos();
            im += (sign as f64) * angle.sin();
        }
        spectral_max = spectral_max.max(re.hypot(im));
    }
    assert!(spectral_max < FOLD_CHALLENGE_OP_NORM_BOUND - 0.1,
        "{label}: candidate is too close to the sampler threshold");
    println!("REPLAY_{label}_CHALLENGE_WEIGHT={}; SPECTRAL_NORM={spectral_max:.9}; LIMIT={FOLD_CHALLENGE_OP_NORM_BOUND}",
        terms.len());
    spectral_max
}

#[cfg(feature = "conditional-fold-audit")]
#[test]
fn test_conditional_original_verifier_replay() {
    use crate::commitment::CommitmentKey;
    use crate::config::{folded_norm_bound, witness_norm_bound};
    use crate::fold::audit_force_fold_challenges;
    use crate::output::verify_output;

    init_common();
    let log_m = std::env::var("PIKKU_ATTACK_LOG_M")
        .ok().and_then(|s| s.parse::<usize>().ok()).unwrap_or(10);
    assert!((10..=18).contains(&log_m));
    let m = 1usize << log_m;
    let rank = commitment_rank(m);
    let zero = RingElement::zero(Representation::IncompleteNTT);
    let one = RingElement::constant(1, Representation::IncompleteNTT);
    let l = lambda();

    // Establish unsatisfiability of the original short-witness input relation.
    // At the Boolean-zero MLE point, the first witness coordinate must equal
    // Lambda, whose centered constant coefficient alone exceeds the total cap.
    let centered_lambda_coefficient = (Q - 1) / 64;
    let mut coeff_l = l.clone();
    coeff_l.from_incomplete_ntt_to_even_odd_coefficients();
    assert_eq!(coeff_l.v[0], Q - centered_lambda_coefficient);
    assert!((centered_lambda_coefficient as f64) > witness_norm_bound(m));

    let mut claims = (0..FOLD_INPUTS).map(|_| EvalClaim {
        point: vec![zero.clone(); log_m], value: zero.clone(),
    }).collect::<Vec<_>>();
    claims[0].value = l.clone();
    let instance = Instance {
        commitment: HorizontallyAlignedMatrix {
            data: vec![zero.clone(); rank * FOLD_INPUTS],
            width: FOLD_INPUTS,
            height: rank,
        },
        claims,
    };
    assert_eq!(instance.claims.len(), FOLD_INPUTS);
    assert_eq!(instance.commitment.height, rank);

    // Actual transcript-derived J0; no fixed offline JL instance is assumed.
    let ratios = projection_shape(m).expect("supported projection shape");
    let mut pre_transcript = statement_transcript(m, &instance);
    let matrices = sample_projection_matrices(&ratios, &mut pre_transcript);
    let a = kernel_with_fixed_first(&matrices[0]);
    let mut pseudo = VerticallyAlignedMatrix {
        data: vec![zero.clone(); FOLD_INPUTS * m],
        width: FOLD_INPUTS, height: m, used_cols: FOLD_INPUTS,
    };
    for (j, &coefficient) in a.iter().enumerate() {
        let scalar = RingElement::constant(coefficient, Representation::IncompleteNTT);
        pseudo.data[j] *= (&l, &scalar);
    }
    assert_eq!(pseudo.col(0)[0], l);
    assert!(pseudo.col(1).iter().all(|x| x == &zero));
    assert!(pseudo.col(2).iter().all(|x| x == &zero));

    let proof = prove_adversarial_fold(m, &instance, &pseudo)
        .expect("test-only prover should produce true nonzero RingSC");
    let expected_rounds = match log_m {
        10 => 28, 18 => 40,
        _ => {
            let input_vars = (FRESH_INPUTS * m).ilog2() as usize;
            let middle_vars = input_vars - ratios[0].ilog2() as usize;
            input_vars + middle_vars + PROJECTION_ROWS.ilog2() as usize
        }
    };
    assert_eq!(proof.round_polynomials.len(), expected_rounds);
    assert!(proof.round_polynomials.iter().any(|pair|
        pair.iter().any(|poly| poly.coeffs != [0, 0])));

    let key = CommitmentKey::sample(m, rank);
    let zero_output_witness = VerticallyAlignedMatrix {
        data: vec![zero.clone(); m], width: 1, height: m, used_cols: 1,
    };
    let cap = folded_norm_bound(m);

    // BASELINE: untouched normal Fiat-Shamir result, with NO override.
    let normal = verify_fold(m, &instance, &proof)
        .expect("unchanged sumcheck verification must accept the malicious transcript");
    assert_eq!(normal.folded_commitment.len(), rank);
    assert!(normal.folded_commitment.iter().all(|x| x == &zero));
    assert_eq!(normal.folded_claim.point.len(), log_m);
    let normal_result = verify_output(
        &key, &zero_output_witness, &normal.folded_commitment,
        &normal.folded_claim, cap,
    );
    if normal.folded_claim.value == zero {
        assert!(normal_result.is_ok(), "true FS zero-slot outcome should admit zero witness");
        println!("REPLAY_NORMAL_FS_ZERO_SLOT=true (rare actual hash outcome)");
    } else {
        let message = normal_result.expect_err("normal nonzero folded claim must reject zero witness");
        assert!(message.contains("evaluation"));
        println!("REPLAY_NORMAL_FS_ZERO_SLOT=false; NORMAL_FS_ZERO_WITNESS_REJECTED=true");
    }

    // Check that BOTH supplied test challenges are actual sampler-support
    // elements: exact weight 23, coefficients +/-1, operator norm < 8.357.
    let good = challenge_galois(1);
    let bad = challenge_galois(3);
    check_accepted_fixed_weight_challenge(&good, "GOOD");
    check_accepted_fixed_weight_challenge(&bad, "BAD");
    assert_ne!(good, bad);
    let mut good_times_l = zero.clone();
    good_times_l *= (&good, &l);
    assert_eq!(good_times_l, zero);
    let mut bad_times_l = zero.clone();
    bad_times_l *= (&bad, &l);
    assert_ne!(bad_times_l, zero);

    // PUBLIC-COIN CONDITIONING: install a scoped override ONLY at the FINAL
    // fold_challenges call inside ORIGINAL verify_fold. The original checks,
    // proof, projection, sumcheck messages and terminal point are untouched.
    // Unlike Output-challenge check, the returned VerifierMessage is not constructed by hand.
    let conditioned_good = {
        let _guard = audit_force_fold_challenges(vec![good.clone(), bad.clone(), one.clone()]);
        verify_fold(m, &instance, &proof)
            .expect("original verify_fold must accept under a supported good final coin")
    };
    assert_eq!(conditioned_good.folded_claim.point, normal.folded_claim.point);
    assert_eq!(conditioned_good.folded_commitment.len(), rank);
    assert!(conditioned_good.folded_commitment.iter().all(|x| x == &zero));
    assert_eq!(conditioned_good.folded_claim.value, zero);
    verify_output(
        &key, &zero_output_witness,
        &conditioned_good.folded_commitment,
        &conditioned_good.folded_claim, cap,
    ).expect("zero opening must pass original verify_output with good final public coin");
    println!("REPLAY_GOOD_ORIGINAL_VERIFY_FOLD_AND_OUTPUT_ACCEPTED=true");

    let conditioned_bad = {
        let _guard = audit_force_fold_challenges(vec![bad.clone(), good.clone(), one.clone()]);
        verify_fold(m, &instance, &proof)
            .expect("original verify_fold should still accept non-favorable public coin")
    };
    assert_eq!(conditioned_bad.folded_claim.point, normal.folded_claim.point);
    assert_eq!(conditioned_bad.folded_commitment.len(), rank);
    assert!(conditioned_bad.folded_commitment.iter().all(|x| x == &zero));
    assert_ne!(conditioned_bad.folded_claim.value, zero);
    let error = verify_output(
        &key, &zero_output_witness,
        &conditioned_bad.folded_commitment,
        &conditioned_bad.folded_claim, cap,
    ).expect_err("bad public coin must reject a zero output witness");
    assert!(error.contains("evaluation"));
    println!("REPLAY_BAD_ORIGINAL_VERIFY_FOLD_ACCEPTED_OUTPUT_REJECTED=true");

    // Guard must be reversible. Re-run normal SHAKE and compare exact outputs,
    // proving conditional injection did not persist across tests.
    let normal_again = verify_fold(m, &instance, &proof)
        .expect("normal SHAKE verifier must be restored after guards drop");
    assert_eq!(normal_again.folded_claim.point, normal.folded_claim.point);
    assert_eq!(normal_again.folded_claim.value, normal.folded_claim.value);
    assert_eq!(normal_again.folded_commitment, normal.folded_commitment);
    println!("REPLAY_FS_STATE_RESTORED_IDENTICALLY=true");
    println!("REPLAY_PASS m=2^{log_m}, rounds={expected_rounds}, rank={rank}");
    println!("REPLAY_SCOPE: conditional public-coin verification; NOT a SHAKE forgery");
}
// CONDITIONAL_VERIFIER_REPLAY_END
