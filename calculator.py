"""Raid planning for the game Rust. No third-party dependencies."""
from decimal import Decimal, InvalidOperation, ROUND_CEILING

TARGETS = [
    {'id': key, 'name': name, 'hp': hp, 'wall': key.endswith('wall')}
    for key, name, hp in [
        ('wood-door', 'Деревянная дверь', 200),
        ('metal-door', 'Железная дверь', 250),
        ('garage-door', 'Гаражная дверь', 600),
        ('armored-door', 'Бронированная дверь', 1000),
        ('wood-wall', 'Деревянная стена', 250),
        ('stone-wall', 'Каменная стена', 500),
        ('metal-wall', 'Металлическая стена', 1000),
        ('armored-wall', 'Бронированная стена', 2000),
    ]
]
TARGET_MAP = {target['id']: target for target in TARGETS}
WEAPONS = []


def register(key, name, category, sulfur=0, powder=0, counts=None, note=''):
    WEAPONS.append(dict(id=key, name=name, category=category, sulfur=sulfur,
                        powder=powder, counts=counts, note=note))


register('rocket', 'Ракета', 'Взрывчатка', 1400, 650, [1, 2, 3, 4, 2, 4, 8, 15])
register('c4', 'C4', 'Взрывчатка', 2200, 1000, [1, 1, 2, 2, 1, 2, 4, 8])
register('satchel', 'Сачель', 'Взрывчатка', 480, 240, [2, 4, 9, 12, 3, 10, 23, 46])
register('bean', 'Бобовая граната', 'Взрывчатка', 120, 60, [6, 18, 42, 56, 13, 46, 112, 223])
register('explosive-ammo', 'Разрывной патрон 5.56', 'Боеприпасы', 25, 10,
         [19, 63, 150, 250, 49, 185, 400, 800],
         'Расход ресурсов на один патрон; рецепт выпускает 2 патрона.')
# These profiles deliberately have no invented structural damage values.
for key, name, category in [
    ('gas', 'Газовый баллон', 'Взрывчатка'),
    ('f1', 'Граната F1', 'Взрывчатка'),
    ('he', '40-мм фугасная граната', 'Взрывчатка'),
    ('hv-rocket', 'Скоростная ракета', 'Взрывчатка'),
    ('incendiary-rocket', 'Зажигательная ракета', 'Огонь'),
    ('mlrs', 'Ракета РСЗО', 'Взрывчатка'),
    ('cannon', 'Пушечное ядро', 'Взрывчатка'),
    ('survey', 'Геологический заряд', 'Взрывчатка'),
    ('mine', 'Мина', 'Взрывчатка'),
    ('molotov', 'Коктейль Молотова', 'Огонь'),
    ('flamethrower', 'Огнемёт', 'Огонь'),
    ('incendiary-ammo', 'Зажигательный патрон 5.56', 'Боеприпасы'),
    ('rifle-ammo', 'Патрон 5.56', 'Боеприпасы'),
    ('hv-ammo', 'Скоростной патрон 5.56', 'Боеприпасы'),
    ('pistol-ammo', 'Пистолетный патрон', 'Боеприпасы'),
    ('pistol-hv', 'Скоростной пистолетный патрон', 'Боеприпасы'),
    ('pistol-fire', 'Зажигательный пистолетный патрон', 'Боеприпасы'),
    ('handmade', 'Самодельный патрон', 'Боеприпасы'),
    ('buckshot', 'Картечь 12-го калибра', 'Боеприпасы'),
    ('slug', 'Пуля 12-го калибра', 'Боеприпасы'),
    ('incendiary-shell', 'Зажигательный патрон 12-го калибра', 'Огонь'),
    ('wood-arrow', 'Деревянная стрела', 'Стрелы'),
    ('bone-arrow', 'Костяная стрела', 'Стрелы'),
    ('hv-arrow', 'Скоростная стрела', 'Стрелы'),
    ('fire-arrow', 'Огненная стрела', 'Огонь'),
    ('nail', 'Гвоздь', 'Боеприпасы'),
    ('rock', 'Камень', 'Инструменты'),
    ('stone-pickaxe', 'Каменная кирка', 'Инструменты'),
    ('pickaxe', 'Кирка', 'Инструменты'),
    ('icepick', 'Ледоруб', 'Инструменты'),
    ('jackhammer', 'Отбойный молоток', 'Инструменты'),
    ('stone-hatchet', 'Каменный топор', 'Инструменты'),
    ('hatchet', 'Топор', 'Инструменты'),
    ('salvaged-axe', 'Самодельный топор', 'Инструменты'),
    ('chainsaw', 'Бензопила', 'Инструменты'),
    ('wood-spear', 'Деревянное копьё', 'Ближний бой'),
    ('stone-spear', 'Каменное копьё', 'Ближний бой'),
    ('bone-knife', 'Костяной нож', 'Ближний бой'),
    ('combat-knife', 'Боевой нож', 'Ближний бой'),
    ('machete', 'Мачете', 'Ближний бой'),
    ('sword', 'Самодельный меч', 'Ближний бой'),
    ('cleaver', 'Самодельный тесак', 'Ближний бой'),
    ('mace', 'Булава', 'Ближний бой'),
    ('paddle', 'Весло', 'Ближний бой'),
    ('custom', 'Другое оружие / свой профиль', 'Свой профиль'),
]:
    register(key, name, category, note='Нужен фактический урон по выбранной цели; для пуль укажите оружие в заметке.')
