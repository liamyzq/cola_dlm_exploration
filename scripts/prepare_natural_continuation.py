"""Document-disjoint natural passage prefixes, with no question or target answer."""
import argparse
import json
import random
import re
from pathlib import Path
from tokenizers import Tokenizer


def prepare(a):
    tok=Tokenizer.from_file(a.tokenizer)
    data=json.loads(Path(a.source).read_text())['data']
    documents=sorted(data,key=lambda x:x['title'])
    assert len({x['title'] for x in documents})==len(documents)
    random.Random(830202).shuffle(documents)
    records=[];excluded=[]
    for rank,document in enumerate(documents):
        target=128+rank%113
        chosen=None
        for paragraph_index,paragraph in enumerate(document['paragraphs']):
            context=paragraph['context']
            if len(tok.encode(context).ids)<target:continue
            for match in re.finditer(r'\S+(?=\s|$)',context):
                prefix=context[:match.end()];n=len(tok.encode(prefix).ids)
                if n>=target:
                    if n<=256:
                        chosen=dict(source_id=document['title'],paragraph_index=paragraph_index,
                                    prompt=prefix,prompt_tokens=n,prompt_remainder=n%16)
                    break
            if chosen is not None:break
        if chosen is None:excluded.append(document['title'])
        else:records.append(chosen)
    assert len(records)>=256, 'Insufficient source documents for the fixed development/confirmation split'
    out=Path(a.output);out.mkdir(parents=True,exist_ok=False)
    for split,rows in [('development',records[:128]),('confirmation',records[128:256])]:
        for index,row in enumerate(rows):row.update(root_id=index,split=split)
        with (out/f'{split}.jsonl').open('w') as f:
            for row in rows:f.write(json.dumps(row)+'\n')
    assert not {x['source_id'] for x in records[:128]} & {x['source_id'] for x in records[128:256]}
    manifest=dict(source=str(Path(a.source).resolve()),source_metadata=json.loads(Path(a.source).with_name('source.json').read_text()),
        purpose='Natural continuation for same-text F/M studies; no QA supervision or training',
        selection='Seed 830202 shuffles sorted article titles; first paragraph reaching target 128+rank%113, cut at first word boundary reaching target, max256 tokens',
        original_documents=len(documents),eligible_documents=len(records),excluded_documents=excluded,
        development_sources=[x['source_id'] for x in records[:128]],confirmation_sources=[x['source_id'] for x in records[128:256]],
        prompt_tokens_range=[min(x['prompt_tokens'] for x in records[:256]),max(x['prompt_tokens'] for x in records[:256])])
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:manifest[k] for k in ['original_documents','eligible_documents','prompt_tokens_range']}))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--tokenizer',required=True);p.add_argument('--output',required=True)
    prepare(p.parse_args())
