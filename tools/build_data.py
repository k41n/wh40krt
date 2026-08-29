import csv, json, re, os, unicodedata
from parse_builds import parse_tab

OUT = '/Users/k41n/projects/wh40k'

# ---------- glossary ----------
def read_pairs(path):
    out = {}
    for row in csv.reader(open(path, encoding='utf-8')):
        if len(row) < 2: continue
        n, d = row[0].strip(), row[1].strip()
        if not n or not d: continue
        if d.startswith('http'): continue
        out.setdefault(n, d)
    return out

talents = read_pairs('s_1647069060.csv')
abilities = read_pairs('s_1806198257.csv')
glossary = {}
for n, d in talents.items(): glossary[n] = {'kind': 'talent', 'desc': d}
for n, d in abilities.items(): glossary.setdefault(n, {'kind': 'ability', 'desc': d})

# ---------- builds ----------
SRC = {
 's_448714743.csv':  'Revan619 — гайд компаньонов',
 's_983023675.csv':  'Revan619 — альтернативные билды компаньонов',
 's_1737934440.csv': 'Revan619 — билды Вольного Торговца',
}

CHARS = [
 # id, en, ru, order-key words used to detect a build title
 ('abelard','Abelard Werserian','Абеляр Версериан','base',['abelard']),
 ('idira','Idira Tlass','Идира Тласс','base',['idira']),
 ('argenta','Sister Argenta','Сестра Арджента','base',['argenta']),
 ('cassia','Cassia Orsellio','Кассия Орселлио','base',['cassia']),
 ('pasqal','Pasqal Haneumann','Паскаль Ханойманн','base',['pasqal','rite of machine spirit']),
 ('heinrix','Heinrix van Calox','Хейнрикс ван Калокс','base',['heinrix']),
 ('jae','Jae Heydari','Джай Хейдари','base',['jae']),
 ('yrliet','Yrliet Lanaevyss','Ирлиэт Ланаэвисс','base',['yrliet']),
 ('ulfar','Ulfar','Ульфар','base',['ulfar']),
 ('marazhai','Marazhai Aezyrraesh','Маражай Аэзирраэш','base',['marazhai']),
 ('kibellah','Kibellah','Кибелла','void_shadows',['kibellah']),
 ('solomorne','Solomorne Anthar','Соломорн Антар','lex_imperialis',['solomorne']),
 ('eogunn','Eogunn Ferbus','Эогунн Фербус','lex_imperialis',['eogunn']),
 ('incendia','Incendia Chorda','Инцендия Чорда','base',['incendia']),
 ('winterscale','Calligos Winterscale','Каллигос Винтерскейл','base',['winterscale','calligos']),
 ('uralon','Uralon the Cruel','Уралон Жестокий','base',['uralon']),
]

ARCH_DLC = {'Blade Dancer':'void_shadows','Bladedancer':'void_shadows',
            'Executioner':'void_shadows','Overseer':'lex_imperialis'}
ARCH_RU = {
 'Warrior':'Воин','Soldier':'Солдат','Operative':'Оперативник','Officer':'Офицер',
 'Blade Dancer':'Танцор смерти','Bladedancer':'Танцор смерти',
 'Assassin':'Ассасин','Vanguard':'Авангард','Arch-Militant':'Архмилитант',
 'Master Tactician':'Мастер-тактик','Grand Strategist':'Великий стратег',
 'Bounty Hunter':'Охотник за головами','Executioner':'Палач','Overseer':'Надзиратель',
 'Exemplar':'Exemplar',
}

def clean_title(t):
    t = re.sub(r'https?://\S+', '', t).strip(' -–—')
    return t.strip()

def slug(s):
    s = re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')
    return s[:60] or 'build'

all_builds = []
for f, src in SRC.items():
    for b in parse_tab(f):
        b['source'] = src
        b['video'] = (re.search(r'https?://\S+', b['title']) or [None])
        m = re.search(r'https?://\S+', b['title'] + ' ' + b['desc'])
        b['video'] = m.group(0).rstrip(' )') if m and 'youtu' in m.group(0) else None
        b['title'] = clean_title(b['title'])
        b['desc'] = re.sub(r'https?://\S+', '', b['desc']).strip()
        all_builds.append(b)

# fix known mis-parse: tier1 must be a real archetype
VALID_T1 = {'Warrior','Soldier','Operative','Officer','Blade Dancer','Bladedancer'}
for b in all_builds:
    if b['tiers'][0] not in VALID_T1:
        # infer from level-1 keystone
        k = (b['levels'].get(1) or [''])[0]
        guess = {'Charge':'Warrior','Run and Gun':'Soldier','Analyse Enemies':'Operative',
                 'Voice of Command':'Officer','Blade Dance':'Blade Dancer'}.get(k)
        b['tiers'][0] = guess or b['tiers'][0]

chars = []
used = set()
for cid, en, ru, dlc, keys in CHARS:
    bs = []
    for i, b in enumerate(all_builds):
        t = b['title'].lower()
        if any(k in t for k in keys):
            bs.append(b); used.add(i)
    if not bs: continue
    kind = 'secret' if cid in ('incendia','winterscale','uralon') else 'companion'
    chars.append(dict(id=cid, en=en, ru=ru, kind=kind, dlc=dlc, builds=bs))

rt_builds = [b for i, b in enumerate(all_builds) if i not in used]
chars.append(dict(id='rogue-trader', en='Rogue Trader (your captain)',
                  ru='Вольный Торговец (ГГ)', kind='rt', dlc='base', builds=rt_builds))

# assign ids + dlc requirement per build
for c in chars:
    seen = {}
    for b in c['builds']:
        s = slug(b['title'])
        seen[s] = seen.get(s, 0) + 1
        b['id'] = s if seen[s] == 1 else f'{s}-{seen[s]}'
        need = {c['dlc']} | {ARCH_DLC[t] for t in b['tiers'] if t in ARCH_DLC}
        need.discard('base')
        b['dlc'] = sorted(need)
        b['tiersRu'] = [ARCH_RU.get(t, t) for t in b['tiers']]
        b['levels'] = {str(k): v for k, v in sorted(b['levels'].items())}

data = dict(
  meta=dict(generated='2026-08-29', levelCap=55,
            tiers=[[1,15,'Тир I'],[16,35,'Тир II'],[36,55,'Тир III — Образец']],
            sources=['https://steamcommunity.com/sharedfiles/filedetails/?id=3398861511',
                     'https://docs.google.com/spreadsheets/d/1rskX4sYcNm6Wqt4rtm8EQqRR4__yrEuxCEzjwoKlHOY/',
                     'https://roguetrader.wiki.fextralife.com/Archetypes']),
  archRu=ARCH_RU, archDlc=ARCH_DLC,
  glossary=glossary, characters=chars)

os.makedirs(OUT, exist_ok=True)
json.dump(data, open(os.path.join(OUT, 'data.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, separators=(',', ':'))
print('chars', len(chars), 'builds', sum(len(c['builds']) for c in chars),
      'glossary', len(glossary))
for c in chars: print(' ', c['id'], len(c['builds']))
