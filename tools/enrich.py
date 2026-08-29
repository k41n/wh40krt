import json, re, difflib

CHARS_SET = {'weapon skill','ballistic skill','strength','toughness','agility',
             'intelligence','perception','willpower','fellowship'}
SKILLS_SET = {'athletics','awareness','carouse','coercion','commerce','demolition',
              'demolitions','logic','medicae','persuasion','tech-use','tech use',
              'lore imperium','lore xenos','lore warp','lore (imperium)','lore (xenos)',
              'lore (warp)','lore imperialis'}
KEYSTONES = {'charge','endure','run and gun','revel in slaughter','analyse enemies',
             'expose weakness','voice of command','bring it down !','bring it down!',
             'blade dance','death from above','versatility','wildfire','seek the opening',
             'hunt down the prey','combat tactics','tactical advantage','unyielding beacon',
             'where it hurts','forced repentance','scourging strikes',
             'cyber-mastiff proficiency','psyber-raven proficiency',
             'servo-skull swarm proficiency','cyber-eagle proficiency'}
ULTIMATES = {'daring breach','firearm mastery','finest hour','dismantling attack',
             'dismantling','death waltz','dispatch','steady superiority','take and hold',
             'wild hunt','carnival of misery','overcharge','orchestrated firestorm'}
ALIAS = {
 'versitility':'Versatility','voice of command':'Voice of Command',
 'bring it down !':'Bring it Down!','ap + 1':'AP +1','ap +1':'AP +1','ap+1':'AP +1',
 'demolitions':'Demolition','tech use':'Tech-Use','allout':'All Out',
 'eagar for battle':'Eager for Battle','unyelding beacon':'Unyielding Beacon',
 'unyelding guard':'Unyielding Guard','get off me!':'Get off Me!',
 'contempt for the weak':'Contempt for the Weak','martial art':'Martial Arts',
}
ROMAN = re.compile(r'\s+(I{1,3}|IV|V|VI{0,3}|IX|X)$', re.I)

def N(d, note):
    if note: d['note'] = note
    return {k: v for k, v in d.items() if v is not None}


def enrich(data):
    g = data['glossary']
    lower = {k.lower(): k for k in g}
    keys = list(lower)
    cache = {}

    def classify(raw):
        r0 = classify_(raw)
        return r0

    def classify_(raw):
        n = raw.strip().rstrip('*').strip()
        if not n: return None
        note = None
        m = re.match(r'^(.*?)\s*\((.+)\)$', n)
        if m and len(m.group(2)) > 3 and m.group(1).strip():
            n, note = m.group(1).strip(), m.group(2).strip()
        low = n.lower()
        if re.fullmatch(r'ap\s*\+\s*1', low): return N({'t':'ap','n':'AP +1'}, note)
        if low in ALIAS: n = ALIAS[low]; low = n.lower()
        if low in CHARS_SET: return N({'t':'char','n':n.title()}, note)
        if low in SKILLS_SET: return N({'t':'skill','n':n.title().replace('Tech-use','Tech-Use')}, note)
        base = ROMAN.sub('', n); rank = n[len(base):].strip() or None
        bl = base.lower()
        if bl in ULTIMATES: return N({'t':'ult','n':base,'r':rank,'d':g.get(lower.get(bl,''),{}).get('desc')}, note)
        if bl in KEYSTONES: return N({'t':'key','n':base,'r':rank,'d':g.get(lower.get(bl,''),{}).get('desc')}, note)
        if low in lower:
            k = lower[low]; return N({'t':g[k]['kind'],'n':k,'d':g[k]['desc']}, note)
        if bl in lower:
            k = lower[bl]; return N({'t':g[k]['kind'],'n':k,'r':rank,'d':g[k]['desc']}, note)
        if bl not in cache:
            m2 = difflib.get_close_matches(bl, keys, n=1, cutoff=0.88)
            cache[bl] = m2[0] if m2 else None
        k = cache[bl]
        if k:
            kk = lower[k]; return N({'t':g[kk]['kind'],'n':kk,'r':rank,'d':g[kk]['desc']}, note)
        return N({'t':'other','n':n,'r':rank}, note)

    for c in data['characters']:
        for b in c['builds']:
            out = {}
            for lv, picks in b['levels'].items():
                rows = []
                for p in picks:
                    opts = [classify(x) for x in re.split(r'\s*/\s*(?![^(]*\))', p)]
                    opts = [o for o in opts if o]
                    if opts: rows.append(opts)
                out[lv] = rows
            b['levels'] = out
    return data

if __name__ == '__main__':
    d = json.load(open('/Users/k41n/projects/wh40k/data.json', encoding='utf-8'))
    d = enrich(d)
    import collections
    cnt = collections.Counter()
    for c in d['characters']:
        for b in c['builds']:
            for lv, rows in b['levels'].items():
                for r in rows:
                    for o in r: cnt[o['t']] += 1
    print(cnt)
    unk = collections.Counter()
    for c in d['characters']:
        for b in c['builds']:
            for lv, rows in b['levels'].items():
                for r in rows:
                    for o in r:
                        if o['t'] == 'other': unk[o['n']] += 1
    print('unknown unique', len(unk), 'occ', sum(unk.values()))
    for k, v in unk.most_common(40): print(v, '|', k)
    json.dump(d, open('/Users/k41n/projects/wh40k/data.json','w',encoding='utf-8'),
              ensure_ascii=False, separators=(',',':'))
