#!/usr/bin/env python3
"""Складывает справочник вещей в data.json (ключ "items").

Источники (лежат рядом, в tools/):
  items_wiki.json    — выгрузка с roguetrader.wh40k.wiki: описание, картинка,
                       тип, редкость, боевые характеристики оружия;
  items_ru_map.json  — русское название вещи -> статья на вики;
  items_ru.json      — перевод описаний на русский (может быть неполным).

Иконки лежат в icons/<slug>.webp, слаг считается из имени файла картинки.

Запуск:  python3 tools/build_items.py
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = os.path.join(ROOT, 'tools')

TYPE_RU = {
    'Gloves': 'Перчатки', 'Helmet': 'Шлем', 'Boots': 'Обувь', 'Cloak': 'Плащ',
    'Accessory': 'Аксессуар', 'Necklace': 'Шея', 'Augment': 'Аугментация',
    'Pet Protocol': 'Протокол питомца', 'Weapon': 'Оружие', 'Drug': 'Препарат',
    'Note': 'Записка',
}
RAR_RU = {'Common': 'обычная', 'Unique': 'уникальная', 'Pattern': 'особый образец'}
CLS_RU = {
    'Shotgun': 'дробовик', 'Pistol': 'пистолет', 'Arc Rifle': 'дуговая винтовка',
    'Sword': 'меч', 'Maul Or Hammer': 'молот', 'Psyker Staff': 'посох псайкера',
    'Knife': 'нож', 'Sniper Rifle': 'снайперская винтовка', 'Chainsaw': 'цепное',
}
HOLD_RU = {'Two Handed': 'двуручное', 'Single Handed': 'одноручное'}
DMG_RU = {
    'Rending': 'рассекающий', 'Impact': 'ударный', 'Shock': 'шоковый',
    'Energy': 'энергетический', 'Power': 'силовой', 'Piercing': 'пробивающий',
    'Fire': 'огонь', 'Toxic': 'токсический', 'Direct': 'прямой', 'Warp': 'варп',
}


def slug(pic):
    return re.sub(r'[^a-z0-9]+', '-', os.path.splitext(pic)[0].lower()).strip('-')


def load(name, default=None):
    p = os.path.join(T, name)
    if not os.path.exists(p):
        if default is None:
            sys.exit('нет файла ' + p)
        return default
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def main():
    wiki = load('items_wiki.json')
    ru_map = load('items_ru_map.json')
    ru_desc = load('items_ru.json', {})

    items, no_icon = {}, 0
    for ru_name, page in ru_map.items():
        w = wiki.get(page)
        if not w:
            continue
        o = {'n': page}
        ic = slug(w['pic']) if w.get('pic') else ''
        if ic and os.path.exists(os.path.join(ROOT, 'icons', ic + '.webp')):
            o['ic'] = ic
        elif ic:
            no_icon += 1
        if w.get('desc'):
            o['d'] = w['desc']
            if ru_desc.get(page):
                o['dr'] = ru_desc[page]
        t = TYPE_RU.get(w.get('type', ''), w.get('type', ''))
        if t:
            o['t'] = t
        if w.get('rar'):
            o['r'] = RAR_RU.get(w['rar'], w['rar'])
        if w.get('tpl') == 'Weapon':
            g = {}
            if w.get('minDamage') and w.get('maxDamage'):
                g['dmg'] = '%s–%s' % (w['minDamage'], w['maxDamage'])
            for src, dst in (('armourPenetration', 'ap'), ('dodgeReduction', 'dr'),
                             ('rateOfFire', 'rof'), ('maxRange', 'rng'), ('ammo', 'ammo')):
                if w.get(src) and w[src] not in ('0', '-1'):
                    g[dst] = w[src]
            cls = ' '.join(x for x in (
                HOLD_RU.get(w.get('holdingType', ''), ''),
                CLS_RU.get(w.get('classification', ''), ''),
            ) if x)
            if cls:
                g['cls'] = cls
            if w.get('damageType'):
                g['dt'] = DMG_RU.get(w['damageType'], w['damageType'])
            if g:
                o['w'] = g
        items[ru_name] = o

    used_icons = sorted({v['ic'] for v in items.values() if v.get('ic')})
    with open(os.path.join(ROOT, 'icons', 'list.json'), 'w', encoding='utf-8') as f:
        json.dump(used_icons, f, separators=(',', ':'))

    dpath = os.path.join(ROOT, 'data.json')
    with open(dpath, encoding='utf-8') as f:
        data = json.load(f)
    data['items'] = items
    with open(dpath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

    translated = sum(1 for v in items.values() if v.get('dr'))
    with_desc = sum(1 for v in items.values() if v.get('d'))
    print('вещей: %d, с иконкой: %d, с описанием: %d, переведено: %d, иконка потерялась: %d'
          % (len(items), sum(1 for v in items.values() if v.get('ic')),
             with_desc, translated, no_icon))


if __name__ == '__main__':
    main()
