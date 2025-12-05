"""
Публичный чат-бот с игрой 🎰 для Telegram группы/канала

Механика:
1. Пользователи платят 35 Telegram Stars за возможность отправить сообщение в группу
2. Обычно отправляют dice стикер (🎰)
3. Telegram автоматически анимирует dice и выдаёт результат
4. Бот проверяет результат и начисляет выигрыш звёздами если есть
5. Блокируются: пересланные сообщения, текст, обычные стикеры
6. 3 страйка = перманентный бан
"""

import os
import logging
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    ChatMemberHandler
)
from telegram.error import BadRequest, TimedOut, NetworkError
from dotenv import load_dotenv
from database import Database
from game_logic import GameLogic
from ton_wallet import TONWallet, TONPaymentService
from userbot_manager import UserBotManager

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация
DATABASE_URL = os.getenv('DATABASE_URL')
db = Database(DATABASE_URL)
game = GameLogic(db)

# TON Wallet инициализация
ton_wallet = None
ton_payment_service = None
TON_ENABLED = False

# User-bot для отправки подарков
userbot_manager = None
USERBOT_ENABLED = False

# Константы
MESSAGE_COST = int(os.getenv('MESSAGE_COST', 20))  # Стоимость отправки сообщения
ADMIN_IDS = [int(admin_id) for admin_id in os.getenv('ADMIN_IDS', '').split(',') if admin_id]
MAX_STRIKES = 3  # Максимум страйков до бана


def is_admin(user_id: int) -> bool:
    """Проверка, является ли пользователь администратором"""
    return user_id in ADMIN_IDS


async def initialize_ton_wallet():
    """Инициализация TON кошелька при запуске бота"""
    global ton_wallet, ton_payment_service, TON_ENABLED

    ton_mnemonic = os.getenv('TON_WALLET_MNEMONIC')
    ton_testnet = os.getenv('TON_TESTNET', 'False').lower() == 'true'

    if not ton_mnemonic:
        logger.warning("TON_WALLET_MNEMONIC not found in .env - TON payments disabled")
        logger.warning("Run 'python setup_ton_wallet.py' to configure TON wallet")
        return

    try:
        logger.info("Initializing TON wallet...")
        ton_wallet = TONWallet(ton_mnemonic, testnet=ton_testnet)

        if await ton_wallet.initialize():
            ton_payment_service = TONPaymentService(ton_wallet)
            TON_ENABLED = True
            logger.info(f"✅ TON payments enabled! Wallet: {ton_wallet.address}")

            balance = await ton_wallet.get_balance()
            logger.info(f"💎 Wallet balance: {balance} TON")

            if balance < 0.1:
                logger.warning(f"⚠️ Low balance! Please top up the wallet")
        else:
            logger.error("Failed to initialize TON wallet - TON payments disabled")
    except Exception as e:
        logger.error(f"Error initializing TON wallet: {e}")


async def initialize_userbot():
    """Инициализация User-bot для отправки подарков"""
    global userbot_manager, USERBOT_ENABLED

    try:
        logger.info("Initializing User-bot for gift sending...")
        userbot_manager = UserBotManager()

        if await userbot_manager.start():
            USERBOT_ENABLED = True
            logger.info("✅ User-bot enabled! Gift sending ready")
            logger.info(f"   Available gifts: 100, 200, 350, 500 Stars")
        else:
            logger.error("Failed to initialize User-bot - gift sending disabled")
            logger.warning("Run 'python quick_auth.py' to configure User-bot")
    except Exception as e:
        logger.error(f"Error initializing User-bot: {e}")
        logger.warning("User-bot disabled - winners will need manual payouts")


