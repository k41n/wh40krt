#!/usr/bin/env python3
"""«Как играется» — чем этот билд отличается от соседних.

Гайд отвечает на вопрос «что брать», но не на вопрос «каково им играть»
и уж точно не на вопрос «чем этот архмилитант отличается от вон того».
Поэтому текст собирается контрастно: для каждого персонажа считается,
насколько редко та или иная черта (оружие, абсолютная и ключевая
способности, качаемые характеристики, таланты) встречается у его билдов,
и в описание идёт именно редкое — то, что отличает сборку от соседей.

Запуск после apply_ru_manual.py (нужны русские названия), до patch_notes.py:
  python3 tools/feel.py
"""
import json, re
from collections import Counter

T1 = {
 'Warrior': 'Первые 15 уровней ты воин: лезешь в ближний бой первым, ловишь удары на себя и отвечаешь тем же.',
 'Soldier': 'Первые 15 уровней ты солдат: стоишь в глубине строя и поливаешь огнём — много выстрелов, мало беготни.',
 'Operative': 'Первые 15 уровней ты оперативник: бьёшь редко, но в слабое место — вешаешь уязвимости и вскрываешь цель для остальных.',
 'Officer': 'Первые 15 уровней ты офицер: сам почти не воюешь, а раздаёшь приказы и лишние ходы союзникам.',
 'Blade Dancer': 'Первые 15 уровней ты танцор клинков: носишься по полю, бьёшь на ходу и уходишь из-под ответа.',
}
T2 = {
 'Arch-Militant': 'С 16-го — архмилитант: чем дольше тянется бой, тем больнее ты бьёшь. Самый неприхотливый стиль — ни расстановки, ни комбо не требует.',
 'Assassin': 'С 16-го — ассасин: весь урон уходит в одну цель, зато она обычно не доживает до своего хода. Нужна аккуратная позиция, по площади ты не работаешь.',
 'Vanguard': 'С 16-го — авангард: стоишь в самой гуще, стягиваешь внимание и почти не падаешь. Урона немного, зато отряд за спиной цел.',
 'Master Tactician': 'С 16-го — мастер-тактик: главный ресурс не твой урон, а лишние ходы для союзников. Играешь скорее диспетчером: сам жмёшь мало, бьют все остальные.',
 'Grand Strategist': 'С 16-го — великий стратег: расставляешь зоны и держишь в них весь отряд. Бой выигрывается расстановкой ещё до первого выстрела.',
 'Bounty Hunter': 'С 16-го — охотник за головами: метишь цель, добиваешь и за убийство возвращаешь себе ход. Бой идёт волнами: убил — снова твой ход.',
 'Executioner': 'С 16-го — палач: вешаешь кровотечения и яды, урон капает сам, пока ты уже бьёшь следующего. Мгновенного взрыва нет, зато к третьему ходу поле тает.',
 'Overseer': 'С 16-го — надзиратель: рядом питомец, и половина твоих действий — команды ему. Решений за ход больше, зато отряд получает и урон, и поддержку.',
}
# то же самое одной строкой — для списка билдов, где решают, что выбрать
SHORT = {
 'Arch-Militant': 'чем дольше бой, тем больнее бьёшь',
 'Assassin': 'весь урон в одну цель',
 'Vanguard': 'стоишь в гуще и держишь удар',
 'Master Tactician': 'раздаёшь отряду лишние ходы',
 'Grand Strategist': 'выигрываешь бой расстановкой зон',
 'Bounty Hunter': 'метишь цель и добиваешь ради лишнего хода',
 'Executioner': 'кровотечения и яды капают сами',
 'Overseer': 'с тобой питомец: и урон, и поддержка',
}

T3 = 'После 36-го идёт гранд-магистр: билд уже собран, дальше только докручиваешь то, что и так работает.'

# оружие → на что это похоже в бою
WEAPON = [
 (r'дробовик|обрез',        'бьёшь в упор, конусом'),
 (r'болтер|болт-',          'ровный поток очередей'),
 (r'плазм',                 'стреляешь редко, но очень больно'),
 (r'мелта',                 'сносишь броню в упор'),
 (r'огнемёт|огнемет|пламя', 'выжигаешь целые пачки'),
 (r'снайпер|длинн?остволь', 'один выстрел — один труп, но издалека'),
 (r'лаз(ер|ган)|винтовк',   'бьёшь точно и часто'),
 (r'посох',                 'бьёшь силами варпа'),
 (r'пистолет',              'стреляешь вплотную, не выходя из свалки'),
 (r'нож|кинжал|клинок|меч|сабл|рапир|пила', 'серия быстрых ударов'),
 (r'молот|кувалда|булав|дубин',        'медленно, зато сносит с одного удара'),
 (r'топор|коса|цеп|копь',              'тяжёлые размашистые удары'),
]


def weapon_sets(b):
    """первое оружие каждого комплекта: у многих билдов их два и они разные"""
    out = []
    for slot, items in b.get('gear', []):
        if 'ружи' not in slot.lower():
            continue
        first = items.split('/')[0].strip().rstrip('.,')
        if first and first not in out:
            out.append(first)
    return out[:2]


