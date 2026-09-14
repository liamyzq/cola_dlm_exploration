"""Separate route capability and native-prefix availability in the R2 diagnostic."""
import argparse,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def main(repo):
    base=repo/'experiments/001_same_prefix_state';res=base/'results'
    rows=json.loads((res/'r2_first_three_v1.json').read_text())+json.loads((res/'r2_matched_full_v1.json').read_text())
    names=['Copy','Chain','Branch','Matched-full'];x=np.arange(4)
    fig,axes=plt.subplots(1,2,figsize=(11,4.3),layout='constrained')
    for offset,field,label,color in [(-.18,'first_edge_correct','First edge correct','#6c7a89'),(.18,'reward','Complete success','#54885a')]:
        vals=[r[field]['count'] for r in rows];bars=axes[0].bar(x+offset,vals,width=.34,label=label,color=color);axes[0].bar_label(bars,labels=[f'{v}/64' for v in vals],padding=3,fontsize=8)
    for offset,field,label,color in [(-.18,'eligible_full','F: full generated block','#245b9f'),(.18,'eligible_mixed','M: first mixed block','#c06626')]:
        vals=[r[field] for r in rows];bars=axes[1].bar(x+offset,vals,width=.34,label=label,color=color);axes[1].bar_label(bars,labels=[f'{v}/64' for v in vals],padding=3,fontsize=8)
    for ax,title in zip(axes,['A  Starting correctly rarely yields a complete route','B  Eligible prefixes are not accepted state pairs']):
        ax.set(xticks=x,xticklabels=names,ylabel='Generations',ylim=(0,75),title=title);ax.spines[['top','right']].set_visible(False);ax.legend(frameon=False,fontsize=8,loc='upper right');ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
    fig.suptitle('R2: bounded task-capability diagnosis',fontsize=15)
    fig.supxlabel('64 generations per cell; one format-matched example; two-word town names; total allocated length <= 512.\nCopy is a format/length control. These task variants change multiple requirements.',fontsize=9)
    out=base/'figures';fig.savefig(out/'r2_route_diagnosis.png',dpi=180);fig.savefig(out/'r2_route_diagnosis.pdf');plt.close(fig)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repo',required=True);main(Path(p.parse_args().repo))
