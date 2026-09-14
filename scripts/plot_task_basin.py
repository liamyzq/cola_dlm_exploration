"""Presentation-only rendering of the frozen task-basin summary artifacts."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def intervals(ax,points,rows,key,xlabel):
    y=np.array([r['estimates'][key]['mean'] for r in rows])*100
    bounds=np.array([r['estimates'][key]['ci95'] for r in rows])*100
    ax.errorbar(points,y,yerr=np.array([y-bounds[:,0],bounds[:,1]-y]),fmt='o-',capsize=4)
    ax.axhline(0,color='0.4',linewidth=1,linestyle='--');ax.set_xlabel(xlabel);ax.set_ylabel('Role difference (percentage points)')


def save(fig,out,name):
    fig.savefig(out/(name+'.pdf'));fig.savefig(out/(name+'.png'),dpi=200);plt.close(fig)


def main():
    p=argparse.ArgumentParser();p.add_argument('--noise',required=True);p.add_argument('--recovery');p.add_argument('--search');p.add_argument('--geometry');p.add_argument('--output',required=True)
    args=p.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':16,'axes.labelsize':18,'xtick.labelsize':16,'ytick.labelsize':16,'legend.fontsize':16,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
    rows=json.loads(Path(args.noise).read_text());points=[r['point'] for r in rows]
    fig,ax=plt.subplots(1,2,figsize=(15,5.5),layout='constrained')
    for key,label in [('queried_damage','Critical field'),('nonqueried_damage','Noncritical field')]:
        ax[0].plot(points,[r['descriptive']['paired_clean/noise'][key]*100 for r in rows],'o-',label=label)
    ax[0].set(xlabel='Noise standard deviation',ylabel='Field damage (%)');ax[0].legend()
    intervals(ax[1],points,rows,'protection','Noise standard deviation')
    for a in ax:a.set_xscale('log',base=2);a.set_xticks(points,labels=[str(x) for x in points])
    save(fig,out,'h1_noise_protection')
    fig,ax=plt.subplots(figsize=(8,5.5),layout='constrained')
    for key,label in [('valid_wrong','Valid wrong value'),('unparseable','Unparseable field')]:
        ax.plot(points,[r['descriptive']['paired_clean/noise'][key]*100 for r in rows],'o-',label=label)
    ax.set(xlabel='Noise standard deviation',ylabel='Field outcome (%)');ax.set_xscale('log',base=2);ax.set_xticks(points,labels=[str(x) for x in points]);ax.legend()
    save(fig,out,'h1_error_types')
    if args.recovery:
        rows=json.loads(Path(args.recovery).read_text());points=[r['point'] for r in rows]
        fig,ax=plt.subplots(1,2,figsize=(15,5.5),layout='constrained')
        for kind,label,style in [('real','Real residual','o-'),('rotated','Rotated residual','s--')]:
            ax[0].plot(points,[r['descriptive']['paired_clean/'+kind]['queried_damage']*100 for r in rows],style,label=label)
        ax[0].set(xlabel='Restart noise fraction',ylabel='Critical-field damage (%)');ax[0].legend()
        intervals(ax[1],points,rows,'G_selective','Restart noise fraction')
        save(fig,out,'h2_residual_direction')
    if args.search:
        data=json.loads(Path(args.search).read_text());fig,axes=plt.subplots(1,2,figsize=(15,5.5),layout='constrained')
        for ax,mode in zip(axes,['ray','combined']):
            rows=[r for r in data['curves'] if r['mode']==mode and r['population']=='paired_clean'];x=[r['radius'] for r in rows]
            for key,label in [('critical_success','Critical target'),('noncritical_success','Noncritical target')]:
                ax.plot(x,[r[key]*100 for r in rows],'o-',label=label)
            ax.set(xlabel='RMS radius',ylabel='Exact-target search success (%)');ax.legend(title='Ray only' if mode=='ray' else 'Combined search')
        save(fig,out,'h1_fixed_search')

    if args.geometry:
        data=json.loads(Path(args.geometry).read_text())
        fig,axes=plt.subplots(1,2,figsize=(15,5.5),layout='constrained')
        for ax,outcome in zip(axes,['valid_wrong','damage']):
            for name,label in [('baseline','Confidence + residual size'),('geometry','With geometry features')]:
                bins=data['outcomes'][outcome]['scores'][name]['calibration']
                ax.plot([r['predicted'] for r in bins],[r['observed'] for r in bins],'o-',label=label)
            ax.plot([0,1],[0,1],linestyle='--',color='0.5',linewidth=1)
            ax.set(xlabel='Predicted probability',ylabel='Observed field-error fraction',xlim=(0,1),ylim=(0,1))
            ax.legend(title='Valid wrong value' if outcome=='valid_wrong' else 'Total field damage',loc='upper left')
        save(fig,out,'geometry_prediction_calibration')

if __name__=='__main__':main()
