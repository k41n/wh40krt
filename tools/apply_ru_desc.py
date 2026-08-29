#!/usr/bin/env python3
"""Русифицирует то, что не покрывает apply_ru.py: описания талантов/способностей
и названия предметов снаряжения.

Описания в игре хранятся отдельными строками, связать их с названием по UUID
нельзя — поэтому ищем английский текст описания в локализации и берём русский
из той же пары. Точное совпадение редко (в игре шаблоны вроде {name}),
поэтому: нормализация -> отбор кандидатов по общим словам -> difflib.

Запуск:
  python3 tools/apply_ru_desc.py path/to/enGB.json path/to/ruRU.json
"""
import json, sys, re, difflib, collections

MIN_RATIO = 0.75          # порог похожести для описаний
MAX_CANDIDATES = 60       # сколько кандидатов прогонять через difflib
STOP_DF = 3000            # слова, встречающиеся чаще, для отбора бесполезны


def load(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)['strings']


def pairs(en_path, ru_path):
    en, ru = load(en_path), load(ru_path)
    out = {}
    for uid, v in en.items():
        t = (v.get('Text') or '').strip()
        r = ru.get(uid)
        if not t or not r:
            continue
        rt = (r.get('Text') or '').strip()
        if rt and t not in out:
            out[t] = rt
    return out


TAG_G = re.compile(r'\{/?g(?:\|[^}]*)?\}')       # {g|Encyclopedia:Dodge}уклонение{/g}
TAG_VAL = re.compile(r'\{(?:uip|unit_stat)\|[^}]*\}')  # вычисляемое число


def clean(s):
    """Игровая разметка -> обычный текст."""
    s = TAG_G.sub('', s)
    s = TAG_VAL.sub('…', s)          # число зависит от характеристик — см. английский текст
    s = s.replace('{br}', '\n')
    s = re.sub(r'\{[^}]*\}', '', s)
    return re.sub(r'[ \t]+', ' ', s).strip()


def norm(s):
    s = re.sub(r'\{[^}]*\}', ' ', s)      # {name}, {mf|..|..} и прочие шаблоны
    s = re.sub(r'<[^>]*>', ' ', s)        # разметка
    s = re.sub(r'[^a-z0-9%+ ]', ' ', s.lower())
    return ' '.join(s.split())


class DescIndex:
    """Обратный индекс по словам: быстро отсекает заведомо чужие строки."""

    def __init__(self, texts):
        self.keys = list(texts)
        self.vals = [texts[k] for k in self.keys]
        self.norm = [norm(k) for k in self.keys]
        self.exact = {n: i for i, n in enumerate(self.norm) if n}
        df = collections.Counter()
        toks = []
        for n in self.norm:
            ts = set(n.split())
            toks.append(ts)
            df.update(ts)
        self.index = collections.defaultdict(list)
        for i, ts in enumerate(toks):
            for t in ts:
                if df[t] <= STOP_DF and len(t) > 2:
                    self.index[t].append(i)

    def find(self, text):
        q = norm(text)
        if not q:
            return None, 0.0
        if q in self.exact:
            return self.vals[self.exact[q]], 1.0
        counts = collections.Counter()
        for t in set(q.split()):
            for i in self.index.get(t, ()):
                counts[i] += 1
        best, ratio = None, 0.0
        sm = difflib.SequenceMatcher()
        sm.set_seq2(q)
        for i, _ in counts.most_common(MAX_CANDIDATES):
            sm.set_seq1(self.norm[i])
            if sm.real_quick_ratio() < ratio or sm.quick_ratio() < ratio:
                continue
            r = sm.ratio()
            if r > ratio:
                best, ratio = self.vals[i], r
        return (best, ratio) if ratio >= MIN_RATIO else (None, ratio)


def item_ru(name, short, cache):
    """Название предмета -> русское из локализации (или None)."""
    if name in cache:
        return cache[name]
    low = ' '.join(name.split()).lower()
    r = short.get(low)
    if r is None:
        # [Sol Pattern] Elite Power Sword -> [sol-pattern] elite power sword
        alt = re.sub(r'\[([^\]]+)\]', lambda m: '[' + m.group(1).replace(' ', '-') + ']', low)
        r = short.get(alt)
    if r is None and len(low) >= 8:
        c = difflib.get_close_matches(low, short, n=1, cutoff=0.88)
        if c:
            r = short[c[0]]
    if r and r.lower() == low:
        r = None                      # в игре строка осталась английской
    cache[name] = r
    return r


def split_items(line):
    """'A / B, C' -> [('A', sep), ...] с сохранением разделителей."""
    return re.split(r'(\s*[/,]\s+|\s+/\s*)', line)


def main(en_path, ru_path):
    p = pairs(en_path, ru_path)
    short = {}
    for k, v in p.items():
        if len(k) <= 70 and '\n' not in k and '{' not in k:
            short.setdefault(k.lower(), v)
    idx = DescIndex({k: v for k, v in p.items() if len(k) > 60})
    print(f'пар: {len(p)}, коротких: {len(short)}, длинных: {len(idx.keys)}')

    d = json.load(open('data.json', encoding='utf-8'))

    # ── описания талантов и способностей ──────────────────────────────
    hit = 0
    for name, v in d['glossary'].items():
        desc = v.get('desc')
        if not desc:
            continue
        ru, _ = idx.find(desc)
        if not ru:
            # гайд иногда добавляет свою шапку: "Iron Arm is a ... Ability, <текст>"
            m = re.match(r'^.{0,80}?\bis an? [^,]{0,60}?\bAbility,\s*(.+)$', desc, re.S)
            if m:
                ru, _ = idx.find(m.group(1))
        if ru:
            v['descRu'] = clean(ru)
            hit += 1
    print(f'описаний переведено: {hit} из {len(d["glossary"])}')

    # ── снаряжение ────────────────────────────────────────────────────
    cache = {}
    tot = got = 0
    for c in d['characters']:
        for b in c['builds']:
            gear = []
            for slot, items in b.get('gear', []):
                slot_ru = item_ru(slot, short, cache) or slot
                lines = items if isinstance(items, list) else [items]
                new = []
                for line in lines:
                    out = []
                    for part in split_items(line):
                        t = part.strip()
                        if not t or re.fullmatch(r'\s*[/,]\s*', part):
                            out.append(part)
                            continue
                        tot += 1
                        r = item_ru(t, short, cache)
                        if r:
                            got += 1
                        out.append(part.replace(t, r or t))
                    new.append(''.join(out))
                gear.append([slot_ru, new if isinstance(items, list) else new[0]])
            if gear:
                b['gear'] = gear
    print(f'предметов переведено: {got} из {tot}')

    d['meta']['ruDesc'] = True
    json.dump(d, open('data.json', 'w', encoding='utf-8'),
              ensure_ascii=False, separators=(',', ':'))
    print('data.json обновлён')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
