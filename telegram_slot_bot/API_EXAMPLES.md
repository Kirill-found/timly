# 🔌 Примеры использования API - Telegram Slot Bot

## Примеры кода для расширения функционала

---

## 📊 Работа с базой данных

### Получение статистики пользователя

```python
from database import Database

db = Database('postgresql://user:pass@localhost/db')

# Получить статистику
stats = db.get_user_stats(user_id=123456789)

print(f"Спинов: {stats['total_spins']}")
print(f"Баланс: {stats['balance']}")
print(f"Прибыль: {stats['profit_loss']}")
```

### Создание пользователя

```python
user = db.get_or_create_user(
    user_id=123456789,
    username="john_doe",
    first_name="John",
    last_name="Doe"
)

print(f"Баланс: {user.balance}")
```

### Изменение баланса

```python
# Списать звёзды
db.update_balance(user_id=123456789, amount=-35)

# Начислить звёзды
db.update_balance(user_id=123456789, amount=100)
```

### Работа с транзакциями

```python
# Логировать транзакцию
db.log_transaction(
    user_id=123456789,
    transaction_type='bonus',
    amount=500,
    description='Ежедневный бонус'
)

# Получить историю
transactions = db.get_user_transactions(user_id=123456789, limit=10)
for tx in transactions:
    print(f"{tx.timestamp}: {tx.transaction_type} {tx.amount}")
```

---

## 🏆 Работа с достижениями

### Разблокировать достижение вручную

```python
from achievements import AchievementManager

achievements = AchievementManager(db)

# Разблокировать
achievement = db.unlock_achievement(
    user_id=123456789,
    achievement_code='first_spin'
)

if achievement:
    print("Достижение разблокировано!")
```

### Проверить наличие достижения

```python
has_jackpot = db.has_achievement(
    user_id=123456789,
    achievement_code='jackpot'
)

if has_jackpot:
    print("У пользователя есть джекпот!")
```

### Получить все достижения пользователя

```python
user_achievements = db.get_user_achievements(user_id=123456789)

for ua in user_achievements:
    achievement = db.session.query(Achievement).filter_by(id=ua.achievement_id).first()
    print(f"{achievement.icon} {achievement.title}")
```

### Создать новое достижение

```python
db.create_achievement(
    code='speedrunner',
    title='⚡ Спидраннер',
    description='Сделайте 100 спинов за час',
    icon='⚡',
    reward=1000,
    requirement_description='100 спинов за 1 час'
)
```

---

## 🎰 Игровая логика

### Проверка выигрыша

```python
from game_logic import GameLogic

game = GameLogic(db)

# После получения dice_value от Telegram
dice_value = 64  # Пример

result = game.check_win(dice_value)

if result['win']:
    print(f"Выигрыш! {result['combination']}")
    print(f"Выплата: {result['payout']}")
else:
    print("Проигрыш")
```

### Расчёт RTP

```python
theoretical_rtp = game.calculate_theoretical_rtp()

if theoretical_rtp:
    print(f"Теоретический RTP: {theoretical_rtp:.2f}%")
```

### Изменение таблицы выплат

```python
# В game_logic.py измените:
PAYOUTS = {
    "🍒🍒🍒": 150,   # Было 100
    "🍋🍋🍋": 300,   # Было 200
    "🍇🍇🍇": 500,   # Было 350
    "7️⃣7️⃣7️⃣": 1000, # Было 500
}
```

---

## 💳 Работа с платежами

### Создание платежа

```python
payment = db.create_payment(
    user_id=123456789,
    telegram_payment_charge_id="unique_charge_id",
    telegram_stars_amount=100,
    game_stars_amount=1000,
    provider_payment_charge_id="provider_id"
)
```

### Завершение платежа

```python
# Автоматически начислит звёзды пользователю
completed_payment = db.complete_payment(payment.id)

if completed_payment.status == 'completed':
    print("Платёж завершён!")
```

### Получить историю платежей

```python
payments = db.get_user_payments(user_id=123456789)

for payment in payments:
    print(f"{payment.timestamp}: {payment.telegram_stars_amount} Stars -> {payment.game_stars_amount} ⭐️")
```

---

## 📈 Аналитика и статистика

### Глобальная статистика

```python
stats = db.get_global_stats()

print(f"""
Всего пользователей: {stats['total_users']}
Активных (24ч): {stats['active_users']}
Новых (24ч): {stats['new_users']}
RTP: {stats['actual_rtp']:.2f}%
Прибыль: {stats['house_profit']}
""")
```