async def send_ton_payout(user_id: int, stars_amount: int, context: ContextTypes.DEFAULT_TYPE):
    """
    Отправить автоматическую выплату в TON пользователю

    Args:
        user_id: Telegram ID пользователя
        stars_amount: Количество stars для конвертации в TON
        context: Telegram context
    """
    global ton_payment_service

    if not TON_ENABLED or not ton_payment_service:
        logger.warning(f"TON payments disabled - cannot send payout to user {user_id}")
        return

    try:
        # Получаем TON адрес пользователя
        user_ton_address = db.get_user_ton_address(user_id)

        if not user_ton_address:
            logger.warning(f"User {user_id} has no TON address - payout skipped")
            # Отправляем сообщение пользователю с инструкцией
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"🎉 Вы выиграли {stars_amount} stars!\n\n"
                         f"Для получения выплаты в TON, отправьте мне команду:\n"
                         f"/setaddress <ваш_TON_адрес>\n\n"
                         f"Пример: /setaddress UQAbc123..."
                )
            except Exception as e:
                logger.error(f"Failed to send TON address request to user {user_id}: {e}")
            return

        # Проверяем баланс
        if not await ton_payment_service.check_balance_sufficient(stars_amount):
            logger.error(f"Insufficient balance for payout to user {user_id}")
            # Уведомляем админов
            for admin_id in ADMIN_IDS:
                try:
                    await context.bot.send_message(
                        chat_id=admin_id,
                        text=f"⚠️ INSUFFICIENT TON BALANCE!\n\n"
                             f"Cannot send payout to user {user_id}\n"
                             f"Amount: {stars_amount} stars → {ton_payment_service.stars_to_ton(stars_amount)} TON\n\n"
                             f"Please top up the wallet!"
                    )
                except Exception:
                    pass
            return

        # Создаем запись транзакции
        ton_amount = ton_payment_service.stars_to_ton(stars_amount)
        transaction = db.create_ton_transaction(
            user_id=user_id,
            amount_stars=stars_amount,
            amount_ton=ton_amount,
            destination=user_ton_address,
            status='pending'
        )

        logger.info(f"Sending {ton_amount} TON to user {user_id} at {user_ton_address}")

        # Отправляем TON
        result = await ton_payment_service.send_payout(
            user_ton_address=user_ton_address,
            stars_amount=stars_amount,
            user_id=user_id
        )

        if result and result.get('success'):
            # Обновляем статус транзакции
            db.update_ton_transaction_status(
                transaction_id=transaction.id,
                status='confirmed',
                transaction_hash=result.get('hash', 'N/A')
            )

            logger.info(f"✅ TON payout successful! User {user_id}, amount: {ton_amount} TON")

            # Уведомляем пользователя
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"✅ Выплата отправлена!\n\n"
                         f"💰 Сумма: {ton_amount} TON\n"
                         f"📍 Адрес: {user_ton_address[:8]}...{user_ton_address[-6:]}\n\n"
                         f"Транзакция будет подтверждена через 10-30 секунд"
                )
            except Exception as e:
                logger.error(f"Failed to send payout notification to user {user_id}: {e}")

        else:
            # Ошибка отправки
            db.update_ton_transaction_status(
                transaction_id=transaction.id,
                status='failed'
            )
            logger.error(f"❌ TON payout failed! User {user_id}, amount: {ton_amount} TON")

            # Уведомляем админов
            for admin_id in ADMIN_IDS:
                try:
                    await context.bot.send_message(
                        chat_id=admin_id,
                        text=f"❌ TON PAYOUT FAILED!\n\n"
                             f"User: {user_id}\n"
                             f"Amount: {ton_amount} TON\n"
                             f"Address: {user_ton_address}\n\n"
                             f"Please check manually!"
                    )
                except Exception:
                    pass

    except Exception as e:
        logger.error(f"Error in send_ton_payout: {e}", exc_info=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start - приветствие в личке"""
    if update.effective_chat.type != 'private':
        return  # Игнорируем в группах

    user = update.effective_user
    db_user = db.get_or_create_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )

    welcome_text = f"""
🎰 <b>Добро пожаловать в Slot Chat Bot!</b>

💰 <b>Как играть:</b>

1️⃣ Вступите в нашу группу: @your_slot_group
2️⃣ Купите право на отправку сообщения за {MESSAGE_COST} ⭐
3️⃣ Отправьте dice стикер 🎰 в группу
4️⃣ Если выигрыш - получите звёзды обратно!

🏆 <b>Таблица выплат:</b>
🍒🍒🍒 = 100 ⭐
🍋🍋🍋 = 200 ⭐
🍇🍇🍇 = 350 ⭐
7️⃣7️⃣7️⃣ = 500 ⭐ (Джекпот!)

⚠️ <b>ПРАВИЛА:</b>
• Разрешены только dice стикеры
• Запрещены: текст, пересланные сообщения, обычные стикеры
• За нарушение - страйк
• 3 страйка = перманентный бан

📊 <b>Ваш баланс:</b> {db_user.balance} ⭐
⚡ <b>Страйков:</b> {db_user.strikes}/3

<b>Команды:</b>
/balance - Проверить баланс
/buy - Купить звёзды
/stats - Статистика
/rules - Правила
    """

    await update.message.reply_text(welcome_text, parse_mode='HTML')


async def handle_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка всех сообщений в группе

    Логика:
    1. Проверяем, не забанен ли пользователь
    2. Проверяем тип сообщения (dice, текст, стикер и т.д.)
    3. Если запрещённый тип - выдаём страйк и удаляем
    4. Если dice - проверяем результат и начисляем выигрыш
    """

    try:
        logger.info(f"[GROUP MESSAGE] Получено сообщение от {update.effective_user.id} в чате {update.effective_chat.id}")
        logger.info(f"[GROUP MESSAGE] Тип чата: {update.effective_chat.type}")

        # Игнорируем сообщения от ботов
        if update.effective_user.is_bot:
            logger.info("[GROUP MESSAGE] Игнорируем сообщение от бота")
            return

        user_id = update.effective_user.id
        logger.info(f"[GROUP MESSAGE] Получаем пользователя {user_id} из БД...")
        user = db.get_user(user_id)
        logger.info(f"[GROUP MESSAGE] Пользователь получен: {user}")

        # Если пользователя нет в БД - создаём
        if not user:
            user = db.get_or_create_user(
                user_id=user_id,
                username=update.effective_user.username,
                first_name=update.effective_user.first_name,
                last_name=update.effective_user.last_name
            )

        # Проверяем бан
        if user.is_banned:
            try:
                await update.message.delete()
                await context.bot.ban_chat_member(
                    chat_id=update.effective_chat.id,
                    user_id=user_id
                )
            except BadRequest:
                pass
            return

        # Админы могут писать всё
        if is_admin(user_id):
            return

        message = update.message

        # Проверка на пересланное сообщение
        if message.forward_origin:
            await give_strike(update, context, user_id, "Пересланные сообщения запрещены")
            return

        # Проверка типа сообщения
        if message.dice:
            # Это dice стикер - разрешено!
            logger.info(f"[GROUP MESSAGE] Dice обнаружен! Значение: {message.dice.value}")
            await handle_dice(update, context, user, message.dice)
            return

        # Любой другой тип сообщения - запрещён
        if message.text or message.sticker or message.photo or message.video or message.document:
            violation_type = "текстовые сообщения" if message.text else "стикеры/медиа"
            logger.info(f"[GROUP MESSAGE] Запрещенный тип: {violation_type}")
            await give_strike(update, context, user_id, f"Запрещены {violation_type}. Разрешены только dice 🎰")
            return

    except Exception as e:
        logger.error(f"[GROUP MESSAGE] Ошибка обработки сообщения: {e}", exc_info=True)


async def give_strike(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, reason: str):
    """Выдать страйк пользователю"""

    # Удаляем сообщение
    try:
        await update.message.delete()
    except BadRequest:
        pass

    # Увеличиваем счётчик страйков
    user = db.get_user(user_id)
    user.strikes += 1
    user.last_strike_at = datetime.utcnow()
    db.session.commit()

    logger.info(f"Strike given to user {user_id}: {reason}. Total strikes: {user.strikes}")

    # Если 3 страйка - бан
    if user.strikes >= MAX_STRIKES:
        user.is_banned = True
        user.ban_reason = f"Автоматический бан за {MAX_STRIKES} страйка"
        db.session.commit()

        try:
            # Баним в группе
            await context.bot.ban_chat_member(
                chat_id=update.effective_chat.id,
                user_id=user_id
            )

            # Уведомляем в группу
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"❌ Пользователь @{update.effective_user.username or update.effective_user.first_name} "
                     f"заблокирован за {MAX_STRIKES} нарушения"
            )
        except BadRequest as e:
            logger.error(f"Failed to ban user {user_id}: {e}")

    else:
        # Предупреждение
        try:
            warning_msg = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"⚠️ @{update.effective_user.username or update.effective_user.first_name}\n"
                     f"<b>Страйк {user.strikes}/{MAX_STRIKES}</b>\n"
                     f"Причина: {reason}",
                parse_mode='HTML'
            )

            # Удаляем предупреждение через 10 секунд
            import asyncio
            await asyncio.sleep(10)
            try:
                await warning_msg.delete()
            except:
                pass
        except BadRequest:
            pass


