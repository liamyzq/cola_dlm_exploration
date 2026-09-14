"""Frozen synthetic role-swap worlds and output-only field scoring for idea 002."""
import argparse
from collections import Counter
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import random
import re

NAMES = '''Alice Bob Carol David Emma Frank Grace Henry Irene Jack Karen Leo Maria Nathan Olivia Peter Quinn Rachel Simon Tina Uma Victor Wendy Xavier Yara Zoe Adam Bella Caleb Diana Ethan Fiona Gavin Hannah Isaac Julia Kevin Laura Mason Nora Owen Paula Riley Sarah Thomas Vera Walter Yasmin Aaron Clara Daniel Elena Felix Hazel Jacob Linda Marcus Naomi Oscar Rose Samuel Teresa Vincent Will'''.split()
KEYS = [('red','blue'), ('east','west'), ('north','south'), ('gold','silver')]
NUMBER = [
 ('The {k} team scored {v} points.', 'How many points did the {k} team score?'),
 ('The {k} box contains {v} balls.', 'How many balls are in the {k} box?'),
 ('There are {v} books on the {k} shelf.', 'How many books are on the {k} shelf?'),
 ('The {k} group collected {v} stamps.', 'How many stamps did the {k} group collect?'),
 ('The {k} team finished with {v} points.', "What was the {k} team's final score?"),
 ('The {k} box holds {v} balls.', 'What is the number of balls in the {k} box?'),
 ('The book count for the {k} shelf is {v}.', 'What is the book count on the {k} shelf?'),
 ("The {k} group's stamp collection totals {v}.", "What is the size of the {k} group's stamp collection?")]
ENTITY = [
 ('{v} captains the {k} team.', 'Who captains the {k} team?'),
 ('{v} leads the {k} group.', 'Who leads the {k} group?'),
 ('{v} manages the {k} branch.', 'Who manages the {k} branch?'),
 ('{v} represents the {k} team.', 'Who represents the {k} team?'),
 ('The captain of the {k} team is {v}.', "Who is the {k} team's captain?"),
 ('The leader of the {k} group is {v}.', "Who is the {k} group's leader?"),
 ('The manager of the {k} branch is {v}.', "Who is the {k} branch's manager?"),
 ('The representative of the {k} team is {v}.', "Who is the {k} team's representative?")]


def text_parts(world, query, variant='record', edit=None):
    vals = list(world['values'])
    if edit is not None:
        vals[edit] = world['alternatives'][edit]
    family = (NUMBER if world['domain']=='number' else ENTITY)[world['template']]
    source = ' '.join(family[0].format(k=world['keys'][i],v=world['values'][i]) for i in world['source_order'])
    question = family[1].format(k=world['keys'][query])
    if variant == 'sentence':
        answer = ' '.join(family[0].format(k=world['keys'][i],v=vals[i]) for i in world['answer_order'])
    else:
        answer = '; '.join(f"{world['keys'][i].capitalize()}: {vals[i]}" for i in world['answer_order']) + '.'
    if variant == 'no_query':
        prefix = f'Context:\n{source}\nRecord:\n'
    elif variant == 'query_only':
        prefix = f'Question: {question}\nRecord:\n'
    else:
        prefix = f'Context:\n{source}\nQuestion: {question}\nRecord:\n'
    return prefix, answer


