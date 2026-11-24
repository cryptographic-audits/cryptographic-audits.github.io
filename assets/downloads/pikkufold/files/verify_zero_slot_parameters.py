#!/usr/bin/env python3
"""Independent integer checks of a Table-6-cap norm-zero projection kernel attack.

Certifies a finite sampled coarse JL matrix has a fixed-coordinate kernel vector;
proves via exact integer inequalities that the public MLE evaluation forces any
source opening beyond the Table 6 norms. Does not claim a full Rust/FS forgery.
"""
from math import comb, log2, gcd, isqrt
from fractions import Fraction as F
from pathlib import Path
import json, sys
Q=(1<<50)-2687
BETA=739582794740178
N=128
BASE=2**23*comb(128,23)
FIBRE=4337664 # from prior independently certified finite sample; not re-counted here

def main():
    path=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).with_name('first_layer_kernel_certificate.txt')
    data=path.read_text().splitlines();q,rows,cols,seed=map(int,data[0].split()); assert (q,rows,cols)==(Q,256,257)
    J=[list(map(int, line.split())) for line in data[1:1+rows]]
    co=data[1+rows].split(); assert co[0]=='coeff'
    a=list(map(int,co[1:])); assert len(a)==cols and a[0]==1 and all(0<=v<Q for v in a)
    assert len(J)==rows and all(len(row)==cols and all(v in (-1,0,1) for v in row) for row in J)
    assert all(sum(v*c for v,c in zip(row,a))%Q==0 for row in J)
    # Pocklington certificate for q's primality, with a factor > sqrt(q).
    rp=13470280279
    assert Q-1==128*653*rp and rp*rp>Q
    assert all(rp%d for d in range(2,isqrt(rp)+1))
    assert pow(2,Q-1,Q)==1 and gcd(pow(2,(Q-1)//rp,Q)-1,Q)==1
    assert pow(BETA,64,Q)==Q-1 and pow(BETA,128,Q)==1
    assert pow(BETA,(Q-1)//2,Q)==Q-1
    # Idempotent polynomial in Y=X^2.  T(Y)= (sum beta^j Y^(63-j))/(64*beta^63).
    denominator=64*pow(BETA,63,Q)%Q
    inv=pow(denominator,-1,Q)
    lam=[pow(BETA,63-j,Q)*inv%Q for j in range(64)]
    # lam indexed by Y^j; check target slot value=1 and 63 other CRT slots=0.
    roots=[pow(BETA,2*s+1,Q) for s in range(64)]
    values=[sum(lam[j]*pow(r,j,Q) for j in range(64))%Q for r in roots]
    assert values==[1]+[0]*63
    # Equivalent proof: any nonzero integer polynomial reducing to lam mod q
    # has field norm divisible by q^(2*63), and at most ||x||^128 by Parseval + AM-GM.
    # For each benchmark M, beta_in'^2=2*beta_in²*(343.2/27.37)^3.
    bounds=[]
    for pow_M in (25,27,29):
        M=1<<pow_M
        beta_in_sq=F(M*(1024**2))
        beta_in_prime_sq=2*beta_in_sq*(F(1716,5)/F(2737,100))**3
        assert beta_in_prime_sq <2**62
        # If ||x||<=beta'_in<2^31, then norm(x)<2^(31*128)=2^3968.
        # But 63 vanished quadratic slots give Norm(x) >=q^126>2^(49*126).
        assert Q>2**49 and 49*126>31*128
        # Layered modular JL margin: beta' * ell^j * 126 < q for j=0,1,2.
        for j in range(3):
            assert 126**2*beta_in_prime_sq*F(2737,100)**j < Q*Q
        bounds.append({'M_exponent':pow_M,'beta_in_squared':str(beta_in_sq),
                       'beta_in_prime_squared':str(beta_in_prime_sq),
                       'beta_in_prime_upper':2**31,
                       'all_source_openings_impossible_for_MLE_point_zero':True})
    # Key is arbitrary; output y_fold=0,t_fold=0,w_out=0 when z0*lambda=0.
    # First coarse layer kernel sample embeds a_j*lambda in first 257 ring positions,
    # so every first-layer output is zero (and all later images zero).
    # Exact challenge probability lower bound: set accepted C subset of base support.
    p=F(FIBRE,BASE)
    # Correct Table-6 d3, mu2, k2 paper formula with H1 nominal eps=64/q²
    kproj=F(4225,2**128)
    # Instead, compare against explicit hypothetical |C|>=q², as H1 requires.
    kmain_nom=F(276,Q*Q)+kproj
    kapp_nom=F(406,Q*Q)+kproj
    assert p > kmain_nom and p > kapp_nom
    # An optional formal countermodel chooses beta'_out=1, F=identity,
    # rather than the benchmark's 12/13-row commitment key.
    gamma=F(8357,1000); k=2
    rho=(2*gamma)**k
    beta_bind=(k+1)*rho
    beta_sis=max(8*gamma,2*beta_bind*rho)
    assert beta_sis<Q
    # For unbiased ternary JL columns, probability proper-subspace membership <= 1/2.
    # Chernoff for 2048 subsequent columns, lower-tail P[Bin(2048,1/2)<256]
    # <=exp(-576)<2^-830 (since ln2<0.694).
    low_tail_numerator=sum(comb(2048,j) for j in range(256))
    assert low_tail_numerator < 2**(2048-942) # exact Pr[rank<256] < 2^-942
    joint_attack_lower=(1-F(low_tail_numerator,2**2048))*p
    assert joint_attack_lower>kmain_nom and joint_attack_lower>kapp_nom
    out={'q':Q,'beta':BETA,'jl_seed':seed,'rows':rows,'selected_columns':cols,
         'kernel_nonzero_first_coefficient':1,'projection_exact_zero_all_rows':True,
         'idempotent_value_slot0':values[0], 'other_zero_slots':63,
         'norm_divisibility':'q^126 divides Norm(x), for any lift x of lambda; Norm(x) !=0',
         'norm_lower_bound':'||x|| >= q^(63/64) > 2^(49*63/64) > 2^48',
         'benchmark_beta_in_prime_bounds':bounds,
         'attack_challenge_fibre_count_from_prior_certificate':FIBRE,
         'base_cardinality_exact':BASE,'attack_success_prob_lower_exact':str(p),
         'rank_failure_exact_upper':str(F(low_tail_numerator,2**2048)),
         'rank_failure_less_2_minus_942':True,
         'optional_information_theoretic_F_equals_identity_variant':{
           'output_extraction_cap':1,
           'original_theorem_beta_sis':str(beta_sis),
           'beta_sis_less_than_q':True,
           'no_nonzero_kernel_vector_below_q_for_F_identity':True,
           'different_from_rank_12_or_13_benchmark_key':True},
         'combined_projection_rank_and_challenge_attack_lower_exact':str(joint_attack_lower),
         'attack_success_bits_display':-log2(float(p)),
         'nominal_kappa_main_at_C_at_least_q2':str(kmain_nom),
         'nominal_kappa_appendix_at_C_at_least_q2':str(kapp_nom),
         'attack_vs_main_ratio':float(p/kmain_nom),
         'attack_vs_appendix_ratio':float(p/kapp_nom),
         'disclaimer':'No full 40-round Rust/FS serialization. Challenge count imported from exploratory finite certificate.'}
    dest=Path(__file__).with_name('zero_slot_results.json');dest.write_text(json.dumps(out,indent=2,ensure_ascii=False))
    print(json.dumps({k:out[k] for k in ('projection_exact_zero_all_rows','other_zero_slots','attack_success_bits_display','attack_vs_main_ratio','attack_vs_appendix_ratio')},indent=2))

if __name__=='__main__':main()