async def handle_dice(update: Update, context: ContextTypes.DEFAULT_TYPE, user, dice):
    """
    Обработка dice стикера

    1. Ждём результат анимации (~3 секунды)
    2. Проверяем выигрыш
    3. Начисляем звёзды если выигрыш
    """

    user_id = user.user_id
    dice_value = dice.value

    logger.info(f"User {user_id} sent dice: {dice_value}")

    # Записываем в статистику
    db.record_dice_value(dice_value)

    # Обновляем статистику пользователя
    user.total_spins += 1
    user.last_spin_at = datetime.utcnow()
    db.session.commit()

    # Ждём анимацию
    import asyncio
    await asyncio.sleep(3.5)

    # Проверяем выигрыш
    result = game.check_win(dice_value)

    if result['win']:
        # ВЫИГРЫШ!
        payout = result['payout']

        # Начисляем звёзды
        db.update_balance(user_id, payout)

        # Логируем транзакцию
        transaction = db.log_transaction(
            user_id=user_id,
            transaction_type='win',
            amount=payout,
            dice_value=dice_value,
            combination=result['combination'],
            description=f"Выигрыш в группе: {result['combination']}"
        )

        # Обновляем статистику
        user_updated = db.get_user(user_id)

        # Отправляем уведомление о выигрыше в группу (с retry при таймауте)
        max_retries = 3
        for attempt in range(max_retries):
            try:
                win_msg = await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"Congrats! ⭐️ will be sent soon",
                    reply_to_message_id=update.message.message_id
                )
                break  # Успешно отправлено
            except (TimedOut, NetworkError) as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Timeout on attempt {attempt + 1}/{max_retries}, retrying...")
                    await asyncio.sleep(2)  # Ждём 2 секунды перед повтором
                else:
                    logger.error(f"Failed to send win message after {max_retries} attempts: {e}")
            except BadRequest as e:
                logger.error(f"Failed to send win message: {e}")
                break

        logger.info(f"User {user_id} won {payout} stars with dice {dice_value}")

        # Автоматическая отправка подарка через User-bot
        if USERBOT_ENABLED and userbot_manager:
            try:
                logger.info(f"Attempting to send {payout} Stars gift to user {user_id}")

                success = await userbot_manager.send_gift(
                    user_id=user_id,
                    stars_amount=payout,
                    message=f"🎰 Поздравляем! Вы выиграли {payout} ⭐ Stars!\n\nКомбинация: {result['combination']}"
                )

                if success:
                    logger.info(f"✅ Gift {payout} Stars sent successfully to user {user_id}")

                    # Уведомляем админов об успешной выплате
                    user = update.effective_user
                    for admin_id in ADMIN_IDS:
                        try:
                            await context.bot.send_message(
                                chat_id=admin_id,
                                text=f"✅ Автоматическая выплата\n\n"
                                     f"Игрок: @{user.username or 'NoUsername'}\n"
                                     f"Имя: {user.first_name}\n"
                                     f"Выигрыш: {payout} ⭐ Stars\n"
                                     f"Комбинация: {result['combination']}\n"
                                     f"Группа: {update.effective_chat.title}\n\n"
                                     f"Подарок отправлен через User-bot!",
                                parse_mode='Markdown'
                            )
                        except Exception as e:
                            logger.error(f"Failed to notify admin: {e}")
                else:
                    logger.error(f"❌ Failed to send gift to user {user_id}")
                    # Если не получилось - отправляем уведомление админу о необходимости ручной выплаты
                    await send_manual_payout_notification(context, update, user_id, payout, result, dice_value)

            except Exception as e:
                logger.error(f"Error sending gift via userbot: {e}")
                # Если ошибка - отправляем уведомление админу о необходимости ручной выплаты
                await send_manual_payout_notification(context, update, user_id, payout, result, dice_value)
        else:
            # User-bot отключен - отправляем уведомление админу о необходимости ручной выплаты
            await send_manual_payout_notification(context, update, user_id, payout, result, dice_value)


