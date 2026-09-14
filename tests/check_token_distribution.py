"""New H1a statistic checks against explicit features and independent splits."""
import numpy as np
from src.methods.token_distribution import token_heterogeneity,pad_after_eos,aggregate_distribution

rng=np.random.default_rng(91)
a=rng.integers(0,5,size=(3,4,7));b=rng.integers(0,5,size=(3,6,7))
# Small vocabulary permits the literal one-hot definition as an independent oracle.
fa=np.eye(5)[a].mean(axis=1).reshape(3,-1)/np.sqrt(7)
fb=np.eye(5)[b].mean(axis=1).reshape(3,-1)/np.sqrt(7)
expected=((fa-fa.mean(axis=0))*(fb-fb.mean(axis=0))).sum()/2
assert np.isclose(token_heterogeneity(a,b),expected)
assert np.isclose(token_heterogeneity(b,a),expected)
identity_a=np.repeat(a[:1],2,axis=0);identity_b=np.repeat(b[:1],2,axis=0)
assert token_heterogeneity(identity_a,identity_b)==0
opposed=np.array([[[0,0]],[[1,1]]])
assert token_heterogeneity(opposed,opposed)==1
assert token_heterogeneity(opposed,opposed[::-1])==-1
assert token_heterogeneity(opposed[:1],opposed[:1]) is None
assert pad_after_eos([7,100257,8,9]).tolist()==[7,100257,100277,100277]
assert pad_after_eos([7,100265,8,9]).tolist()==[7,100265,100277,100277]
clustered=aggregate_distribution([dict(source_id='document-a',h_token=.2),
    dict(source_id='document-a',h_token=.2),dict(source_id='document-b',h_token=.8)],bootstrap=1000)
assert clustered['sources']==2 and clustered['roots']==3
assert np.isclose(clustered['h_token']['mean'],.4)
assert np.allclose(clustered['h_token']['ci95'],[.2,.8])
print('H1a checks passed: explicit features, identity, A/B reversal, signed estimates, EOS, and source clustering.')
