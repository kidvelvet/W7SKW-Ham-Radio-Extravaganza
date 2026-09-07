"""Merge a batch of explanations into build/explanations.json.

Usage:  python3 build/add_expl.py batch.json
Refuses to clobber an existing entry unless the batch sets "_overwrite": true.
Checks the 150-word cap and flags em/en dashes and common AI-vocabulary tells
before anything lands in the file.
"""
import json, pathlib, sys, re

TARGET = pathlib.Path('build/explanations.json')
AI_WORDS = ('crucial','delve','underscore','testament','vibrant','pivotal','showcase',
            'tapestry','foster','seamless','leverage','robust','intricate','realm',
            'landscape','navigate the','it is important to note','serves as','stands as')

batch = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'))
overwrite = batch.pop('_overwrite', False)
cur = json.loads(TARGET.read_text(encoding='utf-8'))
readme = cur.pop('_README')

problems = []
for qid, e in batch.items():
    if qid in cur and not overwrite:
        problems.append(f'{qid}: already present (set _overwrite to replace)')
    if not e.get('src') or not e.get('x'):
        problems.append(f'{qid}: missing src or x')
        continue
    n = len(e['x'].split())
    if n > 150:
        problems.append(f'{qid}: {n} words, over the 150 cap')
    if '—' in e['x'] or '–' in e['x']:
        problems.append(f'{qid}: contains an em/en dash')
    low = e['x'].lower()
    hits = [w for w in AI_WORDS if w in low]
    if hits:
        problems.append(f'{qid}: AI-vocabulary tell {hits}')
if problems:
    print('REFUSED:')
    for p in problems: print('  ', p)
    sys.exit(1)

cur.update(batch)
out = {'_README': readme}
out.update({k: cur[k] for k in sorted(cur)})
TARGET.write_text(json.dumps(out, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')

w = [len(v['x'].split()) for v in cur.values()]
print(f'added {len(batch)}, total {len(cur)}')
print(f'words: min {min(w)}  avg {sum(w)/len(w):.0f}  max {max(w)}')
