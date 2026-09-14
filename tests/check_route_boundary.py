"""Use the official tokenizer to detect false exclusions of valid route prefixes."""
import os
from pathlib import Path
from tokenizers import Tokenizer
from src.tasks.routes import generate_tasks, eligible, intervention_boundary


def main():
    tokenizer=Tokenizer.from_file(str(Path(os.environ['COLA_CHECKPOINT'])/'tokenizer.json'))
    tasks=generate_tasks(16,510001,'easy')
    valid=0
    for task in tasks:
        prompt_len=len(tokenizer.encode(task['prompt']).ids)
        boundary,_=intervention_boundary(task,tokenizer,prompt_len)
        if boundary is None:
            continue
        canonical=tokenizer.encode(' '+' -> '.join(task['trunk'])).ids
        ok,_,_=eligible(task,tokenizer,prompt_len,canonical)
        assert ok
        # A leading newline is a valid prefix layout. Previously this failed
        # merely because its IDs differed from the demonstration's leading space.
        alternate=tokenizer.encode('\n '+' -> '.join(task['trunk'])).ids
        assert eligible(task,tokenizer,prompt_len,alternate)[0]
        wrong=tokenizer.encode(' QQQ '+' -> '.join(task['trunk'])).ids
        assert not eligible(task,tokenizer,prompt_len,wrong)[0]
        valid+=1
    assert valid>0
    print(f'PASS: {valid} tokenizer-based boundaries accept valid layouts and reject malformed trunks.')

if __name__=='__main__':
    main()