async def send_manual_payout_notification(context, update, user_id, payout, result, dice_value):
    """Отправка уведомления админу о необходимости ручной выплаты"""
    user = update.effective_user

    for admin_id in ADMIN_IDS:
        try:
            admin_message = (
                f"🎰 **ТРЕБУЕТСЯ ВЫПЛАТА ЗВЁЗД!**\n\n"
                f"Игрок: @{user.username or 'NoUsername'}\n"
                f"Имя: {user.first_name}\n"
                f"ID: `{user.id}`\n"
                f"Выигрыш: **{payout} звёзд** ⭐\n"
                f"Dice value: {dice_value}\n"
                f"Группа: {update.effective_chat.title}\n\n"
                f"**Как выплатить:**\n"
            )

            if user.username:
                admin_message += f"1. Найдите: @{user.username}\n"
            else:
                admin_message += f"1. Найдите: [Открыть профиль](tg://user?id={user.id})\n"

            admin_message += (
                f"2. Профиль → Меню → Отправить подарок\n"
                f"3. Выберите {payout} звёзд\n"
                f"4. Отправьте"
            )

            await context.bot.send_message(
                chat_id=admin_id,
                text=admin_message,
                parse_mode='Markdown'
            )
            logger.info(f"✅ Уведомление отправлено админу {admin_id}")
        except Exception as e:
            logger.error(f"❌ Ошибка отправки уведомления админу {admin_id}: {e}")


