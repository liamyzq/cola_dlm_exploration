"""Graph-clustered split-sample estimators for fixed candidate sets."""
import numpy as np


def root_statistics(reward_a,reward_b):
    a=np.asarray(reward_a,dtype=float).mean(axis=1)
    b=np.asarray(reward_b,dtype=float).mean(axis=1)
    assert len(a)==len(b) and len(a)>=1
    # Reference is index zero, so stable argmax implements reference-first ties.
    selected=int(np.argmax(a))
    h=float(np.dot(a-a.mean(),b-b.mean())/(len(a)-1)) if len(a)>1 else None
    return dict(h=h,g=float(b[selected]-b[0]),selected=selected,
                reference=float(b[0]),selected_value=float(b[selected]),candidates=len(a))


def aggregate(records,bootstrap=5000,seed=490001):
    """Resample graphs, preserving all roots of each graph as a cluster."""
    grouped={}
    for r in records:
        grouped.setdefault(r['graph_id'],[]).append(r)
    groups=list(grouped.values())
    if not groups:
        return dict(graphs=0,roots=0,h=None,g=None)
    def estimates(rows):
        hs=[r['h'] for r in rows if r['h'] is not None]
        return [float(np.mean(hs)) if hs else np.nan,float(np.mean([r['g'] for r in rows]))]
    point=estimates(records)
    rng=np.random.default_rng(seed)
    values=[]
    for _ in range(bootstrap):
        sample=[r for i in rng.integers(len(groups),size=len(groups)) for r in groups[i]]
        values.append(estimates(sample))
    values=np.asarray(values)
    result=dict(graphs=len(groups),roots=len(records),heterogeneity_roots=sum(r['h'] is not None for r in records))
    for col,name in enumerate(['h','g']):
        finite=values[:,col][np.isfinite(values[:,col])]
        result[name]=dict(mean=point[col],ci95=np.quantile(finite,[.025,.975]).tolist()) if len(finite) else None
    return result
