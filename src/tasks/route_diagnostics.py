"""Causal route-prefix diagnostics, separate from the historical P0 scorer."""
import re


def terminated(text):
    """The declared answer ends at the first newline after nonempty output, or EOS."""
    body=text.lstrip()
    return bool(body and ('\n' in body or '<|endoftext|>' in body or '<|im_end|>' in body))


def trunk_prefix_status(task, text):
    if terminated(text):
        return 'terminated'
    remaining=text.lstrip()
    if not remaining:
        return 'empty'
    for index,town in enumerate(task['trunk']):
        if town.startswith(remaining):
            return 'eligible'
        if not remaining.startswith(town):
            return 'wrong_trunk'
        remaining=remaining[len(town):].lstrip(' \t')
        if not remaining:
            return 'eligible'
        if remaining == '-':
            return 'eligible'
        match=re.match(r'(?:->|→|,)[ \t]*',remaining)
        if not match:
            return 'wrong_trunk'
        remaining=remaining[match.end():]
        if not remaining:
            return 'eligible'
        if index == len(task['trunk'])-1:
            return 'branch_already_crossed'
    return 'wrong_trunk'


def boundary_funnel(task, tokenizer, prompt_tokens, ids):
    trim=prompt_tokens%16
    first=16-trim if trim else 16
    mixed=None
    if trim and len(ids)>=first:
        mixed=dict(boundary=first,free_positions=first,
                   status=trunk_prefix_status(task,tokenizer.decode(ids[:first],skip_special_tokens=False)))
    full=[]
    for n in range(first+(16 if trim else 0),len(ids)+1,16):
        status=trunk_prefix_status(task,tokenizer.decode(ids[:n],skip_special_tokens=False))
        full.append(dict(boundary=n,free_positions=16,status=status))
        # A completed wrong or terminated prefix cannot become a legal trunk
        # by inspecting later text; no future-dependent recovery is allowed.
        if status in ('terminated','wrong_trunk','branch_already_crossed'):
            break
        if status=='eligible':
            break
    return mixed,full


def answer_diagnostics(task, tokenizer, ids):
    text=tokenizer.decode(ids,skip_special_tokens=False)
    termination=None
    for n in range(1,len(ids)+1):
        if terminated(tokenizer.decode(ids[:n],skip_special_tokens=False)):
            termination=n
            break
    line=text.strip().split('\n')[0]
    line=re.split(r'<\|(?:endoftext|im_end)\|>',line,maxsplit=1)[0].strip().removesuffix('.')
    towns=re.split(r'\s*(?:->|→|,)\s*',line)
    roads={tuple(e) for e in task['roads']}
    legal=0
    if towns and towns[0]==task['start']:
        legal=1
        for a,b in zip(towns,towns[1:]):
            if (a,b) not in roads or b in towns[:legal]:
                break
            legal+=1
    return dict(termination_token=termination,
                terminated_legal_trunk=bool(termination is not None and trunk_prefix_status(task,line)=="eligible"),
                generated_tokens_after_termination=0 if termination is None else len(ids)-termination,
                first_edge_correct=bool(len(towns)>=2 and towns[0]==task['start'] and tuple(towns[:2]) in roads),
                legal_prefix_towns=legal)
