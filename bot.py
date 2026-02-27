import requests
import time
import json
import random
import string
import os
import threading
from datetime import datetime, timedelta  # ← ПРАВИЛЬНО

TOKEN = "8466725404:AAFsxikWr8541rgTZcpxZdBXqdO-1qra4Mo"
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID", "-1003117157578")
WITHDRAW_BOT_USERNAME = "OksajdShop_Raketa_bot"
BOT_USERNAME = "Raketa_oxide_bot"
STATS_CHANNEL_ID = "-1003676758694"
STATS_MESSAGE_ID = 28
MAIN_GROUP_ID = "-1003117157578"
GROUP_INVITE_LINK = "https://t.me/+bjAMAhtua9xmNzgy"
MARKET_CHANNEL_ID = "-1003492123267"
MARKET_MESSAGE_ID = 44

# ===== КЕЙС СИСТЕМА =====
CASE_COOLDOWN_FILE = "case_cooldown.json"

ADMIN_IDS = ["6319679398", "6999365345", "6763713561", "8400606365"]

# Настройки шансов (можно менять через команды админа)
CHANCE_SETTINGS = {
    "slots_win_chance": 40,  # шанс выигрыша в слотах в %
    "slots_jackpot_chance": 5,  # шанс джекпота в слотах в %
    "coinflip_win_chance": 50,  # шанс выигрыша в монетке в %
    "dice_win_threshold": 10,  # порог выигрыша в костях (сумма >= этому значению)
    "roulette_red_black_chance": 48.6,  # шанс выпадения красного/черного в рулетке
    "treasury_rob_success": 30,  # шанс успешного ограбления казны в %
     "treasury_rob_escape": 30,  # шанс сбежать при ограблении казны в %
    "treasury_rob_caught": 40  # шанс быть пойманным при ограблении казны в %
}

ADMIN_PRICES = {
    'mute': 50,
    'ban': 100,
    'kick': 15,
    'delete': 5,
    'unmute': 20,
    'unban': 40
}

# ===== МУТ СИСТЕМА =====
MUTE_PRICE_PER_MINUTE = 100  # цена за 1 минуту мута
UNMUTE_PRICE = 500  # цена за размут
SELF_UNMUTE_PRICE = 1000  # цена за саморозмут в ЛС  <-- ДОБАВЬТЕ ЭТУ СТРОКУ

# ===== SECRET CHANCE SYSTEM =====
SECRET_CHANCES_FILE = "secret_chances.json"

# ===== КЕЙС СИСТЕМА =====
CASE_COOLDOWN_FILE = "case_cooldown.json"

def load_secret_chances():
    """Загрузить тайные шансы пользователей"""
    if os.path.exists(SECRET_CHANCES_FILE):
        try:
            with open(SECRET_CHANCES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_secret_chances(secret_chances):
    """Сохранить тайные шансы пользователей"""
    with open(SECRET_CHANCES_FILE, 'w', encoding='utf-8') as f:
        json.dump(secret_chances, f, ensure_ascii=False, indent=2)

def get_user_chances(user_id):
    """Получить реальные шансы для пользователя (тайные или публичные)"""
    secret_chances = load_secret_chances()
    user_id_str = str(user_id)

    # Если у пользователя есть тайные шансы
    if user_id_str in secret_chances:
        # Создаем копию публичных шансов
        user_chances = CHANCE_SETTINGS.copy()

        # Заменяем только те шансы, которые установлены в тайных
        for key, value in secret_chances[user_id_str].items():
            if key in user_chances:
                user_chances[key] = value

        return user_chances
    else:
        # Возвращаем публичные шансы
        return CHANCE_SETTINGS.copy()

# ===== КЕЙС СИСТЕМА ФУНКЦИИ =====
def load_case_cooldown():
    """Загрузить кто уже получил кейс"""
    if os.path.exists(CASE_COOLDOWN_FILE):
        try:
            with open(CASE_COOLDOWN_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_case_cooldown(case_data):
    """Сохранить данные о полученных кейсах"""
    with open(CASE_COOLDOWN_FILE, 'w', encoding='utf-8') as f:
        json.dump(case_data, f, ensure_ascii=False, indent=2)

def has_received_case(user_id):
    """Проверить, получал ли пользователь кейс"""
    case_data = load_case_cooldown()
    return str(user_id) in case_data

def mark_case_received(user_id):
    """Пометить что пользователь получил кейс"""
    case_data = load_case_cooldown()
    case_data[str(user_id)] = {
        "received_at": datetime.now().isoformat(),
        "opened": False,
        "gift_received": None
    }
    save_case_cooldown(case_data)

def mark_case_opened(user_id, gift_id):
    """Пометить что пользователь открыл кейс"""
    case_data = load_case_cooldown()
    user_id_str = str(user_id)
    if user_id_str in case_data:
        case_data[user_id_str]["opened"] = True
        case_data[user_id_str]["gift_received"] = gift_id
        case_data[user_id_str]["opened_at"] = datetime.now().isoformat()
        save_case_cooldown(case_data)

def get_random_gift_from_case():
    """Получить случайный подарок из кейса (обновленная версия для 15 подарков)"""
    import random

    # Всего 15 подарков
    # Распределение шансов:
    # - Легендарные (1-2): 5% шанс каждый (в сумме 10%)
    # - Эпические (3-7, 11-15): 6% шанс каждый (в сумме 60%)
    # - Редкие (8-10): 10% шанс каждый (в сумме 30%)

    # Создаем список с весами для каждого подарка
    gifts_with_weights = []

    for gift_id in range(1, 16):
        if gift_id <= 2:  # Легендарные
            weight = 5  # 5% шанс
        elif gift_id <= 7 or gift_id >= 11:  # Эпические
            weight = 6  # 6% шанс
        else:  # Редкие (8-10)
            weight = 10  # 10% шанс

        gifts_with_weights.extend([gift_id] * weight)

    # Выбираем случайный подарок с учетом весов
    return random.choice(gifts_with_weights)

def handle_case_command(data, message):
    """Получить кейс (можно только 1 раз)"""
    user_id = str(message["from"]["id"])
    user = get_user(data, user_id)
    user_emoji = get_user_emoji(user)

    # Проверяем, получал ли уже кейс
    if has_received_case(user_id):
        send_message(
            message["chat"]["id"],
            f"{user_emoji} ❌ Вы уже получали кейс!\n\n"
            f"💡 Чтобы открыть кейс: `открыть кейс`",
            reply_to=message["message_id"],
            parse_mode="Markdown"
        )
        return

    # Помечаем что получил кейс
    mark_case_received(user_id)

    send_message(
        message["chat"]["id"],
        f"{user_emoji} 🎉 ПОЗДРАВЛЯЕМ! 🎉\n\n"
        f"✨ Вы получили **Эксклюзивный кейс**!\n\n"
        f"📦 Что внутри:\n"
        f"• 1 случайный подарок из 10\n"
        f"• Все подарки имеют равный шанс 10%\n"
        f"• Можно получить только 1 раз\n\n"
        f"💡 Чтобы открыть кейс: `открыть кейс`\n\n"
        f"⚠️ **Кейс можно открыть только 1 раз!**",
        reply_to=message["message_id"],
        parse_mode="Markdown"
    )

def handle_open_case_command(data, message):
    """Открыть кейс"""
    user_id = str(message["from"]["id"])
    user = get_user(data, user_id)
    user_emoji = get_user_emoji(user)

    # Проверяем, получал ли кейс
    if not has_received_case(user_id):
        send_message(
            message["chat"]["id"],
            f"{user_emoji} ❌ У вас нет кейса!\n\n"
            f"💡 Чтобы получить кейс: `кейс`\n"
            f"📦 Кейс можно получить только 1 раз!",
            reply_to=message["message_id"],
            parse_mode="Markdown"
        )
        return

    # Проверяем, не открывал ли уже
    case_data = load_case_cooldown()
    user_case = case_data.get(str(user_id), {})

    if user_case.get("opened", False):
        gift_id = user_case.get("gift_received")
        if gift_id and gift_id in GIFTS:
            gift = GIFTS[gift_id]
            gift_display = format_gift_with_custom_emoji(gift_id)

            send_message(
                message["chat"]["id"],
                f"{user_emoji} ❌ Вы уже открывали кейс!\n\n"
                f"📦 Вы получили: {gift_display}\n"
                f"🎁 Этот подарок уже у вас в профиле",
                reply_to=message["message_id"],
                parse_mode="HTML"
            )
        else:
            send_message(
                message["chat"]["id"],
                f"{user_emoji} ❌ Вы уже открывали кейс!",
                reply_to=message["message_id"]
            )
        return

    # Открываем кейс - получаем случайный подарок
    gift_id = get_random_gift_from_case()
    gift = GIFTS[gift_id]

    # Добавляем подарок пользователю
    if "gifts" not in user:
        user["gifts"] = []

    if gift_id not in user["gifts"]:
        user["gifts"].append(gift_id)
    else:
        # Если уже есть такой подарок, пробуем другой (максимум 3 попытки)
        for _ in range(3):
            gift_id = get_random_gift_from_case()
            if gift_id not in user["gifts"]:
                gift = GIFTS[gift_id]
                user["gifts"].append(gift_id)
                break

    # Помечаем кейс как открытый
    mark_case_opened(user_id, gift_id)
    save_data(data)

    # Форматируем подарок
    gift_display = format_gift_with_custom_emoji(gift_id)

    # Создаем анимацию открытия
    send_message(
        message["chat"]["id"],
        f"{user_emoji} 🎁 ОТКРЫВАЕМ КЕЙС...\n\n"
        f"✨ Магия случая...",
        reply_to=message["message_id"]
    )

    time.sleep(2)

    # Результат
    send_message(
        message["chat"]["id"],
        f"{user_emoji} 🎉 КЕЙС ОТКРЫТ! 🎉\n\n"
        f"✨ Поздравляем! Вы получили:\n\n"
        f"{gift_display}\n"
        f"📊 Редкость: {gift['rarity']}\n\n"
        f"💝 Подарок добавлен в ваш профиль!\n"
        f"🎮 Это был ваш единственный кейс!",
        reply_to=message["message_id"],
        parse_mode="HTML"
    )

def handle_my_case_command(data, message):
    """Показать статус кейса"""
    user_id = str(message["from"]["id"])
    user = get_user(data, user_id)
    user_emoji = get_user_emoji(user)

    case_data = load_case_cooldown()
    user_case = case_data.get(str(user_id))

    if not user_case:
        send_message(
            message["chat"]["id"],
            f"{user_emoji} 📦 Статус кейса:\n\n"
            f"❌ Кейс не получен\n\n"
            f"💡 Чтобы получить кейс: `кейс`\n"
            f"🎁 Можно получить только 1 раз!",
            reply_to=message["message_id"],
            parse_mode="Markdown"
        )
        return

    if user_case.get("opened", False):
        gift_id = user_case.get("gift_received")
        if gift_id and gift_id in GIFTS:
            gift = GIFTS[gift_id]
            gift_display = format_gift_with_custom_emoji(gift_id)
            opened_at = user_case.get("opened_at", "неизвестно")

            try:
                date_obj = datetime.fromisoformat(opened_at)
                date_str = date_obj.strftime("%d.%m.%Y %H:%M")
            except:
                date_str = opened_at

            send_message(
                message["chat"]["id"],
                f"{user_emoji} 📦 Статус кейса:\n\n"
                f"✅ Кейс открыт {date_str}\n\n"
                f"🎁 Вы получили: {gift_display}\n"
                f"📊 Редкость: {gift['rarity']}\n\n"
                f"⚠️ Кейс можно получить только 1 раз!",
                reply_to=message["message_id"],
                parse_mode="HTML"
            )
    else:
        received_at = user_case.get("received_at", "неизвестно")
        try:
            date_obj = datetime.fromisoformat(received_at)
            date_str = date_obj.strftime("%d.%m.%Y %H:%M")
        except:
            date_str = received_at

        send_message(
            message["chat"]["id"],
            f"{user_emoji} 📦 Статус кейса:\n\n"
            f"📦 Кейс получен {date_str}\n"
            f"🔒 Еще не открыт\n\n"
            f"💡 Чтобы открыть: `открыть кейс`\n"
            f"🎁 Внутри случайный подарок!",
            reply_to=message["message_id"],
            parse_mode="Markdown"
        )

BUSINESS_LEVELS = {
    0: {
        'name': 'Нет бизнеса',
        'income': 0,
        'buy_price': 0,
        'upgrade_price': 0,
        'max_items': 0,
        'description': 'Отсутствует',
        'employees': 0,
        'upkeep': 0
    },
    # Уровни 1-5: Начальные бизнесы (окупаемость: 20-24 часа)
    1: {
        'name': '🏪 Уличный ларёк',
        'income': 20,  # Было 100 (слишком много)
        'buy_price': 500,  # Окупаемость: 50 часов
        'upgrade_price': 0,
        'max_items': 1,
        'description': 'Маленький ларёк с фастфудом',
        'employees': 1,
        'upkeep': 2  # 20% от дохода
    },
    2: {
        'name': '🍕 Пиццерия-фудтрак',
        'income': 50,  # Было 250
        'buy_price': 1500,
        'upgrade_price': 1000,
        'max_items': 2,
        'description': 'Мобильная пиццерия',
        'employees': 2,
        'upkeep': 5  # 20% от дохода
    },
    3: {
        'name': '☕ Кофейня',
        'income': 100,  # Было 500
        'buy_price': 3000,
        'upgrade_price': 1500,
        'max_items': 3,
        'description': 'Небольшая уютная кофейня',
        'employees': 3,
        'upkeep': 10
    },
    4: {
        'name': '🍔 Бургерная',
        'income': 160,  # Было 700
        'buy_price': 6000,
        'upgrade_price': 3000,
        'max_items': 3,
        'description': 'Кафе быстрого питания',
        'employees': 4,
        'upkeep': 16
    },
    5: {
        'name': '🏪 Круглосуточный магазин',
        'income': 240,  # Было 1500
        'buy_price': 12000,
        'upgrade_price': 6000,
        'max_items': 4,
        'description': 'Магазин 24/7',
        'employees': 5,
        'upkeep': 24
    },
    # Уровни 6-10: Средний бизнес (окупаемость: 18-22 часа)
    6: {
        'name': '🍽️ Ресторан',
        'income': 260,
        'buy_price': 20000,
        'upgrade_price': 8000,
        'max_items': 5,
        'description': 'Ресторан среднего класса',
        'employees': 8,
        'upkeep': 36
    },
    7: {
        'name': '🏢 Офисное помещение',
        'income': 500,
        'buy_price': 30000,
        'upgrade_price': 10000,
        'max_items': 6,
        'description': 'Офис в бизнес-центре',
        'employees': 10,
        'upkeep': 50
    },
    8: {
        'name': '🛒 Супермаркет',
        'income': 700,
        'buy_price': 50000,
        'upgrade_price': 20000,
        'max_items': 7,
        'description': 'Средний супермаркет',
        'employees': 15,
        'upkeep': 70
    },
    9: {
        'name': '🏪 Мини-маркет сеть',
        'income': 1000,
        'buy_price': 80000,
        'upgrade_price': 30000,
        'max_items': 8,
        'description': 'Несколько магазинов по городу',
        'employees': 20,
        'upkeep': 100
    },
    10: {
        'name': '🏢 Бизнес-центр',
        'income': 1400,
        'buy_price': 120000,
        'upgrade_price': 40000,
        'max_items': 9,
        'description': 'Небольшой бизнес-центр',
        'employees': 25,
        'upkeep': 140
    },
    # Уровни 11-15: Крупный бизнес (окупаемость: 16-20 часов)
    11: {
        'name': '🏨 Гостиница 3*',
        'income': 2000,
        'buy_price': 180000,
        'upgrade_price': 60000,
        'max_items': 10,
        'description': 'Трёхзвёздочная гостиница',
        'employees': 30,
        'upkeep': 200
    },
    12: {
        'name': '🏭 Производственный цех',
        'income': 3000,
        'buy_price': 250000,
        'upgrade_price': 70000,
        'max_items': 11,
        'description': 'Небольшое производство',
        'employees': 35,
        'upkeep': 300
    },
    13: {
        'name': '🛒 Торговый центр',
        'income': 4400,
        'buy_price': 350000,
        'upgrade_price': 100000,
        'max_items': 12,
        'description': 'Средний торговый центр',
        'employees': 50,
        'upkeep': 440
    },
    14: {
        'name': '🏢 Офисный небоскрёб',
        'income': 6400,
        'buy_price': 500000,
        'upgrade_price': 150000,
        'max_items': 13,
        'description': 'Высотное офисное здание',
        'employees': 70,
        'upkeep': 640
    },
    15: {
        'name': '🔞Секс-шоп',
        'income': 4500,
        'buy_price': 700000,
        'upgrade_price': 200000,
        'max_items': 14,
        'description': 'Компания секс-игрушек',
        'employees': 90,
        'upkeep': 900
    },
    # Уровни 16-20: Корпорации (окупаемость: 14-18 часов)
    16: {
        'name': '🏨 Гостиничная сеть',
        'income': 6500,
        'buy_price': 1000000,
        'upgrade_price': 300000,
        'max_items': 15,
        'description': 'Сеть отелей по стране',
        'employees': 120,
        'upkeep': 1300
    },
    17: {
        'name': '🏭 Промышленный завод',
        'income': 9000,
        'buy_price': 1500000,
        'upgrade_price': 500000,
        'max_items': 16,
        'description': 'Крупное производственное предприятие',
        'employees': 160,
        'upkeep': 1800
    },
    18: {
        'name': '🛒 Сеть гипермаркетов',
        'income': 13000,
        'buy_price': 2200000,
        'upgrade_price': 700000,
        'max_items': 17,
        'description': 'Сеть крупных магазинов',
        'employees': 220,
        'upkeep': 2600
    },
    19: {
        'name': '🏢 Деловой квартал',
        'income': 19000,
        'buy_price': 3200000,
        'upgrade_price': 1000000,
        'max_items': 18,
        'description': 'Целый квартал офисных зданий',
        'employees': 300,
        'upkeep': 3800
    },
    20: {
        'name': '✈️ Авиакомпания',
        'income': 28000,
        'buy_price': 4500000,
        'upgrade_price': 1300000,
        'max_items': 20,
        'description': 'Международная авиакомпания',
        'employees': 400,
        'upkeep': 5600
    },
    # Уровни 21-25: Мега-корпорации (окупаемость: 12-16 часов)
    21: {
        'name': '🏦 Банковский холдинг',
        'income': 40000,
        'buy_price': 6000000,
        'upgrade_price': 1500000,
        'max_items': 22,
        'description': 'Финансовая группа',
        'employees': 500,
        'upkeep': 8000
    },
    22: {
        'name': '⚡ Энергетическая корпорация',
        'income': 55000,
        'buy_price': 8000000,
        'upgrade_price': 2000000,
        'max_items': 24,
        'description': 'Поставщик энергии',
        'employees': 650,
        'upkeep': 11000
    },
    23: {
        'name': '🏗️ Строительный концерн',
        'income': 75000,
        'buy_price': 11000000,
        'upgrade_price': 3000000,
        'max_items': 26,
        'description': 'Крупнейшая строительная компания',
        'employees': 850,
        'upkeep': 15000
    },
    24: {
        'name': '🚗 Автомобильный концерн',
        'income': 100000,
        'buy_price': 15000000,
        'upgrade_price': 4000000,
        'max_items': 28,
        'description': 'Производитель автомобилей',
        'employees': 1100,
        'upkeep': 20000
    },
    25: {
        'name': '👑 Империя миллиардера',
        'income': 140000,
        'buy_price': 20000000,
        'upgrade_price': 5000000,
        'max_items': 30,
        'description': 'Финансовая империя',
        'employees': 1500,
        'upkeep': 28000
    },
    # Уровни 26-30: Глобальные корпорации (окупаемость: 10-14 часов)
    26: {
        'name': '🌍 Транснациональная корпорация',
        'income': 200000,
        'buy_price': 28000000,
        'upgrade_price': 8000000,
        'max_items': 32,
        'description': 'Корпорация с филиалами по всему миру',
        'employees': 2000,
        'upkeep': 40000
    },
    27: {
        'name': '🛰️ Космическая компания',
        'income': 280000,
        'buy_price': 40000000,
        'upgrade_price': 12000000,
        'max_items': 34,
        'description': 'Освоение космоса и спутники',
        'employees': 2800,
        'upkeep': 56000
    },
    28: {
        'name': '⚕️ Фармацевтический гигант',
        'income': 400000,
        'buy_price': 55000000,
        'upgrade_price': 15000000,
        'max_items': 36,
        'description': 'Крупнейший производитель лекарств',
        'employees': 3800,
        'upkeep': 80000
    },
    29: {
        'name': '💻 Технологическая империя',
        'income': 550000,
        'buy_price': 75000000,
        'upgrade_price': 20000000,
        'max_items': 38,
        'description': 'IT-гигант мирового масштаба',
        'employees': 5000,
        'upkeep': 110000
    },
    30: {
        'name': '👑 Всемирный конгломерат',
        'income': 750000,
        'buy_price': 100000000,
        'upgrade_price': 25000000,
        'max_items': 40,
        'description': 'Крупнейший бизнес в мире',
        'employees': 7000,
        'upkeep': 150000
    }
}

# ===== BUSINESS TYPES =====
BUSINESS_TYPES = {
    'food': {
        'name': '🍕 Ресторанный бизнес',
        'bonus': '+10% к доходу',
        'levels': [1, 2, 3, 4, 6, 11]
    },
    'retail': {
        'name': '🛒 Розничная торговля',
        'bonus': '+8% к доходу',
        'levels': [5, 8, 9, 13, 18]
    },
    'office': {
        'name': '🏢 Офисный бизнес',
        'bonus': '+7% к доходу',
        'levels': [7, 10, 14, 19]
    },
    'industrial': {
        'name': '🏭 Промышленность',
        'bonus': '+12% к доходу',
        'levels': [12, 17, 22, 23, 24]
    },
    'transport': {
        'name': '✈️ Транспорт',
        'bonus': '+9% к доходу',
        'levels': [15, 20]
    },
    'finance': {
        'name': '🏦 Финансы',
        'bonus': '+15% к доходу',
        'levels': [21, 25, 26]
    },
    'tech': {
        'name': '💻 Технологии',
        'bonus': '+20% к доходу',
        'levels': [27, 28, 29, 30]
    }
}

# ===== КАСТОМНЫЕ ЭМОДЗИ ПОДАРКОВ =====
def format_gift_with_custom_emoji(gift_id):
    """Форматировать подарок с кастомным эмодзи"""
    if gift_id in GIFTS:
        gift = GIFTS[gift_id]
        if 'custom_emoji' in gift:
            return f"{gift['custom_emoji']} {gift['name']}"
        else:
            return f"{gift['emoji']} {gift['name']}"
    return "🎁 Неизвестный подарок"

def format_user_gifts_with_custom_emoji(gifts_list):
    """Форматировать список подарков с кастомными эмодзи"""
    if not gifts_list:
        return "Нет подарков"

    formatted_gifts = []
    for gift_id in gifts_list:
        if gift_id in GIFTS:
            gift = GIFTS[gift_id]
            if 'custom_emoji' in gift:
                formatted_gifts.append(f"{gift['custom_emoji']}")
            else:
                formatted_gifts.append(f"{gift['emoji']}")

    return " ".join(formatted_gifts) if formatted_gifts else "Нет подарков"

def get_profile_decoration_custom(user_data):
    """Получить украшение профиля с кастомными эмодзи"""
    gifts = user_data.get("gifts", [])
    if not gifts:
        return "⚪"

    # Ищем лучший подарок
    rarity_order = {
        'Легендарный': 0,
        'Эпический': 1,
        'Редкий': 2,
        'Обычный': 3
    }
    best_gift = None
    best_rarity = 4

    for gift_id in gifts:
        if gift_id in GIFTS:
            gift = GIFTS[gift_id]
            rarity_rank = rarity_order.get(gift['rarity'], 4)
            if rarity_rank < best_rarity:
                best_rarity = rarity_rank
                best_gift = gift

    if best_gift:
        if 'custom_emoji' in best_gift:
            # Берем только эмодзи без текста
            return best_gift['custom_emoji']
        else:
            return best_gift['emoji']
    return "👤"

def get_business_type(level):
    """Определяет тип бизнеса по уровню"""
    for biz_type, info in BUSINESS_TYPES.items():
        if level in info['levels']:
            return biz_type
    return None

GIFTS = {
    1: {
        'name': 'Кристал',
        'emoji': '💎',
        'rarity': 'Легендарный',
        'color': '🔵',
        'custom_emoji': '<tg-emoji emoji-id="5201914481671682382">💎</tg-emoji>'
    },
    2: {
        'name': 'Корона',
        'emoji': '👑',
        'rarity': 'Легендарный',
        'color': '🟡',
        'custom_emoji': '<tg-emoji emoji-id="5433758796289685818">👑</tg-emoji>'
    },
    3: {
        'name': 'Звезда',
        'emoji': '🌟',
        'rarity': 'Эпический',
        'color': '🟣',
        'custom_emoji': '<tg-emoji emoji-id="5438496463044752972">🌟</tg-emoji>'
    },
    4: {
        'name': 'Магический шар',
        'emoji': '🔮',
        'rarity': 'Эпический',
        'color': '🟣',
        'custom_emoji': '<tg-emoji emoji-id="5350367161514732241">🔮</tg-emoji>'
    },
    5: {
        'name': 'Бабочка',
        'emoji': '🦋',
        'rarity': 'Эпический',  # Повышен до Эпического
        'color': '🔵',
        'custom_emoji': '<tg-emoji emoji-id="5271783484929615967">🦋</tg-emoji>'
    },
    6: {
        'name': 'Глаз',
        'emoji': '👁️',
        'rarity': 'Эпический',  # Повышен до Эпического
        'color': '🩷',
        'custom_emoji': '<tg-emoji emoji-id="5472306823555985042">👁️</tg-emoji>'
    },
    7: {
        'name': 'Пламя',
        'emoji': '🔥',
        'rarity': 'Эпический',  # Повышен до Эпического
        'color': '🟠',
        'custom_emoji': '<tg-emoji emoji-id="5379576216187594028">🔥</tg-emoji>'
    },
    8: {
        'name': 'Снежинка',
        'emoji': '❄️',
        'rarity': 'Редкий',  # Изменено с Обычного на Редкий
        'color': '⚪',
        'custom_emoji': '<tg-emoji emoji-id="5449449325434266744">❄️</tg-emoji>'
    },
    9: {
        'name': 'Клевер удачи',
        'emoji': '🍀',
        'rarity': 'Редкий',  # Изменено с Обычного на Редкий
        'color': '🟢',
        'custom_emoji': '<tg-emoji emoji-id="5458585073060160944">🍀</tg-emoji>'
    },
    10: {
        'name': 'Маска',
        'emoji': '🙂',
        'rarity': 'Редкий',  # Изменено с Обычного на Редкий
        'color': '⚫',
        'custom_emoji': '<tg-emoji emoji-id="5195297345817816825">🙂</tg-emoji>'
    },
    # ===== НОВЫЕ 5 ПОДАРКОВ (все Эпические) =====
    11: {
        'name': 'Зелье',
        'emoji': '🧪',
        'rarity': 'Эпический',
        'color': '🟣',
        'custom_emoji': '<tg-emoji emoji-id="5258208871423425369">🧪</tg-emoji>'
    },
    12: {
        'name': 'Леденец',
        'emoji': '🍭',
        'rarity': 'Эпический',
        'color': '🟣',
        'custom_emoji': '<tg-emoji emoji-id="5230974475209554508">🍭</tg-emoji>'
    },
    13: {
        'name': 'Луна',
        'emoji': '🌛',
        'rarity': 'Эпический',
        'color': '🟣',
        'custom_emoji': '<tg-emoji emoji-id="5238162283368035495">🌛</tg-emoji>'
    },
    14: {
        'name': 'Метла',
        'emoji': '🧹',
        'rarity': 'Эпический',
        'color': '🟣',
        'custom_emoji': '<tg-emoji emoji-id="5278491193053822590">🧹</tg-emoji>'
    },
    15: {
        'name': 'Черный кот',
        'emoji': '🐈‍⬛',
        'rarity': 'Эпический',
        'color': '🟣',
        'custom_emoji': '<tg-emoji emoji-id="5256041592271157291">🐈‍⬛</tg-emoji>'
    }
}

# ===== ПОДАРКИ ИВЕНТА 23 ФЕВРАЛЯ =====
EVENT_GIFTS = {
    # За особые задания
    "order_of_courage": {
        "name": "🎖️ Орден Мужества",
        "emoji": "🎖️",
        "custom_emoji": '<tg-emoji emoji-id="5238027455754680851">🎖️</tg-emoji>',
        "rarity": "Эпический",
        "description": "За 100 ставок в казино"
    },
    "gold_star": {
        "name": "⭐ Золотая Звезда",
        "emoji": "⭐",
        "custom_emoji": '<tg-emoji emoji-id="5316755348751665833">✨</tg-emoji>',
        "rarity": "Легендарный",
        "description": "За 50,000 ₽ выигрыша"
    },
    "assault_badge": {
        "name": "⚡ Знак Штурма",
        "emoji": "⚡",
        "custom_emoji": '<tg-emoji emoji-id="5408884759482868280">⚡️</tg-emoji>',
        "rarity": "Редкий",
        "description": "За 10 ограблений"
    },
    "marshal_star": {
        "name": "👑 Маршальская Звезда",
        "emoji": "👑",
        "custom_emoji": '<tg-emoji emoji-id="5431782733376399004">🇨🇳</tg-emoji>',
        "rarity": "Легендарный",
        "description": "За 15 уровень бизнеса"
    },
    "supply_chest": {
        "name": "📦 Ящик Интенданта",
        "emoji": "📦",
        "custom_emoji": '<tg-emoji emoji-id="5372855983938759801">📦</tg-emoji>',
        "rarity": "Эпический",
        "description": "За 10 подарков в коллекции"
    },
    
    # ТОП-5 ПОДАРКИ
    "victory_sword": {
        "name": "⚔️ Меч Победы",
        "emoji": "⚔️",
        "custom_emoji": '<tg-emoji emoji-id="5201914481671682382">⚔️</tg-emoji>',
        "rarity": "🔴 ЛЕГЕНДАРНЫЙ",
        "description": "Только для 1 места в ивенте!"
    },
    "front_command": {
        "name": "🧭 Фронтовой Компас",
        "emoji": "🧭",
        "custom_emoji": '<tg-emoji emoji-id="5438496463044752972">🧭</tg-emoji>',
        "rarity": "🟣 ЛЕГЕНДАРНЫЙ",
        "description": "Только для 2 места в ивенте!"
    },
    "army_command": {
        "name": "📯 Армейский Рожок",
        "emoji": "📯",
        "custom_emoji": '<tg-emoji emoji-id="5433758796289685818">📯</tg-emoji>',
        "rarity": "🟣 ЭПИЧЕСКИЙ",
        "description": "Только для 3 места в ивенте!"
    },
    "staff_badge": {
        "name": "🗺️ Штабная Карта",
        "emoji": "🗺️",
        "custom_emoji": '<tg-emoji emoji-id="5271783484929615967">🗺️</tg-emoji>',
        "rarity": "🔵 ЭПИЧЕСКИЙ",
        "description": "Только для 4 места в ивенте!"
    },
    "deputy_badge": {
        "name": "🔭 Полевой Бинокль",
        "emoji": "🔭",
        "custom_emoji": '<tg-emoji emoji-id="5458585073060160944">🔭</tg-emoji>',
        "rarity": "🟢 РЕДКИЙ",
        "description": "Только для 5 места в ивенте!"
    }
}

# Добавляем подарки ивента в основной словарь GIFTS
# Находим последний ID в GIFTS и добавляем новые
current_max_id = max(GIFTS.keys()) if GIFTS else 0
for i, (key, gift) in enumerate(EVENT_GIFTS.items(), start=current_max_id + 1):
    GIFTS[i] = gift

# Добавляем подарки ивента в основной словарь GIFTS
# Нужно найти в коде место, где определён словарь GIFTS, и добавить туда эти подарки
# Например, после последнего подарка (15) добавить:

# 16-20: Подарки ивента
GIFTS.update({
    16: EVENT_GIFTS["order_of_courage"],
    17: EVENT_GIFTS["gold_star"],
    18: EVENT_GIFTS["assault_badge"],
    19: EVENT_GIFTS["marshal_star"],
    20: EVENT_GIFTS["supply_chest"],
    21: EVENT_GIFTS["victory_sword"],
    22: EVENT_GIFTS["front_command"],
    23: EVENT_GIFTS["army_command"],
    24: EVENT_GIFTS["staff_badge"],
    25: EVENT_GIFTS["deputy_badge"]
})

# ===== BOOSTERS SYSTEM =====
BOOSTERS = {
    "lucky_charm": {
        "name": "Талисман удачи 🍀",
        "price": 10000,
        "duration": 1800,  # 1 час
        "effect": "+15% к шансам во всех играх",
        "emoji": "🍀",
        "bonus_chance": 15
    },
    "double_income": {
        "name": "Двойной доход 💰",
        "price": 25000,
        "duration": 1440,  # 2 часа
        "effect": "×2 доход от бизнеса",
        "emoji": "💰",
        "multiplier": 2
    },
    "rainbow_bet": {
        "name": "Радужная ставка 🌈",
        "price": 50000,
        "duration": 1800,  # 30 минут
        "effect": "Выигрыш ×3 в слотах",
        "emoji": "🌈",
        "multiplier": 3
    }
}

# ===== CONVENIENCE UPGRADES =====
CONVENIENCE = {
    "lottery_access": {
        "name": "🎫 Доступ к лотерее",
        "price": 5000,
        "effect": "Разблокирует доступ к участию в лотереях",
        "emoji": "🎫"
    },
    "auto_collect": {
        "name": "Авто-сбор доходов",
        "price": 75000,
        "effect": "Автоматически собирает доход каждые 4 часа",
        "emoji": "🤖"
    },
    "batch_processing": {
        "name": "Пакетная обработка",
        "price": 50000,
        "effect": "Продавать несколько товаров сразу",
        "emoji": "📦"
    },
    "analytics_dashboard": {
        "name": "Панель аналитики",
        "price": 100000,
        "effect": "Подробная статистика доходов/расходов",
        "emoji": "📊"
    }
}

# ===== ACHIEVEMENTS SYSTEM =====
ACHIEVEMENTS = {
    "first_deposit": {
        "name": "Первый шаг 💳",
        "description": "Пополнить баланс в первый раз",
        "reward": 500,
        "emoji": "💳",
        "condition": "total_deposited >= 1",
        "hidden": False
    },
    "business_owner": {
        "name": "Предприниматель 🏢",
        "description": "Купить первый бизнес",
        "reward": 1000,
        "emoji": "🏢",
        "condition": "business_level >= 1",
        "hidden": False
    },
    "casino_king": {
        "name": "Король казино 🎰",
        "description": "Выиграть 10,000₽ в казино",
        "reward": 2000,
        "emoji": "🎰",
        "condition": "casino_wins >= 10000",
        "hidden": False
    },
    "market_master": {
        "name": "Мастер рынка 🛍️",
        "description": "Продать 10 товаров на маркетплейсе",
        "reward": 1500,
        "emoji": "🛍️",
        "condition": "items_sold >= 10",
        "hidden": False
    },
    "gift_collector": {
        "name": "Коллекционер 🎁",
        "description": "Собрать 5 разных подарков",
        "reward": 2500,
        "emoji": "🎁",
        "condition": "unique_gifts >= 5",
        "hidden": False
    },
    "rich_man": {
        "name": "Богатей 💎",
        "description": "Накопить 1,000,000₽ на балансе",
        "reward": 10000,
        "emoji": "💎",
        "condition": "balance >= 1000000",
        "hidden": False
    },
    "lucky_charm": {
        "name": "Везунчик 🍀",
        "description": "Выиграть джекпот в слотах",
        "reward": 5000,
        "emoji": "🍀",
        "condition": "jackpot_wins >= 1",
        "hidden": False
    },
    "robber_king": {
        "name": "Король грабителей 👑",
        "description": "Успешно ограбить казну 5 раз",
        "reward": 3000,
        "emoji": "👑",
        "condition": "successful_robs >= 5",
        "hidden": False
    },
    "generous_soul": {
        "name": "Щедрая душа ❤️",
        "description": "Передать 50,000₽ другим игрокам",
        "reward": 2000,
        "emoji": "❤️",
        "condition": "money_given >= 50000",
        "hidden": False
    },
    "gambler": {
        "name": "Азартный игрок 🎲",
        "description": "Сделать 100 ставок в казино",
        "reward": 1500,
        "emoji": "🎲",
        "condition": "total_bets >= 100",
        "hidden": False
    },
    "tycoon": {
        "name": "Магнат 🏦",
        "description": "Достичь 8 уровня бизнеса",
        "reward": 15000,
        "emoji": "🏦",
        "condition": "business_level >= 8",
        "hidden": False
    },
    "philanthropist": {
        "name": "Филантроп 🤝",
        "description": "Пожертвовать 100,000₽ в казну",
        "reward": 5000,
        "emoji": "🤝",
        "condition": "donated_to_treasury >= 100000",
        "hidden": True
    },
    "secret_agent": {
        "name": "Тайный агент 🕵️",
        "description": "Найти секретное достижение",
        "reward": 77777,
        "emoji": "🕵️",
        "condition": "found_secret >= 1",
        "hidden": True
    },
    "night_owl": {
        "name": "Ночная сова 🦉",
        "description": "Сыграть в казино между 00:00 и 05:00",
        "reward": 3000,
        "emoji": "🦉",
        "condition": "night_games >= 1",
        "hidden": True
    },
    "rainbow_hunter": {
        "name": "Охотник за радугой 🌈",
        "description": "Выиграть с бустером 'Радужная ставка'",
        "reward": 4000,
        "emoji": "🌈",
        "condition": "rainbow_wins >= 1",
        "hidden": False
    }
}

RARITY_COLORS = {
    'Легендарный': '🟡',
    'Эпический': '🟣',
    'Редкий': '🔵',
    'Обычный': '⚪'
}

# ===== ИВЕНТ 23 ФЕВРАЛЯ =====
DEFENDER_DAY = {
    "active": False,  # По умолчанию выключен
    "start_date": None,  # Будет установлено при запуске
    "end_date": None,    # Будет установлено при запуске
    "name": "🎖️ День защитника 2026",
    "description": "Военный ивент!",
    
    # Очки ивента
    "points_name": "🎖️ Медали",
    
    # Задания
    "quests": {
        # ЕЖЕДНЕВНЫЕ
        "daily": {
            "play_casino": {
                "name": "🔫 Артиллерия",
                "description": "Сыграть в казино 10 раз",
                "target": 10,
                "reward_points": 50,
                "reward_money": 5000,
                "emoji": "🔫"
            },
            "business_income": {
                "name": "🏭 Тыл",
                "description": "Собрать доход с бизнеса 5 раз",
                "target": 5,
                "reward_points": 30,
                "reward_money": 3000,
                "emoji": "🏭"
            },
            "gift_sell": {
                "name": "🎁 Интендант",
                "description": "Продать 3 подарка",
                "target": 3,
                "reward_points": 40,
                "reward_money": 4000,
                "emoji": "🎁"
            },
            "transfer_money": {
                "name": "🤝 Взаимопомощь",
                "description": "Передать деньги 3 раза",
                "target": 3,
                "reward_points": 25,
                "reward_money": 2000,
                "emoji": "🤝"
            },
            "treasury_rob": {
                "name": "💣 Диверсант",
                "description": "Ограбить казну 2 раза",
                "target": 2,
                "reward_points": 35,
                "reward_money": 3500,
                "emoji": "💣"
            },
            "use_booster": {
                "name": "🚀 Усиление",
                "description": "Использовать бустер",
                "target": 1,
                "reward_points": 20,
                "reward_money": 2000,
                "emoji": "🚀"
            }
        },
        
        # ОСОБЫЕ (на весь ивент)
        "special": {
            "total_bets_100": {
                "name": "🎖️ Боевое крещение",
                "description": "Сделать 100 ставок в казино",
                "target": 100,
                "reward_money": 25000,
                "reward_gift": "order_of_courage",
                "emoji": "🎖️"
            },
            "casino_wins_50000": {
                "name": "⚔️ Победитель",
                "description": "Выиграть 50,000 ₽ в казино",
                "target": 50000,
                "reward_money": 30000,
                "reward_gift": "gold_star",
                "emoji": "⚔️"
            },
            "robbery_10": {
                "name": "💂‍♂️ Штурмовик",
                "description": "Ограбить казну 10 раз",
                "target": 10,
                "reward_money": 20000,
                "reward_gift": "assault_badge",
                "emoji": "💂‍♂️"
            },
            "business_level_15": {
                "name": "🏰 Генерал бизнеса",
                "description": "Достичь 15 уровня бизнеса",
                "target": 15,
                "reward_money": 50000,
                "reward_gift": "marshal_star",
                "emoji": "🏰"
            },
            "gifts_10": {
                "name": "🎁 Коллекционер",
                "description": "Собрать 10 разных подарков",
                "target": 10,
                "reward_money": 20000,
                "reward_gift": "supply_chest",
                "emoji": "🎁"
            }
        }
    },
    
    # ТОП-5 НАГРАДЫ
    "top_rewards": {
        1: {
            "name": "🥇 ГЛАВНОКОМАНДУЮЩИЙ",
            "money": 500000,
            "gift": "victory_sword",
            "badge": "👑",
            "description": "Абсолютный чемпион ивента!"
        },
        2: {
            "name": "🥈 КОМАНДУЮЩИЙ ФРОНТОМ",
            "money": 300000,
            "gift": "front_command",
            "badge": "⚔️",
            "description": "Второй среди лучших!"
        },
        3: {
            "name": "🥉 КОМАНДУЮЩИЙ АРМИЕЙ",
            "money": 200000,
            "gift": "army_command",
            "badge": "🎖️",
            "description": "Тройка лучших!"
        },
        4: {
            "name": "🎖️ НАЧАЛЬНИК ШТАБА",
            "money": 150000,
            "gift": "staff_badge",
            "badge": "📯",
            "description": "Почётное четвёртое место!"
        },
        5: {
            "name": "🪖 ЗАМЕСТИТЕЛЬ КОМАНДУЮЩЕГО",
            "money": 100000,
            "gift": "deputy_badge",
            "badge": "🔫",
            "description": "Замыкает топ-5!"
        }
    }
}

# Файл для сохранения настроек ивента
EVENT_SETTINGS_FILE = "event_settings.json"

DATA_FILE = "data.json"
MARKET_ITEMS_FILE = "market_items.json"
USER_STATES_FILE = "user_states.json"
SETTINGS_FILE = "settings.json"
PROMO_CODES_FILE = "promo_codes.json"
PURCHASES_FILE = "purchases.json"
BOOSTERS_FILE = "boosters.json"
ACHIEVEMENTS_FILE = "achievements.json"



def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {
        "users": {},
        "gift_sales": {},
        "items": {},
        "market_items": {},
        "stats": {
            "total_users": 0,
            "total_transactions": 0,
            "market_sales": 0,
            "promo_codes_used": 0,
            "total_deposited": 0,
            "total_boosters_bought": 0,
            "total_achievements": 0
        },
        "treasury": 50000
    }


def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_market_items():
    if os.path.exists(MARKET_ITEMS_FILE):
        try:
            with open(MARKET_ITEMS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}


def save_market_items(market_items):
    with open(MARKET_ITEMS_FILE, 'w', encoding='utf-8') as f:
        json.dump(market_items, f, ensure_ascii=False, indent=2)


def load_user_states():
    if os.path.exists(USER_STATES_FILE):
        try:
            with open(USER_STATES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}


def save_user_states(user_states):
    with open(USER_STATES_FILE, 'w', encoding='utf-8') as f:
        json.dump(user_states, f, ensure_ascii=False, indent=2)


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                # Обновляем глобальную переменную CHANCE_SETTINGS
                global CHANCE_SETTINGS
                for key in CHANCE_SETTINGS:
                    if key in loaded:
                        CHANCE_SETTINGS[key] = loaded[key]
                return loaded
        except:
            pass
    return CHANCE_SETTINGS.copy()


def save_settings():
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(CHANCE_SETTINGS, f, ensure_ascii=False, indent=2)


def load_promo_codes():
    if os.path.exists(PROMO_CODES_FILE):
        try:
            with open(PROMO_CODES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}


def save_promo_codes(promo_codes):
    with open(PROMO_CODES_FILE, 'w', encoding='utf-8') as f:
        json.dump(promo_codes, f, ensure_ascii=False, indent=2)


def load_purchases():
    if os.path.exists(PURCHASES_FILE):
        try:
            with open(PURCHASES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}


def save_purchases(purchases):
    with open(PURCHASES_FILE, 'w', encoding='utf-8') as f:
        json.dump(purchases, f, ensure_ascii=False, indent=2)


def load_boosters_data():
    if os.path.exists(BOOSTERS_FILE):
        try:
            with open(BOOSTERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}


def save_boosters_data(boosters_data):
    with open(BOOSTERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(boosters_data, f, ensure_ascii=False, indent=2)


def load_achievements_data():
    if os.path.exists(ACHIEVEMENTS_FILE):
        try:
            with open(ACHIEVEMENTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}


def save_achievements_data(achievements_data):
    with open(ACHIEVEMENTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(achievements_data, f, ensure_ascii=False, indent=2)


def get_user(data, user_id):
    user_id = str(user_id)
    if user_id not in data["users"]:
        # Определяем начальный статус
        initial_status = "👤 Пользователь"
        if is_admin(int(user_id)):
            initial_status = "👑 Админ"

        data["users"][user_id] = {
            "balance": 100,
            "username": None,
            "first_name": "Пользователь",
            "status": initial_status,  # НОВОЕ: поле статуса
            "gifts": [],
            "business_level": 0,
            "business_upgrades": [],
            "business_manager": None,
            "business_bonuses": [],
            "business_events": {},
            "business_stock": 0,
            "business_debt": 0,
            "business_insurance": False,
            "last_income": None,
            "last_bonus": None,
            "last_rob": None,
            "registered": datetime.now().isoformat(),
            "market_items": [],
            "total_deposited": 0,
            "total_withdrawn": 0,
            "purchases": [],
            "boosters": {},
            "active_boosters": {},
            "upgrades": [],
            "stats": {
                "casino_wins": 0,
                "total_bets": 0,
                "jackpot_wins": 0,
                "successful_robs": 0,
                "items_sold": 0,
                "money_given": 0,
                "donated_to_treasury": 0,
                "night_games": 0,
                "rainbow_wins": 0,
                "found_secret": 0,
                "business_income_total": 0,
                "business_upgrades_bought": 0,
                "business_events_count": 0
            },
            "achievements": [],
            "achievements_progress": {}
        }
        data["stats"]["total_users"] += 1
        save_data(data)
    return data["users"][user_id]

def handle_set_status(data, message, args):
    """Установить статус пользователю (только для админов)"""
    if not is_admin(message["from"]["id"]):
        send_message(message["chat"]["id"],
                     "❌ Только админы могут устанавливать статусы!",
                     reply_to=message["message_id"])
        return

    if "reply_to_message" not in message:
        send_message(message["chat"]["id"],
                     "❌ Ответьте на сообщение пользователя!",
                     reply_to=message["message_id"])
        return

    if not args:
        send_message(message["chat"]["id"],
                     "❌ Укажите статус!\nПример: статус ⭐ Золотой клиент",
                     reply_to=message["message_id"])
        return

    # Объединяем все аргументы в один статус
    status_text = " ".join(args)

    # Проверяем длину статуса
    if len(status_text) > 50:
        send_message(message["chat"]["id"],
                     "❌ Слишком длинный статус! Максимум 50 символов.",
                     reply_to=message["message_id"])
        return

    target_user = message["reply_to_message"]["from"]
    target_id = str(target_user["id"])
    update_user_info(data, target_id, target_user.get("username"),
                     target_user.get("first_name"))

    user = get_user(data, target_id)
    old_status = user.get("status", "👤 Пользователь")
    user["status"] = status_text

    # Если админ устанавливает статус админу, обновляем его статус
    if is_admin(int(target_id)):
        user["status"] = f"👑 Админ | {status_text}"

    save_data(data)

    target_emoji = get_user_emoji(user)
    target_name = format_user_mention(user, target_id)
    admin_emoji = get_user_emoji(get_user(data, str(message["from"]["id"])))

    send_message(
        message["chat"]["id"],
        f"{admin_emoji} ➜ {target_emoji}\n✅ Статус установлен!\n\n"
        f"👤 Пользователь: {target_name}\n"
        f"📝 Старый статус: {old_status}\n"
        f"📝 Новый статус: {user['status']}",
        reply_to=message["message_id"]
    )

def update_user_info(data, user_id, username, first_name):
    user = get_user(data, user_id)
    user["username"] = username
    user["first_name"] = first_name or "Пользователь"
    save_data(data)

def handle_reset_status(data, message):
    """Сбросить статус пользователя (только для админов)"""
    if not is_admin(message["from"]["id"]):
        send_message(message["chat"]["id"],
                     "❌ Только админы могут сбрасывать статусы!",
                     reply_to=message["message_id"])
        return

    if "reply_to_message" not in message:
        send_message(message["chat"]["id"],
                     "❌ Ответьте на сообщение пользователя!",
                     reply_to=message["message_id"])
        return

    target_user = message["reply_to_message"]["from"]
    target_id = str(target_user["id"])
    update_user_info(data, target_id, target_user.get("username"),
                     target_user.get("first_name"))

    user = get_user(data, target_id)
    old_status = user.get("status", "👤 Пользователь")

    # Устанавливаем стандартный статус
    if is_admin(int(target_id)):
        user["status"] = "👑 Админ"
    else:
        user["status"] = "👤 Пользователь"

    save_data(data)

    target_emoji = get_user_emoji(user)
    target_name = format_user_mention(user, target_id)
    admin_user = get_user(data, str(message["from"]["id"]))
    admin_emoji = get_user_emoji(admin_user)

    send_message(
        message["chat"]["id"],
        f"{admin_emoji} ➜ {target_emoji}\n🔄 Статус сброшен!\n\n"
        f"👤 Пользователь: {target_name}\n"
        f"📝 Старый статус: {old_status}\n"
        f"📝 Новый статус: {user['status']}",
        reply_to=message["message_id"]
    )

def handle_show_status(data, message):
    """Показать статус пользователя"""
    if "reply_to_message" not in message:
        # Показать свой статус
        user_id = str(message["from"]["id"])
        user = get_user(data, user_id)
        status = user.get("status", "👤 Пользователь")

        send_message(message["chat"]["id"],
                     f"📝 Ваш статус: {status}",
                     reply_to=message["message_id"])
        return

    # Показать статус другого пользователя
    target_user = message["reply_to_message"]["from"]
    target_id = str(target_user["id"])
    update_user_info(data, target_id, target_user.get("username"),
                     target_user.get("first_name"))

    user = get_user(data, target_id)
    status = user.get("status", "👤 Пользователь")
    target_name = format_user_mention(user, target_id)

    send_message(message["chat"]["id"],
                 f"📝 Статус {target_name}: {status}",
                 reply_to=message["message_id"])

def handle_my_status(data, message):
    """Показать подробную информацию о статусе"""
    user_id = str(message["from"]["id"])
    user = get_user(data, user_id)
    user_emoji = get_user_emoji(user)
    status = user.get("status", "👤 Пользователь")

    status_info = f"""
{user_emoji} ═══ ВАШ СТАТУС ═══ {user_emoji}

📝 **Текущий статус:** {status}

💡 **О статусах:**
• Статус отображается в вашем профиле
• Статусы устанавливают администраторы
• Статус показывает ваше положение в сообществе

👑 **Стандартные статусы:**
• 👤 Пользователь - обычный участник
• 👑 Админ - администратор проекта

🌟 **Примеры статусов:**
• ⭐ Золотой клиент
• 🏆 Чемпион казино
• 💎 VIP-игрок
• 🤝 Надёжный продавец
• 🎁 Коллекционер

💬 **Для изменения статуса** обратитесь к администратору.
"""

    send_message(message["chat"]["id"], status_info,
                 reply_to=message["message_id"], parse_mode="Markdown")

def format_user_mention(user_data, user_id):
    username = user_data.get("username")
    first_name = user_data.get("first_name", "Пользователь")
    if username:
        return f"@{username} ({first_name})"
    else:
        return f"[{first_name}](tg://user?id={user_id})"


def get_profile_decoration(user_data):
    gifts = user_data.get("gifts", [])
    if not gifts:
        return "⚪"

    rarities = []
    for gift_id in gifts:
        if gift_id in GIFTS:
            rarities.append(GIFTS[gift_id]['rarity'])

    if 'Легендарный' in rarities:
        return "🟡✨"
    elif 'Эпический' in rarities:
        return "🟣💫"
    elif 'Редкий' in rarities:
        return "🔵⭐"
    else:
        return "⚪"


def get_user_emoji(user_data):
    gifts = user_data.get("gifts", [])
    if not gifts:
        return "👤"

    rarity_order = {
        'Легендарный': 0,
        'Эпический': 1,
        'Редкий': 2,
        'Обычный': 3
    }
    best_gift = None
    best_rarity = 4

    for gift_id in gifts:
        if gift_id in GIFTS:
            gift = GIFTS[gift_id]
            rarity_rank = rarity_order.get(gift['rarity'], 4)
            if rarity_rank < best_rarity:
                best_rarity = rarity_rank
                best_gift = gift

    if best_gift:
        return best_gift['emoji']
    return "👤"


def build_profile(data, user_id):
    user = get_user(data, user_id)
    decoration = get_profile_decoration_custom(user)

    username = user.get("username")
    first_name = user.get("first_name", "Пользователь")
    status = user.get("status", "👤 Пользователь")

    if username:
        name_display = f"@{username} ({first_name})"
    else:
        name_display = first_name

    gifts_display = ""
    if user.get("gifts"):
        gift_emojis = format_user_gifts_with_custom_emoji(user["gifts"])
        gifts_display = f"\n🎁 Подарки: {gift_emojis}"
        gifts_list = []
        for g in user["gifts"]:
            if g in GIFTS:
                gift = GIFTS[g]
                if 'custom_emoji' in gift:
                    gifts_list.append(f"   {gift['custom_emoji']} {gift['name']} [{gift['rarity']}]")
                else:
                    gifts_list.append(f"   {gift['emoji']} {gift['name']} [{gift['rarity']}]")
        if gifts_list:
            gifts_display += "\n" + "\n".join(gifts_list)
    else:
        gifts_display = "\n🎁 Подарки: Нет подарков"

    business = ""
    if user.get("business_level", 0) > 0:
        level = user["business_level"]
        biz = BUSINESS_LEVELS.get(level, {})
        business = f"\n🏪 Бизнес: {biz.get('name', 'Неизвестно')} (Уровень {level})"

    market_items = ""
    if user.get("market_items"):
        market_items = f"\n🛍️ Товаров на продаже: {len(user['market_items'])}"

    purchases_count = len(user.get("purchases", []))
    purchases_info = f"\n🛒 Куплено товаров: {purchases_count}"

    # Активные бустеры
    active_boosters = user.get("active_boosters", {})
    boosters_info = ""
    if active_boosters:
        boosters_list = []
        for booster_id, expires_at in active_boosters.items():
            if booster_id in BOOSTERS:
                booster = BOOSTERS[booster_id]
                try:
                    expires_time = datetime.fromisoformat(expires_at)
                    time_left = expires_time - datetime.now()
                    if time_left.total_seconds() > 0:
                        minutes_left = int(time_left.total_seconds() / 60)
                        boosters_list.append(f"{booster['emoji']} {booster['name']} ({minutes_left} мин)")
                except:
                    pass
        if boosters_list:
            boosters_info = "\n🚀 Активные бустеры:\n" + "\n".join([f"   • {b}" for b in boosters_list])

    # Достижения
    achievements_count = len(user.get("achievements", []))
    achievements_info = f"\n🏆 Достижений: {achievements_count}/15"

    profile = f"""
{decoration} ═══════════════════ {decoration}
       📋 ПРОФИЛЬ
{decoration} ═══════════════════ {decoration}

👤 Имя: {name_display}
🆔 ID: {user_id}
📝 Статус: {status}

💰 Баланс: {user.get('balance', 0):,} ₽
💳 Пополнено: {user.get('total_deposited', 0):,} ₽
📤 Выведено: {user.get('total_withdrawn', 0):,} ₽
{business}{market_items}{purchases_info}{achievements_info}{boosters_info}
{gifts_display}

📅 Регистрация: {user.get('registered', 'Неизвестно')[:10]}

{decoration} ═══════════════════ {decoration}
"""
    return profile

def send_message(chat_id, text, reply_to=None, parse_mode=None, reply_markup=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    elif "<tg-emoji" in text or "custom_emoji" in text:  # <-- ДОБАВЬТЕ ЭТУ СТРОКУ
        payload["parse_mode"] = "HTML"  # <-- И ЭТУ СТРОКУ
    if reply_to:
        payload["reply_to_message_id"] = reply_to
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        response = requests.post(url, json=payload, timeout=30)
        result = response.json()
        if not result.get("ok"):
            print(f"❌ Telegram API error: {result}", flush=True)
        return result
    except Exception as e:
        print(f"❌ Error sending message: {e}", flush=True)
        return None


def edit_message(chat_id, message_id, text, parse_mode=None, reply_markup=None):
    """Редактирует сообщение с повторными попытками при ошибках"""
    url = f"http://api.telegram.org/bot{TOKEN}/editMessageText"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text
    }
    if parse_mode:
        payload["parse_mode"] = parse_mode
    if reply_markup:
        payload["reply_markup"] = reply_markup
    
    # Пробуем отправить до 3 раз
    for attempt in range(3):
        try:
            response = requests.post(
                url,
                json=payload,
                timeout=10,
                verify=True  # Проверка SSL
            )
            result = response.json()
            
            if not result.get("ok"):
                error = result.get("description", "")
                if "message is not modified" in error:
                    return {"ok": True, "message": "not_modified"}
                else:
                    print(f"❌ Telegram API edit error: {result}")
            return result
            
        except requests.exceptions.SSLError as e:
            print(f"⚠️ SSL ошибка (попытка {attempt+1}/3): {e}")
            time.sleep(2)  # Ждем 2 секунды перед повтором
            
        except requests.exceptions.ConnectionError as e:
            print(f"⚠️ Ошибка соединения (попытка {attempt+1}/3): {e}")
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Неизвестная ошибка: {e}")
            if attempt == 2:  # Последняя попытка
                return None
            time.sleep(2)
    
    return None


def delete_message(chat_id, message_id):
    url = f"https://api.telegram.org/bot{TOKEN}/deleteMessage"
    payload = {"chat_id": chat_id, "message_id": message_id}
    try:
        response = requests.post(url, json=payload, timeout=30)
        result = response.json()
        if not result.get("ok"):
            print(f"❌ Telegram API delete error: {result}", flush=True)
        return result
    except Exception as e:
        print(f"❌ Error deleting message: {e}", flush=True)
        return None


def answer_callback_query(callback_query_id, text, show_alert=False):
    url = f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery"
    payload = {
        "callback_query_id": callback_query_id,
        "text": text,
        "show_alert": show_alert
    }
    try:
        response = requests.post(url, json=payload, timeout=30)
        return response.json()
    except Exception as e:
        print(f"❌ Error answering callback: {e}", flush=True)
        return None


def update_channel_stats(data):
    total_users = data['stats']['total_users']
    total_transactions = data['stats']['total_transactions']
    treasury = data.get('treasury', 0)
    market_sales = data['stats'].get('market_sales', 0)
    promo_codes_used = data['stats'].get('promo_codes_used', 0)
    total_deposited = data['stats'].get('total_deposited', 0)
    total_boosters_bought = data['stats'].get('total_boosters_bought', 0)
    total_achievements = data['stats'].get('total_achievements', 0)

    total_balance = sum(u.get('balance', 0) for u in data['users'].values())
    total_gifts = sum(len(u.get('gifts', [])) for u in data['users'].values())
    total_businesses = sum(1 for u in data['users'].values() if u.get('business_level', 0) > 0)
    total_active_boosters = sum(len(u.get('active_boosters', {})) for u in data['users'].values())

    top_users = sorted(data['users'].items(), key=lambda x: x[1].get('balance', 0), reverse=True)[:10]
    top_list = []
    for i, (uid, udata) in enumerate(top_users, 1):
        name = udata.get('first_name', 'Пользователь')
        balance = udata.get('balance', 0)
        emoji = get_user_emoji(udata)
        top_list.append(f"{i}. {emoji} {name} - {balance:,} ₽")

    now = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    stats_text = f"""📊 ═══ СТАТИСТИКА БОТА ═══ 📊

👥 Всего пользователей: {total_users}
💰 Всего транзакций: {total_transactions}
🛍️ Продаж на маркете: {market_sales}
💳 Промокодов использовано: {promo_codes_used}
🚀 Бустеров куплено: {total_boosters_bought}
🏆 Всего достижений: {total_achievements}
🏦 Казна: {treasury:,} ₽

💵 Общий баланс всех игроков: {total_balance:,} ₽
🎁 Всего подарков: {total_gifts}
🏢 Игроков с бизнесом: {total_businesses}
💸 Всего пополнено: {total_deposited:,} ₽
⚡ Активных бустеров: {total_active_boosters}

🏆 ТОП-10 БОГАТЕЙШИХ:
{chr(10).join(top_list) if top_list else 'Нет данных'}"""

    result = edit_message(STATS_CHANNEL_ID, STATS_MESSAGE_ID, stats_text)
    if result and result.get("ok"):
        print(f"✅ Статистика обновлена в канале ({now})", flush=True)
    return result


def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    params = {"timeout": 30}
    if offset:
        params["offset"] = offset
    try:
        response = requests.get(url, params=params, timeout=35)
        return response.json()
    except Exception as e:
        print(f"Error getting updates: {e}")
        return None


def is_admin(user_id):
    return str(user_id) in ADMIN_IDS


# ===== НОВЫЕ ФУНКЦИИ ДЛЯ АДМИНОВ =====

def handle_give_booster(data, message, args):
    """Выдать бустер пользователю (админ)"""
    if not is_admin(message["from"]["id"]):
        send_message(message["chat"]["id"],
                     "❌ Только для админов!",
                     reply_to=message["message_id"])
        return

    if "reply_to_message" not in message:
        send_message(message["chat"]["id"],
                     "❌ Ответьте на сообщение пользователя!",
                     reply_to=message["message_id"])
        return

    if not args:
        boosters_list = "\n".join([f"{bid}: {booster['name']}" for bid, booster in BOOSTERS.items()])
        send_message(message["chat"]["id"],
                     f"❌ Укажите ID бустера!\n\nДоступные бустеры:\n{boosters_list}",
                     reply_to=message["message_id"])
        return

    booster_id = args[0]
    if booster_id not in BOOSTERS:
        send_message(message["chat"]["id"],
                     f"❌ Бустер не найден! Доступные: {', '.join(BOOSTERS.keys())}",
                     reply_to=message["message_id"])
        return

    duration_hours = 1  # по умолчанию 1 час
    if len(args) > 1:
        try:
            duration_hours = int(args[1])
        except:
            pass

    target_user = message["reply_to_message"]["from"]
    target_id = str(target_user["id"])
    update_user_info(data, target_id, target_user.get("username"),
                     target_user.get("first_name"))

    target = get_user(data, target_id)
    booster = BOOSTERS[booster_id]

    # Активируем бустер
    expires_at = datetime.now() + timedelta(hours=duration_hours)
    if "active_boosters" not in target:
        target["active_boosters"] = {}
    target["active_boosters"][booster_id] = expires_at.isoformat()

    # Добавляем в статистику пользователя
    if "boosters" not in target:
        target["boosters"] = {}
    if booster_id not in target["boosters"]:
        target["boosters"][booster_id] = 0
    target["boosters"][booster_id] += 1

    save_data(data)

    target_emoji = get_user_emoji(target)
    target_name = format_user_mention(target, target_id)

    send_message(
        message["chat"]["id"],
        f"{target_emoji} ✅ Бустер выдан!\n\n{booster['emoji']} {booster['name']}\n👤 Пользователь: {target_name}\n⏰ Длительность: {duration_hours} час(ов)\n✨ Эффект: {booster['effect']}",
        reply_to=message["message_id"]
    )


def handle_take_booster(data, message, args):
    """Забрать бустер у пользователя (админ)"""
    if not is_admin(message["from"]["id"]):
        send_message(message["chat"]["id"],
                     "❌ Только для админов!",
                     reply_to=message["message_id"])
        return

    if "reply_to_message" not in message:
        send_message(message["chat"]["id"],
                     "❌ Ответьте на сообщение пользователя!",
                     reply_to=message["message_id"])
        return

    if not args:
        boosters_list = "\n".join([f"{bid}: {booster['name']}" for bid, booster in BOOSTERS.items()])
        send_message(message["chat"]["id"],
                     f"❌ Укажите ID бустера!\n\nДоступные бустеры:\n{boosters_list}",
                     reply_to=message["message_id"])
        return

    booster_id = args[0]

    target_user = message["reply_to_message"]["from"]
    target_id = str(target_user["id"])
    update_user_info(data, target_id, target_user.get("username"),
                     target_user.get("first_name"))

    target = get_user(data, target_id)
    active_boosters = target.get("active_boosters", {})

    if booster_id not in active_boosters:
        send_message(message["chat"]["id"],
                     f"❌ У пользователя нет активного бустера {booster_id}!",
                     reply_to=message["message_id"])
        return

    # Удаляем бустер
    del active_boosters[booster_id]
    target["active_boosters"] = active_boosters

    save_data(data)

    booster = BOOSTERS.get(booster_id, {"name": booster_id, "emoji": "🚀"})
    target_emoji = get_user_emoji(target)
    target_name = format_user_mention(target, target_id)

    send_message(
        message["chat"]["id"],
        f"{target_emoji} ❌ Бустер забран!\n\n{booster['emoji']} {booster['name']}\n👤 Пользователь: {target_name}",
        reply_to=message["message_id"]
    )


def handle_give_upgrade(data, message, args):
    """Выдать улучшение пользователю (админ)"""
    if not is_admin(message["from"]["id"]):
        send_message(message["chat"]["id"],
                     "❌ Только для админов!",
                     reply_to=message["message_id"])
        return

    if "reply_to_message" not in message:
        send_message(message["chat"]["id"],
                     "❌ Ответьте на сообщение пользователя!",
                     reply_to=message["message_id"])
        return

    if not args:
        upgrades_list = "\n".join([f"{uid}: {upgrade['name']}" for uid, upgrade in CONVENIENCE.items()])
        send_message(message["chat"]["id"],
                     f"❌ Укажите ID улучшения!\n\nДоступные улучшения:\n{upgrades_list}",
                     reply_to=message["message_id"])
        return

    upgrade_id = args[0]
    if upgrade_id not in CONVENIENCE:
        send_message(message["chat"]["id"],
                     f"❌ Улучшение не найдено! Доступные: {', '.join(CONVENIENCE.keys())}",
                     reply_to=message["message_id"])
        return

    target_user = message["reply_to_message"]["from"]
    target_id = str(target_user["id"])
    update_user_info(data, target_id, target_user.get("username"),
                     target_user.get("first_name"))

    target = get_user(data, target_id)
    upgrade = CONVENIENCE[upgrade_id]

    if upgrade_id in target.get("upgrades", []):
        send_message(message["chat"]["id"],
                     f"❌ У пользователя уже есть это улучшение!",
                     reply_to=message["message_id"])
        return

    # Добавляем улучшение
    if "upgrades" not in target:
        target["upgrades"] = []
    target["upgrades"].append(upgrade_id)

    # Если выдается авто-сбор, устанавливаем время последнего сбора
    if upgrade_id == "auto_collect":
        if "last_income" not in target:
            target["last_income"] = datetime.now().isoformat()
        target["last_auto_collect"] = datetime.now().isoformat()

        # Уведомляем пользователя об ограничениях
        try:
            send_message(
                target_id,
                f"🤖 Вам выдано улучшение 'Авто-сбор доходов'!\n\n"
                f"✨ Эффект: {upgrade['effect']}\n\n"
                f"⚠️ **Внимание:** С этого момента:\n"
                f"• Доходы будут собираться автоматически каждые 4 часа\n"
                f"• Ручной сбор командой /доход будет отключен\n"
                f"• Вы будете получать уведомления в ЛС при каждом авто-сборе\n\n"
                f"💡 Для отключения авто-сбора обратитесь к администратору."
            )
        except:
            pass  # Если не удалось отправить сообщение в ЛС

    save_data(data)

    target_emoji = get_user_emoji(target)
    target_name = format_user_mention(target, target_id)

    # Особое сообщение для авто-сбора
    if upgrade_id == "auto_collect":
        message_text = f"""
{target_emoji} ✅ Улучшение выдано!

🤖 {upgrade['name']}
👤 Пользователь: {target_name}
✨ Эффект: {upgrade['effect']}

⚠️ **Важно:** Пользователю отправлено уведомление о том, что:
• Ручной сбор отключен
• Доходы собираются автоматически каждые 4 часа
• Для отключения авто-сбора нужно обратиться к администратору
"""
    else:
        message_text = f"""
{target_emoji} ✅ Улучшение выдано!

{upgrade['emoji']} {upgrade['name']}
👤 Пользователь: {target_name}
✨ Эффект: {upgrade['effect']}
"""

    send_message(
        message["chat"]["id"],
        message_text,
        reply_to=message["message_id"]
    )

def handle_take_upgrade(data, message, args):
    """Забрать улучшение у пользователя (админ)"""
    if not is_admin(message["from"]["id"]):
        send_message(message["chat"]["id"],
                     "❌ Только для админов!",
                     reply_to=message["message_id"])
        return

    if "reply_to_message" not in message:
        send_message(message["chat"]["id"],
                     "❌ Ответьте на сообщение пользователя!",
                     reply_to=message["message_id"])
        return

    if not args:
        upgrades_list = "\n".join([f"{uid}: {upgrade['name']}" for uid, upgrade in CONVENIENCE.items()])
        send_message(message["chat"]["id"],
                     f"❌ Укажите ID улучшения!\n\nДоступные улучшения:\n{upgrades_list}",
                     reply_to=message["message_id"])
        return

    upgrade_id = args[0]

    target_user = message["reply_to_message"]["from"]
    target_id = str(target_user["id"])
    update_user_info(data, target_id, target_user.get("username"),
                     target_user.get("first_name"))

    target = get_user(data, target_id)
    upgrades = target.get("upgrades", [])

    if upgrade_id not in upgrades:
        send_message(message["chat"]["id"],
                     f"❌ У пользователя нет улучшения {upgrade_id}!",
                     reply_to=message["message_id"])
        return

    # Удаляем улучшение
    upgrades.remove(upgrade_id)
    target["upgrades"] = upgrades

    # Если забирается авто-сбор, уведомляем пользователя
    if upgrade_id == "auto_collect":
        try:
            send_message(
                target_id,
                f"🤖 У вас забрано улучшение 'Авто-сбор доходов'!\n\n"
                f"⚠️ **Изменения:**\n"
                f"• Автоматический сбор доходов отключен\n"
                f"• Теперь вы можете собирать доход вручную командой /доход\n"
                f"• Интервал ручного сбора: 6 минут\n\n"
                f"💡 Для повторной покупки авто-сбора: /улучшения"
            )
        except:
            pass  # Если не удалось отправить сообщение в ЛС

    save_data(data)

    upgrade = CONVENIENCE.get(upgrade_id, {"name": upgrade_id, "emoji": "🛠️"})
    target_emoji = get_user_emoji(target)
    target_name = format_user_mention(target, target_id)

    # Особое сообщение для авто-сбора
    if upgrade_id == "auto_collect":
        message_text = f"""
{target_emoji} ❌ Улучшение забрано!

🤖 {upgrade['name']}
👤 Пользователь: {target_name}

⚠️ **Важно:** Пользователю отправлено уведомление о том, что:
• Автоматический сбор отключен
• Ручной сбор снова доступен командой /доход
• Интервал ручного сбора: 6 минут
"""
    else:
        message_text = f"""
{target_emoji} ❌ Улучшение забрано!

{upgrade['emoji']} {upgrade['name']}
👤 Пользователь: {target_name}
"""

    send_message(
        message["chat"]["id"],
        message_text,
        reply_to=message["message_id"]
    )

def handle_show_user_boosters(data, message):
    """Показать бустеры и улучшения пользователя (админ)"""
    if not is_admin(message["from"]["id"]):
        send_message(message["chat"]["id"],
                     "❌ Только для админов!",
                     reply_to=message["message_id"])
        return

    if "reply_to_message" not in message:
        send_message(message["chat"]["id"],
                     "❌ Ответьте на сообщение пользователя!",
                     reply_to=message["message_id"])
        return

    target_user = message["reply_to_message"]["from"]
    target_id = str(target_user["id"])
    update_user_info(data, target_id, target_user.get("username"),
                     target_user.get("first_name"))

    target = get_user(data, target_id)
    target_emoji = get_user_emoji(target)
    target_name = format_user_mention(target, target_id)

    # Активные бустеры
    active_boosters = target.get("active_boosters", {})
    boosters_text = ""
    if active_boosters:
        boosters_text = "\n🚀 АКТИВНЫЕ БУСТЕРЫ:\n"
        now = datetime.now()
        for booster_id, expires_at_str in active_boosters.items():
            if booster_id in BOOSTERS:
                booster = BOOSTERS[booster_id]
                try:
                    expires_at = datetime.fromisoformat(expires_at_str)
                    if expires_at > now:
                        time_left = expires_at - now
                        minutes_left = int(time_left.total_seconds() / 60)
                        boosters_text += f"• {booster['emoji']} {booster['name']} ({minutes_left} мин)\n"
                    else:
                        boosters_text += f"• {booster['emoji']} {booster['name']} (истек)\n"
                except:
                    boosters_text += f"• {booster['emoji']} {booster['name']}\n"
    else:
        boosters_text = "\n🚀 Активных бустеров нет\n"

    # Улучшения
    upgrades = target.get("upgrades", [])
    upgrades_text = ""
    if upgrades:
        upgrades_text = "\n🛠️ УЛУЧШЕНИЯ:\n"
        for upgrade_id in upgrades:
            if upgrade_id in CONVENIENCE:
                upgrade = CONVENIENCE[upgrade_id]
                upgrades_text += f"• {upgrade['emoji']} {upgrade['name']}\n"
    else:
        upgrades_text = "\n🛠️ Улучшений нет\n"

    # Купленные бустеры
    bought_boosters = target.get("boosters", {})
    bought_text = ""
    if bought_boosters:
        bought_text = "\n📊 КУПЛЕННЫЕ БУСТЕРЫ:\n"
        for booster_id, count in bought_boosters.items():
            if booster_id in BOOSTERS:
                booster = BOOSTERS[booster_id]
                bought_text += f"• {booster['emoji']} {booster['name']}: {count} раз\n"

    text = f"""
{target_emoji} ═══ БУСТЕРЫ И УЛУЧШЕНИЯ ═══ {target_emoji}

👤 Пользователь: {target_name}
🆔 ID: {target_id}
{boosters_text}{upgrades_text}{bought_text}

💡 Команды управления:
• выдать бустер [ID] [часы] - выдать бустер
• забрать бустер [ID] - забрать бустер
• выдать улучшение [ID] - выдать улучшение
• забрать улучшение [ID] - забрать улучшение
"""

    send_message(message["chat"]["id"], text, reply_to=message["message_id"])


# ===== BOOSTERS FUNCTIONS =====

def handle_boosters_shop(data, message):
    """Показать магазин бустеров"""
    user_id = str(message["from"]["id"])
    user = get_user(data, user_id)
    user_emoji = get_user_emoji(user)

    boosters_text = f"""
{user_emoji} ═══ МАГАЗИН БУСТЕРОВ ═══ {user_emoji}

🚀 Бустеры - временные улучшения для игры:

"""

    for booster_id, booster in BOOSTERS.items():
        boosters_text += f"""
{booster['emoji']} {booster['name']}
💰 Цена: {booster['price']:,} ₽
⏰ Длительность: {booster['duration'] // 60} мин
✨ Эффект: {booster['effect']}
🆔 ID: {booster_id}

"""

    boosters_text += f"""
💡 Купить бустер: купить бустер [ID]
Пример: купить бустер lucky_charm

📋 Ваши активные бустеры: /моибустеры
"""

    send_message(message["chat"]["id"], boosters_text, reply_to=message["message_id"])


def handle_buy_booster(data, message, args):
    """Купить бустер"""
    user_id = str(message["from"]["id"])
    user = get_user(data, user_id)

    if not args:
        send_message(message["chat"]["id"],
                    "❌ Укажите ID бустера!\nПример: купить бустер lucky_charm",
                    reply_to=message["message_id"])
        return

    booster_id = args[0]

    if booster_id not in BOOSTERS:
        send_message(message["chat"]["id"],
                    f"❌ Бустер не найден! Доступные бустеры: {', '.join(BOOSTERS.keys())}",
                    reply_to=message["message_id"])
        return

    booster = BOOSTERS[booster_id]

    if user["balance"] < booster["price"]:
        send_message(message["chat"]["id"],
                    f"❌ Недостаточно средств! Нужно: {booster['price']:,} ₽",
                    reply_to=message["message_id"])
        return

    # Проверяем, не активен ли уже такой бустер
    active_boosters = user.get("active_boosters", {})
    if booster_id in active_boosters:
        try:
            expires_at = datetime.fromisoformat(active_boosters[booster_id])
            if expires_at > datetime.now():
                send_message(message["chat"]["id"],
                           f"❌ У вас уже активен этот бустер!\nОн закончится через {(expires_at - datetime.now()).seconds // 60} мин",
                           reply_to=message["message_id"])
                return
        except:
            pass

    # Покупаем бустер
    user["balance"] -= booster["price"]

    # Активируем бустер
    expires_at = datetime.now() + timedelta(seconds=booster["duration"])
    if "active_boosters" not in user:
        user["active_boosters"] = {}
    user["active_boosters"][booster_id] = expires_at.isoformat()

    # Добавляем в статистику пользователя
    if "boosters" not in user:
        user["boosters"] = {}
    if booster_id not in user["boosters"]:
        user["boosters"][booster_id] = 0
    user["boosters"][booster_id] += 1

    # Обновляем общую статистику
    data["stats"]["total_boosters_bought"] = data["stats"].get("total_boosters_bought", 0) + 1

    # ===== ДОБАВЛЕНО: Прогресс ивента =====
    check_event_progress(user, "booster_use", 1)

    save_data(data)

    user_emoji = get_user_emoji(user)

    send_message(message["chat"]["id"],
                f"""
{user_emoji} ✅ Бустер куплен!

{booster['emoji']} {booster['name']}
⏰ Длительность: {booster['duration'] // 60} минут
✨ Эффект: {booster['effect']}
💰 Списано: {booster['price']:,} ₽
💵 Остаток: {user['balance']:,} ₽

Бустер автоматически активирован!
""", reply_to=message["message_id"])


def handle_my_boosters(data, message):
    """Показать активные бустеры пользователя"""
    user_id = str(message["from"]["id"])
    user = get_user(data, user_id)
    user_emoji = get_user_emoji(user)

    active_boosters = user.get("active_boosters", {})

    if not active_boosters:
        send_message(message["chat"]["id"],
                    f"{user_emoji} У вас нет активных бустеров!\n\nПосетите магазин бустеров: /бустеры",
                    reply_to=message["message_id"])
        return

    boosters_text = f"{user_emoji} ═══ ВАШИ БУСТЕРЫ ═══ {user_emoji}\n\n"

    now = datetime.now()
    active_count = 0

    for booster_id, expires_at_str in active_boosters.items():
        if booster_id in BOOSTERS:
            try:
                expires_at = datetime.fromisoformat(expires_at_str)
                if expires_at > now:
                    active_count += 1
                    booster = BOOSTERS[booster_id]
                    time_left = expires_at - now
                    minutes_left = int(time_left.total_seconds() / 60)
                    seconds_left = int(time_left.total_seconds() % 60)

                    boosters_text += f"""
{booster['emoji']} {booster['name']}
⏰ Осталось: {minutes_left} мин {seconds_left} сек
✨ Эффект: {booster['effect']}
━━━━━━━━━━━━━━━
"""
            except:
                pass

    if active_count == 0:
        boosters_text += "⏰ Нет активных бустеров"

    # Показываем купленные бустеры
    bought_boosters = user.get("boosters", {})
    if bought_boosters:
        boosters_text += "\n\n📊 Купленные бустеры:\n"
        for booster_id, count in bought_boosters.items():
            if booster_id in BOOSTERS:
                booster = BOOSTERS[booster_id]
                boosters_text += f"{booster['emoji']} {booster['name']}: {count} раз\n"

    send_message(message["chat"]["id"], boosters_text, reply_to=message["message_id"])


def check_active_booster(user, booster_id):
    """Проверить, активен ли бустер у пользователя"""
    active_boosters = user.get("active_boosters", {})
    if booster_id in active_boosters:
        try:
            expires_at = datetime.fromisoformat(active_boosters[booster_id])
            return expires_at > datetime.now()
        except:
            return False
    return False


def get_booster_bonus(user, game_type):
    """Получить бонус от активных бустеров"""
    bonuses = {
        "chance_bonus": 0,
        "multiplier": 1
    }

    # Проверяем талисман удачи
    if check_active_booster(user, "lucky_charm"):
        bonuses["chance_bonus"] = BOOSTERS["lucky_charm"]["bonus_chance"]

    # Проверяем радужную ставку для слотов
    if game_type == "slots" and check_active_booster(user, "rainbow_bet"):
        bonuses["multiplier"] = BOOSTERS["rainbow_bet"]["multiplier"]

    return bonuses


# ===== CONVENIENCE UPGRADES FUNCTIONS =====

def handle_upgrades_shop(data, message):
    """Показать магазин улучшений"""
    user_id = str(message["from"]["id"])
    user = get_user(data, user_id)
    user_emoji = get_user_emoji(user)

    upgrades_text = f"""
{user_emoji} ═══ МАГАЗИН УЛУЧШЕНИЙ ═══ {user_emoji}

🛠️ Улучшения - постоянные удобства для игры:

"""

    for upgrade_id, upgrade in CONVENIENCE.items():
        owned = upgrade_id in user.get("upgrades", [])
        status = "✅ Куплено" if owned else f"💰 {upgrade['price']:,} ₽"

        upgrades_text += f"""
{upgrade['emoji']} {upgrade['name']}
✨ {upgrade['effect']}
{status}
🆔 ID: {upgrade_id}

"""

    upgrades_text += """
💡 Купить улучшение: купить улучшение [ID]
Пример: купить улучшение auto_collect

📋 Ваши улучшения: /моиулучшения
"""

    send_message(message["chat"]["id"], upgrades_text, reply_to=message["message_id"])


def handle_buy_upgrade(data, message, args):
    """Купить улучшение"""
    user_id = str(message["from"]["id"])
    user = get_user(data, user_id)

    if not args:
        send_message(message["chat"]["id"],
                    "❌ Укажите ID улучшения!\nПример: купить улучшение auto_collect",
                    reply_to=message["message_id"])
        return

    upgrade_id = args[0]

    if upgrade_id not in CONVENIENCE:
        send_message(message["chat"]["id"],
                    f"❌ Улучшение не найдено! Доступные улучшения: {', '.join(CONVENIENCE.keys())}",
                    reply_to=message["message_id"])
        return

    upgrade = CONVENIENCE[upgrade_id]

    if upgrade_id in user.get("upgrades", []):
        send_message(message["chat"]["id"],
                    f"❌ У вас уже есть это улучшение!",
                    reply_to=message["message_id"])
        return

    if user["balance"] < upgrade["price"]:
        send_message(message["chat"]["id"],
                    f"❌ Недостаточно средств! Нужно: {upgrade['price']:,} ₽",
                    reply_to=message["message_id"])
        return

    # Покупаем улучшение
    user["balance"] -= upgrade["price"]

    # Добавляем улучшение
    if "upgrades" not in user:
        user["upgrades"] = []
    user["upgrades"].append(upgrade_id)

    save_data(data)

    user_emoji = get_user_emoji(user)

    send_message(message["chat"]["id"],
                f"""
{user_emoji} ✅ Улучшение куплено!

{upgrade['emoji']} {upgrade['name']}
✨ {upgrade['effect']}
💰 Списано: {upgrade['price']:,} ₽
💵 Остаток: {user['balance']:,} ₽

Улучшение активно постоянно!
""", reply_to=message["message_id"])


def handle_my_upgrades(data, message):
    """Показать улучшения пользователя"""
    user_id = str(message["from"]["id"])
    user = get_user(data, user_id)
    user_emoji = get_user_emoji(user)

    upgrades = user.get("upgrades", [])

    if not upgrades:
        send_message(message["chat"]["id"],
                    f"{user_emoji} У вас нет улучшений!\n\nПосетите магазин улучшений: /улучшения",
                    reply_to=message["message_id"])
        return

    upgrades_text = f"{user_emoji} ═══ ВАШИ УЛУЧШЕНИЯ ═══ {user_emoji}\n\n"

    for upgrade_id in upgrades:
        if upgrade_id in CONVENIENCE:
            upgrade = CONVENIENCE[upgrade_id]
            upgrades_text += f"""
{upgrade['emoji']} {upgrade['name']}
✨ {upgrade['effect']}
━━━━━━━━━━━━━━━
"""

    send_message(message["chat"]["id"], upgrades_text, reply_to=message["message_id"])


def has_upgrade(user, upgrade_id):
    """Проверить, есть ли у пользователя улучшение"""
    return upgrade_id in user.get("upgrades", [])


# ===== ACHIEVEMENTS FUNCTIONS =====

def check_achievement_conditions(user):
    """Проверить условия всех достижений"""
    new_achievements = []

    for achievement_id, achievement in ACHIEVEMENTS.items():
        if achievement_id in user.get("achievements", []):
            continue  # Уже получено

        condition = achievement["condition"]
        user_stats = user.get("stats", {})

        # Проверяем условие достижения
        if condition == "total_deposited >= 1":
            if user.get("total_deposited", 0) >= 1:
                new_achievements.append(achievement_id)

        elif condition == "business_level >= 1":
            if user.get("business_level", 0) >= 1:
                new_achievements.append(achievement_id)

        elif condition == "casino_wins >= 10000":
            if user_stats.get("casino_wins", 0) >= 10000:
                new_achievements.append(achievement_id)

        elif condition == "items_sold >= 10":
            if user_stats.get("items_sold", 0) >= 10:
                new_achievements.append(achievement_id)

        elif condition == "unique_gifts >= 5":
            # Динамическая проверка для 15 подарков
            # Требуется собрать 5 разных подарков (или треть от общего количества, если меньше)
            required_gifts = min(5, len(GIFTS) // 3)  # Треть от общего количества, но минимум 5
            unique_gifts = len(set(user.get("gifts", [])))
            if unique_gifts >= required_gifts:
                new_achievements.append(achievement_id)

        elif condition == "balance >= 1000000":
            if user.get("balance", 0) >= 1000000:
                new_achievements.append(achievement_id)

        elif condition == "jackpot_wins >= 1":
            if user_stats.get("jackpot_wins", 0) >= 1:
                new_achievements.append(achievement_id)

        elif condition == "successful_robs >= 5":
            if user_stats.get("successful_robs", 0) >= 5:
                new_achievements.append(achievement_id)

        elif condition == "money_given >= 50000":
            if user_stats.get("money_given", 0) >= 50000:
                new_achievements.append(achievement_id)

        elif condition == "total_bets >= 100":
            if user_stats.get("total_bets", 0) >= 100:
                new_achievements.append(achievement_id)

        elif condition == "business_level >= 8":
            if user.get("business_level", 0) >= 8:
                new_achievements.append(achievement_id)

        elif condition == "donated_to_treasury >= 100000":
            if user_stats.get("donated_to_treasury", 0) >= 100000:
                new_achievements.append(achievement_id)

        elif condition == "found_secret >= 1":
            if user_stats.get("found_secret", 0) >= 1:
                new_achievements.append(achievement_id)

        elif condition == "night_games >= 1":
            if user_stats.get("night_games", 0) >= 1:
                new_achievements.append(achievement_id)

        elif condition == "rainbow_wins >= 1":
            if user_stats.get("rainbow_wins", 0) >= 1:
                new_achievements.append(achievement_id)

    return new_achievements


def award_achievement(data, user_id, achievement_id, message=None):
    """Выдать достижение пользователю"""
    if achievement_id not in ACHIEVEMENTS:
        return False

    user = get_user(data, user_id)

    if achievement_id in user.get("achievements", []):
        return False  # Уже получено

    achievement = ACHIEVEMENTS[achievement_id]

    # Добавляем достижение
    if "achievements" not in user:
        user["achievements"] = []
    user["achievements"].append(achievement_id)

    # Выдаем награду
    user["balance"] += achievement["reward"]

    # Обновляем статистику
    data["stats"]["total_achievements"] = data["stats"].get("total_achievements", 0) + 1

    save_data(data)

    # Уведомляем пользователя
    if message:
        user_emoji = get_user_emoji(user)
        send_message(
            message["chat"]["id"],
            f"""
{user_emoji} 🏆 НОВОЕ ДОСТИЖЕНИЕ! 🏆

{achievement['emoji']} {achievement['name']}
📝 {achievement['description']}
💰 Награда: {achievement['reward']:,} ₽

💵 Ваш баланс: {user['balance']:,} ₽
""",
            reply_to=message["message_id"]
        )

    return True

def check_and_award_achievements(data, user_id, message=None):
    """Проверить и выдать достижения"""
    user = get_user(data, user_id)
    new_achievements = check_achievement_conditions(user)

    for achievement_id in new_achievements:
        award_achievement(data, user_id, achievement_id, message)

def handle_achievements(data, message):
    """Показать достижения пользователя"""
    user_id = str(message["from"]["id"])
    user = get_user(data, user_id)
    user_emoji = get_user_emoji(user)

    achievements_text = f"""
{user_emoji} ═══ ДОСТИЖЕНИЯ ═══ {user_emoji}

📊 Прогресс: {len(user.get('achievements', []))}/{len(ACHIEVEMENTS)}
💰 Всего наград: {sum(ACHIEVEMENTS[a]['reward'] for a in user.get('achievements', []) if a in ACHIEVEMENTS):,} ₽

"""

    # Группируем достижения по статусу
    user_achievements = user.get("achievements", [])

    # Полученные достижения
    achievements_text += "✅ ПОЛУЧЕННЫЕ:\n"
    for achievement_id in user_achievements:
        if achievement_id in ACHIEVEMENTS:
            achievement = ACHIEVEMENTS[achievement_id]
            achievements_text += f"{achievement['emoji']} {achievement['name']} - +{achievement['reward']:,} ₽\n"

    if len(user_achievements) == 0:
        achievements_text += "Пока нет полученных достижений\n"

    achievements_text += "\n🔒 ДОСТУПНЫЕ:\n"

    # Доступные достижения
    for achievement_id, achievement in ACHIEVEMENTS.items():
        if achievement_id not in user_achievements and not achievement.get("hidden", False):
            # Показываем прогресс
            condition = achievement["condition"]
            progress = "❓"

            if condition == "total_deposited >= 1":
                progress = f"{user.get('total_deposited', 0)}/1"
            elif condition == "business_level >= 1":
                progress = f"{user.get('business_level', 0)}/1"
            elif condition == "casino_wins >= 10000":
                progress = f"{user.get('stats', {}).get('casino_wins', 0)}/10000"
            elif condition == "items_sold >= 10":
                progress = f"{user.get('stats', {}).get('items_sold', 0)}/10"
            elif condition == "unique_gifts >= 5":
                unique_gifts = len(set(user.get("gifts", [])))
                progress = f"{unique_gifts}/5"
            elif condition == "balance >= 1000000":
                progress = f"{user.get('balance', 0):,}/1,000,000"
            elif condition == "jackpot_wins >= 1":
                progress = f"{user.get('stats', {}).get('jackpot_wins', 0)}/1"
            elif condition == "successful_robs >= 5":
                progress = f"{user.get('stats', {}).get('successful_robs', 0)}/5"
            elif condition == "money_given >= 50000":
                progress = f"{user.get('stats', {}).get('money_given', 0):,}/50,000"
            elif condition == "total_bets >= 100":
                progress = f"{user.get('stats', {}).get('total_bets', 0)}/100"
            elif condition == "business_level >= 8":
                progress = f"{user.get('business_level', 0)}/8"

            achievements_text += f"{achievement['emoji']} {achievement['name']} - {progress}\n"

    achievements_text += "\n❓ СЕКРЕТНЫЕ:\n"
    secret_count = sum(1 for a in ACHIEVEMENTS.values() if a.get("hidden", False))
    achievements_text += f"🔒 {secret_count} скрытых достижений\n\n"

    achievements_text += "💡 Достижения открываются автоматически при выполнении условий!"

    send_message(message["chat"]["id"], achievements_text, reply_to=message["message_id"])


def handle_secret_command(data, message):
    """Секретная команда для получения достижения"""
    user_id = str(message["from"]["id"])
    user = get_user(data, user_id)

    # Проверяем, есть ли у пользователя улучшение аналитики
    if not has_upgrade(user, "analytics_dashboard"):
        send_message(message["chat"]["id"],
                    "❌ Эта команда доступна только с улучшением 'Панель аналитики'!",
                    reply_to=message["message_id"])
        return

    # Проверяем время (должна быть ночь)
    current_hour = datetime.now().hour
    if not (0 <= current_hour < 5):
        send_message(message["chat"]["id"],
                    "❌ Секретная команда работает только с 00:00 до 05:00!",
                    reply_to=message["message_id"])
        return

    # Проверяем баланс (должен быть больше 7777)
    if user["balance"] < 7777:
        send_message(message["chat"]["id"],
                    f"❌ Для доступа к секрету нужен баланс не менее 7,777₽! У вас: {user['balance']:,}₽",
                    reply_to=message["message_id"])
        return

    # Выдаем достижение
    if award_achievement(data, user_id, "secret_agent", message):
        # Обновляем статистику
        if "stats" not in user:
            user["stats"] = {}
        user["stats"]["found_secret"] = user["stats"].get("found_secret", 0) + 1
        save_data(data)

        send_message(message["chat"]["id"],
                    "🎉 Вы нашли секретное достижение 'Тайный агент'!",
                    reply_to=message["message_id"])
    else:
        send_message(message["chat"]["id"],
                    "🎭 Вы уже получали это достижение!",
                    reply_to=message["message_id"])

def handle_admin_auto_collect(data, message, args):
    """Админская команда для запуска авто-сбора всем пользователям"""
    user_id = message["from"]["id"]

    # Проверяем права администратора
    if not is_admin(user_id):
        send_message(message["chat"]["id"],
                     "❌ Только для админов!",
                     reply_to=message["message_id"])
        return

    # Проверяем аргументы (необязательный аргумент - принудительный сбор)
    force_collect = False
    if args and args[0] == "force":
        force_collect = True

    now = datetime.now()
    collected_total = 0
    users_processed = 0
    notifications_sent = 0

    send_message(message["chat"]["id"],
                 f"🔄 Запускаю авто-сбор для всех пользователей...\n\n"
                 f"⏰ Время: {now.strftime('%H:%M:%S')}\n"
                 f"📊 Проверяю {len(data['users'])} пользователей...",
                 reply_to=message["message_id"])

    for target_user_id, user in data["users"].items():
        try:
            # Проверяем, есть ли у пользователя улучшение авто-сбора
            if "auto_collect" in user.get("upgrades", []):
                level = user.get("business_level", 0)
                if level > 0:
                    last_auto_collect = user.get("last_auto_collect")

                    # Проверяем, можно ли собирать (если не принудительный режим)
                    can_collect = True
                    if not force_collect and last_auto_collect:
                        last_time = datetime.fromisoformat(last_auto_collect)
                        hours_passed = (now - last_time).total_seconds() / 3600
                        can_collect = hours_passed >= 4

                    if can_collect:
                        biz = BUSINESS_LEVELS[level]
                        income = int(biz['income'] * 4)  # 4 часа дохода

                        # Проверяем бустер двойного дохода
                        if check_active_booster(user, "double_income"):
                            income *= BOOSTERS["double_income"]["multiplier"]

                        user["balance"] += income
                        user["last_auto_collect"] = now.isoformat()
                        user["last_income"] = now.isoformat()
                        collected_total += income
                        users_processed += 1

                        # Уведомляем пользователя в ЛС
                        try:
                            result = send_message(
                                target_user_id,
                                f"🤖 Авто-сбор доходов!\n\n"
                                f"💰 Собрано: {income:,} ₽\n"
                                f"💵 Ваш баланс: {user['balance']:,} ₽\n"
                                f"⏰ Следующий сбор через 4 часа"
                            )
                            if result and result.get("ok"):
                                notifications_sent += 1
                        except Exception as e:
                            print(f"❌ Не удалось отправить уведомление {target_user_id}: {e}")
        except Exception as e:
            print(f"❌ Ошибка при обработке пользователя {target_user_id}: {e}")

    save_data(data)

    # Отправляем отчет админу
    admin_report = f"""
✅ АДМИНСКИЙ АВТО-СБОР ЗАВЕРШЕН!

📊 Статистика:
• 👥 Всего пользователей: {len(data['users'])}
• 🤖 С авто-сбором: {users_processed}
• 💰 Общая сумма: {collected_total:,} ₽
• 📨 Уведомлений отправлено: {notifications_sent}
• ⏰ Время: {now.strftime('%H:%M:%S')}

{"⚡ РЕЖИМ: ПРИНУДИТЕЛЬНЫЙ" if force_collect else "⏳ РЕЖИМ: ТОЛЬКО ГОТОВЫЕ К СБОРУ"}

💡 Команды:
• автосбор - обычный сбор (только если прошло 4 часа)
• автосбор force - принудительный сбор (всем независимо от времени)
"""

    send_message(message["chat"]["id"], admin_report, reply_to=message["message_id"])
    print(f"👑 Админский авто-сбор: {users_processed} пользователей, {collected_total}₽")

def check_auto_collect(data):
    """Проверить и автоматически собрать доходы для всех пользователей с авто-сбором"""
    now = datetime.now()
    collected_total = 0
    users_processed = 0

    for user_id, user in data["users"].items():
        # Проверяем, есть ли у пользователя улучшение авто-сбора
        if "auto_collect" in user.get("upgrades", []):
            level = user.get("business_level", 0)
            if level > 0:
                last_income = user.get("last_income")

                if last_income:
                    try:
                        last_time = datetime.fromisoformat(last_income)
                        hours_passed = (now - last_time).total_seconds() / 3600

                        # Собираем каждые 4 часа
                        if hours_passed >= 4:
                            biz = BUSINESS_LEVELS[level]
                            income = int(biz['income'] * 4)  # 4 часа дохода

                            # Проверяем бустер двойного дохода
                            if check_active_booster(user, "double_income"):
                                income *= BOOSTERS["double_income"]["multiplier"]

                            user["balance"] += income
                            user["last_income"] = now.isoformat()
                            collected_total += income
                            users_processed += 1

                            # Логируем для отладки
                            print(f"🤖 Авто-сбор для {user_id}: +{income}₽")
                    except Exception as e:
                        print(f"❌ Ошибка авто-сбора для {user_id}: {e}")
                else:
                    # Если нет времени последнего сбора, устанавливаем текущее время
                    user["last_income"] = now.isoformat()

    if collected_total > 0:
        save_data(data)
        print(f"💰 Авто-сбор завершен: {users_processed} пользователей, {collected_total}₽")

    return collected_total

# ===== UPDATED GAME FUNCTIONS WITH BOOSTERS =====

def handle_slots(data, message, args):
    user_id = str(message["from"]["id"])
    user = get_user(data, user_id)

    if not args:
        send_message(message["chat"]["id"],
                     "🎰 Укажи ставку, ебать! Пример: слоты 100",
                     reply_to=message["message_id"])
        return

    try:
        bet = int(args[0])
    except:
        send_message(message["chat"]["id"],
                     "❌ Бля, укажи нормальное число, а не хуйню какую-то!",
                     reply_to=message["message_id"])
        return

    if bet < 10:
        send_message(message["chat"]["id"],
                     "❌ Минимальная ставка: 10 ₽, не жмись, чёрт!",
                     reply_to=message["message_id"])
        return

    if bet > 10000:
        send_message(message["chat"]["id"],
                     "❌ Максимальная ставка: 10,000 ₽, не еби мозг!",
                     reply_to=message["message_id"])
        return

    if user["balance"] < bet:
        send_message(
            message["chat"]["id"],
            f"❌ Нихуя себе! Баланс пуст как твоя голова! Ваш баланс: {user['balance']:,} ₽",
            reply_to=message["message_id"])
        return

    symbols = ["🍒", "🍋", "🍊", "🍇", "💎", "7️⃣", "🍀", "⭐"]
    slot1 = random.choice(symbols)
    slot2 = random.choice(symbols)
    slot3 = random.choice(symbols)

    user["balance"] -= bet
    user_stats = user.get("stats", {})
    user_stats["total_bets"] = user_stats.get("total_bets", 0) + 1

    current_hour = datetime.now().hour
    if 0 <= current_hour < 5:
        user_stats["night_games"] = user_stats.get("night_games", 0) + 1

    booster_bonus = get_booster_bonus(user, "slots")
    user_real_chances = get_user_chances(user_id)
    win_chance = user_real_chances['slots_win_chance'] + booster_bonus["chance_bonus"]

    win_roll = random.random() * 100
    win = win_roll < win_chance

    if slot1 == slot2 == slot3:
        jackpot_chance = user_real_chances['slots_jackpot_chance'] + booster_bonus["chance_bonus"]
        is_jackpot = (random.random() * 100) < jackpot_chance

        if slot1 == "💎" and is_jackpot:
            multiplier = 10 * booster_bonus["multiplier"]
            user_stats["jackpot_wins"] = user_stats.get("jackpot_wins", 0) + 1
            result = f"🎉 БЛЯЯЯЯ! ДЖЕКПОТ! Ты выебал систему на {bet * multiplier:,} ₽ (x{multiplier})!"
        elif slot1 == "7️⃣":
            multiplier = 7 * booster_bonus["multiplier"]
            result = f"🎉 Ахуеть! 777! Ты сорвал {bet * multiplier:,} ₽ (x{multiplier})!"
        elif slot1 == "⭐":
            multiplier = 5 * booster_bonus["multiplier"]
            result = f"🎉 Бля, звезда! Забирай {bet * multiplier:,} ₽ (x{multiplier})!"
        else:
            multiplier = 3 * booster_bonus["multiplier"]
            result = f"🎉 Три в ряд! На, заебись: {bet * multiplier:,} ₽ (x{multiplier})!"

        winnings = bet * multiplier
        user["balance"] += winnings
        user_stats["casino_wins"] = user_stats.get("casino_wins", 0) + winnings

        if booster_bonus["multiplier"] > 1:
            user_stats["rainbow_wins"] = user_stats.get("rainbow_wins", 0) + 1
            
        # ===== ДОБАВЛЕНО: Прогресс ивента =====
        check_event_progress(user, "casino_win", winnings)

    elif (slot1 == slot2 or slot2 == slot3 or slot1 == slot3) and win:
        multiplier = 2 * booster_bonus["multiplier"]
        winnings = bet * multiplier
        user["balance"] += winnings
        user_stats["casino_wins"] = user_stats.get("casino_wins", 0) + winnings
        result = f"✨ Две одинаковые! Ну ок, забирай свои {winnings:,} ₽ (x{multiplier})"
        
        # ===== ДОБАВЛЕНО: Прогресс ивента =====
        check_event_progress(user, "casino_win", winnings)
    else:
        result = f"😔 Ебаный рот, проебал {bet:,} ₽! Повезёт в следующий раз, лузер"

    # ===== ДОБАВЛЕНО: Прогресс ивента (ставка) =====
    check_event_progress(user, "casino_bet", 1)

    save_data(data)

    user_emoji = get_user_emoji(user)

    booster_info = ""
    if booster_bonus["chance_bonus"] > 0:
        booster_info = f"\n🍀 Бустер удачи: +{booster_bonus['chance_bonus']}% к шансам"
    if booster_bonus["multiplier"] > 1:
        booster_info += f"\n🌈 Бустер множителя: x{booster_bonus['multiplier']} к выигрышу"

    text = f"""
{user_emoji} ═══ СЛОТЫ ═══ {user_emoji}

  [ {slot1} | {slot2} | {slot3} ]

{result}
{booster_info}

{user_emoji} Твой баланс: {user['balance']:,} ₽
"""
    send_message(message["chat"]["id"], text, reply_to=message["message_id"])
    check_and_award_achievements(data, user_id, message)

def handle_coinflip(data, message, args):
    user_id = str(message["from"]["id"])
    user = get_user(data, user_id)

    if not args:
        send_message(message["chat"]["id"],
                     "🪙 Бля, ставку укажи! Пример: монетка 100",
                     reply_to=message["message_id"])
        return

    try:
        bet = int(args[0])
    except:
        send_message(message["chat"]["id"],
                     "❌ Ебать, число введи нормальное!",
                     reply_to=message["message_id"])
        return

    if bet < 10 or bet > 10000:
        send_message(message["chat"]["id"],
                     "❌ От 10 до 10,000 ₽ ставь, не выебывайся!",
                     reply_to=message["message_id"])
        return

    if user["balance"] < bet:
        send_message(message["chat"]["id"],
                     f"❌ Хуй тебе, а не ставку! Баланс: {user['balance']:,} ₽",
                     reply_to=message["message_id"])
        return

    user["balance"] -= bet
    user_stats = user.get("stats", {})
    user_stats["total_bets"] = user_stats.get("total_bets", 0) + 1

    flip = random.choice(["орёл", "решка"])

    booster_bonus = get_booster_bonus(user, "coinflip")
    user_real_chances = get_user_chances(user_id)
    win_chance = user_real_chances['coinflip_win_chance'] + booster_bonus["chance_bonus"]

    win_roll = random.random() * 100
    win = win_roll < win_chance

    if win:
        winnings = bet * 2
        user["balance"] += winnings
        user_stats["casino_wins"] = user_stats.get("casino_wins", 0) + winnings
        emoji = "🦅" if flip == "орёл" else "👑"
        result = f"🎉 {emoji} {flip.upper()}! Ахуеть, выиграл {winnings:,} ₽!"
        
        # ===== ДОБАВЛЕНО: Прогресс ивента =====
        check_event_progress(user, "casino_win", winnings)
    else:
        emoji = "🦅" if flip == "орёл" else "👑"
        result = f"😔 {emoji} {flip.upper()}! Проебано {bet:,} ₽, сочувствую"

    # ===== ДОБАВЛЕНО: Прогресс ивента (ставка) =====
    check_event_progress(user, "casino_bet", 1)

    save_data(data)

    user_emoji = get_user_emoji(user)

    booster_info = ""
    if booster_bonus["chance_bonus"] > 0:
        booster_info = f"\n🍀 Бустер удачи: +{booster_bonus['chance_bonus']}% к шансам"

    text = f"""
{user_emoji} ═══ МОНЕТКА ═══ {user_emoji}

{result}
{booster_info}

{user_emoji} Твой баланс: {user['balance']:,} ₽
"""
    send_message(message["chat"]["id"], text, reply_to=message["message_id"])
    check_and_award_achievements(data, user_id, message)


def handle_collect_income(data, message):
    user_id = str(message["from"]["id"])
    user = get_user(data, user_id)
    level = user.get("business_level", 0)

    if level == 0:
        send_message(message["chat"]["id"],
                     "❌ У вас нет бизнеса!",
                     reply_to=message["message_id"])
        return

    # ==== ПРОВЕРКА НА АВТО-СБОР ====
    if "auto_collect" in user.get("upgrades", []):
        send_message(message["chat"]["id"],
                     "❌ У вас активен авто-сбор!\n\n"
                     "🤖 Доходы собираются автоматически каждые 4 часа.\n"
                     "⏰ Вы не можете собирать доход вручную.\n\n"
                     "💡 Если хотите отключить авто-сбор, обратитесь к администратору.",
                     reply_to=message["message_id"])
        return
    # ==== КОНЕЦ ПРОВЕРКИ ====

    biz = BUSINESS_LEVELS[level]
    last_income = user.get("last_income")

    if last_income:
        last_time = datetime.fromisoformat(last_income)
        hours_passed = (datetime.now() - last_time).total_seconds() / 3600
        hours_passed = min(hours_passed, 24)
    else:
        hours_passed = 1

    # Стандартный интервал для ручного сбора
    if hours_passed < 0.1:  # 6 минут минимальный интервал
        send_message(message["chat"]["id"],
                     "⏰ Подождите немного перед следующим сбором!",
                     reply_to=message["message_id"])
        return

    income = int(biz['income'] * hours_passed)

    # Проверяем бустер двойного дохода
    if check_active_booster(user, "double_income"):
        income *= BOOSTERS["double_income"]["multiplier"]

    user["balance"] += income
    user["last_income"] = datetime.now().isoformat()
    
    # ===== ДОБАВЛЕНО: Прогресс ивента =====
    check_event_progress(user, "business_collect", 1)
    
    save_data(data)

    user_emoji = get_profile_decoration_custom(user)

    booster_info = ""
    if check_active_booster(user, "double_income"):
        booster_info = f"\n💰 Бустер дохода: x{BOOSTERS['double_income']['multiplier']} к заработку"

    send_message(
        message["chat"]["id"],
        f"""
{user_emoji} 💰 Собрано {income:,} ₽ с бизнеса!
⏰ За {hours_passed:.1f} час(ов)
{booster_info}
💵 Баланс: {user['balance']:,} ₽""",
        reply_to=message["message_id"],
        parse_mode="HTML"
    )

# ===== ЕЖЕДНЕВНЫЙ БОНУС =====
def handle_bonus(data, message):
    """Ежедневный бонус (раз в 24 часа)"""
    user_id = str(message["from"]["id"])
    user = get_user(data, user_id)
    user_emoji = get_user_emoji(user)

    # Проверяем последний бонус
    last_bonus = user.get("last_bonus")
    now = datetime.now()

    if last_bonus:
        last_time = datetime.fromisoformat(last_bonus)
        hours_passed = (now - last_time).total_seconds() / 3600

        if hours_passed < 24:
            next_bonus_in = 24 - hours_passed
            hours_left = int(next_bonus_in)
            minutes_left = int((next_bonus_in - hours_left) * 60)

            send_message(
                message["chat"]["id"],
                f"{user_emoji} ⏰ Бонус уже получен!\n\n"
                f"💰 Следующий бонус через:\n"
                f"⏳ {hours_left} час. {minutes_left} мин.\n\n"
                f"🕐 Время последнего получения: {last_time.strftime('%H:%M')}",
                reply_to=message["message_id"]
            )
            return

    # Выдаем бонус
    bonus_amount = random.randint(100, 500)  # От 100 до 500₽
    user["balance"] += bonus_amount
    user["last_bonus"] = now.isoformat()

    # Сохраняем
    save_data(data)

    send_message(
        message["chat"]["id"],
        f"{user_emoji} 🎁 ЕЖЕДНЕВНЫЙ БОНУС!\n\n"
        f"💰 Вы получили: {bonus_amount:,} ₽\n"
        f"💵 Ваш баланс: {user['balance']:,} ₽\n\n"
        f"⏰ Следующий бонус через 24 часа\n"
        f"🕐 Время получения: {now.strftime('%H:%M:%S')}",
        reply_to=message["message_id"]
    )


def handle_profile(data, message):
    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    username = message["from"].get("username")
    first_name = message["from"].get("first_name", "Пользователь")

    update_user_info(data, user_id, username, first_name)

    target_id = user_id
    if "reply_to_message" in message:
        reply_user = message["reply_to_message"]["from"]
        target_id = reply_user["id"]
        update_user_info(data, target_id, reply_user.get("username"),
                         reply_user.get("first_name"))

    profile = build_profile(data, target_id)
    send_message(chat_id, profile, reply_to=message["message_id"], parse_mode="HTML")  # <-- ДОБАВИТЬ


def handle_gift_give(data, message, args):
    """Выдать подарок пользователю (админ)"""
    if not is_admin(message["from"]["id"]):
        send_message(message["chat"]["id"],
                     "❌ Только админы могут выдавать подарки!",
                     reply_to=message["message_id"])
        return

    if not args:
        # Показываем список подарков прямо в чате
        gifts_list = "🎁 **СПИСОК ПОДАРКОВ (1-15):**\n\n"
        for k, v in GIFTS.items():
            if 'custom_emoji' in v:
                gifts_list += f"{k}. {v['custom_emoji']} {v['name']} [{v['rarity']}]\n"
            else:
                gifts_list += f"{k}. {v['emoji']} {v['name']} [{v['rarity']}]\n"

        gifts_list += "\n**💡 Использование:**\n`подарить [номер] @username`"
        gifts_list += "\n`подарить [номер] [ID]`"

        send_message(message["chat"]["id"],
                     gifts_list,
                     reply_to=message["message_id"],
                     parse_mode="Markdown")
        return

    try:
        gift_id = int(args[0])
    except:
        send_message(message["chat"]["id"],
                     "❌ Укажите номер подарка! Пример: `подарить 1 @username`",
                     reply_to=message["message_id"],
                     parse_mode="Markdown")
        return

    if gift_id not in GIFTS:
        send_message(message["chat"]["id"],
                     f"❌ Подарок не найден! Доступные номера: 1-{len(GIFTS)}",
                     reply_to=message["message_id"])
        return

    # ===== СПОСОБ 1: Через @username =====
    if len(args) > 1 and args[1].startswith('@'):
        username = args[1][1:]  # Убираем @

        # Ищем пользователя по username
        target_user = None
        target_id = None

        for user_id, user_data in data["users"].items():
            if user_data.get("username") == username:
                target_user = user_data
                target_id = user_id
                break

        if not target_user:
            send_message(message["chat"]["id"],
                        f"❌ Пользователь @{username} не найден!",
                        reply_to=message["message_id"])
            return

    # ===== СПОСОБ 2: Через ID пользователя =====
    elif len(args) > 1 and args[1].isdigit():
        target_id = args[1]

        if target_id not in data["users"]:
            send_message(message["chat"]["id"],
                        f"❌ Пользователь с ID {target_id} не найден!",
                        reply_to=message["message_id"])
            return

        target_user = data["users"][target_id]

    # ===== СПОСОБ 3: Через ответ на сообщение (старый способ) =====
    elif "reply_to_message" in message:
        target_user_obj = message["reply_to_message"]["from"]
        target_id = str(target_user_obj["id"])

        if target_id not in data["users"]:
            # Создаем запись если пользователя нет
            update_user_info(data, target_id, target_user_obj.get("username"),
                           target_user_obj.get("first_name"))

        target_user = data["users"][target_id]

    else:
        send_message(message["chat"]["id"],
                     "❌ Укажите получателя!\n\n"
                     "**Способы:**\n"
                     "1. Ответьте на сообщение и напишите `подарить [номер]`\n"
                     "2. Укажите username: `подарить 1 @username`\n"
                     "3. Укажите ID: `подарить 1 5175013270`",
                     reply_to=message["message_id"],
                     parse_mode="Markdown")
        return

    # Проверяем, есть ли уже подарок
    if "gifts" not in target_user:
        target_user["gifts"] = []

    if gift_id in target_user["gifts"]:
        gift = GIFTS[gift_id]
        if 'custom_emoji' in gift:
            gift_display = f"{gift['custom_emoji']} {gift['name']}"
        else:
            gift_display = f"{gift['emoji']} {gift['name']}"

        send_message(message["chat"]["id"],
                     f"❌ У пользователя уже есть этот подарок!\n"
                     f"{gift_display}",
                     reply_to=message["message_id"])
        return

    # Выдаем подарок
    target_user["gifts"].append(gift_id)
    save_data(data)

    gift = GIFTS[gift_id]
    user_emoji = get_user_emoji(target_user)
    target_name = format_user_mention(target_user, target_id)
    admin_user = get_user(data, str(message["from"]["id"]))
    admin_emoji = get_user_emoji(admin_user)

    # Используем кастомное эмодзи
    gift_display = format_gift_with_custom_emoji(gift_id)

    send_message(
        message["chat"]["id"],
        f"{admin_emoji} ➜ {user_emoji}\n"
        f"✅ Подарок выдан!\n\n"
        f"{gift_display}\n"
        f"📊 Редкость: {gift['rarity']}\n"
        f"👤 Получатель: {target_name}",
        reply_to=message["message_id"],
        parse_mode="HTML"
    )

def handle_gift_transfer(data, message, args):
    if "reply_to_message" not in message:
        send_message(
            message["chat"]["id"],
            "❌ Ответьте на сообщение пользователя, которому хотите передать подарок!",
            reply_to=message["message_id"])
        return

    user_id = str(message["from"]["id"])
    user = get_user(data, user_id)

    if not user.get("gifts"):
        send_message(message["chat"]["id"],
                     "❌ У вас нет подарков для передачи!",
                     reply_to=message["message_id"])
        return

    if not args:
        my_gifts = "\n".join([
            f"{g}. {format_gift_with_custom_emoji(g)}"  # <-- ИЗМЕНИТЬ
            for g in user["gifts"] if g in GIFTS
        ])
        send_message(
            message["chat"]["id"],
            f"🎁 Ваши подарки:\n{my_gifts}\n\nИспользуйте: передать [номер]",
            reply_to=message["message_id"],
            parse_mode="HTML"  # <-- ДОБАВИТЬ
        )
        return

    try:
        gift_id = int(args[0])
    except:
        send_message(message["chat"]["id"],
                     "❌ Укажите номер подарка!",
                     reply_to=message["message_id"])
        return

    if gift_id not in user["gifts"]:
        send_message(message["chat"]["id"],
                     "❌ У вас нет этого подарка!",
                     reply_to=message["message_id"])
        return

    target_user = message["reply_to_message"]["from"]
    target_id = str(target_user["id"])

    if target_id == user_id:
        send_message(message["chat"]["id"],
                     "❌ Нельзя передать подарок самому себе!",
                     reply_to=message["message_id"])
        return

    update_user_info(data, target_id, target_user.get("username"),
                     target_user.get("first_name"))
    target = get_user(data, target_id)

    if gift_id in target["gifts"]:
        send_message(message["chat"]["id"],
                     "❌ У получателя уже есть этот подарок!",
                     reply_to=message["message_id"])
        return

    user["gifts"].remove(gift_id)
    target["gifts"].append(gift_id)
    save_data(data)

    gift = GIFTS[gift_id]
    sender_emoji = get_profile_decoration_custom(user)  # <-- ИЗМЕНИТЬ
    receiver_emoji = get_profile_decoration_custom(target)  # <-- ИЗМЕНИТЬ
    sender_name = format_user_mention(user, user_id)
    target_name = format_user_mention(target, target_id)

    gift_display = format_gift_with_custom_emoji(gift_id)  # <-- НОВАЯ СТРОКА

    send_message(
        message["chat"]["id"],
        f"{sender_emoji} ➜ {receiver_emoji}\n✅ Подарок {gift_display}\n{sender_emoji} {sender_name} ➜ {receiver_emoji} {target_name}",
        reply_to=message["message_id"],
        parse_mode="HTML"  # <-- ДОБАВИТЬ
    )


def handle_gift_sell(data, message, args):
    if "reply_to_message" not in message:
        send_message(
            message["chat"]["id"],
            "❌ Ответьте на сообщение пользователя, которому хотите продать подарок!",
            reply_to=message["message_id"])
        return

    user_id = str(message["from"]["id"])
    user = get_user(data, user_id)

    if not user.get("gifts"):
        send_message(message["chat"]["id"],
                     "❌ У вас нет подарков для продажи!",
                     reply_to=message["message_id"])
        return

    if len(args) < 2:
        my_gifts = "\n".join([
            f"{g}. {format_gift_with_custom_emoji(g)}"
            for g in user["gifts"] if g in GIFTS
        ])
        send_message(
            message["chat"]["id"],
            f"🎁 Ваши подарки:\n{my_gifts}\n\nИспользуйте: продать [номер] [цена]",
            reply_to=message["message_id"],
            parse_mode="HTML"
        )
        return

    try:
        gift_id = int(args[0])
        price = int(args[1])
    except:
        send_message(message["chat"]["id"],
                     "❌ Укажите номер подарка и цену! Пример: продать 1 5000",
                     reply_to=message["message_id"])
        return

    if gift_id not in user["gifts"]:
        send_message(message["chat"]["id"],
                     "❌ У вас нет этого подарка!",
                     reply_to=message["message_id"])
        return

    if price <= 0:
        send_message(message["chat"]["id"],
                     "❌ Цена должна быть положительной!",
                     reply_to=message["message_id"])
        return

    target_user = message["reply_to_message"]["from"]
    target_id = str(target_user["id"])

    if target_id == user_id:
        send_message(message["chat"]["id"],
                     "❌ Нельзя продать подарок самому себе!",
                     reply_to=message["message_id"])
        return

    update_user_info(data, target_id, target_user.get("username"),
                     target_user.get("first_name"))
    target = get_user(data, target_id)

    if gift_id in target["gifts"]:
        send_message(message["chat"]["id"],
                     "❌ У покупателя уже есть этот подарок!",
                     reply_to=message["message_id"])
        return

    if target["balance"] < price:
        send_message(
            message["chat"]["id"],
            f"❌ У покупателя недостаточно средств! Нужно: {price:,} ₽",
            reply_to=message["message_id"])
        return

    user["gifts"].remove(gift_id)
    target["gifts"].append(gift_id)
    user["balance"] += price
    target["balance"] -= price
    data["stats"]["total_transactions"] += 1

    # Обновляем статистику продаж
    user_stats = user.get("stats", {})
    user_stats["items_sold"] = user_stats.get("items_sold", 0) + 1

    # ===== ДОБАВЛЕНО: Прогресс ивента =====
    check_event_progress(user, "gift_sell", 1)

    save_data(data)

    gift = GIFTS[gift_id]
    target_name = format_user_mention(target, target_id)
    seller_name = format_user_mention(user, user_id)

    seller_emoji = get_profile_decoration_custom(user)
    buyer_emoji = get_profile_decoration_custom(target)
    gift_display = format_gift_with_custom_emoji(gift_id)

    send_message(message["chat"]["id"],
                 f"""
{seller_emoji} ➜ {buyer_emoji}
💰 Сделка завершена!

{gift_display}
👤 Продавец: {seller_name}
👤 Покупатель: {target_name}
💵 Цена: {price:,} ₽
""",
                 reply_to=message["message_id"],
                 parse_mode="HTML")


# ===== ОГРАБЛЕНИЕ КАЗНЫ =====
def handle_rob_treasury(data, message):
    """Попытаться ограбить казну (раз в час)"""
    user_id = str(message["from"]["id"])
    user = get_user(data, user_id)
    user_emoji = get_user_emoji(user)

    # Проверяем последнее ограбление
    last_rob = user.get("last_rob")
    now = datetime.now()

    if last_rob:
        last_time = datetime.fromisoformat(last_rob)
        minutes_passed = (now - last_time).total_seconds() / 60

        if minutes_passed < 60:
            next_rob_in = 60 - minutes_passed
            minutes_left = int(next_rob_in)
            seconds_left = int((next_rob_in - minutes_left) * 60)

            send_message(
                message["chat"]["id"],
                f"{user_emoji} ⏰ Подождите перед следующим ограблением!\n\n"
                f"💰 Следующая попытка через:\n"
                f"⏳ {minutes_left} мин. {seconds_left} сек.\n\n"
                f"🕐 Последняя попытка: {last_time.strftime('%H:%M:%S')}",
                reply_to=message["message_id"]
            )
            return

    # Проверяем, есть ли деньги в казне
    if "treasury" not in data:
        data["treasury"] = 50000

    if data["treasury"] <= 0:
        send_message(
            message["chat"]["id"],
            f"{user_emoji} 🏦 КАЗНА ПУСТА!\n\n"
            f"💰 В казне: 0 ₽\n"
            f"💡 Попробуйте позже, когда казна пополнится",
            reply_to=message["message_id"]
        )
        return

    # Получаем шансы пользователя
    user_real_chances = get_user_chances(user_id)

    success_chance = user_real_chances['treasury_rob_success']
    escape_chance = user_real_chances['treasury_rob_escape']
    caught_chance = user_real_chances['treasury_rob_caught']

    # Определяем максимальную сумму для ограбления
    max_rob_amount = min(100000, int(data["treasury"] * 0.1))
    min_rob_amount = max(100, int(data["treasury"] * 0.01))

    rob_amount = random.randint(min_rob_amount, max_rob_amount)

    # Симуляция ограбления
    roll = random.random() * 100
    user["last_rob"] = now.isoformat()

    # 1. Успешное ограбление
    if roll < success_chance:
        user["balance"] += rob_amount
        data["treasury"] -= rob_amount

        user_stats = user.get("stats", {})
        user_stats["successful_robs"] = user_stats.get("successful_robs", 0) + 1

        # ===== ДОБАВЛЕНО: Прогресс ивента =====
        check_event_progress(user, "robbery", 1)
        check_event_progress(user, "robbery_success", 1)

        save_data(data)

        send_message(
            message["chat"]["id"],
            f"{user_emoji} 🎉 УСПЕШНОЕ ОГРАБЛЕНИЕ!\n\n"
            f"💰 Украдено: {rob_amount:,} ₽\n"
            f"💵 Ваш баланс: {user['balance']:,} ₽\n"
            f"🏦 Осталось в казне: {data['treasury']:,} ₽\n\n"
            f"🕐 Следующая попытка через 1 час\n"
            f"🎯 Ваш шанс успеха: {success_chance}%",
            reply_to=message["message_id"]
        )

    # 2. Удалось сбежать
    elif roll < success_chance + escape_chance:
        # ===== ДОБАВЛЕНО: Прогресс ивента =====
        check_event_progress(user, "robbery", 1)
        
        save_data(data)

        send_message(
            message["chat"]["id"],
            f"{user_emoji} 🏃‍♂️ УДАЛОСЬ СБЕЖАТЬ!\n\n"
            f"⚠️ Вас заметили, но вы успели сбежать!\n"
            f"💰 Вы ничего не украли\n"
            f"💵 Ваш баланс: {user['balance']:,} ₽\n"
            f"🏦 В казне: {data['treasury']:,} ₽\n\n"
            f"🕐 Следующая попытка через 1 час\n"
            f"🎯 Шанс побега: {escape_chance}%",
            reply_to=message["message_id"]
        )

    # 3. Поймали
    else:
        penalty = min(rob_amount // 2, user["balance"] // 2)
        user["balance"] -= penalty
        data["treasury"] += penalty

        # ===== ДОБАВЛЕНО: Прогресс ивента =====
        check_event_progress(user, "robbery", 1)

        save_data(data)

        send_message(
            message["chat"]["id"],
            f"{user_emoji} 🚔 ВАС ПОЙМАЛИ!\n\n"
            f"👮‍♂️ Охрана поймала вас с поличным!\n"
            f"💰 Штраф: {penalty:,} ₽\n"
            f"💵 Ваш баланс: {user['balance']:,} ₽\n"
            f"🏦 Казне возвращено: {penalty:,} ₽\n"
            f"💸 Всего в казне: {data['treasury']:,} ₽\n\n"
            f"🕐 Следующая попытка через 1 час\n"
            f"☠️ Шанс быть пойманным: {caught_chance}%",
            reply_to=message["message_id"]
        )

    # Проверяем достижения
    check_and_award_achievements(data, user_id, message)


def handle_balance(data, message):
    user_id = str(message["from"]["id"])
    user = get_user(data, user_id)
    update_user_info(data, user_id, message["from"].get("username"),
                     message["from"].get("first_name"))

    decoration = get_profile_decoration(user)
    send_message(message["chat"]["id"],
                 f"{decoration} <tg-emoji emoji-id=\"5337080053119336309\">👍</tg-emoji> Ваш баланс: {user['balance']:,} ₽",
                 reply_to=message["message_id"])


def handle_admin(data, message):
    user_id = message["from"]["id"]
    if not is_admin(user_id):
        send_message(message["chat"]["id"],
                     "❌ У вас нет доступа к админ-панели!",
                     reply_to=message["message_id"])
        return

    admin_text = f"""
👑 ═══ АДМИН-ПАНЕЛЬ ═══ 👑

📋 Команды управления подарками:
• подарить [номер] - выдать подарок (в ответ на сообщение)
  Доступные номера: 1-{len(GIFTS)}

📊 Статистика:
• /stats - общая статистика бота

💰 Управление балансом:
• выдать [сумма] - выдать деньги (в ответ на сообщение)
• забрать [сумма] - забрать деньги (в ответ на сообщение)

🎰 Управление шансами:
• шансы - показать текущие настройки шансов
• шанс [тип] [число]% - установить шанс

💰 Управление промокодами:
• создать код [сумма] - создать промокод для пополнения
• список кодов - показать все промокоды
• удалить код [код] - удалить промокод

🛒 Маркетплейс:
• Управление товарами через ЛС бота

🚀 Управление бустерами и улучшениями:
• /booster_shop - показать магазин бустеров
• /active_boosters - показать активные бустеры
• выдать бустер [ID] [часы] - выдать бустер пользователю (в ответ)
• забрать бустер [ID] - забрать бустер у пользователя (в ответ)
• выдать улучшение [ID] - выдать улучшение пользователю (в ответ)
• забрать улучшение [ID] - забрать улучшение у пользователя (в ответ)
• показать бустеры - показать бустеры и улучшения пользователя (в ответ)

🏆 Управление достижениями:
• /achievements - показать достижения
• /secret - секретная команда

👥 Модерация:
• мут - замутить пользователя
• бан - забанить пользователя
• кик - кикнуть пользователя

📋 Список подарков:
"""
    gifts_list = "\n".join([
        f"{k}. {v['emoji']} {v['name']} [{v['rarity']}]"
        for k, v in GIFTS.items()
    ])
    send_message(message["chat"]["id"],
                 admin_text + gifts_list,
                 reply_to=message["message_id"])


def handle_chance_settings(data, message):
    user_id = message["from"]["id"]
    if not is_admin(user_id):
        send_message(message["chat"]["id"],
                     "❌ Только для админов!",
                     reply_to=message["message_id"])
        return

    settings_text = f"""
🎰 ═══ НАСТРОЙКИ ШАНСОВ ═══ 🎰

🎰 Казино:
• Слоты (шанс выигрыша): {CHANCE_SETTINGS['slots_win_chance']}%
• Слоты (шанс джекпота): {CHANCE_SETTINGS['slots_jackpot_chance']}%
• Монетка (шанс выигрыша): {CHANCE_SETTINGS['coinflip_win_chance']}%
• Кости (порог выигрыша): {CHANCE_SETTINGS['dice_win_threshold']}
• Рулетка (шанс красное/чёрное): {CHANCE_SETTINGS['roulette_red_black_chance']}%

🏦 Ограбление казны:
• Успешное ограбление: {CHANCE_SETTINGS['treasury_rob_success']}%
• Удалось сбежать: {CHANCE_SETTINGS['treasury_rob_escape']}%
• Поймали: {CHANCE_SETTINGS['treasury_rob_caught']}%

💡 Команды для изменения:
• шанс выигрыша [число]% - установить общий шанс выигрыша
• шанс ограбления [число]% - установить шанс успешного ограбления
• слоты шанс [число]% - шанс выигрыша в слотах
• слоты джекпот [число]% - шанс джекпота в слотах
• монетка шанс [число]% - шанс выигрыша в монетке
• рулетка шанс [число]% - шанс красное/чёрное в рулетке
"""
    send_message(message["chat"]["id"],
                 settings_text,
                 reply_to=message["message_id"])


def handle_set_chance(data, message, args):
    user_id = message["from"]["id"]
    if not is_admin(user_id):
        send_message(message["chat"]["id"],
                     "❌ Только для админов!",
                     reply_to=message["message_id"])
        return

    if len(args) < 2:
        send_message(message["chat"]["id"],
                     "❌ Используйте: шанс [тип] [число]%\nПример: шанс выигрыша 45%",
                     reply_to=message["message_id"])
        return

    chance_type = args[0].lower()
    chance_value_str = args[1].rstrip('%')

    try:
        chance_value = float(chance_value_str)
        if chance_value < 0 or chance_value > 100:
            send_message(message["chat"]["id"],
                        "❌ Шанс должен быть от 0 до 100%!",
                        reply_to=message["message_id"])
            return
    except:
        send_message(message["chat"]["id"],
                     "❌ Укажите число! Пример: 45%",
                     reply_to=message["message_id"])
        return

    # Общие команды
    if chance_type == "выигрыша":
        CHANCE_SETTINGS['slots_win_chance'] = int(chance_value)
        CHANCE_SETTINGS['coinflip_win_chance'] = int(chance_value)
        response = f"✅ Общий шанс выигрыша установлен на {chance_value}%"

    elif chance_type == "ограбления":
        CHANCE_SETTINGS['treasury_rob_success'] = int(chance_value)
        # Автоматически пересчитываем остальные шансы
        remaining = 100 - chance_value
        CHANCE_SETTINGS['treasury_rob_escape'] = remaining // 2
        CHANCE_SETTINGS['treasury_rob_caught'] = remaining - (remaining // 2)
        response = f"✅ Шанс успешного ограбления установлен на {chance_value}%"

    # Конкретные настройки для казино
    elif chance_type == "слоты":
        if len(args) < 3:
            send_message(message["chat"]["id"],
                        "❌ Используйте: слоты [тип] [число]%\nПример: слоты шанс 40%",
                        reply_to=message["message_id"])
            return
        sub_type = args[1].lower()
        if sub_type == "шанс":
            CHANCE_SETTINGS['slots_win_chance'] = int(chance_value)
            response = f"✅ Шанс выигрыша в слотах установлен на {chance_value}%"
        elif sub_type == "джекпот":
            CHANCE_SETTINGS['slots_jackpot_chance'] = int(chance_value)
            response = f"✅ Шанс джекпота в слотах установлен на {chance_value}%"
        else:
            send_message(message["chat"]["id"],
                        "❌ Неизвестный тип шанса для слотов!",
                        reply_to=message["message_id"])
            return

    elif chance_type == "монетка":
        CHANCE_SETTINGS['coinflip_win_chance'] = int(chance_value)
        response = f"✅ Шанс выигрыша в монетке установлен на {chance_value}%"

    elif chance_type == "рулетка":
        CHANCE_SETTINGS['roulette_red_black_chance'] = chance_value
        response = f"✅ Шанс красное/чёрное в рулетке установлен на {chance_value}%"

    elif chance_type == "кости":
        try:
            threshold = int(chance_value)
            if threshold < 2 or threshold > 12:
                send_message(message["chat"]["id"],
                            "❌ Порог для костей должен быть от 2 до 12!",
                            reply_to=message["message_id"])
                return
            CHANCE_SETTINGS['dice_win_threshold'] = threshold
            response = f"✅ Порог выигрыша в костях установлен на {threshold}"
        except:
            send_message(message["chat"]["id"],
                        "❌ Укажите целое число для порога костей!",
                        reply_to=message["message_id"])
            return

    else:
        send_message(message["chat"]["id"],
                    "❌ Неизвестный тип шанса!",
                    reply_to=message["message_id"])
        return

    save_settings()
    send_message(message["chat"]["id"],
                 response,
                 reply_to=message["message_id"])


def handle_stats(data, message):
    if not is_admin(message["from"]["id"]):
        send_message(message["chat"]["id"],
                     "❌ Только для админов!",
                     reply_to=message["message_id"])
        return

    users_list = []
    for uid, udata in list(data["users"].items())[:20]:
        name = format_user_mention(udata, uid)
        balance = udata.get('balance', 0)
        gifts_count = len(udata.get('gifts', []))
        users_list.append(f"• {name} - {balance:,} ₽ | 🎁 {gifts_count}")

    stats_text = f"""
📊 ═══ СТАТИСТИКА ═══ 📊

👥 Всего пользователей: {data['stats']['total_users']}
💰 Транзакций: {data['stats']['total_transactions']}
🛍️ Продаж на маркете: {data['stats'].get('market_sales', 0)}
💳 Промокодов использовано: {data['stats'].get('promo_codes_used', 0)}
💸 Всего пополнено: {data['stats'].get('total_deposited', 0):,} ₽
🚀 Бустеров куплено: {data['stats'].get('total_boosters_bought', 0)}
🏆 Всего достижений: {data['stats'].get('total_achievements', 0)}

👤 Последние пользователи:
{chr(10).join(users_list) if users_list else 'Нет данных'}
"""
    send_message(message["chat"]["id"],
                 stats_text,
                 reply_to=message["message_id"])


def handle_give_money(data, message, args):
    if not is_admin(message["from"]["id"]):
        send_message(message["chat"]["id"],
                     "❌ Только для админов!",
                     reply_to=message["message_id"])
        return

    if "reply_to_message" not in message:
        send_message(message["chat"]["id"],
                     "❌ Ответьте на сообщение пользователя!",
                     reply_to=message["message_id"])
        return

    if not args:
        send_message(message["chat"]["id"],
                     "❌ Укажите сумму! Пример: выдать 1000",
                     reply_to=message["message_id"])
        return

    try:
        amount = int(args[0])
    except:
        send_message(message["chat"]["id"],
                     "❌ Укажите число!",
                     reply_to=message["message_id"])
        return

    target_user = message["reply_to_message"]["from"]
    target_id = str(target_user["id"])
    update_user_info(data, target_id, target_user.get("username"),
                     target_user.get("first_name"))

    target = get_user(data, target_id)
    target["balance"] += amount
    save_data(data)

    admin_user = get_user(data, str(message["from"]["id"]))
    admin_emoji = get_profile_decoration_custom(admin_user)  # <-- ИЗМЕНИТЬ
    target_emoji = get_profile_decoration_custom(target)  # <-- ИЗМЕНИТЬ
    target_name = format_user_mention(target, target_id)

    send_message(
        message["chat"]["id"],
        f"{admin_emoji} ➜ {target_emoji}\n✅ Выдано {amount:,} ₽\n{target_emoji} {target_name}",
        reply_to=message["message_id"],
        parse_mode="HTML"  # <-- ДОБАВИТЬ
    )


def handle_take_money(data, message, args):
    if not is_admin(message["from"]["id"]):
        send_message(message["chat"]["id"],
                     "❌ Только для админов!",
                     reply_to=message["message_id"])
        return

    if "reply_to_message" not in message:
        send_message(message["chat"]["id"],
                     "❌ Ответьте на сообщение пользователя!",
                     reply_to=message["message_id"])
        return

    if not args:
        send_message(message["chat"]["id"],
                     "❌ Укажите сумму! Пример: забрать 1000",
                     reply_to=message["message_id"])
        return

    try:
        amount = int(args[0])
    except:
        send_message(message["chat"]["id"],
                     "❌ Укажите число!",
                     reply_to=message["message_id"])
        return

    target_user = message["reply_to_message"]["from"]
    target_id = str(target_user["id"])
    update_user_info(data, target_id, target_user.get("username"),
                     target_user.get("first_name"))

    target = get_user(data, target_id)
    target["balance"] -= amount
    save_data(data)

    admin_user = get_user(data, str(message["from"]["id"]))
    admin_emoji = get_profile_decoration_custom(admin_user)  # <-- ИЗМЕНИТЬ
    target_emoji = get_profile_decoration_custom(target)  # <-- ИЗМЕНИТЬ
    target_name = format_user_mention(target, target_id)

    send_message(
        message["chat"]["id"],
        f"{target_emoji} ➜ {admin_emoji}\n✅ Забрано {amount:,} ₽\n{target_emoji} {target_name}",
        reply_to=message["message_id"],
        parse_mode="HTML"  # <-- ДОБАВИТЬ
    )


def handle_business(data, message):
    user_id = str(message["from"]["id"])
    user = get_user(data, user_id)
    user_emoji = get_profile_decoration_custom(user)
    level = user.get("business_level", 0)

    biz_text = f"{user_emoji} ═══ БИЗНЕС ({level}/30) ═══ {user_emoji}\n\n"

    if level == 0:
        biz_text += "🏪 У вас нет бизнеса!\n\n"
        biz_text += "📋 **Доступные бизнесы:**\n\n"

        # Показываем первые 5 уровней
        for lvl in range(1, 6):
            if lvl in BUSINESS_LEVELS:
                biz = BUSINESS_LEVELS[lvl]
                biz_type = get_business_type(lvl)
                type_emoji = BUSINESS_TYPES.get(biz_type, {}).get('emoji', '📊') if biz_type else '📊'

                biz_text += f"{type_emoji} {biz['name']}\n"
                biz_text += f"💰 Цена: {biz['buy_price']:,} ₽\n"
                biz_text += f"📈 Доход: {biz['income']:,} ₽/час\n"
                biz_text += f"👥 Сотрудники: {biz.get('employees', 0)}\n"
                biz_text += f"💸 Расходы: {biz.get('upkeep', 0):,} ₽/час\n"
                biz_text += "━━━━━━━━━━━━━━━\n"

        biz_text += "\n💡 **Купить:** купить бизнес"
        biz_text += "\n📋 **Весь список:** /бизнес_список"
    else:
        biz = BUSINESS_LEVELS[level]
        biz_type = get_business_type(level)

        biz_text += f"🏢 **Ваш бизнес:** {biz['name']}\n"
        biz_text += f"📊 **Уровень:** {level}/30\n"

        if biz_type:
            type_info = BUSINESS_TYPES[biz_type]
            biz_text += f"📌 **Тип:** {type_info['name']} {type_info['bonus']}\n"

        biz_text += f"📝 **Описание:** {biz['description']}\n\n"

        biz_text += f"💰 **Доход:** {biz['income']:,} ₽/час\n"
        biz_text += f"👥 **Сотрудники:** {biz.get('employees', 0)}\n"
        biz_text += f"💸 **Расходы:** {biz.get('upkeep', 0):,} ₽/час\n"
        biz_text += f"📦 **Макс. товаров:** {biz['max_items']}\n\n"

        if level < 30:
            next_lvl = level + 1
            if next_lvl in BUSINESS_LEVELS:
                next_biz = BUSINESS_LEVELS[next_lvl]
                next_type = get_business_type(next_lvl)
                type_emoji = BUSINESS_TYPES.get(next_type, {}).get('emoji', '📊') if next_type else '📊'

                biz_text += f"⬆️ **Следующий уровень:**\n"
                biz_text += f"{type_emoji} {next_biz['name']}\n"
                biz_text += f"💵 Цена улучшения: {next_biz['upgrade_price']:,} ₽\n"
                biz_text += f"📈 Новый доход: {next_biz['income']:,} ₽/час\n"
                biz_text += f"💡 Улучшить: улучшить бизнес\n"
            else:
                biz_text += "👑 **Максимальный уровень!**\n"
        else:
            biz_text += "👑 **Максимальный уровень!**\n"

        biz_text += "\n💡 **Команды:**\n"
        biz_text += "💰 Собрать доход: доход\n"
        biz_text += "📋 Весь список бизнесов: /бизнес_список\n"
        biz_text += "📊 Информация о бизнесе: /бизнес_инфо [номер]"

    send_message(message["chat"]["id"], biz_text, reply_to=message["message_id"], parse_mode="Markdown")

def handle_business_list(data, message):
    """Показать список всех бизнесов по категориям"""
    user_id = str(message["from"]["id"])
    user = get_user(data, user_id)
    user_emoji = get_user_emoji(user)

    list_text = f"{user_emoji} ═══ КАТАЛОГ БИЗНЕСОВ (1-30) ═══ {user_emoji}\n\n"

    # Группируем бизнесы по типам
    business_by_type = {}
    for biz_type, info in BUSINESS_TYPES.items():
        business_by_type[biz_type] = []

    # Добавляем все бизнесы в соответствующие типы
    for lvl in range(1, 31):
        if lvl in BUSINESS_LEVELS:
            biz = BUSINESS_LEVELS[lvl]
            biz_type = get_business_type(lvl)
            if biz_type in business_by_type:
                business_by_type[biz_type].append((lvl, biz))

    # Выводим по типам
    for biz_type, info in BUSINESS_TYPES.items():
        businesses = business_by_type.get(biz_type, [])
        if businesses:
            list_text += f"\n{info['emoji']} **{info['name']}** {info['bonus']}:\n"

            for lvl, biz in businesses[:5]:  # Показываем первые 5 каждого типа
                list_text += f"{lvl}. {biz['name']} - {biz['buy_price']:,} ₽\n"
                list_text += f"   📈 {biz['income']:,} ₽/час | 👥 {biz.get('employees', 0)}\n"

            if len(businesses) > 5:
                list_text += f"   ... и ещё {len(businesses)-5} бизнесов\n"

    list_text += "\n\n💡 **Как купить:**\n"
    list_text += "Для покупки бизнеса 1 уровня: купить бизнес\n"
    list_text += "Для просмотра конкретного бизнеса: /бизнес_инфо [номер]\n"
    list_text += "Пример: /бизнес_инфо 15"

    keyboard = {
        "inline_keyboard": [
            [
                {"text": "🏪 Малый бизнес (1-5)", "callback_data": "business_category_small"},
                {"text": "🏢 Средний бизнес (6-10)", "callback_data": "business_category_medium"}
            ],
            [
                {"text": "🏭 Крупный бизнес (11-15)", "callback_data": "business_category_large"},
                {"text": "👑 Корпорации (16-20)", "callback_data": "business_category_corporate"}
            ],
            [
                {"text": "🌍 Мегакорпорации (21-30)", "callback_data": "business_category_mega"},
                {"text": "💰 Мой бизнес", "callback_data": "business"}
            ]
        ]
    }

    send_message(message["chat"]["id"], list_text,
                 reply_to=message["message_id"], parse_mode="Markdown", reply_markup=keyboard)

def handle_business_info_detail(data, message, args):
    """Подробная информация о конкретном бизнесе по номеру"""
    user_id = str(message["from"]["id"])
    user = get_user(data, user_id)

    if not args:
        send_message(message["chat"]["id"],
                     "❌ Укажите номер бизнеса!\nПример: /бизнес_инфо 15",
                     reply_to=message["message_id"])
        return

    try:
        level = int(args[0])
    except:
        send_message(message["chat"]["id"],
                     "❌ Укажите число от 1 до 30!",
                     reply_to=message["message_id"])
        return

    if level < 1 or level > 30:
        send_message(message["chat"]["id"],
                     "❌ Уровень должен быть от 1 до 30!",
                     reply_to=message["message_id"])
        return

    if level not in BUSINESS_LEVELS:
        send_message(message["chat"]["id"],
                     "❌ Такого бизнеса не существует!",
                     reply_to=message["message_id"])
        return

    biz = BUSINESS_LEVELS[level]
    biz_type = get_business_type(level)
    current_level = user.get("business_level", 0)

    info_text = f"📊 **ИНФОРМАЦИЯ О БИЗНЕСЕ**\n\n"
    info_text += f"🏢 **{biz['name']}** (Уровень {level})\n\n"

    if biz_type:
        type_info = BUSINESS_TYPES[biz_type]
        info_text += f"📌 **Тип:** {type_info['name']}\n"
        info_text += f"✨ **Бонус:** {type_info['bonus']}\n\n"

    info_text += f"📝 **Описание:** {biz['description']}\n\n"

    info_text += f"💰 **Стоимость покупки:** {biz['buy_price']:,} ₽\n"
    info_text += f"📈 **Базовый доход:** {biz['income']:,} ₽/час\n"
    info_text += f"👥 **Количество сотрудников:** {biz.get('employees', 0)}\n"
    info_text += f"💸 **Расходы на содержание:** {biz.get('upkeep', 0):,} ₽/час\n"
    info_text += f"📦 **Макс. товаров на маркете:** {biz['max_items']}\n\n"

    if current_level >= level:
        info_text += "✅ **Этот бизнес у вас уже есть!**\n"
    elif current_level == level - 1:
        info_text += f"⬆️ **Можно улучшить текущий бизнес до этого уровня!**\n"
        info_text += f"💵 Цена улучшения: {biz['upgrade_price']:,} ₽\n"
    else:
        needed_level = level - 1
        info_text += f"❌ **Необходимо иметь бизнес уровня {needed_level}**\n"
        info_text += f"💡 Сначала купите или улучшите бизнес до уровня {needed_level}\n"

    # Расчет примерного времени окупаемости
    net_income = biz['income'] - biz.get('upkeep', 0)
    if net_income > 0:
        hours_to_roi = biz['buy_price'] / net_income
        days_to_roi = hours_to_roi / 24

        info_text += f"\n📊 **Анализ окупаемости:**\n"
        info_text += f"• Чистый доход: {net_income:,} ₽/час\n"
        info_text += f"• Окупаемость: {int(days_to_roi)} дней\n"
        info_text += f"• Ежедневная прибыль: {net_income * 24:,} ₽/день\n"

    keyboard = None
    if current_level == level - 1:
        keyboard = {
            "inline_keyboard": [[
                {"text": f"🔼 Улучшить за {biz['upgrade_price']:,} ₽",
                 "callback_data": f"upgrade_to_{level}"}
            ]]
        }

    send_message(message["chat"]["id"], info_text,
                 reply_to=message["message_id"], parse_mode="Markdown", reply_markup=keyboard)

def handle_business_category_callback(data, callback_query, category):
    """Показать бизнесы конкретной категории"""
    chat_id = callback_query["message"]["chat"]["id"]
    message_id = callback_query["message"]["message_id"]
    user_id = str(callback_query["from"]["id"])

    category_ranges = {
        'small': (1, 5, '🏪 Малый бизнес'),
        'medium': (6, 10, '🏢 Средний бизнес'),
        'large': (11, 15, '🏭 Крупный бизнес'),
        'corporate': (16, 20, '👑 Корпорации'),
        'mega': (21, 30, '🌍 Мегакорпорации')
    }

    if category not in category_ranges:
        answer_callback_query(callback_query["id"], "❌ Категория не найдена!")
        return

    start, end, category_name = category_ranges[category]

    answer_callback_query(callback_query["id"], f"Загружаем {category_name}...")

    category_text = f"📊 **{category_name}** (Уровни {start}-{end})\n\n"

    for level in range(start, end + 1):
        if level in BUSINESS_LEVELS:
            biz = BUSINESS_LEVELS[level]
            biz_type = get_business_type(level)
            type_emoji = BUSINESS_TYPES.get(biz_type, {}).get('emoji', '📊') if biz_type else '📊'

            category_text += f"{type_emoji} **Уровень {level}: {biz['name']}**\n"
            category_text += f"💰 Цена: {biz['buy_price']:,} ₽\n"
            category_text += f"📈 Доход: {biz['income']:,} ₽/час\n"
            category_text += f"💸 Расходы: {biz.get('upkeep', 0):,} ₽/час\n"
            category_text += f"👥 Сотрудники: {biz.get('employees', 0)}\n"
            category_text += f"🆔 /бизнес_инфо {level}\n"
            category_text += "━━━━━━━━━━━━━━━\n"

    category_text += "\n💡 Нажмите на номер бизнеса для подробной информации!"

    keyboard = {
        "inline_keyboard": [
            [
                {"text": "🏪 Маленький", "callback_data": "business_category_small"},
                {"text": "🏢 Средний", "callback_data": "business_category_medium"}
            ],
            [
                {"text": "🏭 Крупный", "callback_data": "business_category_large"},
                {"text": "👑 Корпорации", "callback_data": "business_category_corporate"}
            ],
            [
                {"text": "🌍 Мега", "callback_data": "business_category_mega"},
                {"text": "📋 Весь список", "callback_data": "business_list"}
            ],
            [
                {"text": "🔙 Назад", "callback_data": "business"}
            ]
        ]
    }

    edit_message(chat_id, message_id, category_text,
                 parse_mode="Markdown", reply_markup=keyboard)

def handle_buy_business(data, message):
    user_id = str(message["from"]["id"])
    user = get_user(data, user_id)

    if user.get("business_level", 0) > 0:
        send_message(message["chat"]["id"],
                     "❌ У вас уже есть бизнес! Используйте: улучшить бизнес",
                     reply_to=message["message_id"])
        return

    price = BUSINESS_LEVELS[1]['buy_price']
    if user["balance"] < price:
        send_message(message["chat"]["id"],
                     f"❌ Недостаточно средств! Нужно: {price:,} ₽",
                     reply_to=message["message_id"])
        return

    user["balance"] -= price
    user["business_level"] = 1
    user["last_income"] = datetime.now().isoformat()
    save_data(data)

    user_emoji = get_profile_decoration_custom(user)  # <-- ИЗМЕНИТЬ
    biz = BUSINESS_LEVELS[1]

    send_message(
        message["chat"]["id"],
        f"{user_emoji} ✅ Вы купили {biz['name']}!\n💰 Доход: {biz['income']} ₽/час\n📦 Макс. товаров: {biz['max_items']}",
        reply_to=message["message_id"],
        parse_mode="HTML"  # <-- ДОБАВИТЬ
    )

    # Проверяем достижения
    check_and_award_achievements(data, user_id, message)


def handle_upgrade_business(data, message):
    user_id = str(message["from"]["id"])
    user = get_user(data, user_id)
    level = user.get("business_level", 0)

    if level == 0:
        send_message(message["chat"]["id"],
                     "❌ У вас нет бизнеса! Используйте: купить бизнес",
                     reply_to=message["message_id"])
        return

    if level >= 30:
        send_message(message["chat"]["id"],
                     "👑 Ваш бизнес уже максимального уровня!",
                     reply_to=message["message_id"])
        return

    next_level = level + 1
    if next_level not in BUSINESS_LEVELS:
        send_message(message["chat"]["id"],
                     "❌ Следующий уровень недоступен!",
                     reply_to=message["message_id"])
        return

    price = BUSINESS_LEVELS[next_level]['upgrade_price']

    if user["balance"] < price:
        send_message(message["chat"]["id"],
                     f"❌ Недостаточно средств! Нужно: {price:,} ₽",
                     reply_to=message["message_id"])
        return

    user["balance"] -= price
    user["business_level"] = next_level

    # ===== ДОБАВЛЕНО: Прогресс ивента =====
    check_event_progress(user, "business_level_up", 1)

    # Обновляем достижения
    check_and_award_achievements(data, user_id, message)

    save_data(data)

    user_emoji = get_profile_decoration_custom(user)
    biz = BUSINESS_LEVELS[next_level]
    biz_type = get_business_type(next_level)
    type_emoji = BUSINESS_TYPES.get(biz_type, {}).get('emoji', '📊') if biz_type else '📊'

    response = f"""
{user_emoji} ⬆️ **БИЗНЕС УЛУЧШЕН!** {user_emoji}

{type_emoji} **Новый бизнес:** {biz['name']}
📊 **Уровень:** {next_level}/30
📈 **Доход:** {biz['income']:,} ₽/час
👥 **Сотрудники:** {biz.get('employees', 0)}
📦 **Макс. товаров:** {biz['max_items']}
💸 **Расходы:** {biz.get('upkeep', 0):,} ₽/час
"""

    if biz_type:
        type_info = BUSINESS_TYPES[biz_type]
        response += f"✨ **Бонус типа:** {type_info['bonus']}\n"

    response += f"\n💰 **Списано:** {price:,} ₽"
    response += f"\n💵 **Остаток:** {user['balance']:,} ₽"

    send_message(message["chat"]["id"], response,
                 reply_to=message["message_id"], parse_mode="Markdown")


def handle_admin_biz(data, message, args):
    if not is_admin(message["from"]["id"]):
        send_message(message["chat"]["id"],
                     "❌ Только для админов!",
                     reply_to=message["message_id"])
        return

    if "reply_to_message" not in message:
        send_message(
            message["chat"]["id"],
            "❌ Ответьте на сообщение пользователя!\nИспользование: /biz [0-30]",
            reply_to=message["message_id"])
        return

    if not args:
        send_message(message["chat"]["id"],
                     "❌ Укажите уровень бизнеса (0-30)!\nПример: /biz 5",
                     reply_to=message["message_id"])
        return

    try:
        level = int(args[0])
    except:
        send_message(message["chat"]["id"],
                     "❌ Укажите число от 0 до 30!",
                     reply_to=message["message_id"])
        return

    if level < 0 or level > 30:
        send_message(message["chat"]["id"],
                     "❌ Уровень должен быть от 0 до 30!",
                     reply_to=message["message_id"])
        return

    target_user = message["reply_to_message"]["from"]
    target_id = str(target_user["id"])
    update_user_info(data, target_id, target_user.get("username"),
                     target_user.get("first_name"))

    target = get_user(data, target_id)
    old_level = target.get("business_level", 0)

    # Исправление: проверяем достижения для уровня бизнеса
    target["business_level"] = level
    if level > 0 and not target.get("last_income"):
        target["last_income"] = datetime.now().isoformat()

    # Обновляем достижения для бизнеса
    if level >= 1 and old_level < 1:
        # Пользователь получил первый бизнес
        award_achievement(data, target_id, "business_owner", message)

    if level >= 25 and old_level < 25:
        # Пользователь достиг высокого уровня бизнеса
        award_achievement(data, target_id, "tycoon", message)

    save_data(data)

    target_emoji = get_user_emoji(target)
    target_name = format_user_mention(target, target_id)

    if level > 0 and level in BUSINESS_LEVELS:
        biz = BUSINESS_LEVELS[level]
        send_message(
            message["chat"]["id"],
            f"{target_emoji} ✅ Бизнес {biz['name']} (ур.{level}) выдан {target_name}\n"
            f"💰 Доход: {biz['income']:,} ₽/час\n"
            f"💵 Стоимость: {biz['buy_price']:,} ₽",
            reply_to=message["message_id"])
    elif level == 0:
        send_message(message["chat"]["id"],
                     f"{target_emoji} ❌ Бизнес забран у {target_name}",
                     reply_to=message["message_id"])
    else:
        send_message(message["chat"]["id"],
                     f"{target_emoji} ❌ Уровень {level} не существует!",
                     reply_to=message["message_id"])

def handle_gifts_list(data, message):
    gifts_text = "🎁 ═══ ПОДАРКИ ═══ 🎁\n\n"

    for rarity in ['Легендарный', 'Эпический', 'Редкий']:
        rarity_gifts = []
        for k, v in GIFTS.items():
            if v['rarity'] == rarity:
                # Используем кастомное эмодзи если есть
                if 'custom_emoji' in v:
                    rarity_gifts.append(f"{k}. {v['custom_emoji']} {v['name']}")
                else:
                    rarity_gifts.append(f"{k}. {v['emoji']} {v['name']}")

        if rarity_gifts:
            gifts_text += f"{RARITY_COLORS[rarity]} {rarity}:\n"
            gifts_text += "\n".join(rarity_gifts) + "\n\n"

    gifts_text += f"📊 Всего подарков: {len(GIFTS)}\n"
    gifts_text += "💡 Подарки выдаются только админами\n"
    gifts_text += "💡 Подарки можно передавать и продавать через маркетплейс"

    send_message(message["chat"]["id"],
                 gifts_text,
                 reply_to=message["message_id"],
                 parse_mode="HTML")  # <-- ВАЖНО: Добавить parse_mode="HTML"

def handle_casino(data, message):
    casino_text = f"""
🎰 ═══ КАЗИНО ═══ 🎰

🎲 Доступные игры:

🎰 слоты [ставка] - Слот-машина (x2-x10)
🪙 монетка [ставка] - Орёл или решка (x2)
🎲 кости [ставка] - Кости (x2-x6)
🎡 рулетка [ставка] [красное/чёрное/число] - Рулетка

💡 Минимальная ставка: 10 ₽
💡 Максимальная ставка: 10,000 ₽

📊 Ваши шансы:
• Слоты: {CHANCE_SETTINGS['slots_win_chance']}% на выигрыш
• Монетка: {CHANCE_SETTINGS['coinflip_win_chance']}% на выигрыш (x2)
• Кости: чем больше выпадет - тем больше выигрыш
• Рулетка: цвет x2, число x35

🚀 Бустеры улучшают ваши шансы и выигрыши!
"""
    send_message(message["chat"]["id"],
                 casino_text,
                 reply_to=message["message_id"])


def handle_dice(data, message, args):
    user_id = str(message["from"]["id"])
    user = get_user(data, user_id)

    if not args:
        send_message(message["chat"]["id"],
                     "🎲 Ставку, блять, поставь! Пример: кости 100",
                     reply_to=message["message_id"])
        return

    try:
        bet = int(args[0])
    except:
        send_message(message["chat"]["id"],
                     "❌ Число, ёпта, а не хуйню какую-то!",
                     reply_to=message["message_id"])
        return

    if bet < 10 or bet > 10000:
        send_message(message["chat"]["id"],
                     "❌ От 10 до 10,000 ₽, не еби мозги!",
                     reply_to=message["message_id"])
        return

    if user["balance"] < bet:
        send_message(message["chat"]["id"],
                     f"❌ Без бабла сидишь, чёрт! Баланс: {user['balance']:,} ₽",
                     reply_to=message["message_id"])
        return

    user["balance"] -= bet
    user_stats = user.get("stats", {})
    user_stats["total_bets"] = user_stats.get("total_bets", 0) + 1

    dice1 = random.randint(1, 6)
    dice2 = random.randint(1, 6)
    total = dice1 + dice2

    dice_emoji = {1: "⚀", 2: "⚁", 3: "⚂", 4: "⚃", 5: "⚄", 6: "⚅"}

    user_real_chances = get_user_chances(user_id)

    if total >= user_real_chances['dice_win_threshold']:
        multiplier = total - 8
        winnings = bet * multiplier
        user["balance"] += winnings
        user_stats["casino_wins"] = user_stats.get("casino_wins", 0) + winnings

        win_phrases = [
            f"🎉 Ахуеть! Сумма {total}! Забирай {winnings:,} ₽ (x{multiplier})!",
            f"🎉 Бля, красава! {winnings:,} ₽ в карман!",
            f"🎉 Ебаный в рот! {winnings:,} ₽ сорвал!",
            f"🎉 Насосал! {winnings:,} ₽ твои!"
        ]
        result = random.choice(win_phrases)
        
        # ===== ДОБАВЛЕНО: Прогресс ивента =====
        check_event_progress(user, "casino_win", winnings)
        
    elif total == 12:
        winnings = bet * 6
        user["balance"] += winnings
        user_stats["casino_wins"] = user_stats.get("casino_wins", 0) + winnings
        result = f"🎉 БЛЯЯЯ! МАКСИМУМ! Ты выиграл {winnings:,} ₽ (x6)!"
        
        # ===== ДОБАВЛЕНО: Прогресс ивента =====
        check_event_progress(user, "casino_win", winnings)
    else:
        lose_phrases = [
            f"😔 Сумма {total}. Проебано {bet:,} ₽, бывает",
            f"😔 {total} выпало. Хуёво, {bet:,} ₽ нахуй",
            f"😔 Всего {total}. {bet:,} ₽ коту под хвост",
            f"😔 Мало - {total}. {bet:,} ₽ в помойке"
        ]
        result = random.choice(lose_phrases)

    # ===== ДОБАВЛЕНО: Прогресс ивента (ставка) =====
    check_event_progress(user, "casino_bet", 1)

    save_data(data)

    user_emoji = get_user_emoji(user)

    text = f"""
{user_emoji} ═══ КОСТИ ═══ {user_emoji}

  {dice_emoji[dice1]} + {dice_emoji[dice2]} = {total}

{result}

{user_emoji} Твой баланс: {user['balance']:,} ₽
"""
    send_message(message["chat"]["id"], text, reply_to=message["message_id"])
    check_and_award_achievements(data, user_id, message)


def handle_roulette(data, message, args):
    """Упрощенная рулетка с множителями и анимацией"""
    user_id = str(message["from"]["id"])
    user = get_user(data, user_id)

    if not args or len(args) < 2:
        send_message(message["chat"]["id"],
                     "🎡 Использование: рулетка [ставка] [множитель]\n\n"
                     "Доступные множители: x2, x3, x5, x10\n"
                     "Пример: рулетка 1000 x5",
                     reply_to=message["message_id"])
        return

    try:
        bet = int(args[0])
    except:
        send_message(message["chat"]["id"],
                     "❌ Ставка должна быть числом!",
                     reply_to=message["message_id"])
        return

    if bet < 10 or bet > 10000:
        send_message(message["chat"]["id"],
                     "❌ Ставка от 10 до 10,000 ₽",
                     reply_to=message["message_id"])
        return

    if user["balance"] < bet:
        send_message(message["chat"]["id"],
                     f"❌ Недостаточно средств! Баланс: {user['balance']:,} ₽",
                     reply_to=message["message_id"])
        return

    multiplier_text = args[1].lower()

    # Проверяем множитель
    multipliers = {
        "x2": 2,
        "x3": 3,
        "x5": 5,
        "x10": 10,
        "2": 2,
        "3": 3,
        "5": 5,
        "10": 10
    }

    if multiplier_text not in multipliers:
        send_message(message["chat"]["id"],
                     "❌ Неверный множитель! Доступно: x2, x3, x5, x10",
                     reply_to=message["message_id"])
        return

    target_multiplier = multipliers[multiplier_text]

    user["balance"] -= bet
    user_stats = user.get("stats", {})
    user_stats["total_bets"] = user_stats.get("total_bets", 0) + 1
    save_data(data)

    user_emoji = get_user_emoji(user)

    # Начинаем анимацию
    animation_message = send_message(
        message["chat"]["id"],
        f"{user_emoji} 🎡 Рулетка крутится...\n\n"
        f"💰 Ставка: {bet:,} ₽\n"
        f"🎯 Цель: x{target_multiplier}\n\n"
        f"🌀🌀🌀",
        reply_to=message["message_id"]
    )

    # Если не удалось отправить сообщение, продолжаем без анимации
    if not animation_message or not animation_message.get("ok"):
        animation_message_id = None
        chat_id = message["chat"]["id"]
    else:
        animation_message_id = animation_message["result"]["message_id"]
        chat_id = animation_message["result"]["chat"]["id"]

    # Шансы выпадения множителей (в сумме 100%)
    # x2: 40%, x3: 30%, x5: 20%, x10: 10%
    chance_weights = {
        2: 40,  # 40% шанс
        3: 30,  # 30% шанс
        5: 20,  # 20% шанс
        10: 10  # 10% шанс
    }

    # Создаем список для случайного выбора с весами
    weighted_multipliers = []
    for mult, weight in chance_weights.items():
        weighted_multipliers.extend([mult] * weight)

    # Анимация кручения (3 секунды)
    symbols = ["⬜️", "🟥", "🟦", "🟩", "🟨", "🟪", "🟫", "⬛️", "🎰", "🎲", "💰", "💎"]
    for i in range(15):
        time.sleep(0.2)  # 15 итераций × 0.2 сек = 3 секунды

        # Создаем анимационный текст
        if i < 12:  # Первые 12 итераций - кручение
            animation_text = f"{user_emoji} 🎡 Рулетка крутится...\n\n"
            animation_text += f"💰 Ставка: {bet:,} ₽\n"
            animation_text += f"🎯 Цель: x{target_multiplier}\n\n"

            # Добавляем анимационные символы
            anim_chars = ""
            for j in range(10):
                symbol = symbols[(i + j) % len(symbols)]
                anim_chars += symbol
            animation_text += f"🌀{anim_chars}🌀"

        else:  # Последние 3 итерации - замедление
            animation_text = f"{user_emoji} 🎡 Рулетка замедляется...\n\n"
            animation_text += f"💰 Ставка: {bet:,} ₽\n"
            animation_text += f"🎯 Цель: x{target_multiplier}\n\n"

            slow_symbols = ["⚫️", "⚪️", "🔴", "🔵", "🟢", "🟡"]
            anim_chars = ""
            for j in range(5):
                symbol = slow_symbols[(i + j) % len(slow_symbols)]
                anim_chars += symbol
            animation_text += f"🎯{anim_chars}🎯"

        # Обновляем сообщение с анимацией
        if animation_message_id:
            try:
                edit_message(chat_id, animation_message_id, animation_text)
            except:
                pass

    # Определяем результат
    result_multiplier = random.choice(weighted_multipliers)

    # Эмодзи для множителей
    multiplier_emojis = {
        2: "🟢",
        3: "🔵",
        5: "🟣",
        10: "🟡"
    }

    result_emoji = multiplier_emojis.get(result_multiplier, "⚪️")

    # Проверяем выигрыш
    if result_multiplier == target_multiplier:
        win = True
        winnings = bet * result_multiplier
        user["balance"] += winnings
        user_stats["casino_wins"] = user_stats.get("casino_wins", 0) + winnings

        win_phrases = [
            f"🎉 АХУЕТЬ! ВЫИГРАЛ x{result_multiplier}!",
            f"🎉 БЛЯЯЯ! СОРВАЛ x{result_multiplier}!",
            f"🎉 НАСОСАЛ! x{result_multiplier} В КАРМАН!",
            f"🎉 УГАДАЛ! x{result_multiplier} КРАСАВА!"
        ]
        result_text = f"{random.choice(win_phrases)}\n💰 +{winnings:,} ₽"
        
        # ===== ДОБАВЛЕНО: Прогресс ивента =====
        check_event_progress(user, "casino_win", winnings)
    else:
        win = False
        lose_phrases = [
            f"😔 Не повезло... Выпало x{result_multiplier}",
            f"😔 Проебал... Был x{result_multiplier}",
            f"😔 Мимо... На рулетке x{result_multiplier}",
            f"😔 Не угадал... Выигрыш x{result_multiplier}"
        ]
        result_text = f"{random.choice(lose_phrases)}\n💸 -{bet:,} ₽"

    # ===== ДОБАВЛЕНО: Прогресс ивента (ставка) =====
    check_event_progress(user, "casino_bet", 1)

    save_data(data)

    # Финальное сообщение
    final_text = f"""
{user_emoji} ═══ РУЛЕТКА ═══ {user_emoji}

{result_emoji} **Выпало: x{result_multiplier}**
🎯 **Вы ставили на: x{target_multiplier}**

{result_text}

📊 **Статистика:**
• x2: 40% шанс
• x3: 30% шанс
• x5: 20% шанс
• x10: 10% шанс

{user_emoji} **Баланс:** {user['balance']:,} ₽
"""

    # Если была анимация, заменяем её
    if animation_message_id:
        try:
            edit_message(chat_id, animation_message_id, final_text, parse_mode="Markdown")
        except:
            # Если не удалось отредактировать, отправляем новое сообщение
            send_message(message["chat"]["id"], final_text,
                        parse_mode="Markdown", reply_to=message["message_id"])
    else:
        send_message(message["chat"]["id"], final_text,
                    parse_mode="Markdown", reply_to=message["message_id"])

    check_and_award_achievements(data, user_id, message)

def handle_transfer_money(data, message, args):
    if "reply_to_message" not in message:
        send_message(
            message["chat"]["id"],
            "❌ Ответь на сообщение, кому даёшь бабло, долбоёб!",
            reply_to=message["message_id"])
        return

    user_id = str(message["from"]["id"])
    user = get_user(data, user_id)

    if not args:
        send_message(message["chat"]["id"],
                     "❌ Бля, сумму укажи! Пример: дать 100",
                     reply_to=message["message_id"])
        return

    try:
        amount = int(args[0])
    except:
        send_message(message["chat"]["id"],
                     "❌ Число, а не хуйня какая-то!",
                     reply_to=message["message_id"])
        return

    if amount <= 0:
        send_message(message["chat"]["id"],
                     "❌ Положительную сумму, ебанашка!",
                     reply_to=message["message_id"])
        return

    if user["balance"] < amount:
        send_message(
            message["chat"]["id"],
            f"❌ Нихуя себе щедрый! Баланс: {user['balance']:,} ₽",
            reply_to=message["message_id"])
        return

    target_user = message["reply_to_message"]["from"]
    target_id = str(target_user["id"])

    if target_id == user_id:
        send_message(message["chat"]["id"],
                     "❌ Самому себе? Ты ебанутый?",
                     reply_to=message["message_id"])
        return

    update_user_info(data, target_id, target_user.get("username"),
                     target_user.get("first_name"))
    target = get_user(data, target_id)

    user["balance"] -= amount
    target["balance"] += amount
    data["stats"]["total_transactions"] += 1

    user_stats = user.get("stats", {})
    user_stats["money_given"] = user_stats.get("money_given", 0) + amount

    # ===== ДОБАВЛЕНО: Прогресс ивента =====
    check_event_progress(user, "money_transfer", 1)

    save_data(data)

    sender_emoji = get_profile_decoration_custom(user)
    receiver_emoji = get_profile_decoration_custom(target)
    sender_name = format_user_mention(user, user_id)
    target_name = format_user_mention(target, target_id)

    transfer_phrases = [
        f"{sender_emoji} ➜ {receiver_emoji}\n💸 Отжарил: {amount:,} ₽\n\n{sender_emoji} {sender_name}\n    ⬇️\n{receiver_emoji} {target_name}",
        f"{sender_emoji} ➜ {receiver_emoji}\n💸 Кинул бабла: {amount:,} ₽\n\n{sender_name} → {target_name}",
        f"{sender_emoji} ➜ {receiver_emoji}\n💸 Заслал деньжат: {amount:,} ₽"
    ]

    send_message(message["chat"]["id"],
                 random.choice(transfer_phrases),
                 reply_to=message["message_id"],
                 parse_mode="HTML")
    check_and_award_achievements(data, user_id, message)

def handle_announcement(data, message):
    user_id = str(message["from"]["id"])
    user = get_user(data, user_id)
    user_emoji = get_user_emoji(user)

    text = message["text"]
    parts = text.split(maxsplit=1)

    if len(parts) < 2:
        send_message(message["chat"]["id"],
                     f"""
{user_emoji} ═══ ОБЪЯВЛЕНИЯ ═══ {user_emoji}

📢 Разместите своё объявление в канале!

💰 Стоимость: 10,000 ₽

📝 Использование:
объявление [ваш текст]

Пример:
объявление Продаю редкие подарки! Пишите в ЛС
""",
                     reply_to=message["message_id"])
        return

    announcement_text = parts[1]
    cost = 10000

    if user["balance"] < cost:
        send_message(message["chat"]["id"],
                     f"""
{user_emoji} ❌ Недостаточно средств!

💰 Ваш баланс: {user['balance']:,} ₽
💵 Нужно: {cost:,} ₽
📉 Не хватает: {cost - user['balance']:,} ₽
""",
                     reply_to=message["message_id"])
        return

    user["balance"] -= cost
    if "treasury" not in data:
        data["treasury"] = 0
    data["treasury"] += cost

    # Обновляем статистику пожертвований
    user_stats = user.get("stats", {})
    user_stats["donated_to_treasury"] = user_stats.get("donated_to_treasury", 0) + cost

    save_data(data)

    username = user.get("username")
    first_name = user.get("first_name", "Пользователь")
    if username:
        author = f"@{username}"
    else:
        author = first_name

    channel_message = f"""
📢 ═══ ОБЪЯВЛЕНИЕ ═══ 📢

{announcement_text}

━━━━━━━━━━━━━━━
👤 Автор: {author}
📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}
"""

    result = send_message(STATS_CHANNEL_ID, channel_message)

    if result and result.get("ok"):
        send_message(message["chat"]["id"],
                     f"""
{user_emoji} ✅ Объявление опубликовано!

💸 Списано: {cost:,} ₽
💰 Ваш баланс: {user['balance']:,} ₽
""",
                     reply_to=message["message_id"])
    else:
        user["balance"] += cost
        data["treasury"] -= cost
        user_stats["donated_to_treasury"] = user_stats.get("donated_to_treasury", 0) - cost
        save_data(data)
        send_message(
            message["chat"]["id"],
            f"{user_emoji} ❌ Ошибка при публикации объявления. Деньги возвращены.",
            reply_to=message["message_id"])


def handle_treasury(data, message):
    user_emoji = get_user_emoji(get_user(data, str(message["from"]["id"])))

    if "treasury" not in data:
        data["treasury"] = 50000
        save_data(data)

    send_message(message["chat"]["id"],
                 f"""
{user_emoji} ═══ КАЗНА ═══ {user_emoji}

🏦 В казне: {data['treasury']:,} ₽

💡 Попробуйте ограбить: ограбить казну
""",
                 reply_to=message["message_id"])


def handle_help(data, message):
    help_text = f"""
📚 ═══ КОМАНДЫ ═══ 📚

👤 Основные команды:
• /start - главное меню
• профиль - ваш профиль
• баланс - ваш баланс
• бонус - ежедневный бонус (раз в 24ч)

💰 Переводы:
• дать [сумма] - передать деньги (в ответ)

💳 Пополнение:
• пополнить - инструкция по пополнению
• ввести код [код] - ввести промокод

🛍️ Маркетплейс:
• Доступен в ЛС через /start

🎰 Казино:
• казино - список игр
• слоты/монетка/кости/рулетка [ставка]

🏢 Бизнес:
• бизнес - информация о бизнесе
• купить бизнес - купить бизнес
• улучшить бизнес - повысить уровень
• доход - собрать доход

🎁 Подарки:
• подарки - список всех подарков
• подарки можно продавать на маркетплейсе

🚀 Бустеры:
• бустеры - магазин бустеров
• купить бустер [ID] - купить бустер
• мои бустеры - активные бустеры

🛠️ Улучшения:
• улучшения - магазин улучшений
• купить улучшение [ID] - купить улучшение

🏆 Достижения:
• достижения - ваши достижения

🔇 Система мута/размута:
• мут [минуты] - замутить пользователя (в ответ) - {MUTE_PRICE_PER_MINUTE}₽/мин
• размут - размутить пользователя (в ответ) - 500₽ (админы бесплатно)
• размутсебя - размутить себя в ЛС - 1,000₽
• инфо_мут - информация о системе мута
• статус_мута - проверить статус пользователя (в ответ)

🏦 Казна:
• казна - посмотреть казну
• ограбить казна - попытаться ограбить (раз в час)

📢 Объявления:
• объявление [текст] - опубликовать объявление (10,000 ₽)

👑 Для админов:
• /admin - админ-панель
• /biz [0-30] - выдать/забрать бизнес
• шансы - показать текущие настройки шансов
• шанс [тип] [число]% - установить шанс
• создать код [сумма] - создать промокод для пополнения
"""
    send_message(message["chat"]["id"],
                 help_text,
                 reply_to=message["message_id"])

# ===== ПРОМОКОДЫ И ПОПОЛНЕНИЕ =====

def generate_promo_code():
    """Генерирует 8-значный промокод"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(8))


def handle_create_promo_code(data, message, args):
    """Создание промокода для пополнения баланса"""
    if not is_admin(message["from"]["id"]):
        send_message(message["chat"]["id"],
                     "❌ Только для админов!",
                     reply_to=message["message_id"])
        return

    if not args:
        send_message(message["chat"]["id"],
                     "❌ Укажите параметры!\n\n"
                     "Примеры:\n"
                     "• создать код 500 - обычный промокод (1 активация)\n"
                     "• создать код 500 10 - мульти промокод (500₽, 10 активаций)",
                     reply_to=message["message_id"])
        return

    try:
        amount = int(args[0])
    except:
        send_message(message["chat"]["id"],
                     "❌ Укажите сумму! Пример: создать код 1000",
                     reply_to=message["message_id"])
        return

    if amount <= 0:
        send_message(message["chat"]["id"],
                     "❌ Сумма должна быть положительной!",
                     reply_to=message["message_id"])
        return

    promo_codes = load_promo_codes()

    # Генерируем уникальный код
    code = generate_promo_code()
    while code in promo_codes:
        code = generate_promo_code()

    # Определяем тип промокода
    if len(args) > 1:
        try:
            max_activations = int(args[1])
            promo_type = "multi"
        except:
            send_message(message["chat"]["id"],
                        "❌ Количество активаций должно быть числом!",
                        reply_to=message["message_id"])
            return
    else:
        promo_type = "single"
        max_activations = 1

    # Создаем промокод
    promo_codes[code] = {
        "amount": amount,
        "type": promo_type,
        "created_by": message["from"]["id"],
        "created_at": datetime.now().isoformat(),
        "max_activations": max_activations,
        "activations_left": max_activations,
        "used_by": [],  # список ID пользователей, активировавших код
        "activations": 0  # количество активаций
    }

    save_promo_codes(promo_codes)

    if promo_type == "single":
        send_message(message["chat"]["id"],
                    f"✅ Обычный промокод создан!\n\n💳 Код: `{code}`\n💰 Сумма: {amount:,} ₽\n🎯 Тип: Обычный (1 активация)",
                    reply_to=message["message_id"],
                    parse_mode="Markdown")
    else:
        send_message(message["chat"]["id"],
                    f"✅ Мульти промокод создан!\n\n💳 Код: `{code}`\n💰 Сумма: {amount:,} ₽\n🎯 Тип: Мульти ({max_activations} активаций)\n👤 1 пользователь = 1 активация",
                    reply_to=message["message_id"],
                    parse_mode="Markdown")

def handle_list_promo_codes(data, message):
    """Показать все промокоды"""
    if not is_admin(message["from"]["id"]):
        send_message(message["chat"]["id"],
                     "❌ Только для админов!",
                     reply_to=message["message_id"])
        return

    promo_codes = load_promo_codes()

    if not promo_codes:
        send_message(message["chat"]["id"],
                     "📭 Промокодов пока нет!",
                     reply_to=message["message_id"])
        return

    active_codes = []
    used_codes = []

    for code, details in promo_codes.items():
        if details["type"] == "multi":
            if details["activations_left"] > 0:
                status = f"Мульти ({details['activations_left']}/{details['max_activations']})"
                active_codes.append(f"• `{code}` - {details['amount']:,} ₽ ({status})")
            else:
                status = f"Мульти (исчерпан)"
                used_codes.append(f"• `{code}` - {details['amount']:,} ₽ ({status})")
        else:
            if not details.get("used", False):
                active_codes.append(f"• `{code}` - {details['amount']:,} ₽ (Обычный)")
            else:
                used_codes.append(f"• `{code}` - {details['amount']:,} ₽ (Использован)")

    text = "📋 ═══ ПРОМОКОДЫ ═══ 📋\n\n"

    if active_codes:
        text += "✅ АКТИВНЫЕ:\n" + "\n".join(active_codes) + "\n\n"

    if used_codes:
        text += "💰 ИСПОЛЬЗОВАННЫЕ:\n" + "\n".join(used_codes)

    send_message(message["chat"]["id"],
                 text,
                 reply_to=message["message_id"],
                 parse_mode="Markdown")

def handle_use_promo_code(data, message, args):
    """Использовать промокод"""
    user_id = str(message["from"]["id"])
    user = get_user(data, user_id)

    if not args:
        send_message(message["chat"]["id"],
                     "❌ Укажите промокод! Пример: ввести код ABC12345",
                     reply_to=message["message_id"])
        return

    code = args[0].upper()
    promo_codes = load_promo_codes()

    if code not in promo_codes:
        send_message(message["chat"]["id"],
                     "❌ Промокод не найден!",
                     reply_to=message["message_id"])
        return

    promo = promo_codes[code]

    # Проверка для мульти промокода
    if promo["type"] == "multi":
        # Проверяем лимит активаций
        if promo["activations_left"] <= 0:
            send_message(message["chat"]["id"],
                        "❌ Лимит активаций этого промокода исчерпан!",
                        reply_to=message["message_id"])
            return

        # Проверяем, активировал ли уже пользователь этот код
        if user_id in promo.get("used_by", []):
            send_message(message["chat"]["id"],
                        "❌ Вы уже активировали этот промокод!",
                        reply_to=message["message_id"])
            return
    else:
        # Для обычного промокода
        if promo.get("used", False):
            send_message(message["chat"]["id"],
                        "❌ Этот промокод уже использован!",
                        reply_to=message["message_id"])
            return

    # Активируем промокод
    amount = promo["amount"]
    user["balance"] += amount
    user["total_deposited"] = user.get("total_deposited", 0) + amount

    if promo["type"] == "multi":
        # Обновляем статистику мульти промокода
        promo["activations_left"] -= 1
        promo["activations"] = promo.get("activations", 0) + 1

        # Добавляем пользователя в список использовавших
        if "used_by" not in promo:
            promo["used_by"] = []
        promo["used_by"].append(user_id)
    else:
        # Помечаем обычный промокод как использованный
        promo["used"] = True
        promo["used_by"] = user_id
        promo["used_at"] = datetime.now().isoformat()

    data["stats"]["promo_codes_used"] = data["stats"].get("promo_codes_used", 0) + 1
    data["stats"]["total_deposited"] = data["stats"].get("total_deposited", 0) + amount

    save_promo_codes(promo_codes)
    save_data(data)

    user_emoji = get_user_emoji(user)

    send_message(message["chat"]["id"],
                 f"""
{user_emoji} ═══ ПОПОЛНЕНИЕ УСПЕШНО ═══ {user_emoji}

✅ Промокод активирован!

💳 Код: {code}
💰 Пополнено: {amount:,} ₽
💵 Новый баланс: {user['balance']:,} ₽

📅 Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}
""",
                 reply_to=message["message_id"])


    # Проверяем достижения
    check_and_award_achievements(data, user_id, message)


def handle_deposit_info(data, message):
    """Информация о пополнении"""
    user_emoji = get_user_emoji(get_user(data, str(message["from"]["id"])))

    info_text = f"""
{user_emoji} ═══ ПОПОЛНЕНИЕ БАЛАНСА ═══ {user_emoji}

💰 Вы можете пополнить баланс с помощью промокодов!

💡 Как это работает:

1. Администратор создает промокод на определенную сумму
2. Вы покупаете промокод у администратора
3. Используете команду: ввести код [КОД]
4. Сумма добавляется на ваш баланс

📋 Ваши депозиты:
💳 Всего пополнено: {get_user(data, str(message["from"]["id"]))['total_deposited']:,} ₽

💬 Для приобретения промокодов обращайтесь к администраторам.
"""
    send_message(message["chat"]["id"],
                 info_text,
                 reply_to=message["message_id"])


# ===== МАРКЕТПЛЕЙС ФУНКЦИИ =====

def generate_item_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10))


def handle_start(data, message):
    user_id = str(message["from"]["id"])
    user = get_user(data, user_id)
    update_user_info(data, user_id, message["from"].get("username"),
                     message["from"].get("first_name"))

    user_emoji = get_user_emoji(user)

    # Проверяем, что это ЛС (chat.type == "private")
    chat_type = message.get("chat", {}).get("type")

    if chat_type != "private":
        # Если это группа, показываем упрощенное сообщение
        send_message(
            message["chat"]["id"],
            f"👋 Привет, {user.get('first_name', 'игрок')}!\n\n"
            f"💰 Ваш баланс: {user['balance']:,} ₽\n\n"
            f"🎮 **Доступные команды в группе:**\n"
            f"• баланс - ваш баланс\n"
            f"• профиль - ваш профиль\n"
            f"• казино - игры\n"
            f"• бизнес - ваш бизнес\n"
            f"• бустеры - магазин бустеров\n"
            f"• достижения - ваши достижения\n\n"
            f"🛍️ **Маркетплейс доступен только в ЛС:**\n"
            f"Перейдите в ЛС: @{BOT_USERNAME}",
            reply_to=message.get("message_id")
        )
        return

    # Это ЛС - показываем полное меню
    keyboard = {
        "inline_keyboard": [
            [{"text": "🛍️ Просмотреть товары", "callback_data": "view_items"}],
            [{"text": "📦 Мои товары на продаже", "callback_data": "my_items"}],
            [{"text": "🛒 Мои покупки", "callback_data": "my_purchases"}],
            [{"text": "🎁 Продать подарок", "callback_data": "sell_gift"}],
            [{"text": "📝 Создать товар", "callback_data": "sell_item"}],
            [{"text": "🚀 Бустеры", "callback_data": "boosters_shop"}],
            [{"text": "🛠️ Улучшения", "callback_data": "upgrades_shop"}],
            [{"text": "🏆 Достижения", "callback_data": "achievements_menu"}],
            [{"text": "📋 Профиль", "callback_data": "profile"}],
            [{"text": "💰 Баланс", "callback_data": "balance"}],
            [{"text": "💳 Пополнить", "callback_data": "deposit"}],
            [{"text": "🎰 Казино", "callback_data": "casino"}],
            [{"text": "🏢 Бизнес", "callback_data": "business"}],
            [{"text": "📚 Помощь", "callback_data": "help"}]
        ]
    }

    welcome_text = f"""
{user_emoji} ═══ ГЛАВНОЕ МЕНЮ ═══ {user_emoji}

💰 Ваш баланс: {user['balance']:,} ₽
🎁 Подарков: {len(user.get('gifts', []))}
🛍️ Товаров на продаже: {len(user.get('market_items', []))}
🛒 Куплено товаров: {len(user.get('purchases', []))}
🚀 Активных бустеров: {len([b for b in user.get('active_boosters', {}).values() if datetime.fromisoformat(b) > datetime.now()])}
🏆 Достижений: {len(user.get('achievements', []))}

📦 **Маркетплейс:**
• Создание и просмотр товаров - только в ЛС
• Покупка товаров - через кнопки в группе
• Получение кодов - в ЛС после покупки

💡 **Другие функции доступны везде!**

Выберите действие:
"""

    send_message(message["chat"]["id"], welcome_text, reply_markup=keyboard)


def handle_my_purchases_callback(data, callback_query):
    """Показать все покупки пользователя"""
    chat_id = callback_query["message"]["chat"]["id"]
    message_id = callback_query["message"]["message_id"]
    user_id = str(callback_query["from"]["id"])

    answer_callback_query(callback_query["id"], "Загружаем ваши покупки...")

    user = get_user(data, user_id)
    purchases = user.get("purchases", [])

    if not purchases:
        keyboard = {
            "inline_keyboard": [
                [{"text": "🔙 Назад", "callback_data": "back_to_menu"}],
                [{"text": "🛍️ Маркетплейс", "callback_data": "marketplace"}],
                [{"text": "📝 Продать товар", "callback_data": "sell_item"}]
            ]
        }
        edit_message(chat_id, message_id,
                    "🛒 У вас пока нет покупок!\n\nПосетите маркетплейс, чтобы купить товары или подарки.",
                    reply_markup=keyboard)
        return

    purchases_text = "🛒 ═══ МОИ ПОКУПКИ ═══ 🛒\n\n"
    keyboard_buttons = []

    for idx, purchase in enumerate(purchases[:10]):  # Показываем последние 10 покупки
        item_name = purchase.get("item_name", "Товар")
        purchase_date = purchase.get("purchase_date", "")
        price = purchase.get("price", 0)
        item_content = purchase.get("item_content", "")
        item_type = purchase.get("item_type", "📦 Товар")

        # Форматируем дату
        try:
            date_obj = datetime.fromisoformat(purchase_date)
            formatted_date = date_obj.strftime("%d.%m.%Y %H:%M")
        except:
            formatted_date = purchase_date

        purchases_text += f"""📦 {item_name}
{item_type}
💰 Цена: {price:,} ₽
📅 Дата покупки: {formatted_date}

🎁 Содержимое:
{item_content}

━━━━━━━━━━━━━━━
"""

        keyboard_buttons.append([{
            "text": f"📦 {item_name[:15]}...",
            "callback_data": f"view_purchase_{idx}"
        }])

    keyboard_buttons.append([{"text": "🔙 Назад", "callback_data": "back_to_menu"}])
    keyboard_buttons.append([{"text": "🛍️ Маркетплейс", "callback_data": "marketplace"}])
    keyboard_buttons.append([{"text": "🔄 Обновить", "callback_data": "my_purchases"}])

    keyboard = {"inline_keyboard": keyboard_buttons}

    edit_message(chat_id, message_id, purchases_text, reply_markup=keyboard)


def handle_view_purchase_callback(data, callback_query, purchase_idx):
    """Показать детали конкретной покупки"""
    chat_id = callback_query["message"]["chat"]["id"]
    message_id = callback_query["message"]["message_id"]
    user_id = str(callback_query["from"]["id"])

    answer_callback_query(callback_query["id"], "Загружаем информацию о покупке...")

    user = get_user(data, user_id)
    purchases = user.get("purchases", [])

    try:
        purchase_idx = int(purchase_idx)
        if purchase_idx < 0 or purchase_idx >= len(purchases):
            raise IndexError
    except (ValueError, IndexError):
        answer_callback_query(callback_query["id"], "❌ Покупка не найдена!", True)
        return

    purchase = purchases[purchase_idx]

    item_name = purchase.get("item_name", "Товар")
    purchase_date = purchase.get("purchase_date", "")
    price = purchase.get("price", 0)
    item_content = purchase.get("item_content", "")
    item_description = purchase.get("item_description", "Без описания")
    item_type = purchase.get("item_type", "📦 Товар")
    seller_name = purchase.get("seller_name", "Неизвестно")

    # Форматируем дату
    try:
        date_obj = datetime.fromisoformat(purchase_date)
        formatted_date = date_obj.strftime("%d.%m.%Y %H:%M")
    except:
        formatted_date = purchase_date

    purchase_text = f"""🛒 ═══ ИНФОРМАЦИЯ О ПОКУПКЕ ═══ 🛒

📦 Название: {item_name}
📝 Описание: {item_description}
{item_type}

💰 Цена: {price:,} ₽
👤 Продавец: {seller_name}
📅 Дата покупки: {formatted_date}

🎁 СОДЕРЖИМОЕ ТОВАРА:
{item_content}

━━━━━━━━━━━━━━━
⚠️ Сохраните это сообщение!
Товар выдается только один раз.
"""

    keyboard = {
        "inline_keyboard": [
            [{"text": "🔙 К списку покупок", "callback_data": "my_purchases"}],
            [{"text": "🛍️ Маркетплейс", "callback_data": "marketplace"}],
            [{"text": "🔙 В меню", "callback_data": "back_to_menu"}]
        ]
    }

    edit_message(chat_id, message_id, purchase_text, reply_markup=keyboard)


def handle_sell_gift_callback(data, callback_query):
    """Начать процесс продажи подарка"""
    chat_id = callback_query["message"]["chat"]["id"]
    message_id = callback_query["message"]["message_id"]
    user_id = str(callback_query["from"]["id"])

    user = get_user(data, user_id)

    if not user.get("gifts"):
        answer_callback_query(callback_query["id"], "❌ У вас нет подарков для продажи!", True)
        return

    answer_callback_query(callback_query["id"], "Выберите подарок для продажи")

    gifts_text = "🎁 ═══ ВЫБЕРИТЕ ПОДАРОК ДЛЯ ПРОДАЖИ ═══ 🎁\n\n"
    keyboard_buttons = []

    for gift_id in user["gifts"]:
        if gift_id in GIFTS:
            gift = GIFTS[gift_id]
            # Используем кастомное эмодзи если есть
            if 'custom_emoji' in gift:
                display_name = f"{gift['custom_emoji']} {gift['name']}"
                gifts_text += f"{gift_id}. {display_name} [{gift['rarity']}]\n"
                keyboard_buttons.append([{
                    "text": f"🎁 {gift['name']} ({gift['rarity']})",
                    "callback_data": f"select_gift_{gift_id}"
                }])
            else:
                display_name = f"{gift['emoji']} {gift['name']}"
                gifts_text += f"{gift_id}. {display_name} [{gift['rarity']}]\n"
                keyboard_buttons.append([{
                    "text": f"{gift['emoji']} {gift['name']}",
                    "callback_data": f"select_gift_{gift_id}"
                }])

    keyboard_buttons.append([{"text": "🔙 Назад", "callback_data": "back_to_menu"}])
    keyboard_buttons.append([{"text": "📝 Продать товар", "callback_data": "sell_item"}])

    keyboard = {"inline_keyboard": keyboard_buttons}

    edit_message(chat_id, message_id, gifts_text, reply_markup=keyboard, parse_mode="HTML")


def handle_sell_item_callback(data, callback_query):
    """Начать процесс продажи товара (текстового, промокода и т.д.)"""
    chat_id = callback_query["message"]["chat"]["id"]
    message_id = callback_query["message"]["message_id"]
    user_id = str(callback_query["from"]["id"])

    answer_callback_query(callback_query["id"], "Начинаем процесс продажи товара...")

    # Сохраняем состояние пользователя
    user_states = load_user_states()
    user_states[user_id] = {
        "state": "waiting_for_item_type",
        "chat_id": chat_id,
        "message_id": message_id
    }
    save_user_states(user_states)

    keyboard = {
        "inline_keyboard": [
            [{"text": "📦 Одиночный товар", "callback_data": "single_item"}],
            [{"text": "📚 Мульти-товар (несколько кодов)", "callback_data": "multi_item"}],
            [{"text": "🔙 Назад", "callback_data": "back_to_menu"}]
        ]
    }

    edit_message(chat_id, message_id,
                 "📝 ═══ ПРОДАЖА ТОВАРА ═══ 📝\n\n"
                 "Выберите тип товара:\n\n"
                 "📦 **Одиночный товар** - 1 код/ключ на весь товар\n"
                 "📚 **Мульти-товар** - несколько кодов/ключей (1 строка = 1 товар)",
                 reply_markup=keyboard, parse_mode="Markdown")

def handle_select_gift_callback(data, callback_query, gift_id):
    """Обработка выбора подарка для продажи"""
    chat_id = callback_query["message"]["chat"]["id"]
    message_id = callback_query["message"]["message_id"]
    user_id = str(callback_query["from"]["id"])

    gift_id = int(gift_id)
    user = get_user(data, user_id)

    if gift_id not in user.get("gifts", []):
        answer_callback_query(callback_query["id"], "❌ У вас нет этого подарка!", True)
        return

    gift = GIFTS[gift_id]

    # Сохраняем состояние
    user_states = load_user_states()
    user_states[user_id] = {
        "state": "waiting_for_gift_price",
        "selected_gift": gift_id,
        "chat_id": chat_id,
        "message_id": message_id
    }
    save_user_states(user_states)

    # Показываем простой запрос цены
    if 'custom_emoji' in gift:
        gift_display = f"{gift['custom_emoji']} {gift['name']}"
    else:
        gift_display = f"{gift['emoji']} {gift['name']}"

    instructions = f"""
💰 **ВВЕДИТЕ ЦЕНУ**

🎁 Подарок: {gift_display}

Просто введите сумму в рублях (только число):

Например: 5000
"""

    keyboard = {
        "inline_keyboard": [
            [{"text": "🔙 Назад", "callback_data": "sell_gift"}]
        ]
    }

    edit_message(chat_id, message_id, instructions,
                 reply_markup=keyboard, parse_mode="HTML")
    answer_callback_query(callback_query["id"], f"Вы выбрали {gift['name']}")

def handle_price_input(data, message):
    """Обработка ввода цены для подарка"""
    user_id = str(message["from"]["id"])
    text = message.get("text", "").strip()

    user_states = load_user_states()
    user_state = user_states.get(user_id, {})

    if user_state.get("state") == "waiting_for_gift_price":
        try:
            price = int(text)
        except ValueError:
            send_message(message["chat"]["id"],
                         "❌ Введите число! Пример: 5000",
                         reply_to=message.get("message_id"))
            return

        # Минимальная и максимальная цена
        if price < 10:
            send_message(message["chat"]["id"],
                         "❌ Минимальная цена: 10 ₽",
                         reply_to=message.get("message_id"))
            return

        if price > 1000000:
            send_message(message["chat"]["id"],
                         "❌ Максимальная цена: 1,000,000 ₽",
                         reply_to=message.get("message_id"))
            return

        gift_id = user_state.get("selected_gift")
        user = get_user(data, user_id)

        if gift_id not in user.get("gifts", []):
            send_message(message["chat"]["id"],
                         "❌ У вас нет этого подарка!",
                         reply_to=message.get("message_id"))
            del user_states[user_id]
            save_user_states(user_states)
            return

        gift = GIFTS.get(gift_id, {})

        # Создаем товар
        item_id = generate_item_id()
        market_items = load_market_items()

        # Определяем отображение с кастомным эмодзи
        if 'custom_emoji' in gift:
            item_name = f"{gift['custom_emoji']} {gift['name']}"
            gift_display = item_name
        else:
            item_name = f"{gift['emoji']} {gift['name']}"
            gift_display = item_name

        # Создаем объект товара
        item = {
            "id": item_id,
            "type": "gift",  # Тип "gift" для подарков
            "gift_id": gift_id,
            "name": item_name,
            "description": f"🎁 Подарок • Редкость: {gift.get('rarity', 'Обычный')}",
            "price": price,
            "seller_id": int(user_id),
            "seller_name": user.get("first_name", "Пользователь"),
            "seller_username": user.get("username"),
            "created": datetime.now().isoformat(),
            "sold": False  # Важно: по умолчанию не продан
        }

        # Сохраняем товар
        market_items[item_id] = item
        save_market_items(market_items)

        # Добавляем в список товаров пользователя
        if "market_items" not in user:
            user["market_items"] = []
        user["market_items"].append(item_id)
        save_data(data)

        # Публикуем в канале маркетплейса
        channel_message = f"""
🛍️ ═══ НОВЫЙ ПОДАРОК ═══ 🛍️

{item_name}
📊 Редкость: {gift.get('rarity', 'Обычный')}

💰 Цена: {price:,} ₽
👤 Продавец: {user.get('first_name', 'Пользователь')}

━━━━━━━━━━━━━━━
🆔 ID товара: {item_id}
"""

        keyboard = {
            "inline_keyboard": [[
                {"text": f"🛒 Купить за {price:,} ₽", "callback_data": f"buy_item_{item_id}"}
            ]]
        }

        print(f"📤 Пытаюсь отправить в канал маркетплейса: {MARKET_CHANNEL_ID}")

        # Отправляем в канал маркетплейса
        result = send_message(MARKET_CHANNEL_ID, channel_message,
                             reply_markup=keyboard, parse_mode="HTML")

        if result:
            print(f"📤 Результат отправки в канал: {result}")
            if result.get("ok"):
                item["channel_message_id"] = result["result"]["message_id"]
                print(f"✅ Сообщение отправлено в канал, ID: {result['result']['message_id']}")
            else:
                print(f"❌ Ошибка отправки в канал: {result.get('description')}")
        else:
            print("❌ Нет результата от send_message для канала")

        save_market_items(market_items)

        # Публикуем в группе
        group_message = f"""
🎉 НОВЫЙ ПОДАРОК НА МАРКЕТПЛЕЙСЕ!

{item_name}
📊 Редкость: {gift.get('rarity', 'Обычный')}

💰 Цена: {price:,} ₽
👤 Продавец: {user.get('first_name', 'Пользователь')}

👇 Нажмите кнопку ниже для покупки
"""

        print(f"📤 Пытаюсь отправить в группу: {MAIN_GROUP_ID}")

        # Публикуем в главной группе
        group_result = send_message(MAIN_GROUP_ID, group_message,
                                   reply_markup=keyboard, parse_mode="HTML")

        if group_result:
            print(f"📤 Результат отправки в группу: {group_result}")
            if group_result.get("ok"):
                item["group_message_id"] = group_result["result"]["message_id"]
                # Формируем ссылку на сообщение в группе
                group_id_str = str(MAIN_GROUP_ID)
                if group_id_str.startswith("-100"):
                    short_id = group_id_str[4:]  # Убираем "-100"
                else:
                    short_id = group_id_str
                item["group_message_link"] = f"https://t.me/c/{short_id}/{group_result['result']['message_id']}"
                print(f"✅ Сообщение отправлено в группу, ID: {group_result['result']['message_id']}")
                print(f"🔗 Ссылка: {item['group_message_link']}")
            else:
                print(f"❌ Ошибка отправки в группу: {group_result.get('description')}")
        else:
            print("❌ Нет результата от send_message для группы")

        save_market_items(market_items)

        # Отправляем подтверждение пользователю
        success_message = f"""
✅ **ПОДАРОК ВЫСТАВЛЕН НА ПРОДАЖУ!**

{gift_display}
📊 Редкость: {gift.get('rarity', 'Обычный')}
💰 Цена: {price:,} ₽

📢 Подарок опубликован в канале и группе.

💡 Товар будет автоматически удален после продажи.
"""

        send_message(message["chat"]["id"], success_message,
                     reply_to=message.get("message_id"), parse_mode="HTML")

        # Очищаем состояние
        del user_states[user_id]
        save_user_states(user_states)

        # Возвращаем в меню
        handle_start(data, {"from": message["from"], "chat": message["chat"]})
        return

    # Если это не ввод цены для подарка, проверяем другие состояния
    elif user_state.get("state") in ["waiting_for_item_name",
                                     "waiting_for_item_description",
                                     "waiting_for_item_content",
                                     "waiting_for_item_price"]:
        # Обработка ввода для обычного товара
        handle_item_input(data, message)
        return

    # Если состояние не определено
    send_message(message["chat"]["id"],
                 "❌ Неизвестная команда. Используйте /start для меню.",
                 reply_to=message.get("message_id"))

def handle_buy_item_callback(data, callback_query, item_id):
    chat_id = callback_query["message"]["chat"]["id"]
    message_id = callback_query["message"]["message_id"]
    user_id = str(callback_query["from"]["id"])

    market_items = load_market_items()

    if item_id not in market_items:
        answer_callback_query(callback_query["id"], "❌ Товар не найден!", True)
        return

    item = market_items[item_id]

    # ИСПРАВЛЕНИЕ: Проверяем мульти-товар иначе
    if item["type"] == "gift":
        # Для подарков: если sold = True, то продан
        if item.get("sold", False):
            answer_callback_query(callback_query["id"], "❌ Товар уже куплен! Этот товар можно купить только 1 раз.", True)
            return
    elif item["type"] == "multi":
        # Для мульти-товаров: проверяем available_items
        available_items = item.get("available_items", [])
        if not available_items:
            answer_callback_query(callback_query["id"], "❌ Все товары уже проданы!", True)
            return
    else:
        # Для обычных товаров: если sold = True
        if item.get("sold", False):
            answer_callback_query(callback_query["id"], "❌ Товар уже куплен!", True)
            return

    if str(item["seller_id"]) == user_id:
        answer_callback_query(callback_query["id"], "❌ Нельзя купить свой же товар!", True)
        return

    buyer = get_user(data, user_id)

    if buyer["balance"] < item["price"]:
        answer_callback_query(callback_query["id"], f"❌ Недостаточно средств! Нужно: {item['price']:,} ₽", True)
        return

    seller_id = str(item["seller_id"])
    seller = get_user(data, seller_id)

    # Совершаем покупку
    buyer["balance"] -= item["price"]
    seller["balance"] += item["price"]

    buyer_name = callback_query['from'].get('first_name', 'Пользователь')

    # Если это подарок - передаем его
    if item["type"] == "gift":
        gift_id = item["gift_id"]

        # Удаляем у продавца
        if gift_id in seller.get("gifts", []):
            seller["gifts"].remove(gift_id)

        # Добавляем покупателю
        if gift_id not in buyer.get("gifts", []):
            buyer.setdefault("gifts", []).append(gift_id)

        gift = GIFTS.get(gift_id, {})
        item_name = f"{gift.get('emoji', '🎁')} {gift.get('name', 'Подарок')}"

        # Добавляем в покупки покупателя
        purchase_data = {
            "item_id": item_id,
            "item_name": item_name,
            "item_type": "🎁 Подарок",
            "item_description": f"Редкость: {gift.get('rarity', 'Обычный')}",
            "item_content": f"🎁 Вы получили подарок: {gift['emoji']} {gift['name']}\n📊 Редкость: {gift['rarity']}",
            "price": item["price"],
            "seller_id": seller_id,
            "seller_name": seller.get('first_name', 'Пользователь'),
            "purchase_date": datetime.now().isoformat()
        }

        # Помечаем как проданный
        item["sold"] = True
        
        # ===== ДОБАВЛЕНО: Прогресс ивента (коллекция подарков) =====
        check_event_progress(buyer, "gift_collect", 1)

    elif item["type"] == "multi":
        # Мульти-товар - берем случайный доступный
        available_items = item.get("available_items", [])
        if not available_items:
            answer_callback_query(callback_query["id"], "❌ Все товары уже проданы!", True)
            # Возвращаем деньги
            buyer["balance"] += item["price"]
            seller["balance"] -= item["price"]
            save_data(data)
            return

        import random
        purchase_item = random.choice(available_items)
        available_items.remove(purchase_item)

        # Обновляем счетчики
        item["available_items"] = available_items
        if "sold_items" not in item:
            item["sold_items"] = []
        item["sold_items"].append(purchase_item)

        # Если товары закончились, помечаем как проданный
        if len(available_items) == 0:
            item["sold"] = True
            item["available_count"] = 0
        else:
            item["available_count"] = len(available_items)

        item_name = item.get("name", "Товар")
        item_description = item.get("description", "")

        purchase_data = {
            "item_id": item_id,
            "item_name": item_name,
            "item_type": "📚 Мульти-товар",
            "item_description": item_description,
            "item_content": purchase_item,
            "original_content": item.get("content", ""),
            "price": item["price"],
            "seller_id": seller_id,
            "seller_name": seller.get('first_name', 'Пользователь'),
            "purchase_date": datetime.now().isoformat(),
            "item_type_specific": item["type"]
        }

    else:
        # Обычный товар
        item_name = item.get("name", "Товар")
        item_content = item.get("content", "")
        item_description = item.get("description", "")

        # Помечаем как проданный
        item["sold"] = True

        purchase_data = {
            "item_id": item_id,
            "item_name": item_name,
            "item_type": "📦 Товар",
            "item_description": item_description,
            "item_content": item_content,
            "price": item["price"],
            "seller_id": seller_id,
            "seller_name": seller.get('first_name', 'Пользователь'),
            "purchase_date": datetime.now().isoformat(),
            "item_type_specific": item["type"]
        }

    # Добавляем в покупки покупателя
    if "purchases" not in buyer:
        buyer["purchases"] = []
    buyer["purchases"].append(purchase_data)

    # Удаляем из списка товаров продавца, если товар полностью продан
    if item.get("sold", False):
        if seller_id in data["users"] and "market_items" in data["users"][seller_id]:
            if item_id in data["users"][seller_id]["market_items"]:
                data["users"][seller_id]["market_items"].remove(item_id)

        # Удаляем сообщение из канала маркетплейса
        if "channel_message_id" in item:
            delete_message(MARKET_CHANNEL_ID, item["channel_message_id"])

    # Обновляем статистику продаж
    seller_stats = seller.get("stats", {})
    seller_stats["items_sold"] = seller_stats.get("items_sold", 0) + 1

    # Обновляем сообщение в канале для мульти-товара
    if item["type"] == "multi" and not item.get("sold", False) and "channel_message_id" in item:
        available_count = item.get("available_count", 0)
        total_count = item.get("total_items", 0)
        sold_count = total_count - available_count

        channel_message = f"""
🛍️ ═══ МУЛЬТИ-ТОВАР ═══ 🛍️

📦 {item.get('name', 'Товар')}
📝 {item.get('description', '')}

📊 Продано: {sold_count}/{total_count} шт.
📊 Осталось: {available_count} шт.
💰 Цена за 1 шт.: {item['price']:,} ₽
👤 Продавец: {seller.get('first_name', 'Пользователь')}

💡 Каждый покупатель получает случайный доступный код!

━━━━━━━━━━━━━━━
🆔 ID товара: {item_id}
"""

        keyboard = {
            "inline_keyboard": [[
                {"text": f"🛒 Купить за {item['price']:,} ₽", "callback_data": f"buy_item_{item_id}"}
            ]]
        }

        edit_message(MARKET_CHANNEL_ID, item["channel_message_id"], channel_message, reply_markup=keyboard)

    save_market_items(market_items)
    data["stats"]["total_transactions"] += 1
    data["stats"]["market_sales"] = data["stats"].get("market_sales", 0) + 1
    save_data(data)

    # Обновляем сообщение
    keyboard = {
        "inline_keyboard": [
            [{"text": "🛍️ К маркетплейсу", "callback_data": "marketplace"}],
            [{"text": "🛒 Мои покупки", "callback_data": "my_purchases"}],
            [{"text": "🔙 В меню", "callback_data": "back_to_menu"}]
        ]
    }

    answer_callback_query(callback_query["id"], f"✅ Покупка совершена! Товар добавлен в раздел 'Мои покупки'.")

    if item["type"] == "gift":
        edit_message(chat_id, message_id,
                     f"✅ Товар '{item.get('name', 'Товар')}' успешно куплен!\n\n"
                     f"💰 Списано: {item['price']:,} ₽\n\n"
                     f"🎁 Товар добавлен в раздел 'Мои покупки'.",
                     reply_markup=keyboard)
    elif item["type"] == "multi":
        edit_message(chat_id, message_id,
                     f"✅ Вы купили товар из набора '{item.get('name', 'Товар')}'!\n\n"
                     f"💰 Списано: {item['price']:,} ₽\n\n"
                     f"🎁 Случайный товар из набора добавлен в раздел 'Мои покупки'.\n"
                     f"📊 Осталось товаров в наборе: {item.get('available_count', 0)}",
                     reply_markup=keyboard)
    else:
        edit_message(chat_id, message_id,
                     f"✅ Товар '{item.get('name', 'Товар')}' успешно куплен!\n\n"
                     f"💰 Списано: {item['price']:,} ₽\n\n"
                     f"🎁 Товар добавлен в раздел 'Мои покупки'.",
                     reply_markup=keyboard)

    # Уведомляем продавца
    if item["type"] == "gift":
        send_message(seller_id, f"""
💰 Ваш товар продан!

📦 Товар: {item.get('name', 'Товар')}
💰 Цена: {item['price']:,} ₽
👤 Покупатель: {buyer_name}
📅 Дата продажи: {datetime.now().strftime('%d.%m.%Y %H:%M')}

💸 Средства зачислены на ваш баланс!
""")
    elif item["type"] == "multi":
        send_message(seller_id, f"""
💰 Товар из вашего набора продан!

📦 Набор: {item.get('name', 'Товар')}
💰 Цена: {item['price']:,} ₽
👤 Покупатель: {buyer_name}
📊 Продано: {item.get('total_items', 0) - item.get('available_count', 0)}/{item.get('total_items', 0)}
📅 Дата продажи: {datetime.now().strftime('%d.%m.%Y %H:%M')}

💸 Средства зачислены на ваш баланс!
""")
    else:
        send_message(seller_id, f"""
💰 Ваш товар продан!

📦 Товар: {item.get('name', 'Товар')}
💰 Цена: {item['price']:,} ₽
👤 Покупатель: {buyer_name}
📅 Дата продажи: {datetime.now().strftime('%d.%m.%Y %H:%M')}

💸 Средства зачислены на ваш баланс!
""")


def handle_remove_item_callback(data, callback_query, item_id):
    chat_id = callback_query["message"]["chat"]["id"]
    message_id = callback_query["message"]["message_id"]
    user_id = str(callback_query["from"]["id"])

    market_items = load_market_items()

    if item_id not in market_items:
        answer_callback_query(callback_query["id"], "❌ Товар не найден!", True)
        return

    item = market_items[item_id]

    if str(item["seller_id"]) != user_id:
        answer_callback_query(callback_query["id"], "❌ Это не ваш товар!", True)
        return

    if item.get("sold", False):
        answer_callback_query(callback_query["id"], "❌ Товар уже продан!", True)
        return

    # Удаляем из канала маркетплейса
    if "channel_message_id" in item:
        delete_message(MARKET_CHANNEL_ID, item["channel_message_id"])

    # Удаляем из списка товаров пользователя
    user = get_user(data, user_id)
    if item_id in user.get("market_items", []):
        user["market_items"].remove(item_id)

    # Удаляем из market_items
    del market_items[item_id]

    save_market_items(market_items)
    save_data(data)

    answer_callback_query(callback_query["id"], "✅ Товар удалён с продажи!")
    handle_my_items_callback(data, callback_query)


def handle_boosters_shop_callback(data, callback_query):
    """Обработка кнопки магазина бустеров"""
    chat_id = callback_query["message"]["chat"]["id"]
    message_id = callback_query["message"]["message_id"]
    user_id = str(callback_query["from"]["id"])

    answer_callback_query(callback_query["id"], "Открываем магазин бустеров...")
    handle_boosters_shop(data, {"chat": {"id": chat_id}, "message_id": message_id, "from": callback_query["from"]})


def handle_upgrades_shop_callback(data, callback_query):
    """Обработка кнопки магазина улучшений"""
    chat_id = callback_query["message"]["chat"]["id"]
    message_id = callback_query["message"]["message_id"]
    user_id = str(callback_query["from"]["id"])

    answer_callback_query(callback_query["id"], "Открываем магазин улучшений...")
    handle_upgrades_shop(data, {"chat": {"id": chat_id}, "message_id": message_id, "from": callback_query["from"]})


def handle_achievements_menu_callback(data, callback_query):
    """Обработка кнопки достижений"""
    chat_id = callback_query["message"]["chat"]["id"]
    message_id = callback_query["message"]["message_id"]
    user_id = str(callback_query["from"]["id"])

    answer_callback_query(callback_query["id"], "Загружаем достижения...")
    handle_achievements(data, {"chat": {"id": chat_id}, "message_id": message_id, "from": callback_query["from"]})


def handle_back_to_menu_callback(data, callback_query):
    chat_id = callback_query["message"]["chat"]["id"]
    message_id = callback_query["message"]["message_id"]
    user_id = str(callback_query["from"]["id"])

    answer_callback_query(callback_query["id"], "Возвращаемся в меню...")
    handle_start(data, {"from": {"id": int(user_id), "username": "", "first_name": ""}, "chat": {"id": chat_id}})


def handle_profile_callback(data, callback_query):
    chat_id = callback_query["message"]["chat"]["id"]
    message_id = callback_query["message"]["message_id"]
    user_id = str(callback_query["from"]["id"])

    answer_callback_query(callback_query["id"], "Загружаем профиль...")

    user = get_user(data, user_id)
    profile = build_profile(data, user_id)

    keyboard = {
        "inline_keyboard": [
            [{"text": "🔙 Назад", "callback_data": "back_to_menu"}]
        ]
    }

    edit_message(chat_id, message_id, profile, reply_markup=keyboard)


def handle_balance_callback(data, callback_query):
    chat_id = callback_query["message"]["chat"]["id"]
    message_id = callback_query["message"]["message_id"]
    user_id = str(callback_query["from"]["id"])

    user = get_user(data, user_id)
    user_emoji = get_user_emoji(user)

    answer_callback_query(callback_query["id"], f"Ваш баланс: {user['balance']:,} ₽")

    keyboard = {
        "inline_keyboard": [
            [{"text": "🔙 Назад", "callback_data": "back_to_menu"}],
            [{"text": "🎰 Казино", "callback_data": "casino"}],
            [{"text": "💳 Пополнить", "callback_data": "deposit"}]
        ]
    }

    edit_message(chat_id, message_id,
                 f"{user_emoji} ═══ БАЛАНС ═══ {user_emoji}\n\n💰 Ваш баланс: {user['balance']:,} ₽\n💳 Пополнено: {user.get('total_deposited', 0):,} ₽\n📤 Выведено: {user.get('total_withdrawn', 0):,} ₽\n\n💡 Пополнить баланс можно через промокоды или переводы от других игроков!",
                 reply_markup=keyboard)


def handle_deposit_callback(data, callback_query):
    """Обработка кнопки пополнения"""
    chat_id = callback_query["message"]["chat"]["id"]
    message_id = callback_query["message"]["message_id"]

    answer_callback_query(callback_query["id"], "Информация о пополнении...")

    handle_deposit_info(data, {"chat": {"id": chat_id}, "message_id": message_id, "from": callback_query["from"]})


def handle_casino_callback(data, callback_query):
    chat_id = callback_query["message"]["chat"]["id"]
    message_id = callback_query["message"]["message_id"]

    answer_callback_query(callback_query["id"], "Открываем казино...")

    casino_text = f"""
🎰 ═══ КАЗИНО ═══ 🎰

🎲 Доступные игры:

🎰 слоты [ставка] - Слот-машина (x2-x10)
🪙 монетка [ставка] - Орёл или решка (x2)
🎲 кости [ставка] - Кости (x2-x6)
🎡 рулетка [ставка] [красное/чёрное/число] - Рулетка

💡 Минимальная ставка: 10 ₽
💡 Максимальная ставка: 10,000 ₽

📊 Ваши шансы:
• Слоты: {CHANCE_SETTINGS['slots_win_chance']}% на выигрыш
• Монетка: {CHANCE_SETTINGS['coinflip_win_chance']}% на выигрыш (x2)
• Кости: чем больше выпадет - тем больше выигрыш
• Рулетка: цвет x2, число x35

💡 Используйте команды в любом чате с ботом!
"""

    keyboard = {
        "inline_keyboard": [
            [{"text": "🔙 Назад", "callback_data": "back_to_menu"}],
            [{"text": "💰 Баланс", "callback_data": "balance"}]
        ]
    }

    edit_message(chat_id, message_id, casino_text, reply_markup=keyboard)


def handle_business_callback(data, callback_query):
    chat_id = callback_query["message"]["chat"]["id"]
    message_id = callback_query["message"]["message_id"]
    user_id = str(callback_query["from"]["id"])

    answer_callback_query(callback_query["id"], "Загружаем бизнес...")

    user = get_user(data, user_id)
    user_emoji = get_profile_decoration_custom(user)  # <-- ИЗМЕНИТЬ
    level = user.get("business_level", 0)

    biz_text = f"{user_emoji} ═══ БИЗНЕС ═══ {user_emoji}\n\n"

    if level == 0:
        biz_text += "🏪 У вас нет бизнеса!\n\n"
        biz_text += "📋 Доступные бизнесы:\n"
        for lvl, biz in BUSINESS_LEVELS.items():
            if lvl > 0 and lvl <= 5:  # Показываем только первые 5 для краткости
                biz_text += f"{biz['name']} - {biz['buy_price']:,} ₽ (доход: {biz['income']} ₽/час)\n"
        biz_text += "\n💡 Купить: купить бизнес"
        biz_text += "\n📋 Весь список: /бизнес_список"
    else:
        biz = BUSINESS_LEVELS[level]
        biz_text += f"🏢 Ваш бизнес: {biz['name']}\n"
        biz_text += f"📊 Уровень: {level}/30\n"
        biz_text += f"💰 Доход: {biz['income']:,} ₽/час\n"
        biz_text += f"📦 Макс. товаров: {biz['max_items']}\n\n"

        if level < 30:
            next_biz = BUSINESS_LEVELS[level + 1]
            biz_text += f"⬆️ Улучшить до {next_biz['name']}: {next_biz['upgrade_price']:,} ₽\n"
            biz_text += "💡 Улучшить: улучшить бизнес\n"
        else:
            biz_text += "👑 Максимальный уровень!\n"

        biz_text += "\n💡 Собрать доход: доход"
        biz_text += "\n📋 Весь список бизнесов: /бизнес_список"

    keyboard = {
        "inline_keyboard": [
            [{"text": "🔙 Назад", "callback_data": "back_to_menu"}]
        ]
    }

    edit_message(chat_id, message_id, biz_text, reply_markup=keyboard)

def handle_help_callback(data, callback_query):
    chat_id = callback_query["message"]["chat"]["id"]
    message_id = callback_query["message"]["message_id"]

    answer_callback_query(callback_query["id"], "Загружаем помощь...")

    help_text = """
📚 ═══ ПОМОЩЬ ═══ 📚

👤 Основные команды:
• /start - главное меню
• профиль - ваш профиль
• баланс - ваш баланс
• бонус - ежедневный бонус

💰 Переводы:
• дать [сумма] - передать деньги (в ответ)

💳 Пополнение:
• пополнить - инструкция по пополнению
• ввести код [код] - ввести промокод

🛍️ Маркетплейс:
• Добавляйте товары через меню
• Покупайте товары других игроков
• Продавайте подарки и товары

🚀 Бустеры:
• бустеры - магазин бустеров
• купить бустер [ID] - купить бустер
• мои бустеры - активные бустеры

🛠️ Улучшения:
• улучшения - магазин улучшений
• купить улучшение [ID] - купить улучшение

🏆 Достижения:
• достижения - ваши достижения
• секрет - секретная команда

🎰 Казино:
• казино - список игр
• слоты/монетка/кости/рулетка [ставка]

🏢 Бизнес:
• бизнес - информация о бизнеса
• купить бизнес - купить бизнес
• улучшить бизнес - повысить уровень
• доход - собрать доход

🎁 Подарки:
• подарки - список всех подарков
• Подарки можно продавать на маркетплейсе
"""

    keyboard = {
        "inline_keyboard": [
            [{"text": "🔙 Назад", "callback_data": "back_to_menu"}],
            [{"text": "🛍️ Маркетплейс", "callback_data": "marketplace"}],
            [{"text": "💳 Пополнить", "callback_data": "deposit"}]
        ]
    }

    edit_message(chat_id, message_id, help_text, reply_markup=keyboard)


def handle_callback_query(data, callback_query):
    callback_data = callback_query.get("data", "")
    chat_type = callback_query["message"]["chat"]["type"]

    # Команды, которые работают ТОЛЬКО в ЛС
    lsonly_callbacks = [
        "view_items", "my_items", "my_purchases", "sell_gift", "sell_item",
        "single_item", "multi_item", "select_gift_", "remove_item_",
        "back_to_menu", "view_purchase_", "marketplace"
    ]

    # Проверяем, нужна ли команде приватность
    needs_privacy = False
    for private_cmd in lsonly_callbacks:
        if callback_data.startswith(private_cmd) or callback_data == private_cmd:
            needs_privacy = True
            break

    # Маркетплейс доступен только в ЛС
    if needs_privacy and chat_type != "private":
        answer_callback_query(
            callback_query["id"],
            "⚠️ Маркетплейс доступен только в личных сообщениях!\n"
            f"Перейдите в ЛС: @{BOT_USERNAME}",
            show_alert=True
        )
        return

    # Обработка покупки - разрешена везде
    if callback_data.startswith("buy_item_"):
        item_id = callback_data.replace("buy_item_", "")
        handle_buy_item_callback(data, callback_query, item_id)

    # Команды, которые работают ВЕЗДЕ
    elif callback_data in ["boosters_shop", "upgrades_shop", "achievements_menu",
                          "profile", "balance", "deposit", "casino", "business",
                          "help"]:
        if callback_data == "boosters_shop":
            handle_boosters_shop_callback(data, callback_query)
        elif callback_data == "upgrades_shop":
            handle_upgrades_shop_callback(data, callback_query)
        elif callback_data == "achievements_menu":
            handle_achievements_menu_callback(data, callback_query)
        elif callback_data == "profile":
            handle_profile_callback(data, callback_query)
        elif callback_data == "balance":
            handle_balance_callback(data, callback_query)
        elif callback_data == "deposit":
            handle_deposit_callback(data, callback_query)
        elif callback_data == "casino":
            handle_casino_callback(data, callback_query)
        elif callback_data == "business":
            handle_business_callback(data, callback_query)
        elif callback_data == "help":
            handle_help_callback(data, callback_query)

    # Команды для ЛС (маркетплейс)
    elif chat_type == "private":
        if callback_data == "marketplace" or callback_data == "view_items":
            handle_marketplace_callback(data, callback_query)
        elif callback_data == "my_items":
            handle_my_items_callback(data, callback_query)
        elif callback_data == "my_purchases":
            handle_my_purchases_callback(data, callback_query)
        elif callback_data.startswith("view_purchase_"):
            purchase_idx = callback_data.replace("view_purchase_", "")
            handle_view_purchase_callback(data, callback_query, purchase_idx)
        elif callback_data == "sell_gift":
            handle_sell_gift_callback(data, callback_query)
        elif callback_data == "sell_item":
            handle_sell_item_callback(data, callback_query)
        elif callback_data == "single_item":
            handle_item_type_callback(data, callback_query, "single")
        elif callback_data == "multi_item":
            handle_item_type_callback(data, callback_query, "multi")
        elif callback_data.startswith("select_gift_"):
            gift_id = callback_data.replace("select_gift_", "")
            handle_select_gift_callback(data, callback_query, gift_id)
        elif callback_data.startswith("remove_item_"):
            item_id = callback_data.replace("remove_item_", "")
            handle_remove_item_callback(data, callback_query, item_id)
        elif callback_data == "back_to_menu":
            handle_back_to_menu_callback(data, callback_query)

    # ==== НОВЫЕ БИЗНЕС КОЛБЭКИ ====
    elif callback_data == "business_list":
        handle_business_list(data, {"from": callback_query["from"],
                                   "chat": {"id": callback_query["message"]["chat"]["id"]},
                                   "message_id": callback_query["message"]["message_id"]})
    elif callback_data.startswith("business_category_"):
        category = callback_data.replace("business_category_", "")
        handle_business_category_callback(data, callback_query, category)
    elif callback_data.startswith("upgrade_to_"):
        try:
            level = int(callback_data.replace("upgrade_to_", ""))
            # Проверяем, можно ли улучшить до этого уровня
            user_id = str(callback_query["from"]["id"])
            user = get_user(data, user_id)
            current_level = user.get("business_level", 0)

            if current_level == level - 1:
                handle_upgrade_business(data, {"from": callback_query["from"],
                                              "chat": {"id": callback_query["message"]["chat"]["id"]},
                                              "message_id": callback_query["message"]["message_id"]})
            else:
                answer_callback_query(callback_query["id"],
                                    "❌ Сначала улучшите бизнес до предыдущего уровня!", True)
        except:
            answer_callback_query(callback_query["id"], "❌ Ошибка!", True)


# ==== НОВАЯ ВЕРСИЯ ====
def handle_buy_item_callback(data, callback_query, item_id):
    chat_id = callback_query["message"]["chat"]["id"]
    message_id = callback_query["message"]["message_id"]
    user_id = str(callback_query["from"]["id"])

    market_items = load_market_items()

    if item_id not in market_items:
        answer_callback_query(callback_query["id"], "❌ Товар не найден!", True)
        return

    item = market_items[item_id]

    if str(item["seller_id"]) == user_id:
        answer_callback_query(callback_query["id"], "❌ Нельзя купить свой же товар!", True)
        return

    buyer = get_user(data, user_id)

    if buyer["balance"] < item["price"]:
        answer_callback_query(callback_query["id"], f"❌ Недостаточно средств! Нужно: {item['price']:,} ₽", True)
        return

    seller_id = str(item["seller_id"])
    seller = get_user(data, seller_id)

    # Для мульти-товаров проверяем, есть ли доступные товары
    if item["type"] == "multi":
        if not item.get("available_items") or len(item["available_items"]) == 0:
            answer_callback_query(callback_query["id"], "❌ Все товары уже проданы!", True)
            return

    # Совершаем покупку
    buyer["balance"] -= item["price"]
    seller["balance"] += item["price"]

    buyer_name = callback_query['from'].get('first_name', 'Пользователь')

    # Получаем товар для покупателя
    if item["type"] == "single":
        # Одиночный товар
        item_content = item.get("content", "")
        item["sold"] = True
        purchase_item = item_content
    else:
        # Мульти-товар - берем случайный доступный
        available_items = item.get("available_items", [])
        if not available_items:
            answer_callback_query(callback_query["id"], "❌ Все товары уже проданы!", True)
            # Возвращаем деньги
            buyer["balance"] += item["price"]
            seller["balance"] -= item["price"]
            save_data(data)
            return

        # Берем первый товар из списка (можно использовать random.choice)
        import random
        purchase_item = random.choice(available_items)
        available_items.remove(purchase_item)

        # Обновляем счетчики
        item["available_items"] = available_items
        if "sold_items" not in item:
            item["sold_items"] = []
        item["sold_items"].append(purchase_item)

        # Если товары закончились, помечаем как проданный
        if len(available_items) == 0:
            item["sold"] = True
            item["available_count"] = 0
        else:
            item["available_count"] = len(available_items)

    # Добавляем в покупки покупателя
    purchase_data = {
        "item_id": item_id,
        "item_name": item.get("name", "Товар"),
        "item_type": "📦 Товар" if item["type"] == "single" else "📚 Мульти-товар",
        "item_description": item.get("description", ""),
        "item_content": purchase_item,  # Только купленный товар
        "original_content": item.get("content", ""),  # Весь исходный список (только для мульти-товаров)
        "price": item["price"],
        "seller_id": seller_id,
        "seller_name": seller.get('first_name', 'Пользователь'),
        "purchase_date": datetime.now().isoformat(),
        "item_type_specific": item["type"]
    }

    if "purchases" not in buyer:
        buyer["purchases"] = []
    buyer["purchases"].append(purchase_data)

    # Удаляем из списка товаров продавца, если товар полностью продан
    if item.get("sold", False):
        if seller_id in data["users"] and "market_items" in data["users"][seller_id]:
            if item_id in data["users"][seller_id]["market_items"]:
                data["users"][seller_id]["market_items"].remove(item_id)

        # Удаляем сообщение из канала маркетплейса
        if "channel_message_id" in item:
            delete_message(MARKET_CHANNEL_ID, item["channel_message_id"])

    # Обновляем статистику продаж
    seller_stats = seller.get("stats", {})
    seller_stats["items_sold"] = seller_stats.get("items_sold", 0) + 1

    # Обновляем сообщение в канале для мульти-товара
    if item["type"] == "multi" and not item.get("sold", False) and "channel_message_id" in item:
        available_count = item.get("available_count", 0)
        total_count = item.get("total_items", 0)
        sold_count = total_count - available_count

        channel_message = f"""
🛍️ ═══ МУЛЬТИ-ТОВАР ═══ 🛍️

📦 {item.get('name', 'Товар')}
📝 {item.get('description', '')}

📊 Продано: {sold_count}/{total_count} шт.
📊 Осталось: {available_count} шт.
💰 Цена за 1 шт.: {item['price']:,} ₽
👤 Продавец: {seller.get('first_name', 'Пользователь')}

💡 Каждый покупатель получает случайный доступный код!

━━━━━━━━━━━━━━━
🆔 ID товара: {item_id}
"""

        keyboard = {
            "inline_keyboard": [[
                {"text": f"🛒 Купить за {item['price']:,} ₽", "callback_data": f"buy_item_{item_id}"}
            ]]
        }

        edit_message(MARKET_CHANNEL_ID, item["channel_message_id"], channel_message, reply_markup=keyboard)

    save_market_items(market_items)
    data["stats"]["total_transactions"] += 1
    data["stats"]["market_sales"] = data["stats"].get("market_sales", 0) + 1
    save_data(data)

    # Обновляем сообщение
    keyboard = {
        "inline_keyboard": [
            [{"text": "🛍️ К маркетплейсу", "callback_data": "marketplace"}],
            [{"text": "🛒 Мои покупки", "callback_data": "my_purchases"}],
            [{"text": "🔙 В меню", "callback_data": "back_to_menu"}]
        ]
    }

    answer_callback_query(callback_query["id"], f"✅ Покупка совершена! Товар добавлен в раздел 'Мои покупки'.")

    if item["type"] == "single":
        edit_message(chat_id, message_id,
                     f"✅ Товар '{item.get('name', 'Товар')}' успешно куплен!\n\n"
                     f"💰 Списано: {item['price']:,} ₽\n\n"
                     f"🎁 Товар добавлен в раздел 'Мои покупки'.",
                     reply_markup=keyboard)
    else:
        edit_message(chat_id, message_id,
                     f"✅ Вы купили товар из набора '{item.get('name', 'Товар')}'!\n\n"
                     f"💰 Списано: {item['price']:,} ₽\n\n"
                     f"🎁 Случайный товар из набора добавлен в раздел 'Мои покупки'.\n"
                     f"📊 Осталось товаров в наборе: {item.get('available_count', 0)}",
                     reply_markup=keyboard)

    # Уведомляем продавца
    if item["type"] == "single":
        send_message(seller_id, f"""
💰 Ваш товар продан!

📦 Товар: {item.get('name', 'Товар')}
💰 Цена: {item['price']:,} ₽
👤 Покупатель: {buyer_name}
📅 Дата продажи: {datetime.now().strftime('%d.%m.%Y %H:%M')}

💸 Средства зачислены на ваш баланс!
""")
    else:
        send_message(seller_id, f"""
💰 Товар из вашего набора продан!

📦 Набор: {item.get('name', 'Товар')}
💰 Цена: {item['price']:,} ₽
👤 Покупатель: {buyer_name}
📊 Продано: {item.get('total_items', 0) - item.get('available_count', 0)}/{item.get('total_items', 0)}
📅 Дата продажи: {datetime.now().strftime('%d.%m.%Y %H:%M')}

💸 Средства зачислены на ваш баланс!
""")

def check_auto_collect(data):
    """Проверить и автоматически собрать доходы для всех пользователей с авто-сбором"""
    now = datetime.now()
    collected_total = 0
    users_processed = 0

    for user_id, user in data["users"].items():
        # Проверяем, есть ли у пользователя улучшение авто-сбора
        if "auto_collect" in user.get("upgrades", []):
            level = user.get("business_level", 0)
            if level > 0:
                last_income = user.get("last_income")

                if last_income:
                    try:
                        last_time = datetime.fromisoformat(last_income)
                        hours_passed = (now - last_time).total_seconds() / 3600

                        # Собираем каждые 4 часа
                        if hours_passed >= 4:
                            biz = BUSINESS_LEVELS[level]
                            income = int(biz['income'] * 4)  # 4 часа дохода

                            # Проверяем бустер двойного дохода
                            if check_active_booster(user, "double_income"):
                                income *= BOOSTERS["double_income"]["multiplier"]

                            user["balance"] += income
                            user["last_income"] = now.isoformat()
                            collected_total += income
                            users_processed += 1

                            # Уведомляем пользователя в ЛС
                            try:
                                send_message(
                                    user_id,
                                    f"🤖 Авто-сбор доходов!\n\n"
                                    f"💰 Собрано: {income:,} ₽\n"
                                    f"💵 Ваш баланс: {user['balance']:,} ₽\n"
                                    f"⏰ Следующий сбор через 4 часа"
                                )
                            except:
                                pass  # Если не можем отправить сообщение, пропускаем

                            # Логируем для отладки
                            print(f"🤖 Авто-сбор для {user_id}: +{income}₽")
                    except Exception as e:
                        print(f"❌ Ошибка авто-сбора для {user_id}: {e}")
                else:
                    # Если нет времени последнего сбора, устанавливаем текущее время
                    user["last_income"] = now.isoformat()

    if collected_total > 0:
        save_data(data)
        print(f"💰 Авто-сбор завершен: {users_processed} пользователей, {collected_total}₽")

    return collected_total

def handle_price_input(data, message):
    """Обработка ввода цены для подарка"""
    user_id = str(message["from"]["id"])
    text = message.get("text", "").strip()

    user_states = load_user_states()
    user_state = user_states.get(user_id, {})

    if user_state.get("state") == "waiting_for_gift_price":
        try:
            price = int(text)
        except ValueError:
            send_message(message["chat"]["id"], "❌ Пожалуйста, введите число! Пример: 5000")
            return

        if price < 10:
            send_message(message["chat"]["id"], "❌ Минимальная цена: 10 ₽")
            return

        if price > 1000000:
            send_message(message["chat"]["id"], "❌ Максимальная цена: 1,000,000 ₽")
            return

        gift_id = user_state.get("selected_gift")
        user = get_user(data, user_id)

        if gift_id not in user.get("gifts", []):
            send_message(message["chat"]["id"], "❌ У вас нет этого подарка!")
            del user_states[user_id]
            save_user_states(user_states)
            return

        gift = GIFTS.get(gift_id, {})

        # Создаем товар
        item_id = generate_item_id()
        market_items = load_market_items()

        item = {
            "id": item_id,
            "type": "gift",
            "gift_id": gift_id,
            "name": f"{gift.get('emoji', '🎁')} {gift.get('name', 'Подарок')}",
            "description": f"Редкость: {gift.get('rarity', 'Обычный')}",
            "price": price,
            "seller_id": int(user_id),
            "seller_name": user.get("first_name", "Пользователь"),
            "seller_username": user.get("username"),
            "created": datetime.now().isoformat(),
            "sold": False
        }

        market_items[item_id] = item
        save_market_items(market_items)

        # Добавляем в список товаров пользователя
        if "market_items" not in user:
            user["market_items"] = []
        user["market_items"].append(item_id)
        save_data(data)

        # Публикуем в канале маркетплейса
        channel_message = f"""
🛍️ ═══ НОВЫЙ ТОВАР ═══ 🛍️

{gift.get('emoji', '🎁')} {gift.get('name', 'Подарок')}
📝 {gift.get('rarity', 'Обычный')} подарок

💰 Цена: {price:,} ₽
👤 Продавец: {user.get('first_name', 'Пользователь')}

━━━━━━━━━━━━━━━
🆔 ID товара: {item_id}
"""

        keyboard = {
            "inline_keyboard": [[
                {"text": f"🛒 Купить за {price:,} ₽", "callback_data": f"buy_item_{item_id}"}
            ]]
        }

        result = send_message(MARKET_CHANNEL_ID, channel_message, reply_markup=keyboard)

        if result and result.get("ok"):
            item["channel_message_id"] = result["result"]["message_id"]
            save_market_items(market_items)

            # Публикуем в группах
            groups = [MAIN_GROUP_ID]  # Добавьте ID других групп при необходимости

            for group_id in groups:
                group_message = f"""
🎉 НОВЫЙ ТОВАР НА МАРКЕТПЛЕЙСЕ!

{gift.get('emoji', '🎁')} {gift.get('name', 'Подарок')}
📝 {gift.get('rarity', 'Обычный')} подарок

💰 Цена: {price:,} ₽
👤 Продавец: {user.get('first_name', 'Пользователь')}

👇 Нажмите кнопку ниже для покупки
"""

                send_message(group_id, group_message, reply_markup=keyboard)

        # Отправляем подтверждение пользователю
        send_message(message["chat"]["id"],
                     f"✅ Товар добавлен на маркетплейс!\n\n{gift.get('emoji', '🎁')} {gift.get('name', 'Подарок')}\n💰 Цена: {price:,} ₽\n\nТовар будет автоматически удален после продажи.")

        # Очищаем состояние
        del user_states[user_id]
        save_user_states(user_states)

        # Возвращаем в меню
        handle_start(data, message)

# Где-то в разделе с функциями маркетплейса
def publish_to_group(item_id, item, seller_name, price):
    """Публикация товара в группе"""

    seller_mention = seller_name
    if item.get("seller_username"):
        seller_mention = f"@{item['seller_username']}"

    # Отладочная информация
    print(f"🚀 Начинаю публикацию товара в группу:", flush=True)
    print(f"   ID товара: {item_id}", flush=True)
    print(f"   Название: {item.get('name')}", flush=True)
    print(f"   Цена: {price} ₽", flush=True)
    print(f"   ID группы: {MAIN_GROUP_ID}", flush=True)
    print(f"   Тип товара: {item.get('type', 'single')}", flush=True)

    if item.get("type") == "single":
        group_message = f"""
🛍️ ═══ НОВЫЙ ТОВАР ═══ 🛍️

📦 **{item['name']}**
📝 {item['description']}

💰 **Цена:** {price:,} ₽
👤 **Продавец:** {seller_mention}

⚠️ **Внимание:** После покупки товар будет отправлен вам в ЛС с ботом!
Нажмите кнопку ниже, чтобы купить этот товар.

👇 **КУПИТЬ:**
"""
    else:
        total_items = item.get("total_items", 1)
        group_message = f"""
🛍️ ═══ НОВЫЙ МУЛЬТИ-ТОВАР ═══ 🛍️

📦 **{item['name']}**
📝 {item['description']}

📊 **Количество:** {total_items} шт.
💰 **Цена за 1 шт.:** {price:,} ₽
👤 **Продавец:** {seller_mention}

⚠️ **Внимание:** После покупки товар будет отправлен вам в ЛС с ботом!
Каждый покупатель получит случайный код из набора.

👇 **КУПИТЬ:**
"""

    keyboard = {
        "inline_keyboard": [[
            {"text": f"🛒 Купить за {price:,} ₽", "callback_data": f"buy_item_{item_id}"}
        ]]
    }

    print(f"📤 Отправляю сообщение...", flush=True)
    print(f"   Текст: {group_message[:100]}...", flush=True)

    result = send_message(MAIN_GROUP_ID, group_message, reply_markup=keyboard, parse_mode="Markdown")

    if result:
        print(f"📤 Результат от Telegram API:", flush=True)
        print(f"   OK: {result.get('ok')}", flush=True)
        print(f"   Description: {result.get('description', 'Нет описания')}", flush=True)
        print(f"   Error Code: {result.get('error_code', 'Нет кода ошибки')}", flush=True)

        if result.get("ok"):
            print(f"✅ УСПЕХ! Сообщение опубликовано в группе!", flush=True)
            print(f"   ID сообщения: {result['result']['message_id']}", flush=True)
            return result
        else:
            print(f"❌ ОШИБКА при публикации!", flush=True)
            return None
    else:
        print(f"❌ НЕТ ОТВЕТА от Telegram API!", flush=True)
        return None

# ==== НОВЫЕ ФУНКЦИИ - ДОБАВИТЬ ====
def handle_item_type_callback(data, callback_query, item_type):
    """Обработка выбора типа товара"""
    chat_id = callback_query["message"]["chat"]["id"]
    message_id = callback_query["message"]["message_id"]
    user_id = str(callback_query["from"]["id"])

    user_states = load_user_states()
    if user_id not in user_states:
        user_states[user_id] = {}

    user_states[user_id].update({
        "state": "waiting_for_item_name",
        "item_type": item_type,
        "chat_id": chat_id,
        "message_id": message_id
    })
    save_user_states(user_states)

    answer_callback_query(callback_query["id"],
                         "📦 Одиночный товар" if item_type == "single" else "📚 Мульти-товар")

    edit_message(chat_id, message_id,
                 "1️⃣ Введите название товара:\n"
                 "Пример: Steam ключи\n"
                 "Пример: Промокоды на Nitro\n"
                 "Пример: Игровые предметы\n\n"
                 "💡 Название должно быть понятным!",
                 reply_markup={"inline_keyboard": [[{"text": "🔙 Назад", "callback_data": "sell_item"}]]})

def handle_price_input(data, message):
    """Обработка ввода цены для подарка"""
    user_id = str(message["from"]["id"])
    text = message.get("text", "").strip()

    user_states = load_user_states()
    user_state = user_states.get(user_id, {})

    if user_state.get("state") == "waiting_for_gift_price":
        try:
            price = int(text)
        except ValueError:
            send_message(message["chat"]["id"],
                         "❌ Введите число!",
                         reply_to=message.get("message_id"))
            return

        # Только минимальная проверка
        if price < 1:
            send_message(message["chat"]["id"],
                         "❌ Цена должна быть больше 0!",
                         reply_to=message.get("message_id"))
            return

        gift_id = user_state.get("selected_gift")
        user = get_user(data, user_id)

        if gift_id not in user.get("gifts", []):
            send_message(message["chat"]["id"],
                         "❌ У вас нет этого подарка!",
                         reply_to=message.get("message_id"))
            del user_states[user_id]
            save_user_states(user_states)
            return

        gift = GIFTS.get(gift_id, {})

        # Создаем товар
        item_id = generate_item_id()
        market_items = load_market_items()

        # Определяем отображение
        if 'custom_emoji' in gift:
            item_name = f"{gift['custom_emoji']} {gift['name']}"
            gift_display = item_name
        else:
            item_name = f"{gift['emoji']} {gift['name']}"
            gift_display = item_name

        item = {
            "id": item_id,
            "type": "gift",
            "gift_id": gift_id,
            "name": item_name,
            "description": f"🎁 Подарок • Редкость: {gift.get('rarity', 'Обычный')}",
            "price": price,
            "seller_id": int(user_id),
            "seller_name": user.get("first_name", "Пользователь"),
            "seller_username": user.get("username"),
            "created": datetime.now().isoformat(),
            "sold": False
        }

        market_items[item_id] = item
        save_market_items(market_items)

        # Добавляем в список товаров пользователя
        if "market_items" not in user:
            user["market_items"] = []
        user["market_items"].append(item_id)
        save_data(data)

        # Публикуем в канале маркетплейса
        channel_message = f"""
🛍️ ═══ НОВЫЙ ПОДАРОК ═══ 🛍️

{item_name}
📊 Редкость: {gift.get('rarity', 'Обычный')}

💰 Цена: {price:,} ₽
👤 Продавец: {user.get('first_name', 'Пользователь')}

━━━━━━━━━━━━━━━
🆔 ID товара: {item_id}
"""

        keyboard = {
            "inline_keyboard": [[
                {"text": f"🛒 Купить за {price:,} ₽", "callback_data": f"buy_item_{item_id}"}
            ]]
        }

        print(f"📤 Пытаюсь отправить в канал маркетплейса: {MARKET_CHANNEL_ID}")

        # Отправляем в канал маркетплейса
        result = send_message(MARKET_CHANNEL_ID, channel_message,
                             reply_markup=keyboard, parse_mode="HTML")

        if result:
            print(f"📤 Результат отправки в канал: {result}")
            if result.get("ok"):
                item["channel_message_id"] = result["result"]["message_id"]
                print(f"✅ Сообщение отправлено в канал, ID: {result['result']['message_id']}")
            else:
                print(f"❌ Ошибка отправки в канал: {result.get('description')}")
        else:
            print("❌ Нет результата от send_message для канала")

        save_market_items(market_items)

        # Публикуем в группе
        group_message = f"""
🎉 НОВЫЙ ПОДАРОК НА МАРКЕТПЛЕЙСЕ!

{item_name}
📊 Редкость: {gift.get('rarity', 'Обычный')}

💰 Цена: {price:,} ₽
👤 Продавец: {user.get('first_name', 'Пользователь')}

👇 Нажмите кнопку ниже для покупки
"""

        print(f"📤 Пытаюсь отправить в группу: {MAIN_GROUP_ID}")

        # Публикуем в главной группе
        group_result = send_message(MAIN_GROUP_ID, group_message,
                                   reply_markup=keyboard, parse_mode="HTML")

        if group_result:
            print(f"📤 Результат отправки в группу: {group_result}")
            if group_result.get("ok"):
                item["group_message_id"] = group_result["result"]["message_id"]
                # Формируем ссылку на сообщение в группе
                group_id_str = str(MAIN_GROUP_ID)
                if group_id_str.startswith("-100"):
                    short_id = group_id_str[4:]  # Убираем "-100"
                else:
                    short_id = group_id_str
                item["group_message_link"] = f"https://t.me/c/{short_id}/{group_result['result']['message_id']}"
                print(f"✅ Сообщение отправлено в группу, ID: {group_result['result']['message_id']}")
                print(f"🔗 Ссылка: {item['group_message_link']}")
            else:
                print(f"❌ Ошибка отправки в группу: {group_result.get('description')}")
        else:
            print("❌ Нет результата от send_message для группы")

        save_market_items(market_items)

        # Отправляем подтверждение пользователю
        success_message = f"""
✅ **ПОДАРОК ВЫСТАВЛЕН НА ПРОДАЖУ!**

{gift_display}
📊 Редкость: {gift.get('rarity', 'Обычный')}
💰 Цена: {price:,} ₽

📢 Подарок опубликован в канале и группе.

💡 Товар будет автоматически удален после продажи.
"""

        send_message(message["chat"]["id"], success_message,
                     reply_to=message.get("message_id"), parse_mode="HTML")

        # Очищаем состояние
        del user_states[user_id]
        save_user_states(user_states)

        # Возвращаем в меню
        handle_start(data, {"from": message["from"], "chat": message["chat"]})

# ===== МУТ СИСТЕМА =====
MUTE_PRICE_PER_MINUTE = 100  # цена за 1 минуту мута
UNMUTE_PRICE = 500  # цена за размут

def handle_mute(data, message, args):
    """Мут пользователя за деньги"""
    user_id = str(message["from"]["id"])
    user = get_user(data, user_id)

    if "reply_to_message" not in message:
        send_message(message["chat"]["id"],
                    "❌ Ответьте на сообщение пользователя, которого хотите замутить!",
                    reply_to=message["message_id"])
        return

    if len(args) < 1:
        send_message(message["chat"]["id"],
                    f"❌ Укажите количество минут!\n\nПример: мут 10\nЦена: {MUTE_PRICE_PER_MINUTE} ₽ за минуту",
                    reply_to=message["message_id"])
        return

    try:
        minutes = int(args[0])
    except ValueError:
        send_message(message["chat"]["id"],
                    "❌ Укажите число минут! Пример: мут 5",
                    reply_to=message["message_id"])
        return

    if minutes <= 0:
        send_message(message["chat"]["id"],
                    "❌ Количество минут должно быть больше 0!",
                    reply_to=message["message_id"])
        return

    if minutes > 1440:  # максимум 24 часа (1440 минут)
        send_message(message["chat"]["id"],
                    "❌ Максимальное время мута - 24 часа!",
                    reply_to=message["message_id"])
        return

    # Рассчитываем стоимость
    total_price = minutes * MUTE_PRICE_PER_MINUTE

    if user["balance"] < total_price:
        send_message(message["chat"]["id"],
                    f"❌ Недостаточно средств!\nНужно: {total_price:,} ₽\nВаш баланс: {user['balance']:,} ₽",
                    reply_to=message["message_id"])
        return

    target_user = message["reply_to_message"]["from"]
    target_id = str(target_user["id"])

    if target_id == user_id:
        send_message(message["chat"]["id"],
                    "❌ Нельзя замутить самого себя!",
                    reply_to=message["message_id"])
        return

    # Проверяем, не является ли цель админом
    if is_admin(int(target_id)):
        send_message(message["chat"]["id"],
                    "❌ Нельзя замутить администратора!",
                    reply_to=message["message_id"])
        return

    update_user_info(data, target_id, target_user.get("username"),
                    target_user.get("first_name"))

    target = get_user(data, target_id)

    # Списываем деньги
    user["balance"] -= total_price

    # Добавляем деньги в казну
    if "treasury" not in data:
        data["treasury"] = 0
    data["treasury"] += total_price

    # Проверяем чат (должна быть группа)
    chat_id = message["chat"]["id"]
    chat_type = message["chat"].get("type")

    if chat_type not in ["group", "supergroup"]:
        send_message(message["chat"]["id"],
                    "❌ Мут можно использовать только в группах!",
                    reply_to=message["message_id"])
        # Возвращаем деньги
        user["balance"] += total_price
        data["treasury"] -= total_price
        save_data(data)
        return

    # Выполняем мут через API Telegram
    mute_until = int(time.time()) + (minutes * 60)

    url = f"https://api.telegram.org/bot{TOKEN}/restrictChatMember"
    payload = {
        "chat_id": chat_id,
        "user_id": int(target_id),
        "permissions": {
            "can_send_messages": False,
            "can_send_media_messages": False,
            "can_send_polls": False,
            "can_send_other_messages": False,
            "can_add_web_page_previews": False,
            "can_change_info": False,
            "can_invite_users": False,
            "can_pin_messages": False
        },
        "until_date": mute_until
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        result = response.json()

        if result.get("ok"):
            # Успешный мут
            save_data(data)

            user_emoji = get_user_emoji(user)
            target_emoji = get_user_emoji(target)
            target_name = format_user_mention(target, target_id)

            # Публикуем уведомление о муте
            mute_notification = f"""
🔇 ПОЛЬЗОВАТЕЛЬ ЗАМУЧЕН ЗА ДЕНЬГИ

{target_emoji} Пользователь: {target_name}
⏰ Время мута: {minutes} минут
💰 Стоимость: {total_price:,} ₽
💸 Оплатил: {user.get('first_name', 'Пользователь')}

⚠️ Пользователь не сможет писать в чат до {datetime.fromtimestamp(mute_until).strftime('%H:%M:%S')}
"""

            send_message(
                chat_id,
                mute_notification,
                reply_to=message["message_id"]
            )

            # Отправляем подтверждение в ЛС инициатору
            try:
                send_message(
                    user_id,
                    f"✅ Мут успешно выполнен!\n\n"
                    f"👤 Пользователь: {target_name}\n"
                    f"⏰ Время: {minutes} минут\n"
                    f"💰 Списано: {total_price:,} ₽\n"
                    f"💵 Ваш баланс: {user['balance']:,} ₽\n\n"
                    f"📢 Уведомление о муте отправлено в группу."
                )
            except:
                pass

            # Логируем в админ-канал
            try:
                log_message = f"""
🔇 МУТ ЗА ДЕНЬГИ

👤 Инициатор: {user.get('first_name', 'Пользователь')} (ID: {user_id})
👤 Цель: {target_name} (ID: {target_id})
⏰ Время: {minutes} минут
💰 Сумма: {total_price:,} ₽
📅 Время окончания: {datetime.fromtimestamp(mute_until).strftime('%d.%m.%Y %H:%M:%S')}
💬 Группа: {chat_id}
"""
                if ADMIN_CHAT_ID:
                    send_message(ADMIN_CHAT_ID, log_message)
            except:
                pass

        else:
            # Ошибка при муте
            error_desc = result.get("description", "Неизвестная ошибка")

            # Возвращаем деньги
            user["balance"] += total_price
            data["treasury"] -= total_price
            save_data(data)

            if "bot was kicked" in error_desc.lower() or "bot is not a member" in error_desc.lower():
                send_message(message["chat"]["id"],
                           "❌ Бот не является администратором в этой группе!",
                           reply_to=message["message_id"])
            elif "not enough rights" in error_desc.lower():
                send_message(message["chat"]["id"],
                           "❌ У бота недостаточно прав для мута!",
                           reply_to=message["message_id"])
            else:
                send_message(message["chat"]["id"],
                           f"❌ Ошибка при муте: {error_desc}",
                           reply_to=message["message_id"])

    except Exception as e:
        print(f"❌ Ошибка при выполнении мута: {e}", flush=True)
        # Возвращаем деньги при ошибке
        user["balance"] += total_price
        if "treasury" in data:
            data["treasury"] -= total_price
        save_data(data)

        send_message(message["chat"]["id"],
                    "❌ Произошла ошибка при муте. Попробуйте позже.",
                    reply_to=message["message_id"])

def handle_paid_unmute(data, message):
    """Размут пользователя за деньги"""
    user_id = str(message["from"]["id"])
    user = get_user(data, user_id)

    if "reply_to_message" not in message:
        send_message(message["chat"]["id"],
                    "❌ Ответьте на сообщение пользователя, которого хотите размутить!",
                    reply_to=message["message_id"])
        return

    # Проверяем стоимость (500₽)
    UNMUTE_PRICE = 500
    if user["balance"] < UNMUTE_PRICE:
        send_message(message["chat"]["id"],
                    f"❌ Недостаточно средств!\nНужно: {UNMUTE_PRICE:,} ₽\nВаш баланс: {user['balance']:,} ₽",
                    reply_to=message["message_id"])
        return

    target_user = message["reply_to_message"]["from"]
    target_id = str(target_user["id"])

    if target_id == user_id:
        send_message(message["chat"]["id"],
                    "❌ Нельзя размутить самого себя!",
                    reply_to=message["message_id"])
        return

    update_user_info(data, target_id, target_user.get("username"),
                    target_user.get("first_name"))

    target = get_user(data, target_id)

    # Проверяем, не является ли цель админом
    if is_admin(int(target_id)):
        send_message(message["chat"]["id"],
                    "❌ Администраторы не могут быть замучены!",
                    reply_to=message["message_id"])
        return

    # Списываем деньги
    user["balance"] -= UNMUTE_PRICE

    # Добавляем деньги в казну
    if "treasury" not in data:
        data["treasury"] = 0
    data["treasury"] += UNMUTE_PRICE

    # Проверяем чат (должна быть группа)
    chat_id = message["chat"]["id"]
    chat_type = message["chat"].get("type")

    if chat_type not in ["group", "supergroup"]:
        send_message(message["chat"]["id"],
                    "❌ Размут можно использовать только в группах!",
                    reply_to=message["message_id"])
        # Возвращаем деньги
        user["balance"] += UNMUTE_PRICE
        data["treasury"] -= UNMUTE_PRICE
        save_data(data)
        return

    # Выполняем размут через API Telegram
    url = f"https://api.telegram.org/bot{TOKEN}/restrictChatMember"
    payload = {
        "chat_id": chat_id,
        "user_id": int(target_id),
        "permissions": {
            "can_send_messages": True,
            "can_send_media_messages": True,
            "can_send_polls": True,
            "can_send_other_messages": True,
            "can_add_web_page_previews": True,
            "can_change_info": False,
            "can_invite_users": False,
            "can_pin_messages": False
        }
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        result = response.json()

        if result.get("ok"):
            # Успешный размут
            save_data(data)

            user_emoji = get_user_emoji(user)
            target_emoji = get_user_emoji(target)
            target_name = format_user_mention(target, target_id)

            # Публикуем уведомление о размуте
            unmute_notification = f"""
🔊 ПОЛЬЗОВАТЕЛЬ РАЗМУЧЕН ЗА ДЕНЬГИ

{target_emoji} Пользователь: {target_name}
💸 Оплатил: {user.get('first_name', 'Пользователь')}
💰 Стоимость размута: {UNMUTE_PRICE:,} ₽

✅ Теперь пользователь может писать в чат!
            """

            send_message(
                chat_id,
                unmute_notification,
                reply_to=message["message_id"]
            )

            # Отправляем подтверждение в ЛС инициатору
            try:
                send_message(
                    user_id,
                    f"✅ Размут успешно выполнен!\n\n"
                    f"👤 Пользователь: {target_name}\n"
                    f"💰 Списано: {UNMUTE_PRICE:,} ₽\n"
                    f"💵 Ваш баланс: {user['balance']:,} ₽\n\n"
                    f"📢 Уведомление о размуте отправлено в группу."
                )
            except:
                pass

            # Логируем в админ-канал
            try:
                log_message = f"""
🔊 РАЗМУТ ЗА ДЕНЬГИ

👤 Инициатор: {user.get('first_name', 'Пользователь')} (ID: {user_id})
👤 Цель: {target_name} (ID: {target_id})
💰 Сумма: {UNMUTE_PRICE:,} ₽
📅 Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
💬 Группа: {chat_id}
"""
                if ADMIN_CHAT_ID:
                    send_message(ADMIN_CHAT_ID, log_message)
            except:
                pass

        else:
            # Ошибка при размуте
            error_desc = result.get("description", "Неизвестная ошибка")

            # Возвращаем деньги
            user["balance"] += UNMUTE_PRICE
            data["treasury"] -= UNMUTE_PRICE
            save_data(data)

            if "bot was kicked" in error_desc.lower() or "bot is not a member" in error_desc.lower():
                send_message(message["chat"]["id"],
                           "❌ Бот не является администратором в этой группе!",
                           reply_to=message["message_id"])
            elif "not enough rights" in error_desc.lower():
                send_message(message["chat"]["id"],
                           "❌ У бота недостаточно прав для размута!",
                           reply_to=message["message_id"])
            else:
                # Проверяем, не размучен ли уже пользователь
                if "CHAT_NOT_MODIFIED" in error_desc:
                    send_message(message["chat"]["id"],
                               "❌ Пользователь уже не замучен!",
                               reply_to=message["message_id"])
                else:
                    send_message(message["chat"]["id"],
                               f"❌ Ошибка при размуте: {error_desc}",
                               reply_to=message["message_id"])

    except Exception as e:
        print(f"❌ Ошибка при выполнении размута: {e}", flush=True)
        # Возвращаем деньги при ошибке
        user["balance"] += UNMUTE_PRICE
        if "treasury" in data:
            data["treasury"] -= UNMUTE_PRICE
        save_data(data)

        send_message(message["chat"]["id"],
                    "❌ Произошла ошибка при размуте. Попробуйте позже.",
                    reply_to=message["message_id"])

def handle_self_unmute(data, message):
    """Размутить себя за деньги (только в ЛС)"""
    user_id = str(message["from"]["id"])
    user = get_user(data, user_id)

    # Проверяем, что это ЛС
    chat_type = message.get("chat", {}).get("type")
    if chat_type != "private":
        send_message(message["chat"]["id"],
                     "❌ Размут себя доступен только в личных сообщениях с ботом!\n"
                     f"Перейдите в ЛС: @{BOT_USERNAME}",
                     reply_to=message["message_id"])
        return

    # Проверяем стоимость
    if user["balance"] < SELF_UNMUTE_PRICE:
        send_message(message["chat"]["id"],
                     f"❌ Недостаточно средств!\n"
                     f"Нужно: {SELF_UNMUTE_PRICE:,} ₽\n"
                     f"Ваш баланс: {user['balance']:,} ₽",
                     reply_to=message["message_id"])
        return

    # Получаем информацию о пользователе для уведомления в группах
    user_emoji = get_user_emoji(user)
    user_name = user.get("first_name", "Пользователь")
    user_tg_id = int(user_id)  # ID пользователя для Telegram API

    # Списываем деньги
    user["balance"] -= SELF_UNMUTE_PRICE

    # Добавляем деньги в казну
    if "treasury" not in data:
        data["treasury"] = 0
    data["treasury"] += SELF_UNMUTE_PRICE

    save_data(data)

    # ОТПРАВЛЯЕМ СООБЩЕНИЕ В ГРУППУ ПЕРЕД РАЗМУТОМ
    group_notification = f"""
🔊 ═══ АВТО-РАЗМУТ ═══ 🔊

{user_emoji} Пользователь: {user_name}
💸 Оплатил за размут: {SELF_UNMUTE_PRICE:,} ₽
📅 Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}

⏳ Идет процесс размута...
"""

    # Отправляем в главную группу
    group_message = None
    try:
        group_message = send_message(MAIN_GROUP_ID, group_notification)
    except Exception as e:
        print(f"❌ Не удалось отправить уведомление в группу: {e}")

    # ВЫПОЛНЯЕМ ФАКТИЧЕСКИЙ РАЗМУТ В ГРУППЕ
    unmute_success = False

    try:
        # Выполняем размут через API Telegram
        url = f"https://api.telegram.org/bot{TOKEN}/restrictChatMember"
        payload = {
            "chat_id": MAIN_GROUP_ID,
            "user_id": user_tg_id,
            "permissions": {
                "can_send_messages": True,
                "can_send_media_messages": True,
                "can_send_polls": True,
                "can_send_other_messages": True,
                "can_add_web_page_previews": True,
                "can_change_info": False,
                "can_invite_users": False,
                "can_pin_messages": False
            }
        }

        response = requests.post(url, json=payload, timeout=30)
        result = response.json()

        if result.get("ok"):
            unmute_success = True
            print(f"✅ Успешный размут пользователя {user_name} (ID: {user_id}) в группе")
        else:
            error_desc = result.get("description", "Неизвестная ошибка")
            if "CHAT_NOT_MODIFIED" in error_desc:
                # Пользователь уже не замучен - это тоже успех
                unmute_success = True
                print(f"ℹ️ Пользователь {user_name} уже не замучен в группе")
            else:
                print(f"❌ Ошибка размута: {error_desc}")
                print(f"   Ответ API: {result}")

    except Exception as e:
        print(f"❌ Ошибка при размуте: {e}")
        import traceback
        traceback.print_exc()

    # ОБНОВЛЯЕМ СООБЩЕНИЕ В ГРУППЕ
    if unmute_success:
        final_group_message = f"""
🔊 ═══ АВТО-РАЗМУТ УСПЕШЕН ═══ 🔊

{user_emoji} Пользователь: {user_name}
💸 Оплатил за размут: {SELF_UNMUTE_PRICE:,} ₽
📅 Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}

✅ Пользователь успешно размучен!
💡 Теперь он может свободно общаться в чате.
"""

        if group_message and group_message.get("ok"):
            try:
                edit_message(MAIN_GROUP_ID, group_message["result"]["message_id"], final_group_message)
            except:
                # Если не удалось отредактировать, отправляем новое
                send_message(MAIN_GROUP_ID, final_group_message)
        else:
            # Если первое сообщение не отправилось, отправляем новое
            send_message(MAIN_GROUP_ID, final_group_message)

    else:
        # Если размут не удался, удаляем сообщение из группы и возвращаем деньги
        if group_message and group_message.get("ok"):
            try:
                delete_message(MAIN_GROUP_ID, group_message["result"]["message_id"])
            except:
                pass

        # Возвращаем деньги
        user["balance"] += SELF_UNMUTE_PRICE
        data["treasury"] -= SELF_UNMUTE_PRICE
        save_data(data)

    # СООБЩЕНИЕ ПОЛЬЗОВАТЕЛЮ В ЛС
    if unmute_success:
        success_message = f"""
{user_emoji} ═══ РАЗМУТ СЕБЯ УСПЕШЕН ═══ {user_emoji}

✅ Вы успешно размучены!

💰 Списано: {SELF_UNMUTE_PRICE:,} ₽
💵 Ваш баланс: {user['balance']:,} ₽

📢 Уведомление отправлено в группу.
🔓 Теперь вы можете писать в чате проекта!
"""
    else:
        success_message = f"""
{user_emoji} ═══ РАЗМУТ НЕ УДАЛСЯ ═══ {user_emoji}

❌ Не удалось выполнить размут!

⚠️ Возможные причины:
1. Бот не администратор в группе
2. У бота недостаточно прав
3. Технические проблемы

💸 Деньги возвращены на баланс
💰 Ваш баланс: {user['balance']:,} ₽

🔄 Попробуйте позже или обратитесь к администратору.
"""

    send_message(message["chat"]["id"], success_message,
                 reply_to=message["message_id"], parse_mode="Markdown")

    # Логируем в админ-канал
    try:
        if unmute_success:
            log_message = f"""
🔊 АВТО-РАЗМУТ СЕБЯ (УСПЕХ)

👤 Пользователь: {user_name} (ID: {user_id})
💰 Сумма: {SELF_UNMUTE_PRICE:,} ₽
📅 Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}

✅ Пользователь самостоятельно оплатил размут через ЛС бота.
"""
        else:
            log_message = f"""
🔊 АВТО-РАЗМУТ СЕБЯ (ОШИБКА)

👤 Пользователь: {user_name} (ID: {user_id})
💰 Сумма: {SELF_UNMUTE_PRICE:,} ₽ (возвращены)
📅 Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
❌ Ошибка: Не удалось выполнить размут

⚠️ Пользователь пытался размутиться, но возникли проблемы.
"""

        if ADMIN_CHAT_ID:
            send_message(ADMIN_CHAT_ID, log_message)
    except Exception as e:
        print(f"❌ Не удалось отправить логи админам: {e}")

def handle_admin_unmute(data, message):
    """Размут пользователя (бесплатно для админов)"""
    if not is_admin(message["from"]["id"]):
        send_message(message["chat"]["id"],
                    "❌ Только для админов!",
                    reply_to=message["message_id"])
        return

    if "reply_to_message" not in message:
        send_message(message["chat"]["id"],
                    "❌ Ответьте на сообщение пользователя!",
                    reply_to=message["message_id"])
        return

    target_user = message["reply_to_message"]["from"]
    target_id = str(target_user["id"])

    update_user_info(data, target_id, target_user.get("username"),
                    target_user.get("first_name"))

    target = get_user(data, target_id)

    # Проверяем чат (должна быть группа)
    chat_id = message["chat"]["id"]
    chat_type = message["chat"].get("type")

    if chat_type not in ["group", "supergroup"]:
        send_message(message["chat"]["id"],
                    "❌ Размут можно использовать только в группах!",
                    reply_to=message["message_id"])
        return

    # Выполняем размут через API Telegram
    url = f"https://api.telegram.org/bot{TOKEN}/restrictChatMember"
    payload = {
        "chat_id": chat_id,
        "user_id": int(target_id),
        "permissions": {
            "can_send_messages": True,
            "can_send_media_messages": True,
            "can_send_polls": True,
            "can_send_other_messages": True,
            "can_add_web_page_previews": True,
            "can_change_info": False,
            "can_invite_users": False,
            "can_pin_messages": False
        }
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        result = response.json()

        if result.get("ok"):
            target_emoji = get_user_emoji(target)
            target_name = format_user_mention(target, target_id)
            admin_user = get_user(data, str(message["from"]["id"]))
            admin_emoji = get_user_emoji(admin_user)

            send_message(
                message["chat"]["id"],
                f"{admin_emoji} 🔊 {target_emoji}\n✅ Администратор размутил пользователя!\n\n"
                f"👤 Пользователь: {target_name}",
                reply_to=message["message_id"]
            )

        else:
            error_desc = result.get("description", "Неизвестная ошибка")

            if "bot was kicked" in error_desc.lower() or "bot is not a member" in error_desc.lower():
                send_message(message["chat"]["id"],
                           "❌ Бот не является администратором в этой группе!",
                           reply_to=message["message_id"])
            elif "not enough rights" in error_desc.lower():
                send_message(message["chat"]["id"],
                           "❌ У бота недостаточно прав для размута!",
                           reply_to=message["message_id"])
            elif "CHAT_NOT_MODIFIED" in error_desc:
                send_message(message["chat"]["id"],
                           "❌ Пользователь уже не замучен!",
                           reply_to=message["message_id"])
            else:
                send_message(message["chat"]["id"],
                           f"❌ Ошибка при размуте: {error_desc}",
                           reply_to=message["message_id"])

    except Exception as e:
        print(f"❌ Ошибка при выполнении размута: {e}", flush=True)
        send_message(message["chat"]["id"],
                    "❌ Произошла ошибка при размуте. Попробуйте позже.",
                    reply_to=message["message_id"])

def handle_mute_info(data, message):
    """Информация о системе мута"""
    user_id = str(message["from"]["id"])
    user = get_user(data, user_id)
    user_emoji = get_user_emoji(user)

    info_text = f"""
{user_emoji} ═══ СИСТЕМА МУТА И РАЗМУТА ═══ {user_emoji}

🔇 **МУТ пользователя за деньги:**
• 1 минута мута = {MUTE_PRICE_PER_MINUTE} ₽
• 1 час (60 минут) = {MUTE_PRICE_PER_MINUTE * 60:,} ₽
• 24 часа (1440 минут) = {MUTE_PRICE_PER_MINUTE * 1440:,} ₽

🔊 **РАЗМУТ пользователя:**
• Размут любого пользователя = 500 ₽
• Для администраторов размут бесплатный

📝 **Как использовать:**
1. **Мут:** Ответьте на сообщение командой `мут [минуты]`
   Пример: `мут 10` (замутит на 10 минут за {MUTE_PRICE_PER_MINUTE * 10} ₽)

2. **Размут:** Ответьте на сообщение командой `размут`
   Стоимость: 500 ₽

⚡ **Особенности:**
• Деньги списываются с вашего баланса
• 100% от суммы идет в казну проекта
• Работает только в группах, где бот - администратор
• Нельзя мутить/размутить администраторов
• Нельзя мутить/размутить самого себя
• Макс. время мута - 24 часа

💡 **Советы:**
• Проверьте права бота в группе перед использованием
• Убедитесь, что у вас достаточно средств
• После мута публикуется уведомление в группу
• Размут работает даже если мут был выдан другим пользователем

🎮 **Примеры использования:**
1. Замутить пользователя на 30 минут:
   `мут 30` → стоимость: {MUTE_PRICE_PER_MINUTE * 30} ₽

2. Размутить пользователя:
   `размут` → стоимость: 500 ₽

3. Администратор может размутить бесплатно:
   `размут` → бесплатно

⚠️ **Внимание:** Работает только в группах!
"""

    send_message(message["chat"]["id"], info_text, reply_to=message["message_id"], parse_mode="Markdown")

def handle_check_mute_status(data, message):
    """Проверить статус пользователя (замучен или нет)"""
    if "reply_to_message" not in message:
        send_message(message["chat"]["id"],
                    "❌ Ответьте на сообщение пользователя, чтобы проверить его статус!",
                    reply_to=message["message_id"])
        return

    target_user = message["reply_to_message"]["from"]
    target_id = str(target_user["id"])

    update_user_info(data, target_id, target_user.get("username"),
                    target_user.get("first_name"))

    target = get_user(data, target_id)
    target_emoji = get_user_emoji(target)
    target_name = format_user_mention(target, target_id)

    # Отправляем информацию о пользователе
    user_info = f"""
{target_emoji} ═══ ИНФОРМАЦИЯ О ПОЛЬЗОВАТЕЛЕ ═══ {target_emoji}

👤 Пользователь: {target_name}
🆔 ID: {target_id}
💰 Баланс: {target.get('balance', 0):,} ₽
🎁 Подарков: {len(target.get('gifts', []))}
🏢 Бизнес: {BUSINESS_LEVELS.get(target.get('business_level', 0), {}).get('name', 'Нет бизнеса')}

💡 **Статус в группе:**
• Бот не может проверить технический статус мута через API
• Для проверки статуса попробуйте:
  1. Мутнуть пользователя (система сама проверит статус)
  2. Размутить пользователя (система проверит, замучен ли он)

⚡ **Доступные действия:**
• Мут: `мут [минуты]` - {MUTE_PRICE_PER_MINUTE} ₽/мин
• Размут: `размут` - 500 ₽

📊 **Статистика пользователя:**
• Пополнено: {target.get('total_deposited', 0):,} ₽
• Выведено: {target.get('total_withdrawn', 0):,} ₽
• В казино: {target.get('stats', {}).get('casino_wins', 0):,} ₽
• Продаж: {target.get('stats', {}).get('items_sold', 0)}
"""

    send_message(message["chat"]["id"], user_info, reply_to=message["message_id"], parse_mode="Markdown")

def process_message(data, message):
    if "text" not in message:
        # Проверяем, не ожидаем ли мы ввода данных
        user_id = str(message["from"]["id"])
        user_states = load_user_states()
        if user_id in user_states:
            state = user_states[user_id].get("state")
            if state in ["waiting_for_item_name", "waiting_for_item_description",
                        "waiting_for_item_content", "waiting_for_item_price",
                        "waiting_for_gift_price"]:
                # Пользователь что-то отправил (может быть фото и т.д.)
                send_message(message["chat"]["id"], "❌ Пожалуйста, отправьте только текст!")
        return

    text = message["text"].strip()

    # ===== ВАЖНО: СНАЧАЛА ПРОВЕРЯЕМ ВВОД ЦЕНЫ ДЛЯ ПОДАРКА =====
    user_id = str(message["from"]["id"])
    user_states = load_user_states()
    if user_id in user_states:
        state = user_states[user_id].get("state")
        if state == "waiting_for_gift_price":
            # Это ввод цены для подарка - обрабатываем сразу
            handle_price_input(data, message)
            return
    # ===== КОНЕЦ ПРОВЕРКИ ВВОДА ЦЕНЫ =====

    parts = text.split()
    command = parts[0].lower() if parts else ""
    args = parts[1:] if len(parts) > 1 else []

    user_id = message["from"]["id"]
    username = message["from"].get("username", "no_username")
    print(f"📩 Сообщение от {username} (ID: {user_id}): {text}", flush=True)

    update_user_info(data, user_id, message["from"].get("username"),
                     message["from"].get("first_name"))

    # ===== КОМАНДА "КЛИК" =====
    if command == "клик":
        if message.get("chat", {}).get("type") == "private":
            # Это личные сообщения - начисляем 1₽
            user = get_user(data, user_id)
            user["balance"] += 5
            save_data(data)

            user_emoji = get_user_emoji(user)
            send_message(message["chat"]["id"],
                        f"{user_emoji} ✅ +5\n💰 Ваш баланс: {user['balance']:,} ₽",
                        reply_to=message.get("message_id"))
        else:
            # Это группа - удаляем сообщение
            try:
                delete_message(message["chat"]["id"], message["message_id"])
                send_message(message["chat"]["id"],
                           "❌ Команда 'клик' работает только в личных сообщениях с ботом!",
                           reply_to=message.get("message_id"))
            except:
                pass
        return

    # Проверяем, не ожидаем ли мы ввода данных для товара
    user_states = load_user_states()
    if str(user_id) in user_states:
        state = user_states[str(user_id)].get("state")
        if state in ["waiting_for_item_name", "waiting_for_item_description",
                    "waiting_for_item_content", "waiting_for_item_price"]:
            handle_item_input(data, message)
            return
        # УБРАЛИ проверку waiting_for_gift_price здесь, так как она уже выше

    # Проверка на промокод (8 символов, буквы и цифры)
    if len(text) == 8 and text.isalnum() and text.isupper():
        handle_use_promo_code(data, message, [text])
        return

    # ===== КОМАНДЫ, КОТОРЫЕ РАБОТАЮТ ТОЛЬКО В ЛС =====
    chat_type = message.get("chat", {}).get("type")
    lsonly_commands = [
        "старт", "начать", "передать", "transfer", "продать", "sell",
        "подарки", "gifts", "маркетплейс", "market", "магазин",
        "новыйтовар", "создатьтовар", "sellitem", "ввести", "активировать",
        "activate", "пополнить", "депозит", "deposit", "моипокупки",
        "my_purchases", "моитовары", "my_items"
    ]

    if command in lsonly_commands and chat_type != "private":
        send_message(
            message["chat"]["id"],
            f"⚠️ Команда работает только в личных сообщениях!\n\n"
            f"Перейдите в ЛС с ботом: @{BOT_USERNAME}",
            reply_to=message.get("message_id"),
            parse_mode="Markdown"
        )
        return

    # ===== ОБЫЧНЫЕ КОМАНДЫ (РАБОТАЮТ ВЕЗДЕ) =====
    if command in ["/start", "старт", "начать"]:
        handle_start(data, message)
    elif command in ["профиль", "profile", "п"]:
        handle_profile(data, message)
    elif command in ["баланс", "balance", "б"]:
        handle_balance(data, message)
    elif command in ["подарить", "give"]:
        handle_gift_give(data, message, args)
    elif command in ["передать", "transfer"]:
        handle_gift_transfer(data, message, args)
    elif command in ["продать", "sell"]:
        handle_gift_sell(data, message, args)
    elif command in ["подарки", "gifts"]:
        handle_gifts_list(data, message)
    elif command == "/admin":
        handle_admin(data, message)
    elif command in ["/stats", "стата", "статистика"]:
        handle_stats(data, message)
    elif command in ["выдать", "give_money"]:
        handle_give_money(data, message, args)
    elif command in ["забрать", "take_money"]:
        handle_take_money(data, message, args)
    elif command in ["дать", "give_to"]:
        handle_transfer_money(data, message, args)
    elif command in ["/help", "помощь", "команды"]:
        handle_help(data, message)
    elif command in ["казино", "casino"]:
        handle_casino(data, message)
    elif command in ["слоты", "slots", "слот"]:
        handle_slots(data, message, args)
    elif command in ["монетка", "coin", "coinflip"]:
        handle_coinflip(data, message, args)
    elif command in ["кости", "dice", "кость"]:
        handle_dice(data, message, args)
    elif command in ["рулетка", "roulette"]:
        handle_roulette(data, message, args)
    elif command in ["бизнес", "business"]:
        handle_business(data, message)
    elif command in ["купить"]:
        if len(args) > 0:
            if args[0] in ["бизнес", "business"]:
                handle_buy_business(data, message)
            elif args[0] in ["бустер", "booster"] and len(args) > 1:
                handle_buy_booster(data, message, args[1:])
            elif args[0] in ["улучшение", "upgrade"] and len(args) > 1:
                handle_buy_upgrade(data, message, args[1:])
    elif command in ["улучшить"]:
        if len(args) > 0 and args[0] in ["бизнес", "business"]:
            handle_upgrade_business(data, message)
    elif command in ["доход", "income"]:
        handle_collect_income(data, message)
    elif command == "/biz":
        handle_admin_biz(data, message, args)
    elif command in ["бонус", "bonus"]:
        handle_bonus(data, message)
    elif command in ["ограбить"]:
        if len(args) > 0 and args[0] in ["казну", "казна", "treasury"]:
            handle_rob_treasury(data, message)
    elif command in ["казна", "treasury"]:
        handle_treasury(data, message)
    elif command in ["объявление", "announcement"]:
        handle_announcement(data, message)
    elif command in ["шансы", "настройки", "settings"]:
        handle_chance_settings(data, message)
    elif command in ["шанс", "chance"]:
        handle_set_chance(data, message, args)
    elif command in ["пополнить", "депозит", "deposit"]:
        handle_deposit_info(data, message)
    elif command in ["ввести", "активировать", "activate"]:
        if len(args) > 0 and args[0] in ["код", "code"]:
            handle_use_promo_code(data, message, args[1:] if len(args) > 1 else [])
    elif command in ["создать"]:
        if len(args) > 0 and args[0] in ["код", "code"]:
            handle_create_promo_code(data, message, args[1:] if len(args) > 1 else [])
    elif command in ["список"]:
        if len(args) > 0 and args[0] in ["кодов", "codes"]:
            handle_list_promo_codes(data, message)
    elif command in ["бустеры", "boosters", "бустер"]:
        handle_boosters_shop(data, message)
    elif command in ["моибустеры", "myboosters", "моибустер"]:
        handle_my_boosters(data, message)
    elif command in ["улучшения", "upgrades", "улучшение"]:
        handle_upgrades_shop(data, message)
    elif command in ["моиулучшения", "myupgrades", "моиулучшение"]:
        handle_my_upgrades(data, message)
    elif command in ["достижения", "achievements", "достижение"]:
        handle_achievements(data, message)
    elif command in ["секрет", "secret"]:
        handle_secret_command(data, message)
    elif command in ["маркетплейс", "market", "магазин"]:
        # Открываем меню маркетплейса через /start
        handle_start(data, message)

    # ===== НОВЫЕ БИЗНЕС-КОМАНДЫ =====
    elif command in ["бизнес_список", "бизнесы", "business_list", "businesses"]:
        handle_business_list(data, message)
    elif command in ["бизнес_инфо", "business_info"]:
        handle_business_info_detail(data, message, args)

    # ===== НОВЫЕ КОМАНДЫ СТАТУСОВ =====
    elif command in ["статус", "status"]:
        if len(args) > 0:
            if args[0] in ["сброс", "reset"] and is_admin(message["from"]["id"]):
                handle_reset_status(data, message)
            elif is_admin(message["from"]["id"]):
                handle_set_status(data, message, args)
            else:
                send_message(message["chat"]["id"],
                            "❌ Только админы могут устанавливать статусы!",
                            reply_to=message["message_id"])
        else:
            handle_show_status(data, message)
    elif command in ["мойстатус", "mystatus"]:
        handle_my_status(data, message)

    # ===== АДМИНСКИЕ КОМАНДЫ АВТО-СБОРА =====
    elif command in ["автосбор", "autocollect"] and is_admin(user_id):
        handle_admin_auto_collect(data, message, args)
    elif command in ["автостата", "autostats", "статаавто"] and is_admin(user_id):
        handle_admin_auto_stats(data, message)

    # ===== НОВЫЕ КОМАНДЫ ДЛЯ АДМИНОВ =====
    elif command in ["выдать", "give"] and len(args) > 0:
        if args[0] in ["бустер", "booster"]:
            handle_give_booster(data, message, args[1:] if len(args) > 1 else [])
        elif args[0] in ["улучшение", "upgrade"]:
            handle_give_upgrade(data, message, args[1:] if len(args) > 1 else [])
    elif command in ["забрать", "take"] and len(args) > 0:
        if args[0] in ["бустер", "booster"]:
            handle_take_booster(data, message, args[1:] if len(args) > 1 else [])
        elif args[0] in ["улучшение", "upgrade"]:
            handle_take_upgrade(data, message, args[1:] if len(args) > 1 else [])
    elif command in ["показать", "show"] and len(args) > 0:
        if args[0] in ["бустеры", "boosters"]:
            handle_show_user_boosters(data, message)

    # ===== КОМАНДЫ МУТА И РАЗМУТА =====
    elif command in ["мут", "mute"]:
        handle_mute(data, message, args)
    elif command in ["размут", "unmute"]:
        # Если админ - бесплатный размут, иначе платный
        if is_admin(message["from"]["id"]):
            handle_admin_unmute(data, message)
        else:
            handle_paid_unmute(data, message)
    elif command in ["размутсебя", "саморозмут", "self_unmute", "размут_себя"]:
        handle_self_unmute(data, message)
    elif command in ["статус_мута", "mute_status", "проверить_мут", "check_mute"]:
        handle_check_mute_status(data, message)
    elif command in ["инфо_мут", "mute_info", "мут_инфо"]:
        handle_mute_info(data, message)
    # ===== АДМИНСКИЕ КОМАНДЫ ИВЕНТА =====
    if command in ["/event_start", "ивент_старт"] and is_admin(user_id):
        handle_admin_event_start(data, message, args)
    elif command in ["/event_stop", "ивент_стоп"] and is_admin(user_id):
        handle_admin_event_stop(data, message, args)
    elif command in ["/event_status", "ивент_статус"] and is_admin(user_id):
        handle_admin_event_status(data, message)
    elif command in ["/event_reset", "ивент_сброс"] and is_admin(user_id):
        handle_admin_event_reset(data, message, args)
    elif command in ["/event_add", "ивент_дать"] and is_admin(user_id):
        handle_admin_event_add_points(data, message, args)
    
    # ===== ОБЫЧНЫЕ КОМАНДЫ ИВЕНТА =====
    elif command in ["ивент", "23февраля", "защитник"]:
        handle_event_status(data, message)
    elif command in ["топ_ивент", "топ"]:
        handle_event_top(data, message)
    # ===== НОВЫЕ КОМАНДЫ КЕЙСА =====
    elif command in ["кейс", "case", "чекейс"]:
        handle_case_command(data, message)
    elif command in ["открытькейс", "открыть_кейс", "open_case", "откройкейс"]:
        handle_open_case_command(data, message)
    elif command in ["мойкейс", "mycase", "статускейса", "статус_кейса"]:
        handle_my_case_command(data, message)

def handle_self_unmute(data, message):
    """Размутить себя за деньги (только в ЛС)"""
    user_id = str(message["from"]["id"])
    user = get_user(data, user_id)

    # Проверяем, что это ЛС
    chat_type = message.get("chat", {}).get("type")
    if chat_type != "private":
        send_message(message["chat"]["id"],
                     "❌ Размут себя доступен только в личных сообщениях с ботом!\n"
                     f"Перейдите в ЛС: @{BOT_USERNAME}",
                     reply_to=message["message_id"])
        return

    # Проверяем стоимость
    if user["balance"] < SELF_UNMUTE_PRICE:
        send_message(message["chat"]["id"],
                     f"❌ Недостаточно средств!\n"
                     f"Нужно: {SELF_UNMUTE_PRICE:,} ₽\n"
                     f"Ваш баланс: {user['balance']:,} ₽",
                     reply_to=message["message_id"])
        return

    # Получаем информацию о пользователе для уведомления в группах
    user_emoji = get_user_emoji(user)
    user_name = user.get("first_name", "Пользователь")

    # Списываем деньги
    user["balance"] -= SELF_UNMUTE_PRICE

    # Добавляем деньги в казну
    if "treasury" not in data:
        data["treasury"] = 0
    data["treasury"] += SELF_UNMUTE_PRICE

    save_data(data)

    # Отправляем сообщение пользователю
    send_message(message["chat"]["id"],
                 f"{user_emoji} ═══ РАЗМУТ СЕБЯ ═══ {user_emoji}\n\n"
                 f"✅ Вы успешно размутили себя!\n\n"
                 f"💰 Списано: {SELF_UNMUTE_PRICE:,} ₽\n"
                 f"💵 Ваш баланс: {user['balance']:,} ₽\n\n"
                 f"⚠️ **Внимание:** Эта команда не снимает технические муты!\n"
                 f"Она предназначена для восстановления репутации в проекте.\n\n"
                 f"📢 Объявление о вашем размуте отправлено в группу.",
                 reply_to=message["message_id"],
                 parse_mode="Markdown")

    # Отправляем уведомление в группу
    group_notification = f"""
🔊 ═══ АВТО-РАЗМУТ ═══ 🔊

{user_emoji} Пользователь: {user_name}
💸 Оплатил за размут: {SELF_UNMUTE_PRICE:,} ₽
📅 Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}

✅ Пользователь сам оплатил размут через бота!
💡 Теперь он может свободно общаться в чате.
"""

    # Отправляем в главную группу
    try:
        send_message(MAIN_GROUP_ID, group_notification)
    except Exception as e:
        print(f"❌ Не удалось отправить уведомление в группу: {e}")

    # Логируем в админ-канал
    try:
        log_message = f"""
🔊 АВТО-РАЗМУТ СЕБЯ

👤 Пользователь: {user_name} (ID: {user_id})
💰 Сумма: {SELF_UNMUTE_PRICE:,} ₽
📅 Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}

✅ Пользователь самостоятельно оплатил размут через ЛС бота.
"""
        if ADMIN_CHAT_ID:
            send_message(ADMIN_CHAT_ID, log_message)
    except Exception as e:
        print(f"❌ Не удалось отправить логи админам: {e}")

def cleanup_expired_boosters(data):
    """Очистка истекших бустеров"""
    now = datetime.now()
    cleaned_count = 0

    for user_id, user in data["users"].items():
        active_boosters = user.get("active_boosters", {})
        expired_boosters = []

        for booster_id, expires_at_str in active_boosters.items():
            try:
                expires_at = datetime.fromisoformat(expires_at_str)
                if expires_at <= now:
                    expired_boosters.append(booster_id)
            except:
                expired_boosters.append(booster_id)

        for booster_id in expired_boosters:
            del active_boosters[booster_id]
            cleaned_count += 1

    if cleaned_count > 0:
        save_data(data)
        print(f"🧹 Очищено {cleaned_count} истекших бустеров")

    return cleaned_count

# ===== TIC-TAC-TOE GAME SYSTEM =====
TIC_TAC_TOE_GAMES_FILE = "tic_tac_toe_games.json"
TIC_TAC_TOE_TIMEOUT = 60  # 1 минута на ход

class TicTacToeGame:
    def __init__(self, game_id, player1_id, player2_id, bet_amount, chat_id):
        self.game_id = game_id
        self.player1_id = str(player1_id)
        self.player2_id = str(player2_id)
        self.bet_amount = bet_amount
        self.chat_id = chat_id
        self.board = [[" " for _ in range(3)] for _ in range(3)]
        self.current_player = player1_id  # X начинает
        self.player_symbols = {player1_id: "❌", player2_id: "⭕️"}
        self.status = "waiting_accept"  # waiting_accept, active, finished
        self.winner = None
        self.moves = []
        self.start_time = datetime.now()
        self.last_move_time = datetime.now()
        self.message_id = None
        self.is_draw = False
        self.player1_accepted = False
        self.player2_accepted = False
        self.empty_cell_char = "ㅤ"  # Невидимый символ для кнопок

    def to_dict(self):
        return {
            "game_id": self.game_id,
            "player1_id": self.player1_id,
            "player2_id": self.player2_id,
            "bet_amount": self.bet_amount,
            "chat_id": self.chat_id,
            "board": self.board,
            "current_player": str(self.current_player),
            "player_symbols": {k: v for k, v in self.player_symbols.items()},
            "status": self.status,
            "winner": str(self.winner) if self.winner else None,
            "moves": self.moves,
            "start_time": self.start_time.isoformat(),
            "last_move_time": self.last_move_time.isoformat(),
            "message_id": self.message_id,
            "is_draw": self.is_draw,
            "player1_accepted": self.player1_accepted,
            "player2_accepted": self.player2_accepted,
            "empty_cell_char": self.empty_cell_char
        }

    @classmethod
    def from_dict(cls, data):
        game = cls(
            data["game_id"],
            int(data["player1_id"]),
            int(data["player2_id"]),
            data["bet_amount"],
            data["chat_id"]
        )
        game.board = data["board"]
        game.current_player = int(data["current_player"])
        game.player_symbols = {int(k): v for k, v in data["player_symbols"].items()}
        game.status = data["status"]
        game.winner = int(data["winner"]) if data["winner"] else None
        game.moves = data["moves"]
        game.start_time = datetime.fromisoformat(data["start_time"])
        game.last_move_time = datetime.fromisoformat(data["last_move_time"])
        game.message_id = data["message_id"]
        game.is_draw = data["is_draw"]
        game.player1_accepted = data["player1_accepted"]
        game.player2_accepted = data["player2_accepted"]
        game.empty_cell_char = data.get("empty_cell_char", "ㅤ")
        return game

# ===== TIC-TAC-TOE FUNCTIONS =====
def load_tic_tac_toe_games():
    if os.path.exists(TIC_TAC_TOE_GAMES_FILE):
        try:
            with open(TIC_TAC_TOE_GAMES_FILE, 'r', encoding='utf-8') as f:
                games_data = json.load(f)
                return {game_id: TicTacToeGame.from_dict(data) for game_id, data in games_data.items()}
        except:
            pass
    return {}

def save_tic_tac_toe_games(games):
    games_data = {game_id: game.to_dict() for game_id, game in games.items()}
    with open(TIC_TAC_TOE_GAMES_FILE, 'w', encoding='utf-8') as f:
        json.dump(games_data, f, ensure_ascii=False, indent=2)

def create_game_keyboard(game):
    """Создать клавиатуру с игровым полем 3x3"""
    keyboard_rows = []

    for i in range(3):
        row_buttons = []
        for j in range(3):
            cell_text = game.board[i][j]
            if cell_text == " ":
                # Пустая клетка - кнопка с невидимым символом
                row_buttons.append({
                    "text": game.empty_cell_char,
                    "callback_data": f"ttt_move_{game.game_id}_{i}_{j}"
                })
            else:
                # Занятая клетка - показываем символ
                row_buttons.append({
                    "text": cell_text,
                    "callback_data": "ttt_noop"
                })
        keyboard_rows.append(row_buttons)

    # Добавляем дополнительные кнопки под полем
    if game.status == "active":
        keyboard_rows.append([
            {"text": "🏳️ Сдаться", "callback_data": f"ttt_surrender_{game.game_id}"},
            {"text": "📊 Статус", "callback_data": f"ttt_status_{game.game_id}"}
        ])
    elif game.status == "waiting_accept":
        keyboard_rows.append([
            {"text": "✅ Принять", "callback_data": f"ttt_accept_{game.game_id}"},
            {"text": "❌ Отклонить", "callback_data": f"ttt_reject_{game.game_id}"}
        ])

    return {"inline_keyboard": keyboard_rows}

def check_winner(board, symbol):
    """Проверка победителя"""
    # Проверка строк
    for row in board:
        if all(cell == symbol for cell in row):
            return True

    # Проверка столбцов
    for col in range(3):
        if all(board[row][col] == symbol for row in range(3)):
            return True

    # Проверка диагоналей
    if all(board[i][i] == symbol for i in range(3)):
        return True
    if all(board[i][2-i] == symbol for i in range(3)):
        return True

    return False

def check_draw(board):
    """Проверка ничьей"""
    for row in board:
        for cell in row:
            if cell == " ":
                return False
    return True

def format_game_info(game, data):
    """Форматировать информацию об игре"""
    player1 = get_user(data, game.player1_id)
    player2 = get_user(data, game.player2_id)

    player1_name = player1.get("first_name", "Игрок 1")
    player2_name = player2.get("first_name", "Игрок 2")

    if game.status == "waiting_accept":
        return f"""
🎮 ═══ ВЫЗОВ НА КРЕСТИКИ-НОЛИКИ ═══ 🎮

👤 Инициатор: {player1_name} (❌)
🎯 Соперник: {player2_name} (⭕️)
💰 Ставка: {game.bet_amount:,} ₽
⏰ Время на ход: 60 секунд

⚠️ Оба игрока подтверждают участие!
"""
    elif game.status == "active":
        current_player = get_user(data, str(game.current_player))
        current_name = current_player.get("first_name", "Игрок")
        current_symbol = game.player_symbols[game.current_player]

        time_left = TIC_TAC_TOE_TIMEOUT - (datetime.now() - game.last_move_time).seconds
        if time_left < 0:
            time_left = 0

        return f"""
🎮 ═══ КРЕСТИКИ-НОЛИКИ ═══ 🎮

👥 Игроки: {player1_name} (❌) vs {player2_name} (⭕️)
💰 Ставка: {game.bet_amount:,} ₽
👤 Текущий ход: {current_name} ({current_symbol})
⏰ Осталось времени: {time_left} секунд
📊 Ходов сделано: {len(game.moves)}

💡 Нажмите на пустую клетку для хода!
"""
    elif game.status == "finished":
        if game.winner:
            winner = get_user(data, str(game.winner))
            winner_name = winner.get("first_name", "Победитель")
            winner_symbol = game.player_symbols[game.winner]

            loser_id = game.player2_id if str(game.winner) == game.player1_id else game.player1_id
            loser = get_user(data, loser_id)
            loser_name = loser.get("first_name", "Проигравший")

            return f"""
🎮 ═══ КРЕСТИКИ-НОЛИКИ: ПОБЕДА! ═══ 🎮

🏆 ПОБЕДИТЕЛЬ: {winner_name} ({winner_symbol})
💰 Выигрыш: {game.bet_amount:,} ₽
📅 Время игры: {(datetime.now() - game.start_time).seconds} секунд
📊 Ходов: {len(game.moves)}

💸 Проигравший: {loser_name}
"""
        elif game.is_draw:
            return f"""
🎮 ═══ КРЕСТИКИ-НОЛИКИ: НИЧЬЯ! ═══ 🎮

🤝 НИЧЬЯ!
💰 Оба игрока получают свои ставки обратно
📅 Время игры: {(datetime.now() - game.start_time).seconds} секунд
📊 Ходов: {len(game.moves)}

👥 Игроки: {player1_name} (❌) и {player2_name} (⭕️)
"""

# ===== TIC-TAC-TOE COMMAND HANDLERS =====
def handle_tic_tac_toe_callback(data, callback_query, game_id, action, row=None, col=None):
    """Обработчик callback-ов для игры"""
    chat_id = callback_query["message"]["chat"]["id"]
    message_id = callback_query["message"]["message_id"]
    user_id = callback_query["from"]["id"]

    tic_tac_toe_games = load_tic_tac_toe_games()

    if game_id not in tic_tac_toe_games:
        answer_callback_query(callback_query["id"], "❌ Игра не найдена!", True)
        return

    game = tic_tac_toe_games[game_id]
    data = load_data()  # Перезагружаем данные

    if action == "accept":
        # Принять игру
        if str(user_id) not in [game.player1_id, game.player2_id]:
            answer_callback_query(callback_query["id"], "❌ Это не ваша игра!", True)
            return

        if game.status != "waiting_accept":
            answer_callback_query(callback_query["id"], "❌ Игра уже начата!", True)
            return

        # Подтверждаем участие
        if str(user_id) == game.player1_id:
            game.player1_accepted = True
        else:
            game.player2_accepted = True

        # Проверяем баланс игрока
        player = get_user(data, str(user_id))
        if player["balance"] < game.bet_amount:
            answer_callback_query(callback_query["id"],
                                f"❌ У вас недостаточно средств! Нужно: {game.bet_amount:,} ₽",
                                True)
            return

        # Замораживаем деньги
        player["balance"] -= game.bet_amount

        # Если оба игрока подтвердили, начинаем игру
        if game.player1_accepted and game.player2_accepted:
            game.status = "active"
            game.last_move_time = datetime.now()

            # Сохраняем
            save_data(data)
            save_tic_tac_toe_games(tic_tac_toe_games)

            # Обновляем сообщение
            keyboard = create_game_keyboard(game)
            message_text = format_game_info(game, data)

            edit_message(chat_id, message_id, message_text, reply_markup=keyboard)
            answer_callback_query(callback_query["id"], "✅ Игра начата! Делайте ход!")
        else:
            # Еще ждем подтверждения второго игрока
            save_data(data)
            save_tic_tac_toe_games(tic_tac_toe_games)

            # Обновляем сообщение
            keyboard = create_game_keyboard(game)
            message_text = format_game_info(game, data)

            edit_message(chat_id, message_id, message_text, reply_markup=keyboard)
            answer_callback_query(callback_query["id"], "✅ Вы подтвердили участие!")

    elif action == "reject":
        # Отклонить игру
        if str(user_id) not in [game.player1_id, game.player2_id]:
            answer_callback_query(callback_query["id"], "❌ Это не ваша игра!", True)
            return

        # Возвращаем деньги первому игроку
        player1 = get_user(data, game.player1_id)
        player1["balance"] += game.bet_amount

        game.status = "finished"

        # Сохраняем
        save_data(data)
        save_tic_tac_toe_games(tic_tac_toe_games)

        # Обновляем сообщение
        player_name = callback_query["from"].get("first_name", "Игрок")
        message_text = f"❌ Игра отклонена пользователем {player_name}!"

        edit_message(chat_id, message_id, message_text)
        answer_callback_query(callback_query["id"], "❌ Вы отклонили игру")

    elif action == "move":
        # Сделать ход
        if game.status != "active":
            answer_callback_query(callback_query["id"], "❌ Игра не активна!", True)
            return

        if str(user_id) != str(game.current_player):
            answer_callback_query(callback_query["id"], "❌ Сейчас не ваш ход!", True)
            return

        # Проверяем, не занята ли клетка
        if game.board[row][col] != " ":
            answer_callback_query(callback_query["id"], "❌ Клетка уже занята!", True)
            return

        # Делаем ход
        symbol = game.player_symbols[user_id]
        game.board[row][col] = symbol
        game.moves.append({
            "player": str(user_id),
            "row": row,
            "col": col,
            "symbol": symbol,
            "time": datetime.now().isoformat()
        })
        game.last_move_time = datetime.now()

        # Проверяем победителя
        if check_winner(game.board, symbol):
            game.winner = user_id
            game.status = "finished"

            # Выплачиваем выигрыш
            winner_user = get_user(data, str(user_id))
            winner_user["balance"] += game.bet_amount * 2

            # Обновляем статистику
            winner_stats = winner_user.get("stats", {})
            winner_stats["casino_wins"] = winner_stats.get("casino_wins", 0) + game.bet_amount

            answer_callback_query(callback_query["id"], "🎉 Вы выиграли!")

        elif check_draw(game.board):
            game.is_draw = True
            game.status = "finished"

            # Возвращаем деньги обоим игрокам
            player1 = get_user(data, game.player1_id)
            player2 = get_user(data, game.player2_id)

            player1["balance"] += game.bet_amount
            player2["balance"] += game.bet_amount

            answer_callback_query(callback_query["id"], "🤝 Ничья!")

        else:
            # Продолжаем игру
            game.current_player = (
                int(game.player2_id)
                if str(user_id) == game.player1_id
                else int(game.player1_id)
            )
            answer_callback_query(callback_query["id"], "✅ Ход сделан!")

        # Обновляем сообщение
        save_data(data)
        save_tic_tac_toe_games(tic_tac_toe_games)

        keyboard = create_game_keyboard(game)
        message_text = format_game_info(game, data)

        edit_message(chat_id, message_id, message_text, reply_markup=keyboard)

    elif action == "surrender":
        # Сдаться
        if str(user_id) not in [game.player1_id, game.player2_id]:
            answer_callback_query(callback_query["id"], "❌ Это не ваша игра!", True)
            return

        if game.status != "active":
            answer_callback_query(callback_query["id"], "❌ Игра не активна!", True)
            return

        # Определяем победителя
        winner_id = (
            game.player2_id
            if str(user_id) == game.player1_id
            else game.player1_id
        )

        game.winner = int(winner_id)
        game.status = "finished"

        # Выплачиваем выигрыш победителю
        winner_user = get_user(data, winner_id)
        winner_user["balance"] += game.bet_amount * 2

        # Обновляем статистику
        winner_stats = winner_user.get("stats", {})
        winner_stats["casino_wins"] = winner_stats.get("casino_wins", 0) + game.bet_amount

        # Сохраняем
        save_data(data)
        save_tic_tac_toe_games(tic_tac_toe_games)

        # Обновляем сообщение
        keyboard = create_game_keyboard(game)
        message_text = format_game_info(game, data)

        edit_message(chat_id, message_id, message_text, reply_markup=keyboard)
        answer_callback_query(callback_query["id"], "🏳️ Вы сдались!")

    elif action == "status":
        # Показать статус
        player = get_user(data, str(user_id))
        player_name = player.get("first_name", "Игрок")

        time_left = TIC_TAC_TOE_TIMEOUT - (datetime.now() - game.last_move_time).seconds
        if time_left < 0:
            time_left = 0

        status_text = f"""
🎮 Статус игры для {player_name}:

💰 Ставка: {game.bet_amount:,} ₽
👤 Ваш символ: {game.player_symbols.get(user_id, '?')}
⏰ Осталось времени: {time_left} секунд
📊 Ходов сделано: {len(game.moves)}
🎯 Статус: {'Активна' if game.status == 'active' else 'Завершена'}
"""
        answer_callback_query(callback_query["id"], status_text, True)

def handle_tic_tac_toe_invite(data, message, args):
    """Создать игру в крестики-нолики"""
    if "reply_to_message" not in message:
        send_message(message["chat"]["id"],
                    "❌ Ответьте на сообщение пользователя, которому хотите бросить вызов!",
                    reply_to=message["message_id"])
        return

    if not args:
        send_message(message["chat"]["id"],
                    "❌ Укажите ставку!\n\nПример: крестики 100",
                    reply_to=message["message_id"])
        return

    try:
        bet = int(args[0])
    except ValueError:
        send_message(message["chat"]["id"],
                    "❌ Ставка должна быть числом!",
                    reply_to=message["message_id"])
        return

    if bet < 10:
        send_message(message["chat"]["id"],
                    "❌ Минимальная ставка: 10 ₽",
                    reply_to=message["message_id"])
        return

    if bet > 10000:
        send_message(message["chat"]["id"],
                    "❌ Максимальная ставка: 10,000 ₽",
                    reply_to=message["message_id"])
        return

    player1_id = message["from"]["id"]
    player1 = get_user(data, str(player1_id))

    if player1["balance"] < bet:
        send_message(message["chat"]["id"],
                    f"❌ У вас недостаточно средств!\nВаш баланс: {player1['balance']:,} ₽",
                    reply_to=message["message_id"])
        return

    target_user = message["reply_to_message"]["from"]
    player2_id = target_user["id"]

    if player1_id == player2_id:
        send_message(message["chat"]["id"],
                    "❌ Нельзя играть с самим собой!",
                    reply_to=message["message_id"])
        return

    # Проверяем баланс второго игрока
    player2 = get_user(data, str(player2_id))
    if player2["balance"] < bet:
        target_name = target_user.get("first_name", "Пользователь")
        send_message(message["chat"]["id"],
                    f"❌ У {target_name} недостаточно средств для этой ставки!",
                    reply_to=message["message_id"])
        return

    # Проверяем, нет ли уже активных игр у игроков
    tic_tac_toe_games = load_tic_tac_toe_games()
    for game_id, game in tic_tac_toe_games.items():
        if game.status != "finished":
            if (str(player1_id) in [game.player1_id, game.player2_id] or
                str(player2_id) in [game.player1_id, game.player2_id]):
                send_message(message["chat"]["id"],
                           "❌ У вас или у соперника уже есть активная игра!",
                           reply_to=message["message_id"])
                return

    # Создаем игру
    game_id = f"{player1_id}_{player2_id}_{int(time.time())}"
    game = TicTacToeGame(
        game_id=game_id,
        player1_id=player1_id,
        player2_id=player2_id,
        bet_amount=bet,
        chat_id=message["chat"]["id"]
    )

    # Резервируем деньги
    player1["balance"] -= bet
    save_data(data)

    tic_tac_toe_games[game_id] = game
    save_tic_tac_toe_games(tic_tac_toe_games)

    # Отправляем сообщение с игровым полем
    keyboard = create_game_keyboard(game)
    message_text = format_game_info(game, data)

    result = send_message(message["chat"]["id"], message_text,
                         reply_to=message["message_id"],
                         reply_markup=keyboard)

    if result and result.get("ok"):
        game.message_id = result["result"]["message_id"]
        save_tic_tac_toe_games(tic_tac_toe_games)

def handle_tic_tac_toe_help(data, message):
    """Помощь по игре в крестики-нолики"""
    help_text = """
🎮 ═══ КРЕСТИКИ-НОЛИКИ: ПОМОЩЬ ═══ 🎮

📋 **Как играть:**
1. Бросьте вызов другому игроку:
   `крестики 100` (в ответ на сообщение)

2. Оба игрока должны принять вызов, нажав "✅ Принять"

3. Игра начинается! Первый игрок (❌) ходит первым

4. Нажмите на пустую клетку на поле (невидимая кнопка) чтобы сделать ход

5. Игра продолжается до победы или ничьей

📊 **Правила:**
• Минимальная ставка: 10 ₽
• Максимальная ставка: 10,000 ₽
• Время на ход: 60 секунд
• Если игрок не успевает сделать ход - он проигрывает
• Ничья - деньги возвращаются обоим игрокам

🎯 **Команды:**
• `крестики [ставка]` - бросить вызов (в ответ)
• `сдаться` - сдаться в активной игре
• `игра` - показать статус вашей игры
• `крестики_помощь` - эта справка

💡 **Советы:**
• Проверьте баланс соперника перед вызовом
• Время отсчитывается с момента последнего хода
• Игровое поле обновляется автоматически после каждого хода
"""

    send_message(message["chat"]["id"], help_text, reply_to=message["message_id"])

def handle_tic_tac_toe_status_cmd(data, message):
    """Показать статус текущей игры (команда)"""
    player_id = message["from"]["id"]
    tic_tac_toe_games = load_tic_tac_toe_games()

    # Ищем все игры с этим игроком
    active_games = []
    finished_games = []

    for game_id, game in tic_tac_toe_games.items():
        if str(player_id) in [game.player1_id, game.player2_id]:
            if game.status == "active":
                active_games.append(game)
            elif game.status == "finished":
                finished_games.append(game)

    if not active_games and not finished_games:
        send_message(message["chat"]["id"],
                    "❌ У вас нет активных или завершенных игр!",
                    reply_to=message["message_id"])
        return

    status_text = "🎮 ═══ ВАШИ ИГРЫ ═══ 🎮\n\n"

    if active_games:
        status_text += "🔥 **АКТИВНЫЕ ИГРЫ:**\n"
        for game in active_games:
            opponent_id = game.player2_id if str(player_id) == game.player1_id else game.player1_id
            opponent = get_user(data, opponent_id)
            opponent_name = opponent.get("first_name", "Игрок")

            time_left = TIC_TAC_TOE_TIMEOUT - (datetime.now() - game.last_move_time).seconds
            if time_left < 0:
                time_left = 0

            status_text += f"""
💰 Ставка: {game.bet_amount:,} ₽
👤 Соперник: {opponent_name}
🎯 Ваш символ: {game.player_symbols.get(player_id, '?')}
⏰ Осталось времени: {time_left} секунд
📊 Ходов: {len(game.moves)}
━━━━━━━━━━━━━━━
"""

    if finished_games:
        status_text += "\n📊 **ЗАВЕРШЕННЫЕ ИГРЫ:**\n"
        for game in finished_games[-5:]:  # Последние 5 игр
            opponent_id = game.player2_id if str(player_id) == game.player1_id else game.player1_id
            opponent = get_user(data, opponent_id)
            opponent_name = opponent.get("first_name", "Игрок")

            if game.winner:
                result = "🏆 Выиграли" if str(game.winner) == str(player_id) else "💸 Проиграли"
            elif game.is_draw:
                result = "🤝 Ничья"
            else:
                result = "❓ Неизвестно"

            status_text += f"""
💰 Ставка: {game.bet_amount:,} ₽
👤 Соперник: {opponent_name}
🎯 Результат: {result}
📊 Ходов: {len(game.moves)}
━━━━━━━━━━━━━━━
"""

    status_text += "\n💡 Для новой игры: `крестики [ставка]` (в ответ на сообщение)"

    send_message(message["chat"]["id"], status_text, reply_to=message["message_id"])

def handle_surrender(data, message):
    """Сдаться в активной игре (команда)"""
    player_id = message["from"]["id"]
    tic_tac_toe_games = load_tic_tac_toe_games()

    # Ищем активную игру с этим игроком
    active_game = None
    for game_id, game in tic_tac_toe_games.items():
        if (str(player_id) in [game.player1_id, game.player2_id] and
            game.status == "active"):
            active_game = game
            break

    if not active_game:
        send_message(message["chat"]["id"],
                    "❌ У вас нет активной игры для сдачи!",
                    reply_to=message["message_id"])
        return

    # Определяем победителя
    winner_id = (
        active_game.player2_id
        if str(player_id) == active_game.player1_id
        else active_game.player1_id
    )

    active_game.winner = int(winner_id)
    active_game.status = "finished"

    # Обновляем балансы
    data = load_data()
    winner_user = get_user(data, winner_id)
    winner_user["balance"] += active_game.bet_amount * 2

    # Обновляем статистику
    winner_stats = winner_user.get("stats", {})
    winner_stats["casino_wins"] = winner_stats.get("casino_wins", 0) + active_game.bet_amount

    save_data(data)
    save_tic_tac_toe_games(tic_tac_toe_games)

    # Отправляем подтверждение
    surrendering_user = get_user(data, str(player_id))
    surrendering_name = surrendering_user.get("first_name", "Игрок")

    send_message(message["chat"]["id"],
                f"✅ {surrendering_name}, вы сдались в игре!\n💰 Ваш соперник получает {active_game.bet_amount:,} ₽",
                reply_to=message["message_id"])

    # Обновляем игровое сообщение, если оно есть
    if active_game.message_id:
        keyboard = create_game_keyboard(active_game)
        message_text = format_game_info(active_game, data)

        try:
            edit_message(active_game.chat_id, active_game.message_id, message_text, reply_markup=keyboard)
        except:
            pass

def check_tic_tac_toe_timeouts():
    """Проверка таймаутов в играх"""
    tic_tac_toe_games = load_tic_tac_toe_games()
    current_time = datetime.now()
    timeout_count = 0

    for game_id, game in list(tic_tac_toe_games.items()):
        if game.status == "active":
            time_since_last_move = (current_time - game.last_move_time).seconds

            if time_since_last_move > TIC_TAC_TOE_TIMEOUT:
                # Таймаут - проигрыш игрока, который должен был ходить
                loser_id = game.current_player
                winner_id = (
                    game.player2_id
                    if str(loser_id) == game.player1_id
                    else game.player1_id
                )

                game.winner = int(winner_id)
                game.status = "finished"

                # Обновляем балансы
                data = load_data()
                winner_user = get_user(data, winner_id)
                loser_user = get_user(data, str(loser_id))

                winner_user["balance"] += game.bet_amount * 2

                # Обновляем статистику
                winner_stats = winner_user.get("stats", {})
                winner_stats["casino_wins"] = winner_stats.get("casino_wins", 0) + game.bet_amount

                # Сохраняем
                save_data(data)
                save_tic_tac_toe_games(tic_tac_toe_games)

                # Обновляем сообщение, если оно есть
                if game.message_id:
                    keyboard = create_game_keyboard(game)
                    message_text = format_game_info(game, data)

                    try:
                        edit_message(game.chat_id, game.message_id, message_text, reply_markup=keyboard)
                    except:
                        pass

                timeout_count += 1

    return timeout_count

# ===== ИНТЕГРАЦИЯ В СУЩЕСТВУЮЩИЙ КОД =====
# 1. В существующую функцию handle_callback_query добавить в конец:
#
# def handle_callback_query(data, callback_query):
#     # ... ваш существующий код ...
#
#     # ДОБАВИТЬ ЭТО В САМЫЙ КОНЕЦ ФУНКЦИИ:
#     elif callback_data.startswith("ttt_"):
#         # Обработка игр в крестики-нолики
#         parts = callback_data.split("_")
#
#         if len(parts) >= 3:
#             action = parts[1]
#             game_id = parts[2]
#
#             if action == "noop":
#                 answer_callback_query(callback_query["id"], "❌ Эта клетка уже занята!")
#                 return
#
#             if action == "move" and len(parts) >= 5:
#                 row = int(parts[3])
#                 col = int(parts[4])
#                 handle_tic_tac_toe_callback(data, callback_query, game_id, action, row, col)
#             else:
#                 handle_tic_tac_toe_callback(data, callback_query, game_id, action)

# 2. В существующую функцию process_message добавить команды:
#
# def process_message(data, message):
#     # ... ваш существующий код ...
#
#     # В СУЩЕСТВУЮЩИЙ БЛОК if-elif КОМАНД ДОБАВИТЬ:
#     elif command in ["крестики", "tictactoe", "ttt", "крестикинолики"]:
#         handle_tic_tac_toe_invite(data, message, args)
#     elif command in ["сдаться", "surrender", "ff", "giveup"]:
#         handle_surrender(data, message)
#     elif command in ["игра", "mygame", "статусигры", "gamestatus"]:
#         handle_tic_tac_toe_status_cmd(data, message)
#     elif command in ["крестики_помощь", "ttt_help", "крестикипомощь"]:
#         handle_tic_tac_toe_help(data, message)

# 3. В существующую функцию main добавить:
#
# def main():
#     # ... ваш существующий код ...
#
#     last_timeout_check = time.time()  # ДОБАВИТЬ ЭТУ СТРОЧКУ
#
#     while True:
#         try:
#             # ... ваш существующий код ...
#
#             current_time = time.time()
#
#             # ДОБАВИТЬ ЭТО В ЦИКЛ:
#             # Проверяем таймауты в играх каждые 10 секунд
#             if current_time - last_timeout_check >= 10:
#                 timeout_count = check_tic_tac_toe_timeouts()
#                 if timeout_count > 0:
#                     print(f"⏰ Проверка таймаутов: завершено {timeout_count} игр по таймауту")
#                 last_timeout_check = current_time
#
#             time.sleep(0.5)

# ===== ФУНКЦИИ СОХРАНЕНИЯ ИВЕНТА =====
def save_event_settings():
    """Сохранить настройки ивента"""
    settings = {
        "active": DEFENDER_DAY["active"],
        "start_date": DEFENDER_DAY["start_date"],
        "end_date": DEFENDER_DAY["end_date"]
    }
    with open(EVENT_SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

def load_event_settings():
    """Загрузить настройки ивента"""
    global DEFENDER_DAY
    if os.path.exists(EVENT_SETTINGS_FILE):
        try:
            with open(EVENT_SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                DEFENDER_DAY["active"] = settings.get("active", False)
                DEFENDER_DAY["start_date"] = settings.get("start_date")
                DEFENDER_DAY["end_date"] = settings.get("end_date")
        except:
            pass

# ===== ФУНКЦИИ ПРОГРЕССА ИВЕНТА =====
def progress_quest(event, quest_type, quest_id, amount=1):
    """Увеличивает прогресс задания"""
    if quest_type not in event:
        event[quest_type] = {}
    
    if quest_id not in event[quest_type]:
        event[quest_type][quest_id] = 0
    
    event[quest_type][quest_id] += amount
    
    # Проверяем, не выполнено ли
    quest_data = DEFENDER_DAY["quests"][quest_type][quest_id]
    if event[quest_type][quest_id] >= quest_data["target"]:
        return True
    return False

def complete_quest(user, quest_type, quest_id):
    """Выдаёт награду за выполненное задание"""
    event = user["event_data"]
    
    if f"{quest_id}_completed" in event:
        return False  # Уже выполнено
    
    quest_data = DEFENDER_DAY["quests"][quest_type][quest_id]
    
    # Начисляем очки
    if "reward_points" in quest_data:
        event["points"] = event.get("points", 0) + quest_data["reward_points"]
        user["balance"] += quest_data["reward_money"]
    
    # Если есть подарок
    if "reward_gift" in quest_data:
        if "gifts" not in user:
            user["gifts"] = []
        # Находим ID подарка
        for gid, gdata in GIFTS.items():
            if gdata.get("name") == EVENT_GIFTS[quest_data["reward_gift"]]["name"]:
                user["gifts"].append(gid)
                break
    
    # Отмечаем как выполненное
    event[f"{quest_id}_completed"] = True
    
    return True

def check_event_progress(user, action, amount=1):
    """Проверяет и обновляет прогресс ивента"""
    if not DEFENDER_DAY["active"]:
        return
    
    now = datetime.now()
    
    # Проверяем, не закончился ли ивент
    if DEFENDER_DAY["end_date"]:
        end = datetime.fromisoformat(DEFENDER_DAY["end_date"])
        if now > end:
            return
    
    if "event_data" not in user:
        user["event_data"] = {
            "points": 0,
            "daily": {},
            "special": {},
            "last_daily_reset": now.isoformat()
        }
    
    event = user["event_data"]
    
    # Проверяем, не пора ли сбросить ежедневные
    last_reset = datetime.fromisoformat(event["last_daily_reset"])
    if now.date() > last_reset.date():
        event["daily"] = {}
        event["last_daily_reset"] = now.isoformat()
    
    # Обрабатываем действие
    if action == "casino_bet":
        if progress_quest(event, "daily", "play_casino", amount):
            complete_quest(user, "daily", "play_casino")
        if progress_quest(event, "special", "total_bets_100", amount):
            complete_quest(user, "special", "total_bets_100")
    
    elif action == "casino_win":
        if progress_quest(event, "special", "casino_wins_50000", amount):
            complete_quest(user, "special", "casino_wins_50000")
    
    elif action == "business_collect":
        if progress_quest(event, "daily", "business_income", amount):
            complete_quest(user, "daily", "business_income")
    
    elif action == "gift_sell":
        if progress_quest(event, "daily", "gift_sell", amount):
            complete_quest(user, "daily", "gift_sell")
    
    elif action == "money_transfer":
        if progress_quest(event, "daily", "transfer_money", amount):
            complete_quest(user, "daily", "transfer_money")
    
    elif action == "robbery":
        if progress_quest(event, "daily", "treasury_rob", amount):
            complete_quest(user, "daily", "treasury_rob")
        if progress_quest(event, "special", "robbery_10", amount):
            complete_quest(user, "special", "robbery_10")
    
    elif action == "booster_use":
        if progress_quest(event, "daily", "use_booster", amount):
            complete_quest(user, "daily", "use_booster")
    
    elif action == "business_level_up":
        if user.get("business_level", 0) >= 15:
            complete_quest(user, "special", "business_level_15")
    
    elif action == "gift_collect":
        unique_gifts = len(set(user.get("gifts", [])))
        if unique_gifts >= 10:
            complete_quest(user, "special", "gifts_10")

# ===== ФУНКЦИИ ОТОБРАЖЕНИЯ ИВЕНТА =====
def handle_event_status(data, message):
    """Показать статус ивента"""
    user_id = str(message["from"]["id"])
    user = get_user(data, user_id)
    
    if not DEFENDER_DAY["active"]:
        send_message(
            message["chat"]["id"],
            "❌ Ивент сейчас не активен!",
            reply_to=message["message_id"]
        )
        return
    
    if "event_data" not in user:
        user["event_data"] = {
            "points": 0,
            "daily": {},
            "special": {},
            "last_daily_reset": datetime.now().isoformat()
        }
    
    event = user["event_data"]
    points = event.get("points", 0)
    
    # Время до конца
    end = datetime.fromisoformat(DEFENDER_DAY["end_date"])
    time_left = end - datetime.now()
    days = time_left.days
    hours = time_left.seconds // 3600
    
    text = f"""
🎖️ ═══ ДЕНЬ ЗАЩИТНИКА ═══ 🎖️

🎖️ ВАШИ МЕДАЛИ: {points}
⏳ ДО КОНЦА: {days}д {hours}ч

📋 ЕЖЕДНЕВНЫЕ ЗАДАНИЯ:
"""
    
    # Ежедневные задания
    for qid, qdata in DEFENDER_DAY["quests"]["daily"].items():
        progress = event["daily"].get(qid, 0)
        target = qdata["target"]
        
        if progress >= target:
            status = "✅ ВЫПОЛНЕНО"
        else:
            status = f"{progress}/{target}"
        
        text += f"\n{qdata['emoji']} {qdata['name']}: {status}"
        text += f"\n   +{qdata['reward_points']} медалей, {qdata['reward_money']} ₽\n"
    
    text += "\n⚔️ ОСОБЫЕ ЗАДАНИЯ:\n"
    
    # Особые задания
    for qid, qdata in DEFENDER_DAY["quests"]["special"].items():
        completed = event.get(f"{qid}_completed", False)
        
        if completed:
            status = "✅ ВЫПОЛНЕНО"
        else:
            # Показываем прогресс
            if qid == "business_level_15":
                progress = user.get("business_level", 0)
                status = f"{progress}/{qdata['target']}"
            elif qid == "gifts_10":
                progress = len(set(user.get("gifts", [])))
                status = f"{progress}/{qdata['target']}"
            elif qid == "total_bets_100":
                progress = user.get("stats", {}).get("total_bets", 0)
                status = f"{progress}/{qdata['target']}"
            elif qid == "casino_wins_50000":
                progress = user.get("stats", {}).get("casino_wins", 0)
                status = f"{progress}/{qdata['target']}"
            elif qid == "robbery_10":
                progress = user.get("stats", {}).get("successful_robs", 0)
                status = f"{progress}/{qdata['target']}"
            else:
                status = "❌ НЕ ВЫПОЛНЕНО"
        
        text += f"\n{qdata['emoji']} {qdata['name']}: {status}"
        text += f"\n   Награда: {qdata['reward_money']} ₽ + подарок\n"
    
    text += "\n🏆 ТОП-5 ГЕРОЕВ: /топ_ивент"
    
    send_message(
        message["chat"]["id"],
        text,
        reply_to=message["message_id"]
    )

def handle_event_top(data, message):
    """Показать топ-5 ивента"""
    if not DEFENDER_DAY["active"]:
        send_message(
            message["chat"]["id"],
            "❌ Ивент сейчас не активен!",
            reply_to=message["message_id"]
        )
        return
    
    # Собираем всех участников
    participants = []
    for uid, udata in data["users"].items():
        if "event_data" in udata:
            points = udata["event_data"].get("points", 0)
            if points > 0:
                name = udata.get("first_name", "Пользователь")
                participants.append((name, points))
    
    # Сортируем по очкам
    participants.sort(key=lambda x: x[1], reverse=True)
    
    # Берём топ-5
    top_5 = participants[:5]
    
    # Время до конца
    end = datetime.fromisoformat(DEFENDER_DAY["end_date"])
    time_left = end - datetime.now()
    days = time_left.days
    hours = time_left.seconds // 3600
    
    text = f"""
🏆 ═══ ТОП-5 ИВЕНТА ═══ 🏆

⏳ ДО КОНЦА: {days}д {hours}ч

"""
    
    if not top_5:
        text += "Пока нет участников 😢\n"
        text += "Стань первым!"
    else:
        for i, (name, points) in enumerate(top_5, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            text += f"{medal} {name} — {points} медалей\n"
    
    text += "\n🎁 НАГРАДЫ ТОП-5:\n"
    
    for place, reward in DEFENDER_DAY["top_rewards"].items():
        text += f"\n{place} МЕСТО: {reward['badge']} {reward['name']}"
        text += f"\n   💰 {reward['money']:,} ₽ + эксклюзивный подарок\n"
    
    send_message(
        message["chat"]["id"],
        text,
        reply_to=message["message_id"]
    )

# ===== АДМИНСКИЕ ФУНКЦИИ ИВЕНТА =====
def handle_admin_event_start(data, message, args):
    """Запустить ивент (только для админов)"""
    if not is_admin(message["from"]["id"]):
        send_message(message["chat"]["id"],
                     "❌ Только для админов!",
                     reply_to=message["message_id"])
        return
    
    # Проверяем, не запущен ли уже ивент
    if DEFENDER_DAY["active"]:
        send_message(message["chat"]["id"],
                     "❌ Ивент уже запущен!\n"
                     f"📅 Начало: {DEFENDER_DAY['start_date']}\n"
                     f"📅 Конец: {DEFENDER_DAY['end_date']}",
                     reply_to=message["message_id"])
        return
    
    # Определяем длительность ивента
    days = 3  # По умолчанию 3 дня
    if args and args[0].isdigit():
        days = int(args[0])
        if days < 1 or days > 30:
            send_message(message["chat"]["id"],
                         "❌ Длительность должна быть от 1 до 30 дней!",
                         reply_to=message["message_id"])
            return
    
    # Запускаем ивент
    now = datetime.now()
    DEFENDER_DAY["active"] = True
    DEFENDER_DAY["start_date"] = now.isoformat()
    DEFENDER_DAY["end_date"] = (now + timedelta(days=days)).isoformat()
    
    # Сохраняем настройки ивента в файл
    save_event_settings()
    
    # Отправляем уведомление в канал
    announcement = f"""
🎖️ ═══ ИВЕНТ ЗАПУЩЕН! ═══ 🎖️

{DEFENDER_DAY['name']}

📅 Длительность: {days} дней
📅 Конец: {(now + timedelta(days=days)).strftime('%d.%m.%Y %H:%M')}

🎯 ЧТО НУЖНО ДЕЛАТЬ:
• Играть в казино
• Собирать доход с бизнеса
• Продавать подарки
• Переводить деньги
• Грабить казну
• Использовать бустеры

🏆 ТОП-5 ПОЛУЧАТ:
• 🥇 500,000 ₽ + легендарный подарок
• 🥈 300,000 ₽ + легендарный подарок
• 🥉 200,000 ₽ + эпический подарок
• 4-5 места: 150,000-100,000 ₽ + редкие подарки

💡 Команда: /ивент - ваш прогресс
🏆 Команда: /топ_ивент - топ участников

Удачи, солдаты! 🪖
"""
    
    send_message(STATS_CHANNEL_ID, announcement)
    
    # Отправляем подтверждение админу
    send_message(message["chat"]["id"],
                 f"✅ Ивент запущен на {days} дней!\n"
                 f"📅 Конец: {(now + timedelta(days=days)).strftime('%d.%m.%Y %H:%M')}",
                 reply_to=message["message_id"])

def handle_admin_event_stop(data, message, args):
    """Остановить ивент и раздать награды (только для админов)"""
    if not is_admin(message["from"]["id"]):
        send_message(message["chat"]["id"],
                     "❌ Только для админов!",
                     reply_to=message["message_id"])
        return
    
    if not DEFENDER_DAY["active"]:
        send_message(message["chat"]["id"],
                     "❌ Ивент сейчас не активен!",
                     reply_to=message["message_id"])
        return
    
    # Подтверждение
    if not args or args[0].lower() != "yes":
        send_message(message["chat"]["id"],
                     "⚠️ ВНИМАНИЕ! Это остановит ивент и раздаст награды.\n"
                     "Для подтверждения: /event_stop yes",
                     reply_to=message["message_id"])
        return
    
    # Раздаём награды
    send_message(message["chat"]["id"],
                 "🔄 Раздача наград...",
                 reply_to=message["message_id"])
    
    distribute_event_rewards(data)
    
    send_message(message["chat"]["id"],
                 "✅ Ивент остановлен, награды розданы!",
                 reply_to=message["message_id"])

def handle_admin_event_status(data, message):
    """Показать статус ивента (для админов)"""
    if not is_admin(message["from"]["id"]):
        send_message(message["chat"]["id"],
                     "❌ Только для админов!",
                     reply_to=message["message_id"])
        return
    
    if not DEFENDER_DAY["active"]:
        status = "❌ Ивент не активен"
        start = "Не запущен"
        end = "Не запущен"
        participants = 0
        top_5 = []
    else:
        status = "✅ Ивент активен"
        start = datetime.fromisoformat(DEFENDER_DAY["start_date"]).strftime('%d.%m.%Y %H:%M')
        end = datetime.fromisoformat(DEFENDER_DAY["end_date"]).strftime('%d.%m.%Y %H:%M')
        
        # Считаем участников
        participants = 0
        for uid, udata in data["users"].items():
            if "event_data" in udata:
                participants += 1
        
        # Считаем топ-5
        top_players = []
        for uid, udata in data["users"].items():
            if "event_data" in udata:
                points = udata["event_data"].get("points", 0)
                if points > 0:
                    name = udata.get("first_name", "Пользователь")
                    top_players.append((name, points))
        
        top_players.sort(key=lambda x: x[1], reverse=True)
        top_5 = top_players[:5]
    
    text = f"""
👑 ═══ АДМИН: ИВЕНТ ═══ 👑

{status}

📅 Начало: {start}
📅 Конец: {end}

📊 УЧАСТНИКОВ: {participants}

🏆 ТЕКУЩИЙ ТОП-5:
"""
    
    if top_5:
        for i, (name, points) in enumerate(top_5, 1):
            text += f"\n{i}. {name} — {points} медалей"
    else:
        text += "\nПока нет участников"
    
    text += "\n\n📋 КОМАНДЫ АДМИНА:"
    text += "\n• /event_start [дни] - запустить ивент"
    text += "\n• /event_stop - остановить ивент"
    text += "\n• /event_stop yes - подтвердить остановку"
    text += "\n• /event_status - этот статус"
    text += "\n• /event_reset - сбросить прогресс всех (осторожно!)"
    text += "\n• /event_reset confirm - подтвердить сброс"
    text += "\n• /event_add [количество] - добавить медали (в ответ)"
    
    send_message(message["chat"]["id"],
                 text,
                 reply_to=message["message_id"])

def handle_admin_event_reset(data, message, args):
    """Сбросить прогресс ивента у всех (только для админов)"""
    if not is_admin(message["from"]["id"]):
        send_message(message["chat"]["id"],
                     "❌ Только для админов!",
                     reply_to=message["message_id"])
        return
    
    # Двойное подтверждение
    if not args or args[0].lower() != "confirm":
        send_message(message["chat"]["id"],
                     "⚠️ ВНИМАНИЕ! Это удалит ВЕСЬ прогресс ивента у всех игроков!\n"
                     "Для подтверждения: /event_reset confirm",
                     reply_to=message["message_id"])
        return
    
    count = 0
    for uid, udata in data["users"].items():
        if "event_data" in udata:
            del udata["event_data"]
            count += 1
    
    save_data(data)
    
    send_message(message["chat"]["id"],
                 f"✅ Прогресс ивента сброшен у {count} игроков!",
                 reply_to=message["message_id"])

def handle_admin_event_add_points(data, message, args):
    """Добавить медали игроку (только для админов)"""
    if not is_admin(message["from"]["id"]):
        send_message(message["chat"]["id"],
                     "❌ Только для админов!",
                     reply_to=message["message_id"])
        return
    
    if not DEFENDER_DAY["active"]:
        send_message(message["chat"]["id"],
                     "❌ Ивент не активен!",
                     reply_to=message["message_id"])
        return
    
    if "reply_to_message" not in message:
        send_message(message["chat"]["id"],
                     "❌ Ответьте на сообщение пользователя!\n"
                     "Использование: /event_add [количество]",
                     reply_to=message["message_id"])
        return
    
    if not args:
        send_message(message["chat"]["id"],
                     "❌ Укажите количество медалей!\n"
                     "Пример: /event_add 100",
                     reply_to=message["message_id"])
        return
    
    try:
        points = int(args[0])
    except:
        send_message(message["chat"]["id"],
                     "❌ Количество должно быть числом!",
                     reply_to=message["message_id"])
        return
    
    if points <= 0:
        send_message(message["chat"]["id"],
                     "❌ Количество должно быть больше 0!",
                     reply_to=message["message_id"])
        return
    
    target_user = message["reply_to_message"]["from"]
    target_id = str(target_user["id"])
    
    update_user_info(data, target_id, target_user.get("username"),
                     target_user.get("first_name"))
    
    target = get_user(data, target_id)
    
    if "event_data" not in target:
        target["event_data"] = {
            "points": 0,
            "daily": {},
            "special": {},
            "last_daily_reset": datetime.now().isoformat()
        }
    
    target["event_data"]["points"] = target["event_data"].get("points", 0) + points
    
    save_data(data)
    
    target_name = format_user_mention(target, target_id)
    
    send_message(message["chat"]["id"],
                 f"✅ Добавлено {points} медалей пользователю {target_name}",
                 reply_to=message["message_id"])

# ===== ФУНКЦИЯ РАЗДАЧИ НАГРАД =====
def distribute_event_rewards(data):
    """
    Раздача наград по окончании ивента
    """
    if not DEFENDER_DAY["active"]:
        return
    
    print("🎖️ НАЧАЛО РАЗДАЧИ НАГРАД ЗА ИВЕНТ")
    
    # Собираем всех участников
    participants = []
    for uid, udata in data["users"].items():
        if "event_data" in udata:
            points = udata["event_data"].get("points", 0)
            if points > 0:
                name = udata.get("first_name", "Пользователь")
                participants.append((uid, name, points, udata))
    
    # Сортируем по очкам
    participants.sort(key=lambda x: x[2], reverse=True)
    
    # Берём топ-5
    top_5 = participants[:5]
    
    print(f"🏆 ТОП-5 ИВЕНТА:")
    for i, (uid, name, points, _) in enumerate(top_5, 1):
        print(f"   {i}. {name} - {points} медалей")
    
    # Раздаём награды топ-5
    for position, (uid, name, points, user) in enumerate(top_5, 1):
        reward = DEFENDER_DAY["top_rewards"][position]
        
        # Деньги
        user["balance"] += reward["money"]
        
        # Подарок
        if "gifts" not in user:
            user["gifts"] = []
        
        # Находим ID подарка
        for gid, gdata in GIFTS.items():
            if gdata.get("name") == EVENT_GIFTS[reward["gift"]]["name"]:
                user["gifts"].append(gid)
                break
        
        # Отправляем уведомление в ЛС
        try:
            gift_name = EVENT_GIFTS[reward["gift"]]["name"]
            gift_emoji = EVENT_GIFTS[reward["gift"]]["emoji"]
            
            send_message(
                uid,
                f"""
🏆 ═══ ПОЗДРАВЛЯЕМ! ═══ 🏆

Вы заняли {position} МЕСТО в ивенте!

💰 ДЕНЕЖНЫЙ ПРИЗ: {reward['money']:,} ₽
🎁 ЭКСКЛЮЗИВНЫЙ ПОДАРОК: {gift_emoji} {gift_name}

📝 {reward['description']}

💎 Этот подарок больше нигде не получить!
"""
            )
        except:
            pass
    
    # Всем остальным участникам - утешительные призы
    for uid, name, points, user in participants[5:]:
        consolation = 10000  # 10,000 ₽ за участие
        
        user["balance"] += consolation
        
        try:
            send_message(
                uid,
                f"""
🎖️ СПАСИБО ЗА УЧАСТИЕ!

К сожалению, вы не вошли в топ-5 😔

💰 УТЕШИТЕЛЬНЫЙ ПРИЗ: {consolation:,} ₽

💡 В следующий раз обязательно получится!
"""
            )
        except:
            pass
    
    # Отключаем ивент
    DEFENDER_DAY["active"] = False
    DEFENDER_DAY["start_date"] = None
    DEFENDER_DAY["end_date"] = None
    save_event_settings()
    
    # Очищаем данные ивента у всех
    for uid, udata in data["users"].items():
        if "event_data" in udata:
            del udata["event_data"]
    
    save_data(data)
    
    # Публикуем результаты в канале
    results_text = "🏆 ═══ ИТОГИ ИВЕНТА ═══ 🏆\n\n"
    
    for i, (uid, name, points, _) in enumerate(top_5, 1):
        reward = DEFENDER_DAY["top_rewards"][i]
        results_text += f"{i}. {name} — {points} медалей\n"
        results_text += f"   🏅 {reward['name']} + {reward['money']:,} ₽\n\n"
    
    send_message(STATS_CHANNEL_ID, results_text)
    
    print(f"✅ Награды розданы! Топ-5 получили призы")

def check_event_end():
    """Проверяет, не пора ли закончить ивент"""
    if not DEFENDER_DAY["active"]:
        return False
    
    if not DEFENDER_DAY["end_date"]:
        return False
    
    now = datetime.now()
    end = datetime.fromisoformat(DEFENDER_DAY["end_date"])
    
    # Если ивент закончился
    if now >= end:
        print("🎖️ Ивент закончился, раздаём награды...")
        data = load_data()
        distribute_event_rewards(data)
        return True
    
    return False

def main():
    print("🤖 Telegram Bot запускается...")

    if not TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN не установлен!")
        print("Пожалуйста, добавьте токен бота в Secrets.")
        return

    print(f"✅ Токен загружен: {TOKEN[:15]}...")

    data = load_data()
    load_settings()
    load_promo_codes()
def main():
    print("🤖 Telegram Bot запускается...")
    
    # ... существующий код ...
    
    data = load_data()
    load_settings()
    load_promo_codes()
    # ===== ДОБАВЛЕНО =====
    load_event_settings()  # Загружаем настройки ивента
    if DEFENDER_DAY["active"]:
        print(f"🎖️ Ивент активен! Конец: {DEFENDER_DAY['end_date']}")
    else:
        print("🎖️ Ивент не активен (ждёт команды админа)")
    print(f"📊 Загружено {data['stats']['total_users']} пользователей")
    print(f"🎰 Настройки шансов загружены")
    print(f"💳 Система промокодов готова к работе")
    print(f"🚀 Система бустеров готова к работе")
    print(f"🏆 Система достижений готова к работе")

    print("\n" + "="*50)
    print("🔒 КОНСОЛЬНЫЕ КОМАНДЫ ДЛЯ ТАЙНЫХ ШАНСОВ")
    print("="*50)
    print("• secret list - показать пользователей с тайными шансами")
    print("• secret set [id] [%] all - установить ВСЕ шансы казино")
    print("• secret setall [id] [слоты] [джекпот] [монетка] [кости] [рулетка] [успех] [побег]")
    print("• secret reset [id] - сбросить тайные шансы")
    print("• secret clear - очистить все тайные шансы")
    print("• secret check [id] - проверить шансы пользователя")
    print("• exit - выйти из консольного режима")
    print("• help - показать справку")
    print("="*50 + "\n")

    # Запускаем консольный поток в отдельном потоке
    def console_commands():
        """Обработка консольных команд для тайных шансов"""
        nonlocal data  # Используем nonlocal для доступа к переменной data

        while True:
            try:
                command = input("🔒 Консоль> ").strip().lower()

                if command == "exit":
                    print("👋 Выход из консольного режима")
                    break

                elif command == "secret list":
                    secret_chances = load_secret_chances()
                    if not secret_chances:
                        print("📭 Нет пользователей с тайными шансами")
                    else:
                        print(f"📋 Пользователи с тайными шансы ({len(secret_chances)}):")
                        for user_id, chances in secret_chances.items():
                            user_data = data["users"].get(user_id, {})
                            user_name = user_data.get("first_name", "Пользователь")
                            username = user_data.get("username", "")
                            if username:
                                user_display = f"@{username} ({user_name})"
                            else:
                                user_display = user_name

                            print(f"\n👤 {user_display} (ID: {user_id}):")

                            # Выводим все казино шансы как группа
                            print("   🎰 КАЗИНО:")
                            if "slots_win_chance" in chances:
                                public = CHANCE_SETTINGS["slots_win_chance"]
                                val = chances["slots_win_chance"]
                                diff = val - public
                                diff_sign = "+" if diff > 0 else ""
                                print(f"     • Слоты: {val}% (публично: {public}%, {diff_sign}{diff})")

                            if "slots_jackpot_chance" in chances:
                                public = CHANCE_SETTINGS["slots_jackpot_chance"]
                                val = chances["slots_jackpot_chance"]
                                diff = val - public
                                diff_sign = "+" if diff > 0 else ""
                                print(f"     • Джекпот: {val}% (публично: {public}%, {diff_sign}{diff})")

                            if "coinflip_win_chance" in chances:
                                public = CHANCE_SETTINGS["coinflip_win_chance"]
                                val = chances["coinflip_win_chance"]
                                diff = val - public
                                diff_sign = "+" if diff > 0 else ""
                                print(f"     • Монетка: {val}% (публично: {public}%, {diff_sign}{diff})")

                            if "dice_win_threshold" in chances:
                                public = CHANCE_SETTINGS["dice_win_threshold"]
                                val = chances["dice_win_threshold"]
                                # Для костей меньше порог = лучше
                                diff = public - val
                                if diff > 0:
                                    print(f"     • Кости: порог {val} (публично: {public}, лучше на {diff})")
                                elif diff < 0:
                                    print(f"     • Кости: порог {val} (публично: {public}, хуже на {abs(diff)})")
                                else:
                                    print(f"     • Кости: порог {val} (публично: {public})")

                            if "roulette_red_black_chance" in chances:
                                public = CHANCE_SETTINGS["roulette_red_black_chance"]
                                val = chances["roulette_red_black_chance"]
                                diff = val - public
                                diff_sign = "+" if diff > 0 else ""
                                print(f"     • Рулетка: {val}% (публично: {public}%, {diff_sign}{diff})")

                            # Отдельно шансы ограбления казны (по желанию)
                            if "treasury_rob_success" in chances or "treasury_rob_escape" in chances or "treasury_rob_caught" in chances:
                                print("   🏦 ОГРАБЛЕНИЕ КАЗНЫ:")
                                if "treasury_rob_success" in chances:
                                    public = CHANCE_SETTINGS["treasury_rob_success"]
                                    val = chances["treasury_rob_success"]
                                    diff = val - public
                                    diff_sign = "+" if diff > 0 else ""
                                    print(f"     • Успех: {val}% (публично: {public}%, {diff_sign}{diff})")

                                if "treasury_rob_escape" in chances:
                                    public = CHANCE_SETTINGS["treasury_rob_escape"]
                                    val = chances["treasury_rob_escape"]
                                    diff = val - public
                                    diff_sign = "+" if diff > 0 else ""
                                    print(f"     • Побег: {val}% (публично: {public}%, {diff_sign}{diff})")

                                if "treasury_rob_caught" in chances:
                                    public = CHANCE_SETTINGS["treasury_rob_caught"]
                                    val = chances["treasury_rob_caught"]
                                    diff = val - public
                                    diff_sign = "+" if diff > 0 else ""
                                    print(f"     • Поимка: {val}% (публично: {public}%, {diff_sign}{diff})")

                elif command.startswith("secret set "):
                    try:
                        parts = command.split()
                        if len(parts) < 4:
                            print("❌ Используйте: secret set [id] [%] [тип]")
                            print("   Типы:")
                            print("   • all - все шансы казино (кроме ограбления)")
                            print("   • casino - все шансы казино (кроме ограбления)")
                            print("   • robbery - только ограбление казны")
                            print("   • robbery_success - только шанс успеха ограбления")
                            print("   • robbery_escape - только шанс побега")
                            print("   • robbery_caught - только шанс поимки")
                            continue

                        user_id = parts[2]
                        value = float(parts[3])
                        chance_type = parts[4] if len(parts) > 4 else "all"

                        # Проверяем существование пользователя
                        if user_id not in data["users"]:
                            print(f"❌ Пользователь {user_id} не найден!")
                            # Показываем ближайших пользователей
                            similar_users = [uid for uid in data["users"].keys() if user_id in uid]
                            if similar_users[:5]:
                                print("   Возможно вы имели в виду:")
                                for uid in similar_users[:5]:
                                    user_data = data["users"][uid]
                                    name = user_data.get("first_name", "Пользователь")
                                    print(f"   • {uid}: {name}")
                            continue

                        # Проверка значения
                        if chance_type in ["all", "casino"]:
                            if not 0 <= value <= 100:
                                print(f"❌ Процент должен быть от 0 до 100!")
                                continue
                            value = int(value)
                        elif chance_type == "robbery":
                            if not 0 <= value <= 100:
                                print(f"❌ Процент должен быть от 0 до 100!")
                                continue
                            value = int(value)
                        elif chance_type in ["robbery_success", "robbery_escape", "robbery_caught"]:
                            if not 0 <= value <= 100:
                                print(f"❌ Процент должен быть от 0 до 100!")
                                continue
                            value = int(value)
                        elif chance_type == "dice":
                            if not 2 <= value <= 12:
                                print(f"❌ Порог для костей должен быть от 2 до 12!")
                                continue
                            value = int(value)

                        # Загружаем текущие тайные шансы
                        secret_chances = load_secret_chances()

                        if user_id not in secret_chances:
                            secret_chances[user_id] = {}

                        # Получаем информацию о пользователе
                        user_data = data["users"][user_id]
                        user_name = user_data.get("first_name", "Пользователь")

                        # Устанавливаем шансы в зависимости от типа
                        if chance_type in ["all", "casino"]:
                            # Устанавливаем все шансы казино
                            secret_chances[user_id]["slots_win_chance"] = value
                            secret_chances[user_id]["coinflip_win_chance"] = value
                            secret_chances[user_id]["roulette_red_black_chance"] = value

                            # Для джекпота устанавливаем отдельно (можно пропорционально)
                            jackpot_value = max(1, int(value / 8))
                            secret_chances[user_id]["slots_jackpot_chance"] = jackpot_value

                            # Для костей: чем выше процент, тем ниже порог (лучше для игрока)
                            dice_threshold = max(2, min(12, 13 - int(value / 10)))
                            secret_chances[user_id]["dice_win_threshold"] = dice_threshold

                            print(f"✅ Установлены все шансы казино для {user_name} (ID: {user_id}):")
                            print(f"   🎰 Слоты: {value}% (публично: {CHANCE_SETTINGS['slots_win_chance']}%)")
                            print(f"   🎰 Джекпот: {jackpot_value}% (публично: {CHANCE_SETTINGS['slots_jackpot_chance']}%)")
                            print(f"   🪙 Монетка: {value}% (публично: {CHANCE_SETTINGS['coinflip_win_chance']}%)")
                            print(f"   🎲 Кости: порог {dice_threshold} (публично: {CHANCE_SETTINGS['dice_win_threshold']})")
                            print(f"   🎡 Рулетка: {value}% (публично: {CHANCE_SETTINGS['roulette_red_black_chance']}%)")

                        elif chance_type == "robbery":
                            # Устанавливаем шансы ограбления
                            secret_chances[user_id]["treasury_rob_success"] = value
                            remaining = 100 - value
                            escape_chance = remaining // 2
                            caught_chance = remaining - escape_chance

                            secret_chances[user_id]["treasury_rob_escape"] = escape_chance
                            secret_chances[user_id]["treasury_rob_caught"] = caught_chance

                            print(f"✅ Установлены шансы ограбления для {user_name} (ID: {user_id}):")
                            print(f"   🏦 Успех: {value}% (публично: {CHANCE_SETTINGS['treasury_rob_success']}%)")
                            print(f"   🏦 Побег: {escape_chance}% (публично: {CHANCE_SETTINGS['treasury_rob_escape']}%)")
                            print(f"   🏦 Поимка: {caught_chance}% (публично: {CHANCE_SETTINGS['treasury_rob_caught']}%)")

                        elif chance_type == "robbery_success":
                            secret_chances[user_id]["treasury_rob_success"] = value
                            print(f"✅ Установлен шанс успеха ограбления для {user_name} (ID: {user_id}):")
                            print(f"   🏦 Успех: {value}% (публично: {CHANCE_SETTINGS['treasury_rob_success']}%)")

                        elif chance_type == "robbery_escape":
                            secret_chances[user_id]["treasury_rob_escape"] = value
                            print(f"✅ Установлен шанс побега для {user_name} (ID: {user_id}):")
                            print(f"   🏦 Побег: {value}% (публично: {CHANCE_SETTINGS['treasury_rob_escape']}%)")

                        elif chance_type == "robbery_caught":
                            secret_chances[user_id]["treasury_rob_caught"] = value
                            print(f"✅ Установлен шанс поимки для {user_name} (ID: {user_id}):")
                            print(f"   🏦 Поимка: {value}% (публично: {CHANCE_SETTINGS['treasury_rob_caught']}%)")

                        elif chance_type == "dice":
                            secret_chances[user_id]["dice_win_threshold"] = value
                            print(f"✅ Установлен порог костей для {user_name} (ID: {user_id}):")
                            print(f"   🎲 Кости: порог {value} (публично: {CHANCE_SETTINGS['dice_win_threshold']})")
                            print(f"   💡 Чем меньше порог - тем легче выиграть!")

                        save_secret_chances(secret_chances)

                    except ValueError:
                        print("❌ Значение должно быть числом!")
                    except Exception as e:
                        print(f"❌ Ошибка: {e}")
                        import traceback
                        traceback.print_exc()

                elif command.startswith("secret setall "):
                    """Установить конкретные значения для каждого шанса"""
                    try:
                        parts = command.split()
                        if len(parts) < 8:
                            print("❌ Используйте: secret setall [id] [слоты%] [джекпот%] [монетка%] [кости_порог] [рулетка%] [успех%] [побег%]")
                            print("   Пример: secret setall 123456789 50 10 45 4 46 40 30")
                            print("   Последние два параметра (успех, побег) - для ограбления")
                            print("   Шанс поимки будет расчитан автоматически")
                            continue

                        user_id = parts[2]

                        # Парсим все значения
                        slots_value = int(parts[3])
                        jackpot_value = int(parts[4])
                        coin_value = int(parts[5])
                        dice_value = int(parts[6])
                        roulette_value = float(parts[7])
                        robbery_success = int(parts[8]) if len(parts) > 8 else None
                        robbery_escape = int(parts[9]) if len(parts) > 9 else None

                        # Проверяем существование пользователя
                        if user_id not in data["users"]:
                            print(f"❌ Пользователь {user_id} не найден!")
                            continue

                        # Проверка значений
                        checks = [
                            ("Слоты", slots_value, 0, 100),
                            ("Джекпот", jackpot_value, 0, 100),
                            ("Монетка", coin_value, 0, 100),
                            ("Кости", dice_value, 2, 12),
                            ("Рулетка", roulette_value, 0, 48.6)
                        ]

                        for name, val, min_val, max_val in checks:
                            if not min_val <= val <= max_val:
                                print(f"❌ {name}: {val} должно быть от {min_val} до {max_val}!")
                                return

                        if robbery_success is not None and not 0 <= robbery_success <= 100:
                            print(f"❌ Успех ограбления: {robbery_success} должно быть от 0 до 100!")
                            return

                        if robbery_escape is not None and not 0 <= robbery_escape <= 100:
                            print(f"❌ Побег: {robbery_escape} должно быть от 0 до 100!")
                            return

                        # Загружаем текущие тайные шансы
                        secret_chances = load_secret_chances()

                        if user_id not in secret_chances:
                            secret_chances[user_id] = {}

                        # Устанавливаем все значения
                        secret_chances[user_id]["slots_win_chance"] = slots_value
                        secret_chances[user_id]["slots_jackpot_chance"] = jackpot_value
                        secret_chances[user_id]["coinflip_win_chance"] = coin_value
                        secret_chances[user_id]["dice_win_threshold"] = dice_value
                        secret_chances[user_id]["roulette_red_black_chance"] = roulette_value

                        if robbery_success is not None:
                            secret_chances[user_id]["treasury_rob_success"] = robbery_success
                            if robbery_escape is not None:
                                secret_chances[user_id]["treasury_rob_escape"] = robbery_escape
                                caught_value = 100 - robbery_success - robbery_escape
                                secret_chances[user_id]["treasury_rob_caught"] = max(0, caught_value)

                        save_secret_chances(secret_chances)

                        user_data = data["users"][user_id]
                        user_name = user_data.get("first_name", "Пользователь")

                        print(f"✅ Установлены все шансы для {user_name} (ID: {user_id}):")
                        print(f"   🎰 Слоты: {slots_value}%")
                        print(f"   🎰 Джекпот: {jackpot_value}%")
                        print(f"   🪙 Монетка: {coin_value}%")
                        print(f"   🎲 Кости: порог {dice_value}")
                        print(f"   🎡 Рулетка: {roulette_value}%")

                        if robbery_success is not None:
                            print(f"   🏦 Успех ограбления: {robbery_success}%")
                            if robbery_escape is not None:
                                print(f"   🏦 Побег: {robbery_escape}%")
                                print(f"   🏦 Поимка: {100 - robbery_success - robbery_escape}%")

                    except ValueError:
                        print("❌ Все значения должны быть числами!")
                    except Exception as e:
                        print(f"❌ Ошибка: {e}")

                elif command.startswith("secret reset "):
                    try:
                        parts = command.split()
                        if len(parts) < 3:
                            print("❌ Используйте: secret reset [id]")
                            continue

                        user_id = parts[2]
                        secret_chances = load_secret_chances()

                        if user_id in secret_chances:
                            user_data = data["users"].get(user_id, {})
                            user_name = user_data.get("first_name", "Пользователь")

                            del secret_chances[user_id]
                            save_secret_chances(secret_chances)

                            print(f"✅ Сброшены все тайные шансы для {user_name} (ID: {user_id})")
                        else:
                            print(f"ℹ️ У пользователя {user_id} нет тайных шансов")

                    except Exception as e:
                        print(f"❌ Ошибка: {e}")

                elif command == "secret clear":
                    confirm = input("⚠️ Очистить ВСЕ тайные шансы? (yes/no): ")
                    if confirm.lower() in ["yes", "y", "да"]:
                        save_secret_chances({})
                        print("✅ Все тайные шансы очищены")
                    else:
                        print("❌ Отменено")

                elif command.startswith("secret check "):
                    try:
                        parts = command.split()
                        if len(parts) < 3:
                            print("❌ Используйте: secret check [id]")
                            continue

                        user_id = parts[2]

                        if user_id not in data["users"]:
                            print(f"❌ Пользователь {user_id} не найден!")
                            continue

                        user_real_chances = get_user_chances(user_id)
                        user_data = data["users"].get(user_id, {})
                        user_name = user_data.get("first_name", "Пользователь")
                        username = user_data.get("username", "")

                        if username:
                            user_display = f"@{username} ({user_name})"
                        else:
                            user_display = user_name

                        secret_chances = load_secret_chances()
                        has_secret = user_id in secret_chances

                        print(f"\n🔍 РЕАЛЬНЫЕ ШАНСЫ для {user_display} (ID: {user_id}):")
                        print("═" * 50)

                        # Казино шансы
                        print("\n🎰 КАЗИНО:")
                        casino_chances = [
                            ("Слоты (выигрыш)", "slots_win_chance", True, "%"),
                            ("Слоты (джекпот)", "slots_jackpot_chance", True, "%"),
                            ("Монетка", "coinflip_win_chance", True, "%"),
                            ("Кости (порог)", "dice_win_threshold", False, ""),
                            ("Рулетка", "roulette_red_black_chance", True, "%")
                        ]

                        for name, key, is_percent, suffix in casino_chances:
                            real_value = user_real_chances.get(key, "?")
                            public_value = CHANCE_SETTINGS.get(key, "?")

                            if has_secret and key in secret_chances.get(user_id, {}):
                                if is_percent:
                                    diff = real_value - public_value
                                    diff_sign = "+" if diff > 0 else ""
                                    print(f"   🔒 {name}: {real_value}{suffix} (тайный, видит {public_value}{suffix} [{diff_sign}{diff}])")
                                else:
                                    diff = public_value - real_value  # Для костей: меньше = лучше
                                    if diff > 0:
                                        print(f"   🔒 {name}: {real_value}{suffix} (тайный, видит {public_value}{suffix} [лучше на {diff}])")
                                    elif diff < 0:
                                        print(f"   🔒 {name}: {real_value}{suffix} (тайный, видит {public_value}{suffix} [хуже на {abs(diff)}])")
                                    else:
                                        print(f"   🔒 {name}: {real_value}{suffix} (тайный, видит {public_value}{suffix})")
                            else:
                                print(f"   📊 {name}: {real_value}{suffix} (публичный)")

                        # Шансы ограбления
                        print("\n🏦 ОГРАБЛЕНИЕ КАЗНЫ:")
                        robbery_chances = [
                            ("Успех", "treasury_rob_success", True, "%"),
                            ("Побег", "treasury_rob_escape", True, "%"),
                            ("Поимка", "treasury_rob_caught", True, "%")
                        ]

                        for name, key, is_percent, suffix in robbery_chances:
                            real_value = user_real_chances.get(key, "?")
                            public_value = CHANCE_SETTINGS.get(key, "?")

                            if has_secret and key in secret_chances.get(user_id, {}):
                                diff = real_value - public_value
                                diff_sign = "+" if diff > 0 else ""
                                print(f"   🔒 {name}: {real_value}{suffix} (тайный, видит {public_value}{suffix} [{diff_sign}{diff}])")
                            else:
                                print(f"   📊 {name}: {real_value}{suffix} (публичный)")

                        print("═" * 50)
                        if has_secret:
                            print("⚠️ У пользователя есть тайные шансы!")
                        else:
                            print("✅ Пользователь использует публичные шансы")

                    except Exception as e:
                        print(f"❌ Ошибка: {e}")

                elif command == "help":
                    print("\n" + "="*60)
                    print("📚 ДОСТУПНЫЕ КОНСОЛЬНЫЕ КОМАНДЫ ДЛЯ ТАЙНЫХ ШАНСОВ")
                    print("="*60)
                    print("\n📋 Информация:")
                    print("  • secret list - список пользователей с тайными шансами")
                    print("  • secret check [id] - детальная проверка шансов пользователя")

                    print("\n⚙️ Установка всех шансов казино (просто):")
                    print("  • secret set [id] [%] all - установить ВСЕ шансы казино")
                    print("      Пример: secret set 123456789 80 all")
                    print("      Это установит: слоты, монетку, рулетку = 80%")
                    print("                     джекпот = 10%, кости порог = 5")

                    print("\n⚙️ Установка конкретных значений (продвинуто):")
                    print("  • secret setall [id] [слоты] [джекпот] [монетка] [кости] [рулетка] [успех] [побег]")
                    print("      Пример: secret setall 123456789 50 10 45 4 46 40 30")
                    print("      Последние два параметра опциональны (для ограбления)")

                    print("\n⚙️ Установка отдельных шансов:")
                    print("  • secret set [id] [%] robbery - все шансы ограбления")
                    print("  • secret set [id] [%] robbery_success - только успех")
                    print("  • secret set [id] [%] robbery_escape - только побег")
                    print("  • secret set [id] [%] robbery_caught - только поимка")
                    print("  • secret set [id] [значение] dice - порог костей (2-12)")

                    print("\n🗑️ Очистка:")
                    print("  • secret reset [id] - сбросить тайные шансы для пользователя")
                    print("  • secret clear - очистить все тайные шансы")

                    print("\n🚪 Выход:")
                    print("  • exit - выйти из консольного режима")
                    print("  • help - показать эту справку")
                    print("\n" + "="*60)

                elif command == "":
                    continue

                else:
                    print("❌ Неизвестная команда. Введите 'help' для списка команд")

            except KeyboardInterrupt:
                print("\n👋 Возвращаемся к основному боту...")
                break
            except Exception as e:
                print(f"❌ Ошибка в консоли: {e}")
                import traceback
                traceback.print_exc()

    # Запускаем консоль в отдельном потоке
   # console_thread = threading.Thread(target=console_commands, daemon=True)
   # console_thread.start()

    offset = None
    stats_update_interval = 1
    cleanup_interval = 300  # 5 минут

    update_channel_stats(data)
    last_stats_update = time.time()
    last_cleanup = time.time()

    print("✅ Бот запущен и готов к работе!")
    print("💬 Команды бота работают параллельно с консолью\n")

    while True:
        try:
            updates = get_updates(offset)

            if updates and updates.get("ok"):
                for update in updates.get("result", []):
                    offset = update["update_id"] + 1

                    if "message" in update:
                        process_message(data, update["message"])
                    elif "callback_query" in update:
                        handle_callback_query(data, update["callback_query"])

            current_time = time.time()

            # Обновляем статистику в канале
            if current_time - last_stats_update >= stats_update_interval:
                data = load_data()
                update_channel_stats(data)
                last_stats_update = current_time

            # Очищаем истекшие бустеры
            if current_time - last_cleanup >= cleanup_interval:
                cleaned = cleanup_expired_boosters(data)
                if cleaned > 0:
                    print(f"🧹 Очищено {cleaned} истекших бустеров")
                last_cleanup = current_time

            time.sleep(0.5)

        except KeyboardInterrupt:
            print("\n👋 Бот остановлен")
            break
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
from flask import Flask
from threading import Thread
import os

# Создаем Flask приложение
app = Flask(__name__)

# Обязательно добавь простую главную страницу
@app.route('/')
def home():
    return "Bot is running!"

# Leapcell будет проверять этот адрес
@app.route('/kaithheathcheck')
def health():
    return "OK", 200

def run():
    # КРИТИЧЕСКИ ВАЖНО: слушать порт 8080
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)

# Запускаем Flask в отдельном потоке
flask_thread = Thread(target=run)
flask_thread.daemon = True
flask_thread.start()
print("✅ Веб-сервер для Leapcell запущен на порту 8080")
