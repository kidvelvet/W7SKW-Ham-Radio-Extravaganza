"""Extract all three question pools from the supplied flashcard decks,
cross-validating each against its plain-text pool file."""
import re, json, base64, pathlib

def grab_deck(path):
    """Pull the ALL[...] array out of a flashcard HTML file."""
    s = pathlib.Path(path).read_text(encoding='utf-8')
    j = s.index('[', s.index('ALL')); d = 0
    for k in range(j, len(s)):
        if s[k] == '[': d += 1
        elif s[k] == ']':
            d -= 1
            if d == 0: return json.loads(s[j:k+1])
    raise ValueError('unterminated array in ' + path)

def parse_pool(path):
    t = pathlib.Path(path).read_text(encoding='utf-8')
    return re.findall(
        r'^([EGT]\d[A-Z]\d{2}) \(([A-D])\)\s*(\[[^\]]*\])?\s*\n(.+?)\n((?:[A-D]\..+\n?){4})',
        t, re.M)

SUB_NAMES = {
 'T0':'Electrical & RF Safety','T1':'FCC Rules & Regulations','T2':'Operating Procedures',
 'T3':'Radio Wave Propagation','T4':'Station Setup','T5':'Electrical Principles',
 'T6':'Electronic Components','T7':'Station Equipment','T8':'Modulation & Modes',
 'T9':'Antennas & Feed Lines',
 'G0':'Electrical & RF Safety','G1':'FCC Rules & Regulations','G2':'Operating Procedures',
 'G3':'Radio Wave Propagation','G4':'Amateur Radio Practices','G5':'Electrical Principles',
 'G6':'Circuit Components','G7':'Practical Circuits','G8':'Signals & Emissions',
 'G9':'Antennas & Feed Lines',
 'E0':'Safety','E1':'FCC Rules & Regulations','E2':'Operating Procedures',
 'E3':'Radio Wave Propagation','E4':'Amateur Practices','E5':'Electrical Principles',
 'E6':'Circuit Components','E7':'Practical Circuits','E8':'Signals & Emissions',
 'E9':'Antennas & Transmission Lines',
}

POOLS = [
  dict(key='tech',  name='Technician',    element='Element 2', valid='2026-2030',
       short='T', accent='#1e5fbf', accentDark='#5b9bff',
       deck='pools/Technician Exam/US_Technician_2026-2030_Flashcards.html',
       txt ='pools/Technician Exam/US_Technician_2026-2030_Current_Question_Pool.txt',
       withdrawn=None),
  dict(key='gen',   name='General',       element='Element 3', valid='2023-2027',
       short='G', accent='#0f7a52', accentDark='#4fcf9a',
       deck='pools/General Exam/US_General_2023-2027_Flashcards.html',
       txt ='pools/General Exam/US_General_2023-2027_Active_Question_Pool.txt',
       withdrawn='pools/General Exam/US_General_2023-2027_Withdrawn_Questions.txt'),
  dict(key='extra', name='Amateur Extra', element='Element 4', valid='2024-2028',
       short='E', accent='#7a3aa8', accentDark='#c08bf0',
       deck='pools/Amateur Extra Exam/US_Amateur_Extra_2024-2028_Flashcards.html',
       txt ='pools/Amateur Extra Exam/US_Amateur_Extra_2024-2028_Active_Question_Pool.txt',
       withdrawn='pools/Amateur Extra Exam/US_Amateur_Extra_2024-2028_Withdrawn_Questions.txt'),
]

out = {'pools': {}, 'order': [p['key'] for p in POOLS]}
report = []