async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /balance - показать баланс (только в личке)"""
    if update.effective_chat.type != 'private':
        return

    user_id = update.effective_user.id
    user = db.get_user(user_id)

    if not user:
        await update.message.reply_text("❌ Используйте /start сначала")
        return

    text = f"""
💰 <b>Ваш баланс</b>

Звёзды: <b>{user.balance} ⭐</b>
Спинов: {user.total_spins}
Выиграно: {user.total_won} ⭐

⚡ Страйков: <b>{user.strikes}/3</b>
    """

    await update.message.reply_text(text, parse_mode='HTML')


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /stats - статистика (только в личке)"""
    if update.effective_chat.type != 'private':
        return

    user_id = update.effective_user.id
    stats = db.get_user_stats(user_id)

    if not stats:
        await update.message.reply_text("❌ Используйте /start сначала")
        return

    text = f"""
📊 <b>Ваша статистика</b>

🎰 Всего спинов: <b>{stats['total_spins']}</b>
🏆 Всего выиграно: <b>{stats['total_won']} ⭐</b>
💎 Самый большой выигрыш: <b>{stats['biggest_win']} ⭐</b>
💰 Текущий баланс: <b>{stats['balance']} ⭐</b>

⚡ Страйков: <b>{db.get_user(user_id).strikes}/3</b>
    """

    await update.message.reply_text(text, parse_mode='HTML')


