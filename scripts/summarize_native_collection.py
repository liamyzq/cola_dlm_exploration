"""Describe a terminal ordered candidate collection and its full proposal funnel."""
import argparse,json,statistics
from datetime import datetime
from pathlib import Path


def summarize(path):
    assert (path/'exit.txt').read_text().strip()=='0'
    cfg=json.loads((path/'candidates/config.json').read_text());launch=json.loads((path/'launch.json').read_text())
    rows=[json.loads(x) for x in (path/'candidates/roots.jsonl').read_text().splitlines()]
    assert [x['root_id'] for x in rows]==list(range(8,8+len(rows)))
    arms=[a for x in rows for a in x['arms']];proposals=[p for a in arms for p in a['proposals']];accepted=[p for p in proposals if p['accepted']]
    assert len(accepted)==cfg['pair_target'] or rows[-1]['root_id']==127
    assert len(accepted)<=cfg['pair_target']
    return dict(experiment=launch['experiment'],commit=launch['commit'],cohort=cfg['cohort'],eta=cfg['etas'][0],epsilon=cfg['epsilon'],attempted_roots=len(rows),live_roots=len(arms),paired_roots=len(accepted),last_root=rows[-1]['root_id'],calibration_pairs=cfg['calibration_pairs'],root_statuses={s:sum(x['root_status']==s for x in rows) for s in sorted({x['root_status'] for x in rows})},proposal_count=len(proposals),same_token_proposals=sum(p['same_tokens'] for p in proposals),same_token_kl_rejected=sum(p['same_tokens'] and (p['kl_sum']>.01 or p['kl_max']>.0025) for p in proposals),raw_duplicates=sum(p['duplicate'] for p in proposals),effective_duplicates=sum(p['effective_cache_duplicate'] is True for p in proposals),accepted_kl_sum_range=[min(p['kl_sum'] for p in accepted),max(p['kl_sum'] for p in accepted)] if accepted else None,accepted_kl_max=max((p['kl_max'] for p in accepted),default=None),accepted_kl_per_generated_position_range=[min(p['kl_sum']/p['free_positions'] for p in accepted),max(p['kl_sum']/p['free_positions'] for p in accepted)] if accepted else None,accepted_latent_delta_median=statistics.median(p['delta_norm'] for p in accepted) if accepted else None,accepted_bf16_delta_median=statistics.median(p['dit_input_bf16_delta_norm'] for p in accepted) if accepted else None,accepted_free_positions_histogram={str(k):sum(p['free_positions']==k for p in accepted) for k in sorted({p['free_positions'] for p in accepted})},root_seconds=sum(x['root_seconds'] for x in rows),proposal_arm_seconds=sum(a['elapsed_seconds'] for a in arms),wall_seconds=(path/'exit.txt').stat().st_mtime-datetime.fromisoformat(launch['recorded_at']).timestamp(),root_calls={k:sum(x['root_calls'][k] for x in rows) for k in rows[0]['root_calls']},proposal_calls={k:sum(a['calls'][k] for a in arms) for k in arms[0]['calls']},artifact_dir=str(path),coverage_interpretation='Descriptive under stop-at-target collection; calibration used a different proposal cap')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('runs',nargs='+');p.add_argument('--output',required=True);a=p.parse_args()
    results=[summarize(Path(x)) for x in a.runs];Path(a.output).write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2))
