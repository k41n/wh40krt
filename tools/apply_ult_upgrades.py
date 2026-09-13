#!/usr/bin/env python3
"""Улучшения абсолютных способностей.

Римская цифра рядом с ультой в таблице гайда («Death Waltz II», «Finest Hour IV»)
— это не ранг, а номер варианта улучшения, который игра предлагает выбрать на
этом уровне. Здесь к каждой такой записи подкладывается текст выбранного
варианта (tools/ult_upgrades.json, из wh40k.wiki), чтобы в приложении было
видно, что именно брать в окне выбора.

Запуск после apply_ru_manual.py (нужны русские названия), до feel.py:
  python3 tools/apply_ult_upgrades.py
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    ups = json.load(open(os.path.join(HERE, 'ult_upgrades.json'), encoding='utf-8'))
    ups = {k.lower(): v for k, v in ups.items() if not k.startswith('_')}
    d = json.load(open('data.json', encoding='utf-8'))
    hit, miss = 0, set()
    for c in d['characters']:
        for b in c['builds']:
            for alts in b['levels'].values():
                for alt in alts:
                    for e in alt:
                        if e.get('t') != 'ult' or not e.get('r'):
                            continue
                        n = e['n'].lower()
                        key = next((k for k in ups if k.startswith(n) or n.startswith(k)), None)
                        v = ups.get(key, {}).get(e['r']) if key else None
                        if not v:
                            miss.add((e['n'], e['r']))
                            continue
                        e['ud'], e['udr'] = v
                        hit += 1
    json.dump(d, open('data.json', 'w', encoding='utf-8'),
              ensure_ascii=False, separators=(',', ':'))
    print('upgrades', hit, 'missed', sorted(miss))


if __name__ == '__main__':
    main()
