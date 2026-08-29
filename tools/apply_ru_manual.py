#!/usr/bin/env python3
"""Накладывает ручной перевод из tools/ru_manual.json.

Здесь лежит то, чего нет в локализации игры: названия и описания билдов
(это текст автора гайда), пояснения к слотам, редкие предметы и те описания
талантов, которые автор написал сам, а не скопировал из игры.

Запуск (после build_data.py, enrich.py, apply_ru.py, apply_ru_desc.py):
  python3 tools/apply_ru_manual.py
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def split_items(line):
    return re.split(r'(\s*[/,]\s+|\s+/\s*)', line)


def main():
    man = json.load(open(os.path.join(HERE, 'ru_manual.json'), encoding='utf-8'))
    d = json.load(open('data.json', encoding='utf-8'))
    stat = dict.fromkeys(('titles', 'descs', 'glossary', 'slots', 'items', 'notes', 'skills'), 0)
    missed = {k: set() for k in stat}

    for name, v in d['glossary'].items():
        if v.get('desc') and not v.get('descRu'):
            ru = man['glossary'].get(name)
            if ru:
                v['descRu'] = ru
                stat['glossary'] += 1
            else:
                missed['glossary'].add(name)

    for c in d['characters']:
        h = man.get('howto', {}).get(c['id'])
        if h:
            c['how'] = h['text']
            if h.get('pick'):
                c['pick'] = h['pick']
        for b in c['builds']:
            ru = man['titles'].get(b['title'])
            if ru:
                b['titleRu'] = ru
                stat['titles'] += 1
            elif not re.search('[А-Яа-я]', b['title']):
                missed['titles'].add(b['title'])

            if b.get('desc'):
                ru = man['descs'].get(b['desc'])
                if ru:
                    b['descRu'] = ru
                    stat['descs'] += 1
                elif not re.search('[А-Яа-я]', b['desc']):
                    missed['descs'].add(b['desc'])

            gear = []
            for slot, items in b.get('gear', []):
                if not re.search('[А-Яа-я]', slot):
                    ru = man['slots'].get(slot) or man['items'].get(slot)
                    if ru:
                        slot, stat['slots'] = ru, stat['slots'] + 1
                    else:
                        missed['slots'].add(slot)
                lines = items if isinstance(items, list) else [items]
                new = []
                for line in lines:
                    out = []
                    for part in split_items(line):
                        t = part.strip()
                        if not t or re.fullmatch(r'\s*[/,]\s*', part) or re.search('[А-Яа-я]', t):
                            out.append(part)
                            continue
                        ru = man['items'].get(t)
                        if ru:
                            stat['items'] += 1
                            out.append(part.replace(t, ru))
                        else:
                            missed['items'].add(t)
                            out.append(part)
                    new.append(''.join(out))
                gear.append([slot, new if isinstance(items, list) else new[0]])
            if gear:
                b['gear'] = gear

            sk = [man.get('skills', {}).get(x, x) for x in b.get('skills', [])]
            if sk != b.get('skills', []):
                b['skills'] = sk
                stat['skills'] += len(sk)

            for rows in b['levels'].values():
                for row in rows:
                    for o in row:
                        n = o.get('note')
                        if n and not re.search('[А-Яа-я]', n):
                            ru = man['notes'].get(n)
                            if ru:
                                o['note'] = ru
                                stat['notes'] += 1
                            else:
                                missed['notes'].add(n)

    # описание из глоссария -> в сами выборы, чтобы карточка показывала русский текст
    dr = 0
    for c in d['characters']:
        for b in c['builds']:
            for rows in b['levels'].values():
                for row in rows:
                    for o in row:
                        g = d['glossary'].get(o['n'])
                        if g and g.get('descRu'):
                            o['dr'] = g['descRu']
                            dr += 1
    print('описаний проброшено в выборы:', dr)

    print('подставлено:', ', '.join(f'{k} {v}' for k, v in stat.items()))
    for k, s in missed.items():
        if s:
            print(f'  без ручного перевода ({k}, {len(s)}):', ', '.join(sorted(s)[:6]))
    d['meta']['ruManual'] = True
    json.dump(d, open('data.json', 'w', encoding='utf-8'),
              ensure_ascii=False, separators=(',', ':'))
    print('data.json обновлён')


if __name__ == '__main__':
    main()