WEAPON_MAP = {weapon['id']: weapon for weapon in WEAPONS}


def number(value, label, maximum=10000000):
    if isinstance(value, bool):
        raise ValueError(f'{label}: требуется число')
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f'{label}: требуется число') from None
    if not result.is_finite() or result < 0 or result > maximum:
        raise ValueError(f'{label}: число должно быть от 0 до {maximum}')
    return result


def calculate(payload):
    if not isinstance(payload, dict):
        raise ValueError('Ожидается объект запроса')
    weapon = WEAPON_MAP.get(payload.get('weapon'))
    if weapon is None:
        raise ValueError('Неизвестное средство рейда')
    rows = payload.get('rows')
    if not isinstance(rows, list) or not 1 <= len(rows) <= 100:
        raise ValueError('Добавьте от 1 до 100 целей')
    details, missing, total = [], [], 0
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError('Неверная цель')
        target = TARGET_MAP.get(row.get('target'))
        quantity = row.get('quantity')
        if target is None or type(quantity) is not int or not 1 <= quantity <= 1000:
            raise ValueError('Неверная цель или количество (1–1000)')
        side = row.get('side', 'hard')
        if side not in ('hard', 'soft'):
            raise ValueError('Неизвестная сторона стены')
        hp = number(row.get('hp', target['hp']), 'Здоровье', target['hp'])
        if hp == 0:
            raise ValueError('Здоровье должно быть больше нуля')
        damage = row.get('damage')
        if damage not in (None, ''):
            damage = number(damage, 'Урон')
            count = int((hp / damage).to_integral_value(rounding=ROUND_CEILING)) if damage else None
        elif weapon['counts'] and hp == target['hp']:
            count = weapon['counts'][TARGETS.index(target)]
        else:
            count = None
        if count is None:
            missing.append(target['name'])
        else:
            total += count * quantity
        details.append(dict(target=target['name'], side=side, quantity=quantity,
                            per_target=count, amount=count * quantity if count is not None else None))
    resources = payload.get('resources', {})
    if not isinstance(resources, dict):
        raise ValueError('Неверные ресурсы')
    # Unknown recipes stay unknown rather than appearing to cost zero sulfur.
    known_recipe = weapon['counts'] is not None
    sulfur = resources.get('sulfur', weapon['sulfur'] if known_recipe else None)
    powder = resources.get('powder', weapon['powder'] if known_recipe else None)
    sulfur = number(sulfur, 'Сера') if sulfur not in (None, '') else None
    powder = number(powder, 'Порох') if powder not in (None, '') else None
    if sulfur is not None and powder is not None and sulfur < powder * 2:
        raise ValueError('Сера всего должна включать серу для пороха (2 серы на 1 порох)')
    amount = None if missing else total
    return dict(amount=amount, sulfur=float(sulfur * amount) if sulfur is not None and amount is not None else None,
                powder=float(powder * amount) if powder is not None and amount is not None else None,
                charcoal=float(powder * amount * 3) if powder is not None and amount is not None else None,
                details=details, missing=missing, weapon=weapon['name'])
