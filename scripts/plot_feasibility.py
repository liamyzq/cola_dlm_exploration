"""Plot observed native-state feasibility; no future effects enter these figures."""
import argparse,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def main(repo):
    res=repo/'experiments/001_same_prefix_state/results';eta=json.loads((res/'r3_eta_v1.json').read_text());collection=json.loads((res/'r3_collection_v1.json').read_text())
    colors={'F':'#245b9f','M':'#c06626'};fig,axes=plt.subplots(2,2,figsize=(11,7.6),layout='constrained')
    levels=[.01,.03,.1,.3];x=np.arange(4)
    for offset,cohort in [(-.18,'F'),(.18,'M')]:
        vals=[eta[cohort]['arms'][str(e)]['paired_roots'] for e in levels]
        bars=axes[0,0].bar(x+offset,vals,width=.34,color=colors[cohort],label=cohort)
        axes[0,0].bar_label(bars,labels=[f'{v}/8' for v in vals],padding=3,fontsize=9)
    axes[0,0].set(xticks=x,xticklabels=[str(e) for e in levels],xlabel='Noise perturbation eta',ylabel='Paired roots',ylim=(0,8.3),title='A  Calibration: eight fixed roots per cohort');axes[0,0].legend(frameon=False)
    for offset,row in zip([-.18,.18],collection):
        vals=[row['attempted_roots'],row['live_roots'],row['paired_roots']]
        bars=axes[0,1].bar(np.arange(3)+offset,vals,width=.34,color=colors[row['cohort']],label=row['cohort']);axes[0,1].bar_label(bars,padding=3,fontsize=9)
    axes[0,1].set(xticks=np.arange(3),xticklabels=['Attempted','Live','Paired'],ylabel='Additional roots',ylim=(0,43),title='B  Ordered collection: stop at pair target')
    for row in collection:
        cohort=row['cohort'];data=[json.loads(s) for s in (Path(row['artifact_dir'])/'candidates/roots.jsonl').read_text().splitlines()]
        proposals=[p for root in data for arm in root['arms'] for p in arm['proposals'] if p['accepted']]
        axes[1,0].scatter([p['kl_sum'] for p in proposals],[p['dit_input_bf16_delta_norm'] for p in proposals],s=28,alpha=.8,color=colors[cohort],label=f'{cohort} ({len(proposals)})')
    axes[1,0].axvline(.01,color='#555555',ls='--',lw=1);axes[1,0].set(xscale='log',xlabel='Current-block symmetric KL (nats)',ylabel='BF16 DiT-input displacement (L2)',title='C  Accepted collection alternatives');axes[1,0].legend(frameon=False,fontsize=9)
    seconds=[(r['root_seconds']+r['proposal_arm_seconds'])/r['paired_roots'] for r in collection]
    bars=axes[1,1].bar(['F','M'],seconds,color=[colors['F'],colors['M']],width=.55);axes[1,1].bar_label(bars,labels=[f'{s:.1f} s' for s in seconds],padding=3)
    axes[1,1].set(ylabel='Worker-seconds / accepted pair',ylim=(0,max(seconds)*1.25),title='D  Root and proposal cost, including failures')
    for ax in axes.flat:
        ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
    fig.suptitle('Native same-text states are feasible under strict acceptance',fontsize=15)
    fig.supxlabel('Frozen CoLa checkpoint; exact IDs; KL sum <= 0.01, max position <= 0.0025.\nCollection coverage is descriptive. Cost excludes calibration and future rollouts.',fontsize=9)
    out=repo/'experiments/001_same_prefix_state/figures';out.mkdir(exist_ok=True)
    fig.savefig(out/'r3_feasibility.png',dpi=180);fig.savefig(out/'r3_feasibility.pdf');plt.close(fig)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repo',required=True);main(Path(p.parse_args().repo))