### Топ игроков

```python
top_users = db.get_top_users(limit=10)

for i, user in enumerate(top_users, 1):
    print(f"{i}. @{user.username}: {user.balance} ⭐️")
```

### SQL запросы для аналитики

```python
from sqlalchemy import func
from models import Transaction

# Спинов за сегодня
today_spins = db.session.query(func.count(Transaction.id))\
    .filter(
        Transaction.transaction_type == 'spin',
        func.date(Transaction.timestamp) == func.current_date()
    ).scalar()

print(f"Спинов сегодня: {today_spins}")

# RTP за последние 7 дней
from datetime import datetime, timedelta
week_ago = datetime.utcnow() - timedelta(days=7)

wagered = db.session.query(func.sum(func.abs(Transaction.amount)))\
    .filter(
        Transaction.transaction_type == 'spin',
        Transaction.timestamp >= week_ago
    ).scalar() or 0

won = db.session.query(func.sum(Transaction.amount))\
    .filter(
        Transaction.transaction_type == 'win',
        Transaction.timestamp >= week_ago
    ).scalar() or 0

rtp_7d = (won / wagered * 100) if wagered > 0 else 0
print(f"RTP за 7 дней: {rtp_7d:.2f}%")
```

---

## 🤖 Добавление новых команд

### Простая команда

```python
# В bot.py

async def daily_bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /daily - ежедневный бонус"""
    user_id = update.effective_user.id
    user = db.get_user(user_id)

    # Проверка последнего бонуса
    if user.last_bonus_at:
        time_since = datetime.utcnow() - user.last_bonus_at
        if time_since.total_seconds() < 86400:  # 24 часа
            hours_left = 24 - (time_since.total_seconds() / 3600)
            await update.message.reply_text(
                f"⏰ Следующий бонус через {hours_left:.1f} часов"
            )
            return

    # Выдаём бонус
    bonus = 100
    db.update_balance(user_id, bonus)
    user.last_bonus_at = datetime.utcnow()
    db.session.commit()

    await update.message.reply_text(
        f"🎁 Вы получили ежедневный бонус: {bonus} ⭐️"
    )

# В main() добавьте:
application.add_handler(CommandHandler("daily", daily_bonus))
```

### Команда с параметрами

```python
async def send_gift(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /gift <user_id> <amount> - отправить подарок"""
    sender_id = update.effective_user.id

    if len(context.args) < 2:
        await update.message.reply_text(
            "Использование: /gift <user_id> <amount>"
        )
        return

    try:
        recipient_id = int(context.args[0])
        amount = int(context.args[1])

        # Проверка баланса
        sender = db.get_user(sender_id)
        if sender.balance < amount:
            await update.message.reply_text("❌ Недостаточно звёзд")
            return

        # Перевод
        db.update_balance(sender_id, -amount)
        db.update_balance(recipient_id, amount)

        # Логирование
        db.log_transaction(
            user_id=sender_id,
            transaction_type='gift_sent',
            amount=-amount,
            description=f"Подарок пользователю {recipient_id}"
        )

        db.log_transaction(
            user_id=recipient_id,
            transaction_type='gift_received',
            amount=amount,
            description=f"Подарок от пользователя {sender_id}"
        )

        await update.message.reply_text(
            f"✅ Отправлено {amount} ⭐️ пользователю {recipient_id}"
        )

    except ValueError:
        await update.message.reply_text("❌ Неверные параметры")

# Зарегистрировать:
application.add_handler(CommandHandler("gift", send_gift))
```

---

## 🎯 Inline кнопки

### Меню с кнопками

```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def games_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /games - меню игр"""

    keyboard = [
        [
            InlineKeyboardButton("🎰 Слоты", callback_data="game_slots"),
            InlineKeyboardButton("🎲 Кости", callback_data="game_dice")
        ],
        [
            InlineKeyboardButton("⚽ Футбол", callback_data="game_football"),
            InlineKeyboardButton("🏀 Баскетбол", callback_data="game_basketball")
        ],
        [InlineKeyboardButton("❌ Закрыть", callback_data="close")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🎮 Выберите игру:",
        reply_markup=reply_markup
    )

async def games_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий кнопок"""
    query = update.callback_query
    await query.answer()

    if query.data == "close":
        await query.message.delete()
        return

    game_type = query.data.replace("game_", "")
    await query.message.edit_text(f"Запускаем {game_type}...")

# Зарегистрировать:
application.add_handler(CommandHandler("games", games_menu))
application.add_handler(CallbackQueryHandler(games_callback, pattern='^game_'))
```

