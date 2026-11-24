#!/usr/bin/env python3
"""Independent memory-bounded certified-count extension of an actual-q zero-slot search.

Checks every candidate exact in F_q, norm <= gamma with rational-trig root
intervals, and counts negacyclic Y-rotation/sign orbits by canonical bitmasks.
Odd weight 23 implies orbit length 128 in Y (and 256 in full X ring).
Never infers a population rate by random sampling.
"""
from pathlib import Path
from math import comb,log2
import json,sys
import numpy as np
from reproduce_enumeration import certified_unit_table, SCALE
from verify_actual_q50_zeros import decode,Q,BETA,WEIGHT

mask=(1<<64)-1
re,im=certified_unit_table(64)
pow_beta=[pow(BETA,j,Q) for j in range(64)]
base=2**23*comb(128,23)
lim=(8357**2*SCALE**2)//10**6
lim82=(82**2*SCALE*SCALE)//100

def key_rot(a):
    P=sum(1<<i for i,v in enumerate(a) if v==1)
    N=sum(1<<i for i,v in enumerate(a) if v==-1)
    best=None
    for t in range(64):
        if t:
            p=((P<<t)&mask)|(N>>(64-t))
            n=((N<<t)&mask)|(P>>(64-t))
        else:p,n=P,N
        z=(p,n) if p<n else (n,p)
        if best is None or z<best:best=z
    return best

def readfiles(paths):
    files=list(paths)
    total=accepted=accept82=rejected=unknown=0
    seen=set(); seen82=set(); examples=[]
    for p in files:
        with open(p,'r',encoding='utf-8') as f:
            for line in f:
                if not line.strip():continue
                a=decode(line);total+=1
                idx=[i for i,v in enumerate(a) if v]
                assert sum(a[i]*pow_beta[i] for i in idx)%Q==0
                v=np.array([a[i] for i in idx],dtype=np.int64)
                vr=np.sum(re[idx]*v[:,None],axis=0)
                vi=np.sum(im[idx]*v[:,None],axis=0)
                hi=int(np.max((np.abs(vr)+WEIGHT)**2+(np.abs(vi)+WEIGHT)**2))
                lo=int(np.max(np.maximum(np.abs(vr)-WEIGHT,0)**2+np.maximum(np.abs(vi)-WEIGHT,0)**2))
                if hi<=lim:
                    accepted+=1
                    key=key_rot(a)
                    if key not in seen and len(examples)<8:
                        examples.append({'pos':idx,'sign':[a[i] for i in idx], 'upper_sq_int':hi})
                    seen.add(key)
                    if hi<=lim82:seen82.add(key);accept82+=1
                elif lo>lim: rejected+=1
                else:unknown+=1
        print('checked',p.name,'total',total,'accepted',accepted,'orbits',len(seen),flush=True)
    assert unknown==0
    assert 256*len(seen)<=base
    return {'files':len(files),'source_candidates':total,'accepted_8357':accepted,
            'accepted_8200':accept82,'rejected_8357':rejected,'unclassified':unknown,
            'canonical_even_Y_orbits_8357':len(seen),
            'distinct_signed_full_X_rotations_8357':256*len(seen),
            'canonical_even_Y_orbits_8200':len(seen82),
            'distinct_signed_full_X_rotations_8200':256*len(seen82),
            'zero_fibre_nonunit_lower_exact':f'({256*len(seen)-1})/{base}',
            'sampling_probability_lower_exact':f'{256*len(seen)}/{base}',
            'sampling_probability_lower_bits_display':-log2(256*len(seen)/base),
            'gamma':'8357/1000','q':Q,'beta':BETA,
            'memberships':'interval root table with integer-square envelopes; no undecided samples',
            'orbit_justification':'weight23 odd implies signed negacyclic Y^t orbit has 128 elements; X^t adds the other parity, producing 256 distinct X rotations',
            'examples':examples}

if __name__=='__main__':
    paths=[Path(p) for p in sys.argv[1:]]
    if not paths:paths=[Path('/mnt/data/pikkufold_attack/actual_q50_candidate_codes_all.txt')]
    out=readfiles(paths)
    destination=Path(__file__).with_name('more_orbits_results.json')
    destination.write_text(json.dumps(out,indent=2),encoding='utf-8')
    print('RESULT',json.dumps({k:v for k,v in out.items() if k!='examples'},indent=2),flush=True)