async def rules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /rules - правила"""
    rules_text = """
📜 <b>ПРАВИЛА ГРУППЫ</b>

✅ <b>РАЗРЕШЕНО:</b>
• Отправка dice стикера 🎰

❌ <b>ЗАПРЕЩЕНО:</b>
• Текстовые сообщения
• Пересланные сообщения
• Обычные стикеры
• Фото, видео, файлы

⚠️ <b>СИСТЕМА СТРАЙКОВ:</b>
• 1 нарушение = 1 страйк
• 3 страйка = перманентный бан
• Страйки не сбрасываются

🏆 <b>ТАБЛИЦА ВЫПЛАТ:</b>
🍒🍒🍒 = 100 ⭐
🍋🍋🍋 = 200 ⭐
🍇🍇🍇 = 350 ⭐
7️⃣7️⃣7️⃣ = 500 ⭐ (Джекпот!)

💡 <b>Удачи в игре!</b>
    """

    await update.message.reply_text(rules_text, parse_mode='HTML')


# ==================== ADMIN COMMANDS ====================

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /adminstats - глобальная статистика (только для админов)"""
    user_id = update.effective_user.id

    if not is_admin(user_id):
        return

    stats = db.get_global_stats()

    text = f"""
📊 <b>Глобальная статистика</b>

👥 Всего пользователей: <b>{stats['total_users']}</b>
🎰 Всего спинов: <b>{stats['total_spins']}</b>
🏆 Всего выиграно: <b>{stats['total_won']} ⭐</b>
💹 Прибыль: <b>{stats['house_profit']} ⭐</b>
📈 RTP: <b>{stats['actual_rtp']:.2f}%</b>
    """

    await update.message.reply_text(text, parse_mode='HTML')


async def clear_strikes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /clearstrikes <user_id> - очистить страйки (админ)"""
    user_id = update.effective_user.id

    if not is_admin(user_id):
        return

    if len(context.args) < 1:
        await update.message.reply_text("Использование: /clearstrikes <user_id>")
        return

    try:
        target_user_id = int(context.args[0])
        user = db.get_user(target_user_id)

        if not user:
            await update.message.reply_text(f"❌ Пользователь {target_user_id} не найден")
            return

        old_strikes = user.strikes
        user.strikes = 0
        db.session.commit()

        await update.message.reply_text(
            f"✅ Страйки пользователя {target_user_id} очищены\n"
            f"Было: {old_strikes}, стало: 0"
        )
    except ValueError:
        await update.message.reply_text("❌ Неверный ID пользователя")


async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /unban <user_id> - разбанить (админ)"""
    user_id = update.effective_user.id

    if not is_admin(user_id):
        return

    if len(context.args) < 1:
        await update.message.reply_text("Использование: /unban <user_id>")
        return

    try:
        target_user_id = int(context.args[0])
        db.unban_user(target_user_id)

        # Разбаниваем в группе
        try:
            await context.bot.unban_chat_member(
                chat_id=update.effective_chat.id,
                user_id=target_user_id
            )
        except BadRequest:
            pass

        await update.message.reply_text(f"✅ Пользователь {target_user_id} разблокирован")
    except ValueError:
        await update.message.reply_text("❌ Неверный ID пользователя")