---

## 🔔 Уведомления и рассылки

### Отправка уведомления пользователю

```python
async def notify_user(context: ContextTypes.DEFAULT_TYPE, user_id: int, message: str):
    """Отправить уведомление пользователю"""
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=message,
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Failed to notify user {user_id}: {e}")
```

### Рассылка всем пользователям

```python
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /broadcast - рассылка всем (только админ)"""
    user_id = update.effective_user.id

    if not is_admin(user_id):
        return

    if len(context.args) < 1:
        await update.message.reply_text("Использование: /broadcast <текст>")
        return

    message = ' '.join(context.args)

    # Получить всех пользователей
    users = db.session.query(User).filter_by(is_banned=False).all()

    sent = 0
    failed = 0

    for user in users:
        try:
            await context.bot.send_message(
                chat_id=user.user_id,
                text=message,
                parse_mode='HTML'
            )
            sent += 1
            await asyncio.sleep(0.05)  # Защита от rate limit
        except Exception:
            failed += 1

    await update.message.reply_text(
        f"✅ Рассылка завершена\n"
        f"Отправлено: {sent}\n"
        f"Ошибок: {failed}"
    )

# Зарегистрировать:
application.add_handler(CommandHandler("broadcast", broadcast))
```

---

## ⏰ Запланированные задачи

### Ежедневная задача

```python
from telegram.ext import Application
import asyncio

async def daily_task(application: Application):
    """Ежедневная задача"""
    while True:
        await asyncio.sleep(86400)  # 24 часа

        # Пример: начислить бонус всем активным пользователям
        active_users = db.session.query(User)\
            .filter(User.last_spin_at >= datetime.utcnow() - timedelta(days=1))\
            .all()

        for user in active_users:
            db.update_balance(user.user_id, 50)
            db.log_transaction(
                user_id=user.user_id,
                transaction_type='bonus',
                amount=50,
                description='Бонус за активность'
            )

            # Уведомить
            try:
                await application.bot.send_message(
                    chat_id=user.user_id,
                    text="🎁 Вы получили бонус 50 ⭐️ за активность!"
                )
            except Exception:
                pass

# В main() добавьте:
application.job_queue.run_repeating(
    callback=daily_task,
    interval=86400,  # каждые 24 часа
    first=10  # первый запуск через 10 секунд
)
```

---

## 🎨 Форматирование сообщений

### HTML форматирование

```python
text = """
<b>Жирный текст</b>
<i>Курсив</i>
<u>Подчёркнутый</u>
<code>Моноширинный</code>
<pre>Блок кода</pre>
<a href="https://example.com">Ссылка</a>
"""

await update.message.reply_text(text, parse_mode='HTML')
```

### Markdown форматирование

```python
text = """
*Жирный текст*
_Курсив_
`Моноширинный`
```Блок кода```
[Ссылка](https://example.com)
"""

await update.message.reply_text(text, parse_mode='MarkdownV2')
```

---

## 🛡️ Middleware и фильтры

### Проверка бана перед каждой командой

```python
def check_ban(func):
    """Декоратор для проверки бана"""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id

        if db.is_user_banned(user_id):
            await update.message.reply_text(
                "❌ Вы заблокированы в этом боте."
            )
            return

        return await func(update, context)

    return wrapper

# Использование:
@check_ban
async def spin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... код команды spin
    pass
```

### Rate limiting

```python
from collections import defaultdict
from datetime import datetime

user_last_action = defaultdict(lambda: datetime.min)

def rate_limit(seconds=3):
    """Декоратор для ограничения частоты команд"""
    def decorator(func):
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            user_id = update.effective_user.id
            now = datetime.now()

            if (now - user_last_action[user_id]).total_seconds() < seconds:
                await update.message.reply_text(
                    "⏰ Пожалуйста, подождите немного"
                )
                return

            user_last_action[user_id] = now
            return await func(update, context)

        return wrapper
    return decorator

# Использование:
@rate_limit(seconds=5)
async def spin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Пользователь может крутить спин раз в 5 секунд
    pass
```

---

**Эти примеры помогут вам расширить функционал бота! 🚀**
