#!/usr/bin/env python3
"""Подставляет официальные русские названия в data.json.

Нужны два файла локализации из папки игры:
  <Steam>/Warhammer 40,000 Rogue Trader/WH40KRT_Data/StreamingAssets/Localization/
      enGB.json
      ruRU.json

Запуск:
  python3 tools/apply_ru.py path/to/enGB.json path/to/ruRU.json

Скрипт сопоставляет строки по UUID: en[uuid] -> ru[uuid], затем ищет каждое
английское название таланта/способности/характеристики/навыка в этой карте
и дописывает поле "ru" рядом с английским. Английское название остаётся
на месте — оно нужно, чтобы сверяться с вики.
"""
import json, sys, collections, re, difflib

def load(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)['strings']

def build_map(en_path, ru_path):
    en, ru = load(en_path), load(ru_path)
    pairs = collections.defaultdict(collections.Counter)
    for uid, v in en.items():
        t = (v.get('Text') or '').strip()
        if not t or len(t) > 60 or '\n' in t or '{' in t:
            continue
        r = ru.get(uid)
        if not r:
            continue
        rt = (r.get('Text') or '').strip()
        if not rt or len(rt) > 80 or '\n' in rt:
            continue
        pairs[t.lower()][rt] += 1
    # для каждого английского названия берём самый частый русский вариант
    return {k: c.most_common(1)[0][0] for k, c in pairs.items()}

ABBR = {'bs':'ballistic skill','ws':'weapon skill','tgh':'toughness','agi':'agility',
        'int':'intelligence','per':'perception','wp':'willpower','fel':'fellowship',
        'str':'strength'}
MANUAL = {
    'ap +1': 'ОД +1',
    'dismantling': 'Препарирование цели',
    'ballistic score': 'Дальний Бой',
    'pa': 'Ношение силовой брони',
    'ap +1 - ballistic skill': 'ОД +1 и Дальний Бой',
    'choice 1': 'Вариант 1', 'choice 2': 'Вариант 2', 'choice 3': 'Вариант 3',
    'scourging strike + where it hurts': 'Секущие удары + По больному',
    # сокращения и опечатки автора гайда
    'bolt exp': 'Знаток болтерного оружия',
    'bolt expert': 'Знаток болтерного оружия',
    'bolt prof': 'Обращение с болтерным оружием',
    'bolt proficiency': 'Обращение с болтерным оружием',
    'plasma proficiency': 'Обращение с плазменным оружием',
    'power weapon specialist': 'Знаток силового оружия',
    'hail of bullets': 'Свинцовый шквал',
    'attach bayonets!': 'Примкнуть штыки!',
    'ferver': 'Рвение',
    'dissary': 'Дезориентация',
    'warp curse': 'Волна варп-проклятия',
    'base skill: lore': 'Базовый навык: Знания',
    'sanctic': 'Экзорцизм',
}
ROMAN = re.compile(r'\s+(I{1,3}|IV|V|VI{0,3}|IX|X)$')


def variants(name):
    """Английское название из гайда -> кандидаты для поиска в локализации игры."""
    low = ' '.join(name.split()).lower()
    yield low
    yield low + '!'
    yield ROMAN.sub('', low)
    m = re.fullmatch(r'lore[ :]+\(?(\w+)\)?', low)
    if m:
        yield f'lore ({m.group(1)})'
    m = re.fullmatch(r'(?:base|advanced) skill:\s*(.+)', low)
    if m:
        yield m.group(1)
        yield f'lore ({m.group(1)})'
    m = re.fullmatch(r'characteristic training\s*:\s*(.+)', low)
    if m:
        full = ABBR.get(m.group(1).strip(), m.group(1).strip())
        yield f'characteristic training: {full}'
    yield low.replace('-', ' ')
    yield low.replace(' ', '-')
    # сокращения, которыми пользуется автор гайда
    x = re.sub(r'\bprof\b', 'proficiency', low)
    x = re.sub(r'\bspec\b', 'specialist', x)
    x = re.sub(r'\bexp\b', 'expert', x)
    x = re.sub(r'\bchar(?:acter)? training\s*:?\s*', 'characteristic training: ', x)
    if x != low:
        yield x
        m2 = re.fullmatch(r'characteristic training:\s*(.+)', x)
        if m2:
            yield 'characteristic training: ' + ABBR.get(m2.group(1).strip(), m2.group(1).strip())
    yield re.sub(r'\s*\+\s*', ' ', ' '.join(low.split()))


def tr_line(line, ru_for):
    """Строка вида "Athletics / Carouse, Medicae" -> перевод по кускам."""
    out = []
    for part in re.split(r'(\s*[/,]\s*)', line):
        if not part or re.fullmatch(r'\s*[/,]\s*', part):
            out.append(part)
            continue
        t = part.strip()
        out.append(part.replace(t, ru_for(t) or t) if t else part)
    return ''.join(out)


def apply(data, m):
    keys = list(m)
    hit = miss = fuzzy = 0
    seen_miss = collections.Counter()
    cache = {}

    def ru_for(name):
        nonlocal hit, miss, fuzzy
        if name in cache:
            r = cache[name]
        else:
            low = ' '.join(name.split()).lower()
            # ручной словарь идёт первым: в игре часть строк осталась
            # непереведённой (choice 1 -> Choice 1), автоподстановка их не чинит
            r = MANUAL.get(low)
            if r is None:
                for v in variants(name):
                    if v in m:
                        r = m[v]
                        break
            if r is None:
                if len(low) >= 6:
                    c = difflib.get_close_matches(low, keys, n=1, cutoff=0.85)
                    if c:
                        r = m[c[0]]
                        fuzzy += 1
            cache[name] = r
        if r and r.lower() != name.lower():
            hit += 1
            return r
        miss += 1
        seen_miss[name] += 1
        return None

    # архетипы уже переведены вручную в build_data.py; из локализации берём
    # только те, где перевода ещё нет (значение совпадает с английским ключом)
    for k, v in list(data.get('archRu', {}).items()):
        if v and v != k:
            continue
        r = m.get(k.lower())
        if r and r.lower() != k.lower():
            data['archRu'][k] = r

    for c in data['characters']:
        for b in c['builds']:
            b['tiersRu'] = [data['archRu'].get(t, t) for t in b['tiers']]
            b['skills'] = [tr_line(line, ru_for) for line in b.get('skills', [])]
            for rows in b['levels'].values():
                for row in rows:
                    for o in row:
                        r = ru_for(o['n'])
                        if r:
                            o['ru'] = r
    print(f'подставлено: {hit} (из них по похожести: {fuzzy}), не найдено: {miss}')
    for n, k in seen_miss.most_common(25):
        print('  нет перевода:', repr(n), f'({k})')
    return data


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    m = build_map(sys.argv[1], sys.argv[2])
    print('пар в словаре локализации:', len(m))
    d = json.load(open('data.json', encoding='utf-8'))
    d = apply(d, m)
    d['meta']['ru'] = True
    json.dump(d, open('data.json', 'w', encoding='utf-8'),
              ensure_ascii=False, separators=(',', ':'))
    print('data.json обновлён')
