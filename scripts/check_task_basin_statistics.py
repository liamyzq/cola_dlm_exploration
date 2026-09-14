"""Check role-swap estimands against discriminating constructed world outcomes."""
from scripts.analyze_task_basin import effects, calibration


def run():
    rows=[]
    # Both question conditions have identical overall error counts while each
    # queried field is always protected: P must be +1, not zero.
    for domain in ('number','entity'):
        for world in range(4):
            for q in (0,1):
                statuses=['valid_wrong','valid_wrong'];statuses[q]='correct'
                rows.append(dict(world_id=f'{domain}-{world}',query=q,domain=domain,template=world,
                    paired_clean=True,sigma=.2,kind='noise',seed_id=0,status=statuses,
                    any_fact_changed=True,token_disagreement=.1,word_edit_distance=.1))
    result=effects(rows,'noise')[0]['estimates']['protection']
    assert result['mean']==1.,result
    # Identical input scored under two role labels must cancel within world.
    for r in rows:r['status']=['correct','valid_wrong']
    assert effects(rows,'noise')[0]['estimates']['protection']['mean']==0.
    # Real residual protects critical only; rotations damage both: selective=1.
    recovery=[]
    for r in rows:
        real=dict(r,noise_fraction=.25,kind='real');real['status']=['valid_wrong','valid_wrong'];real['status'][r['query']]='correct'
        recovery.append(real)
        recovery.extend(dict(r,noise_fraction=.25,kind='rotated',rotation_id=i,status=['valid_wrong','valid_wrong']) for i in range(4))
    est=effects(recovery,'recovery')[0]['estimates']
    assert est['G_selective']['mean']==1.
    assert est['G_selective_valid_wrong']['mean']==1.
    assert est['G_selective_unparseable']['mean']==0.
    # Domain macro remains equally weighted under unequal retained coverage.
    duplicated=[dict(r,world_id='extra-'+r['world_id']) for r in rows if r['domain']=='number']
    for r in rows:r['status']=['valid_wrong','valid_wrong'] if r['domain']=='entity' else (['correct','valid_wrong'] if r['query']==0 else ['valid_wrong','correct'])
    for r in duplicated:r['status']=['correct','valid_wrong'] if r['query']==0 else ['valid_wrong','correct']
    assert effects(rows+duplicated,'noise')[0]['estimates']['protection']['mean']==.5
    c=calibration(rows,'noise');assert c['chosen_point']==.2 and c['role_effects_used_for_selection'] is False
    print('PASS: paired role contrast, identical-input null, selective rotation contrast, domain macro, lexical-only calibration.')

if __name__=='__main__':run()
