"""Cross-split future token-position distribution heterogeneity."""
import numpy as np
from src.methods.same_prefix_statistics import aggregate


def pad_after_eos(tokens, eos_ids=(100257,100265), pad_id=100277):
    x=np.asarray(tokens,dtype=np.int64).copy()
    stop=np.isin(x,eos_ids)
    after=np.zeros_like(stop)
    after[...,1:]=np.maximum.accumulate(stop,axis=-1)[...,:-1]
    x[after]=pad_id
    return x


def token_heterogeneity(tokens_a,tokens_b):
    """Unbiased cross-split variation; common noise within each split is allowed."""
    a=pad_after_eos(tokens_a);b=pad_after_eos(tokens_b)
    assert a.ndim==b.ndim==3 and a.shape[0]==b.shape[0] and a.shape[2]==b.shape[2]
    k=a.shape[0]
    if k<2:return None
    # Entry (j,l) estimates <mu_j^A,mu_l^B>. No vocabulary-sized vector.
    cross=np.empty((k,k),dtype=float)
    for j in range(k):
        for l in range(k):
            cross[j,l]=(a[j,:,None,:]==b[l,None,:,:]).mean()
    return float((np.trace(cross)-cross.sum()/k)/(k-1))


def aggregate_distribution(records,bootstrap=5000,seed=490001):
    # Reuse the existing clustered estimator with source documents as clusters.
    rows=[dict(graph_id=r['source_id'],h=r['h_token'],g=0.) for r in records]
    measured=aggregate(rows,bootstrap=bootstrap,seed=seed)
    return dict(sources=measured['graphs'],roots=measured['roots'],
                measured_roots=measured.get('heterogeneity_roots',0),h_token=measured['h'])
