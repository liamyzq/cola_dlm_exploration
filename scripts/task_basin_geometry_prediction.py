"""Auxiliary held-out prediction after recovery, grouped strictly by world."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder,StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GroupKFold
from sklearn.metrics import roc_auc_score
from scripts.analyze_task_basin import clustered,read_records


def main():
    p=argparse.ArgumentParser();p.add_argument('--recovery',nargs='+',required=True);p.add_argument('--search',nargs='+',required=True)
    p.add_argument('--features',required=True);p.add_argument('--sigma',type=float,required=True);p.add_argument('--output',required=True)
    a=p.parse_args();search={(r['world_id'],r['query'],r['field']):r for r in read_records(a.search,'search_summary.jsonl')}
    features={(r['world_id'],r['query'],r['field']):r for r in [json.loads(line) for line in Path(a.features).read_text().splitlines()]}
    rows=[]
    for r in read_records(a.recovery):
        if r['kind']!='real' or not r['paired_clean']:continue
        for field in (0,1):
            key=r['world_id'],r['query'],field
            if key not in search:continue
            c=features[key];s=search[key];ray=s['ray_minimum_found_rms'];distance=s['minimum_found_rms']
            x=[r['domain'],str(field),str(c['original_id']),r['noise_fraction'],r['rms'],c['gap'],c['entropy'],c['position'],
               0. if ray is None else ray,int(ray is None),*[(int(distance is not None and distance<=k*a.sigma)) for k in (1,2,4)],c['gradient_frobenius']]
            rows.append(dict(world_id=r['world_id'],domain=r['domain'],template=r['template'],x=x,
                damage=int(r['status'][field]!='correct'),valid_wrong=int(r['status'][field]=='valid_wrong')))
    x=np.array([r['x'] for r in rows],dtype=object);groups=np.array([r['world_id'] for r in rows]);meta={r['world_id']:r for r in rows}
    result=dict(protocol='Post-recovery four-world-grouped-fold fixed-C=1 logistic prediction. Residual norm is not a pre-corruption feature.',worlds=len(meta),field_seed_rows=len(rows),outcomes={})
    for outcome in ['valid_wrong','damage']:
        y=np.array([r[outcome] for r in rows]);folds=list(GroupKFold(4).split(x,y,groups));preds={};fold_info=[]
        for name,cols in [('baseline',list(range(8))),('geometry',list(range(14)))]:
            prediction=np.full(len(y),np.nan)
            for f,(train,test) in enumerate(folds):
                if len(np.unique(y[train]))<2:
                    if name=='baseline':fold_info.append(dict(fold=f,train_positive=int(y[train].sum()),test_positive=int(y[test].sum()),estimable=False))
                    continue
                model=make_pipeline(ColumnTransformer([('category',OneHotEncoder(handle_unknown='ignore'),list(range(3))),('numeric',StandardScaler(),list(range(3,len(cols))))]),LogisticRegression(C=1.,max_iter=2000))
                model.fit(x[train][:,cols],y[train]);prediction[test]=model.predict_proba(x[test][:,cols])[:,1]
                if name=='baseline':fold_info.append(dict(fold=f,train_positive=int(y[train].sum()),test_positive=int(y[test].sum()),estimable=True))
            preds[name]=prediction
        valid=np.isfinite(preds['baseline'])&np.isfinite(preds['geometry']);scores={};increments={}
        for name,pr in preds.items():
            pp=np.clip(pr,1e-7,1-1e-7);scores[name]=dict(log_loss=-y*np.log(pp)-(1-y)*np.log1p(-pp),brier=(pr-y)**2)
        for metric in ('log_loss','brier'):
            gains=scores['baseline'][metric]-scores['geometry'][metric];grouped=defaultdict(list)
            for i in np.flatnonzero(valid):grouped[rows[i]['world_id']].append(float(gains[i]))
            wr=[dict(world_id=w,domain=meta[w]['domain'],template=meta[w]['template'],value=float(np.mean(v))) for w,v in grouped.items()]
            increments[metric]=clustered(wr)
        model_scores={}
        for name,pr in preds.items():
            calibration=[]
            for low in np.linspace(0,.9,10):
                bin_index=np.minimum((pr*10).astype(int),9)
                mask=valid&(bin_index==round(low*10))
                if mask.any():calibration.append(dict(lower=float(low),n=int(mask.sum()),predicted=float(pr[mask].mean()),observed=float(y[mask].mean())))
            model_scores[name]=dict(log_loss=float(np.mean(scores[name]['log_loss'][valid])) if valid.any() else None,
                brier=float(np.mean(scores[name]['brier'][valid])) if valid.any() else None,
                auroc=float(roc_auc_score(y[valid],pr[valid])) if valid.any() and len(np.unique(y[valid]))==2 else None,
                fold_auroc=[float(roc_auc_score(y[test],pr[test])) if np.isfinite(pr[test]).all() and len(np.unique(y[test]))==2 else None for train,test in folds],calibration=calibration)
        result['outcomes'][outcome]=dict(positive_rows=int(y.sum()),folds=fold_info,scored_rows=int(valid.sum()),scores=model_scores,geometry_increment=increments)
    Path(a.output).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

if __name__=='__main__':main()