def token_layout(tokenizer, world, query, variant='record'):
    prefix, answer = text_parts(world,query,variant)
    enc = tokenizer.encode(prefix+answer)
    p = len(tokenizer.encode(prefix).ids)
    if enc.ids[:p] != tokenizer.encode(prefix).ids:
        raise ValueError('prefix_token_boundary')
    if len(enc.ids)>256 or len(enc.ids)-p>32:
        raise ValueError('length_limit')
    targets, spans = [], []
    for field in (0,1):
        _, target = text_parts(world,query,variant,field)
        alt = tokenizer.encode(prefix+target)
        diff = [i for i,(a,b) in enumerate(zip(enc.ids,alt.ids)) if a!=b]
        if not diff or diff[0]<p or (variant!='sentence' and (len(alt.ids)!=len(enc.ids) or len(diff)!=1)):
            raise ValueError('not_single_token_edit')
        # Locate the value in the answer using its keyed field or source clause.
        if variant=='sentence':
            family=(NUMBER if world['domain']=='number' else ENTITY)[world['template']]
            clause=family[0].format(k=world['keys'][field],v=world['values'][field])
            start=answer.index(clause)+clause.index(world['values'][field])
        else:
            marker=world['keys'][field].capitalize()+': '
            start=answer.index(marker)+len(marker)
        lo,hi=enc.offsets[diff[0]]
        a,b=len(prefix)+start,len(prefix)+start+len(world['values'][field])
        if not (lo<b and hi>a):
            raise ValueError('edit_outside_value')
        targets.append(alt.ids[p:]); spans.append(diff[0]-p)
    # Fixed trailer, truncated only beyond the scored answer to its last DiT block.
    end = ((len(enc.ids)+15)//16)*16
    trailer = enc.ids + tokenizer.encode('\nEnd of record.'*16).ids
    return dict(prefix=prefix,answer=answer,prefix_ids=enc.ids[:p],answer_ids=enc.ids[p:],
                target_ids=targets,field_positions=spans,offsets=enc.offsets,
                full_ids=trailer[:end],prefix_length=p,answer_length=len(enc.ids)-p)


def build_worlds(tokenizer):
    rng=random.Random(20260914)
    worlds=[]; used=set(); excluded=Counter(); examined=Counter()
    for split,count,families in [('smoke',2,range(4)),('dev',8,range(4)),('test',32,range(4,8))]:
        for domain in ('number','entity'):
            for family in families:
                for slot in range(count):
                    order=slot%4
                    near=(slot//4)%2==0
                    for attempt in range(10000):
                        examined[f'{split}/{domain}/{family}']+=1
                        if domain=='entity':
                            vals=rng.sample(NAMES,4)
                        else:
                            orig=rng.sample(range(3,99),2)
                            if near:
                                alt=[v+rng.choice([-1,1]) for v in orig]
                            else:
                                alt=[rng.choice([u for u in range(3,99) if len(str(u))==len(str(v)) and abs(u-v)>=3]) for v in orig]
                            if min(alt)<3 or max(alt)>98 or len(set(orig+alt))!=4:
                                excluded['numeric_constraints']+=1; continue
                            vals=list(map(str,orig+alt))
                        identity=(domain,*vals)
                        if identity in used:
                            excluded['repeated_fact_tuple']+=1; continue
                        world=dict(world_id=f'{split}-{domain}-{family}-{slot:02}',index=len(worlds),
                            split=split,domain=domain,template=family,slot=slot,seed=20260914,
                            keys=list(KEYS[(slot+family)%4]),values=vals[:2],alternatives=vals[2:],
                            source_order=[1,0] if order//2 else [0,1],
                            answer_order=[1,0] if order%2 else [0,1],
                            edit_class=('adjacent' if near else 'nonadjacent') if domain=='number' else 'name',
                            boundary=split=='test' and slot<16,controls=split=='test' and slot<8)
                        try:
                            layouts=[token_layout(tokenizer,world,q) for q in (0,1)]
                            if layouts[0]['prefix_length']!=layouts[1]['prefix_length']:
                                raise ValueError('query_prefix_length')
                            if layouts[0]['answer_ids']!=layouts[1]['answer_ids']:
                                raise ValueError('query_answer_ids')
                        except ValueError as exc:
                            excluded[str(exc)]+=1; continue
                        world['layouts']=layouts
                        used.add(identity); worlds.append(world); break
                    else:
                        raise RuntimeError(f'Insufficient tokenizer-eligible candidates: {split}/{domain}/{family}/{slot}')
    return worlds,dict(excluded=excluded,examined=examined,counts=Counter(w['split'] for w in worlds),
                       eligible_names=sorted({v for w in worlds if w['domain']=='entity' for v in w['values']+w['alternatives']}))


def normalize(value,domain):
    value=value.strip().strip('"\'').strip()
    if value.endswith('.'):
        value=value[:-1].rstrip()
    if domain=='number':
        if not re.fullmatch(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)',value):
            return None
        try:
            return str(Decimal(value).normalize())
        except InvalidOperation:
            return None
    value=' '.join(value.strip('.,!?"\'()[]').split()).casefold()
    return value if re.fullmatch(r"[a-z]+(?:[ '\-][a-z]+)*",value) else None


def parse_record(text,keys,domain):
    values={k:[] for k in keys}
    invalid=set()
    key_pattern='|'.join(re.escape(k) for k in keys)
    for segment in re.split(r'[;\n]',text):
        segment=segment.strip()
        if not segment:
            continue
        match=re.fullmatch(rf'({key_pattern})\s*[:=]\s*(.*?)\s*',segment,re.I)
        if match:
            key=match.group(1).casefold(); value=normalize(match.group(2),domain)
            if value is None or re.search(r'\b(?:not|no|never)\b',match.group(2),re.I):
                invalid.add(key)
            else:
                values[key].append(value)
        else:
            # An unregistered sentence cannot silently affirm a mentioned field.
            for key in keys:
                if re.search(rf'\b{re.escape(key)}\b',segment,re.I):
                    invalid.add(key)
    return {k:None if k in invalid or len(set(values[k]))!=1 else values[k][0] for k in keys},any(len(v)>1 for v in values.values())


def edit_distance(a,b):
    row=list(range(len(b)+1))
    for i,x in enumerate(a):
        new=[i+1]
        for j,y in enumerate(b):
            new.append(min(new[-1]+1,row[j+1]+1,row[j]+(x!=y)))
        row=new
    return row[-1]


def parse_sentence(text,world):
    template=(NUMBER if world['domain']=='number' else ENTITY)[world['template']][0]
    values={k:[] for k in world['keys']}; invalid=set()
    for clause in re.split(r'(?<=\.)\s+',text.strip()):
        matched=False
        for key in world['keys']:
            pattern=re.escape(template.format(k=key,v='VALUE')).replace('VALUE',r'(.+?)')
            match=re.fullmatch(pattern,clause,re.I)
            if match:
                value=normalize(match.group(1),world['domain']); matched=True
                if value is None: invalid.add(key)
                else: values[key].append(value)
        if not matched:
            for key in world['keys']:
                if re.search(rf'\b{key}\b',clause,re.I): invalid.add(key)
    return {k:None if k in invalid or len(set(values[k]))!=1 else values[k][0] for k in values},any(len(v)>1 for v in values.values())


def score_output(world,layout,ids,text):
    if world.get('variant')=='sentence':
        parsed,repeat=parse_sentence(text,world)
    else:
        parsed,repeat=parse_record(text,world['keys'],world['domain'])
    status=['unparseable' if parsed[k] is None else 'correct' if parsed[k]==normalize(v,world['domain']) else 'valid_wrong'
            for k,v in zip(world['keys'],world['values'])]
    return dict(status=status,repetition=repeat,parsed=parsed,
        token_disagreement=sum(a!=b for a,b in zip(ids,layout['answer_ids']))/len(layout['answer_ids']),
        word_edit_distance=edit_distance(layout['answer'].split(),text.split())/max(1,len(layout['answer'].split())),
        exact_target=[ids==t for t in layout['target_ids']],
        any_fact_changed=any(s!='correct' for s in status))


def named_seed(world,phase,seed,extra=0):
    # Fixed arithmetic namespaces, independent of worker/query/batch ordering.
    return 20260914 + world['index']*1000000 + phase*10000 + seed*100 + extra


def main():
    from tokenizers import Tokenizer
    p=argparse.ArgumentParser(); p.add_argument('--tokenizer',required=True); p.add_argument('--output',required=True)
    args=p.parse_args(); out=Path(args.output); out.mkdir(parents=True,exist_ok=True)
    worlds,audit=build_worlds(Tokenizer.from_file(args.tokenizer))
    (out/'worlds.jsonl').write_text(''.join(json.dumps(w)+'\n' for w in worlds))
    (out/'tokenizer_audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps(audit))

if __name__=='__main__':
    main()
