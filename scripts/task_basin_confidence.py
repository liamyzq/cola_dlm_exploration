"""World-held-out predictive confidence control; no causal mediation claims."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GroupKFold
from scripts.analyze_task_basin import clustered, read_records


def main():
    p=argparse.ArgumentParser();p.add_argument('--inputs',nargs='+',required=True);p.add_argument('--sigma',type=float,required=True);p.add_argument('--output',required=True);p.add_argument('--worlds',required=True)
    a=p.parse_args();rows=read_records(a.inputs);anchors=read_records(a.inputs,'anchors.jsonl')
    worlds={w['world_id']:w for w in [json.loads(line) for line in Path(a.worlds).read_text().splitlines()]}
    confidence={(r['world_id'],r['query'],c['field']):c for r in anchors for c in r['confidence']}
    groups=defaultdict(list)
    for r in rows:
        if r['sigma']==a.sigma and r['paired_clean']:
            for field in (0,1):groups[(r['world_id'],r['query'],field)].append(r['status'][field]!='correct')
    meta={r['world_id']:r for r in rows}; examples=[]
    for (w,q,f),ys in sorted(groups.items()):
        c=confidence[w,q,f];m=meta[w]
        examples.append(dict(world_id=w,domain=m['domain'],template=m['template'],rate=float(np.mean(ys)),n=len(ys),
            x=[str(c['original_id']),str(c['alternative_id']),str(f),m['domain'],str(m['template']),str(worlds[w]['source_order']),str(worlds[w]['answer_order']),c['position'],c['gap'],c['entropy'],int(q==f)]))
    x=np.array([r['x'] for r in examples],dtype=object);y=np.array([r['rate'] for r in examples]);ns=np.array([r['n'] for r in examples])
    world_ids=np.array([r['world_id'] for r in examples]);splits=list(GroupKFold(4).split(x,y,world_ids));predictions={};coefs=[]
    for name,cols in [('confidence',list(range(10))),('confidence_plus_role',list(range(11)))]:
        pred=np.zeros(len(y))
        for train,test in splits:
            # Aggregate Bernoulli counts into weighted positive/negative examples.
            xx=np.repeat(x[train][:,cols],2,axis=0); yy=np.tile([0,1],len(train)); weights=np.stack([ns[train]*(1-y[train]),ns[train]*y[train]],-1).reshape(-1)
            keep=weights>0
            if len(np.unique(yy[keep]))<2:
                pred[test]=np.average(y[train],weights=ns[train]);continue
            cat=list(range(7));num=list(range(7,len(cols)))
            transform=ColumnTransformer([('tokens',OneHotEncoder(handle_unknown='ignore'),cat),('numeric',StandardScaler(),num)])
            fit=make_pipeline(transform,LogisticRegression(C=1.,max_iter=2000))
            fit.fit(xx[keep],yy[keep],logisticregression__sample_weight=weights[keep])
            pred[test]=fit.predict_proba(x[test][:,cols])[:,1]
            if name=='confidence_plus_role':coefs.append(float(fit[-1].coef_[0,-1]))
        predictions[name]=pred
    scores={}
    for name,pred in predictions.items():
        pp=np.clip(pred,1e-7,1-1e-7)
        scores[name]=dict(log_loss=-y*np.log(pp)-(1-y)*np.log1p(-pp),brier=y*(1-pred)**2+(1-y)*pred**2)
    improvements={}
    for metric in ('log_loss','brier'):
        gains=scores['confidence'][metric]-scores['confidence_plus_role'][metric]
        grouped=defaultdict(list)
        for r,g in zip(examples,gains):grouped[r['world_id']].append(float(g))
        wr=[dict(world_id=w,domain=meta[w]['domain'],template=meta[w]['template'],value=float(np.mean(v))) for w,v in grouped.items()]
        improvements[metric]=clustered(wr)
    result=dict(protocol='fixed C=1 regularized logistic; four world-grouped folds; probability score increments, not causal mediation',
        clean_gap_quantiles_by_role={str(role):np.quantile([float(r['x'][-3]) for r in examples if r['x'][-1]==role],[0,.25,.5,.75,1]).tolist() for role in (0,1)},
        field_query_rows=len(examples),worlds=len(set(world_ids)),role_coefficients=coefs,
        mean_scores={name:{metric:float(np.mean(v)) for metric,v in d.items()} for name,d in scores.items()},
        role_increment=improvements)
    Path(a.output).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

if __name__=='__main__':main()