def main_weapon(b):
    """по оружию и судим о стиле боя; второй комплект тоже называем"""
    sets = weapon_sets(b)
    if not sets:
        return None, None
    first = sets[0]
    low = first.lower()
    flavor = next((f for rx, f in WEAPON if re.search(rx, low)), None)
    return first, flavor


def picks(b):
    """что билд реально берёт: ульты, ключевые, таланты, характеристики"""
    ults, keys, talents, stats = [], [], [], Counter()
    for lv, rows in sorted(b['levels'].items(), key=lambda kv: int(kv[0])):
        for row in rows:
            o = row[0]
            n = o.get('ru') or o['n']
            t = o['t']
            if t == 'ult' and n not in ults:
                ults.append(n)
            elif t == 'key' and n not in keys:
                keys.append(n)
            elif t == 'talent' and n not in talents:
                talents.append(n)
            elif t == 'char':
                stats[n] += 1
    return {'ult': ults, 'key': keys, 'talent': talents,
            'stat': [s for s, _ in stats.most_common(2)],
            'weapon': main_weapon(b)[0]}


def rare(values, counts, total, limit=2):
    """черты, которые есть у этого билда и почти нет у соседних"""
    cap = max(1, int(total * 0.3))
    return [v for v in values if counts[v] <= cap][:limit]


def clauses(b, p, cnt, total):
    """кусочки описания, от самого отличающего к общему"""
    out = []
    weapon, flavor = main_weapon(b)
    if weapon:
        uniq = cnt['weapon'][weapon] <= max(1, int(total * 0.3))
        name = weapon
        sets = weapon_sets(b)
        if not uniq and len(sets) > 1:       # первое оружие как у соседей — назовём второе
            name = ' и '.join(sets)
        out.append(('weapon', uniq, f'{name}: {flavor}' if flavor else name))
    for u in rare(p['ult'], cnt['ult'], total, 1):
        out.append(('ult', True, f'ульта «{u}»'))
    for k in rare(p['key'], cnt['key'], total, 1):
        out.append(('key', True, f'ключевая «{k}»'))
    tal = rare(p['talent'], cnt['talent'], total, 2)
    if tal:
        word = 'таланты ' if len(tal) > 1 else 'талант '
        out.append(('talent', True, word + ' и '.join(f'«{t}»' for t in tal)))
    if p['stat']:
        st = cnt['stat']
        uniq = any(st[s] <= max(1, int(total * 0.3)) for s in p['stat'])
        out.append(('stat', uniq, 'качаешь ' + ' и '.join(s.lower() for s in p['stat'])))
    return out


def cap(s):
    return s[0].upper() + s[1:] if s else s


def short_line(b, cl, extra=0):
    """строка для списка: сначала то, чем билд отличается, потом суть архетипа"""
    # оружие всегда впереди — это самое осязаемое, а дальше редкие черты
    head = [c for t, _, c in cl if t == 'weapon']
    uniq = [c for t, u, c in cl if u and t != 'weapon']
    head += uniq[:2 + extra]
    if extra and len(uniq) < 2 + extra:      # редкого не хватило — берём общее
        head += [c for t, u, c in cl if not u and t != 'weapon'][:extra]
    if not head:
        head = [c for _, _, c in cl][:1 + extra]
    tail = SHORT.get(b['tiers'][1])
    line = cap(', '.join(head)) if head else ''
    if tail:
        line = (line + '. ' if line else '') + cap(tail)
    return line + '.'


def long_line(b, cl, many):
    parts = [T1.get(b['tiers'][0]), T2.get(b['tiers'][1])]
    w = next((c for t, _, c in cl if t == 'weapon'), None)
    if w:
        parts.append(f'В руках — {w}.')
    body = [c for t, u, c in cl if u and t in ('ult', 'key', 'talent', 'stat')]
    if many and body:
        parts.append('Чем отличается от соседних сборок: ' + ', '.join(body) + '.')
    elif body:
        parts.append(cap(', '.join(body)) + '.')
    parts.append(T3)
    return ' '.join(p for p in parts if p)


def main():
    d = json.load(open('data.json', encoding='utf-8'))
    n = 0
    for c in d['characters']:
        builds = c['builds']
        total = len(builds)
        ps = {b['id']: picks(b) for b in builds}
        cnt = {k: Counter() for k in ('ult', 'key', 'talent', 'stat', 'weapon', 'arch')}
        for b in builds:
            p = ps[b['id']]
            for k in ('ult', 'key', 'talent', 'stat'):
                for v in p[k]:
                    cnt[k][v] += 1
            if p['weapon']:
                cnt['weapon'][p['weapon']] += 1
            cnt['arch'][b['tiers'][1]] += 1

        seen = {}
        for b in builds:
            p = ps[b['id']]
            cl = clauses(b, p, cnt, total)
            line = short_line(b, cl)
            extra = 0
            while line in seen and extra < 3:       # соседи не должны совпадать
                extra += 1
                line = short_line(b, cl, extra)
            seen[line] = b['id']
            b['feelShort'] = line
            b['feel'] = long_line(b, cl, total > 1)
            n += 1
    print('описаний «как играется»:', n)
    json.dump(d, open('data.json', 'w', encoding='utf-8'),
              ensure_ascii=False, separators=(',', ':'))
    print('data.json обновлён')


if __name__ == '__main__':
    main()