for p in POOLS:
    arr = grab_deck(p['deck'])
    blocks = {b[0]: b for b in parse_pool(p['txt'])}
    withdrawn = set()
    if p['withdrawn']:
        withdrawn = set(re.findall(r'^([EGT]\d[A-Z]\d{2})$',
                        pathlib.Path(p['withdrawn']).read_text(), re.M))

    mism = 0
    for c in arr:
        b = blocks.get(c['id'])
        if not b:
            mism += 1; continue
        if c['correct_letter'] != b[1]: mism += 1
        if c['question'].strip() != b[3].strip(): mism += 1
        ch = dict(re.findall(r'^([A-D])\. (.+)$', b[4], re.M))
        for L in 'ABCD':
            if c['answers'].get(L, '').strip() != ch.get(L, '').strip(): mism += 1

    # hard guarantees
    # Question ids are rendered into the DOM, so pin their shape explicitly here
    # rather than relying on the cross-check against the text pool to imply it.
    bad_ids = [c['id'] for c in arr if not re.fullmatch(r'[EGT]\d[A-Z]\d{2}', c['id'])]
    assert not bad_ids, f"{p['name']}: malformed question ids {bad_ids[:5]}"
    assert mism == 0, f"{p['name']}: {mism} mismatches vs text pool"
    assert not (withdrawn & {c['id'] for c in arr}), f"{p['name']}: withdrawn question present"
    assert all(set(c['answers']) == set('ABCD') and c['correct_letter'] in 'ABCD' for c in arr)

    # Write figures out as real PNG files rather than inlining ~1 MB of base64.
    # They load from the service-worker cache, so offline still works.
    figdir = pathlib.Path('docs/figures'); figdir.mkdir(parents=True, exist_ok=True)
    figs = {}
    for c in arr:
        if not c.get('figure_data'): continue
        name = c['figure']
        if name in figs: continue
        head, b64 = c['figure_data'].split(',', 1)
        assert 'image/png' in head, f'unexpected image type for {name}: {head[:40]}'
        # The decks are third-party input, so a figure name is never trusted as a
        # path. Strip any directories, allowlist the characters, then confirm the
        # resolved target really lands inside docs/figures.
        stem = pathlib.PurePosixPath(name.replace('\\', '/')).name
        if not stem.lower().endswith('.png'):
            stem += '.png'
        assert re.fullmatch(r'[A-Za-z0-9._-]{1,64}\.png', stem), f'unsafe figure name: {name!r}'
        fname = f"{p['key']}-{stem}"
        target = (figdir/fname).resolve()
        assert target.parent == figdir.resolve(), f'figure path escapes figures dir: {name!r}'
        target.write_bytes(base64.b64decode(b64))
        figs[name] = 'figures/' + fname

    qs = sorted(({'id':c['id'], 'g':c['group'], 's':c['subelement'],
                  'q':c['question'].strip(),
                  'a':[c['answers'][L].strip() for L in 'ABCD'],
                  'c':'ABCD'.index(c['correct_letter']),
                  'r':(c.get('refs') or '').strip('[]'),
                  'f':c.get('figure') or ''} for c in arr), key=lambda x: x['id'])

    groups = sorted({q['g'] for q in qs})
    examLen = len(groups)                      # one question drawn per group
    passing = -(-examLen * 74 // 100)          # 74%, rounded up
    subs = {k: SUB_NAMES[k] for k in sorted({q['s'] for q in qs})}
    missing = [k for k in subs if k not in SUB_NAMES]
    assert not missing, f'unnamed subelements: {missing}'

    out['pools'][p['key']] = {
        'key':p['key'], 'name':p['name'], 'element':p['element'], 'valid':p['valid'],
        'short':p['short'], 'accent':p['accent'], 'accentDark':p['accentDark'],
        'examLen':examLen, 'pass':passing,
        'subelements':subs, 'groups':groups, 'questions':qs, 'figures':figs,
    }
    # `withdrawn` is a build-time assertion only - the app never reads it,
    # so it is deliberately not shipped in pools.json.
    report.append((p['name'], len(qs), len(groups), examLen, passing, len(figs), len(withdrawn)))

# ---- merge study-mode explanations (study only; never shown during an exam) ----
EXPL = pathlib.Path('build/explanations.json')
expl = json.loads(EXPL.read_text(encoding='utf-8')) if EXPL.exists() else {}
expl.pop('_README', None)

valid_ids = {q['id'] for p in out['pools'].values() for q in p['questions']}
orphans = sorted(set(expl) - valid_ids)
assert not orphans, f'explanations for unknown question ids: {orphans[:5]}'

over, attached = [], 0
for p in out['pools'].values():
    for q in p['questions']:
        e = expl.get(q['id'])
        if not e:
            continue
        words = len(e['x'].split())
        if words > 150:
            over.append((q['id'], words))
        q['x'] = e['x']
        q['xs'] = e['src']
        attached += 1
assert not over, f'explanations over 150 words: {over[:5]}'

pathlib.Path('build/pools.json').write_text(json.dumps(out, separators=(',',':')), encoding='utf-8')

print(f"{'pool':16}{'qs':>5}{'grps':>6}{'exam':>6}{'pass':>6}{'figs':>6}{'wdrn':>6}")
for r in report:
    print(f'{r[0]:16}{r[1]:5}{r[2]:6}{r[3]:6}{r[4]:6}{r[5]:6}{r[6]:6}')
print('pools.json', round(pathlib.Path('build/pools.json').stat().st_size/1024), 'KB')
total_q = sum(len(p['questions']) for p in out['pools'].values())
print(f'explanations {attached}/{total_q} ({100*attached/total_q:.1f}%)')