async def setaddress_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /setaddress - установить TON адрес для получения выплат"""
    if update.effective_chat.type != 'private':
        return

    user_id = update.effective_user.id

    if not context.args or len(context.args) == 0:
        await update.message.reply_text(
            "❌ Укажите ваш TON адрес\n\n"
            "Использование:\n"
            "/setaddress <TON_адрес>\n\n"
            "Пример:\n"
            "/setaddress UQAbc123...\n\n"
            "TON адрес можно найти в вашем кошельке (Tonkeeper, TON Wallet и т.д.)"
        )
        return

    ton_address = context.args[0].strip()

    # Базовая валидация TON адреса (начинается с UQ, EQ или kQ)
    if not (ton_address.startswith('UQ') or ton_address.startswith('EQ') or ton_address.startswith('kQ')):
        await update.message.reply_text(
            "❌ Неверный формат TON адреса\n\n"
            "TON адрес должен начинаться с UQ, EQ или kQ\n\n"
            "Пример правильного адреса:\n"
            "UQAbc123..."
        )
        return

    if len(ton_address) < 48:
        await update.message.reply_text(
            "❌ TON адрес слишком короткий\n\n"
            "Проверьте правильность адреса"
        )
        return

    # Сохраняем адрес
    db.set_user_ton_address(user_id, ton_address, verified=True)

    await update.message.reply_text(
        f"✅ TON адрес сохранён!\n\n"
        f"📍 Адрес: {ton_address[:8]}...{ton_address[-6:]}\n\n"
        f"Теперь все ваши выигрыши будут автоматически отправляться на этот адрес в течение 10-60 секунд после победы!\n\n"
        f"💎 Курс конвертации: 1000 stars = 1 TON"
    )

    logger.info(f"User {user_id} set TON address: {ton_address}")


async def myaddress_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /myaddress - показать текущий TON адрес"""
    if update.effective_chat.type != 'private':
        return

    user_id = update.effective_user.id
    ton_address = db.get_user_ton_address(user_id)

    if not ton_address:
        await update.message.reply_text(
            "❌ У вас не установлен TON адрес\n\n"
            "Используйте /setaddress <адрес> чтобы установить"
        )
        return

    await update.message.reply_text(
        f"💎 Ваш TON адрес:\n\n"
        f"{ton_address}\n\n"
        f"Все выигрыши будут автоматически отправляться на этот адрес"
    )


def main():
    """Запуск бота"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
        return

    # Создаём приложение
    application = Application.builder().token(token).build()

    # Команды (работают в личке)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("balance", balance_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("rules", rules_command))
    application.add_handler(CommandHandler("setaddress", setaddress_command))
    application.add_handler(CommandHandler("myaddress", myaddress_command))

    # Админ команды
    application.add_handler(CommandHandler("adminstats", admin_stats))
    application.add_handler(CommandHandler("clearstrikes", clear_strikes))
    application.add_handler(CommandHandler("unban", unban_user))

    # Обработка ВСЕХ сообщений в группах и суперг руппах
    application.add_handler(
        MessageHandler(
            (filters.ChatType.GROUP | filters.ChatType.SUPERGROUP) & ~filters.COMMAND,
            handle_group_message
        )
    )

    # Инициализация TON кошелька
    logger.info("Initializing TON wallet...")
    asyncio.get_event_loop().run_until_complete(initialize_ton_wallet())

    # Инициализация User-bot для подарков
    logger.info("Initializing User-bot...")
    asyncio.get_event_loop().run_until_complete(initialize_userbot())

    # Запускаем бота
    logger.info("🎰 Group Slot Bot запущен!")
    logger.info(f"MESSAGE_COST: {MESSAGE_COST} stars")
    logger.info(f"MAX_STRIKES: {MAX_STRIKES}")
    logger.info(f"TON PAYMENTS: {'✅ ENABLED' if TON_ENABLED else '❌ DISABLED'}")
    logger.info(f"USERBOT GIFTS: {'✅ ENABLED' if USERBOT_ENABLED else '❌ DISABLED'}")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
