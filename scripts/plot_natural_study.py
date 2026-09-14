"""Plot the fixed F pilot and independent confirmation without pooling them."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path('experiments/001_same_prefix_state')
pilot = json.loads((ROOT / 'results/r4_pilot_f_v1.json').read_text())
confirmation = json.loads((ROOT / 'results/r4_confirmation_f_v1.json').read_text())
plt.rcParams.update({'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False})
fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), gridspec_kw={'width_ratios': [1.25, 1]})
ax = axes[0]
for y, (label, row, color) in enumerate([('Development pilot', pilot, '#687b8c'), ('Independent confirmation', confirmation, '#146a86')]):
    h = row['h_token'];mean = h['mean'] * 10000
    low, high = np.array(h['ci95']) * 10000
    ax.errorbar(mean, y, xerr=[[mean - low], [high - mean]], fmt='o', color=color, capsize=5, markersize=7)
    ax.annotate(f"{row['paired_roots']} accepted pairs", (mean, y), xytext=(0, 17), textcoords='offset points', ha='center', fontsize=10)
ax.axvline(0, color='#aab1b6', linestyle='--', linewidth=1)
ax.set_yticks([0, 1], ['Development pilot', 'Independent confirmation'])
ax.set_ylim(-.5, 1.55)
ax.set_xlabel(r'$H_{token}$ ($10^{-4}$); 95% source bootstrap interval')
ax.set_title('Declared distribution endpoint', loc='left', fontweight='bold')
ax = axes[1]
counts = [confirmation['attempted_roots'], confirmation['root_statuses'].get('live', 0), confirmation['paired_roots']]
ax.bar(['Attempted', 'Live', 'Paired'], counts, color=['#bccbd3', '#6d98aa', '#146a86'], width=.58)
for i, value in enumerate(counts):ax.text(i, value + 2, str(value), ha='center')
ax.set_ylim(0, max(counts) * 1.18)
ax.set_ylabel('Fixed confirmation sources')
ax.set_title('Native-candidate coverage', loc='left', fontweight='bold')
fig.suptitle('Same-text F states: feasibility and future-distribution evidence', x=.05, ha='left', fontsize=14, fontweight='bold')
fig.text(.05, .025, 'Eta 0.03; raw block KL <= 0.01; 32 future tokens. Failed roots remain in coverage; H is conditional on pairs.', fontsize=9)
fig.tight_layout(rect=[.015, .07, .995, .91])
for extension in ('png', 'pdf'):fig.savefig(ROOT / f'figures/r4_distribution.{extension}', dpi=200)
