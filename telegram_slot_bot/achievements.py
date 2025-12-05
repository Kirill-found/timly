from database import Database
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class AchievementManager:
    """Менеджер достижений"""

    # Определение всех достижений в игре
    ACHIEVEMENTS = [
        {
            'code': 'first_spin',
            'title': '🎰 Первый спин',
            'description': 'Сделайте свой первый спин',
            'icon': '🎰',
            'reward': 50,
            'requirement': 'Сделать 1 спин'
        },
        {
            'code': 'beginner',
            'title': '🌟 Новичок',
            'description': 'Сделайте 10 спинов',
            'icon': '🌟',
            'reward': 100,
            'requirement': 'Сделать 10 спинов'
        },
        {
            'code': 'experienced',
            'title': '⭐ Опытный',
            'description': 'Сделайте 100 спинов',
            'icon': '⭐',
            'reward': 500,
            'requirement': 'Сделать 100 спинов'
        },
        {
            'code': 'veteran',
            'title': '💫 Ветеран',
            'description': 'Сделайте 1000 спинов',
            'icon': '💫',
            'reward': 2000,
            'requirement': 'Сделать 1000 спинов'
        },
        {
            'code': 'first_win',
            'title': '🎉 Первая победа',
            'description': 'Выиграйте первый раз',
            'icon': '🎉',
            'reward': 100,
            'requirement': 'Выиграть хотя бы раз'
        },
        {
            'code': 'lucky_10',
            'title': '🍀 Везунчик',
            'description': 'Выиграйте 10 раз',
            'icon': '🍀',
            'reward': 300,
            'requirement': 'Выиграть 10 раз'
        },
        {
            'code': 'lucky_100',
            'title': '🎊 Счастливчик',
            'description': 'Выиграйте 100 раз',
            'icon': '🎊',
            'reward': 1000,
            'requirement': 'Выиграть 100 раз'
        },
        {
            'code': 'jackpot',
            'title': '💎 Джекпот!',
            'description': 'Выбейте три семёрки',
            'icon': '💎',
            'reward': 500,
            'requirement': 'Получить комбинацию 7️⃣7️⃣7️⃣'
        },
        {
            'code': 'big_spender',
            'title': '💸 Щедрый',
            'description': 'Потратьте 10,000 звёзд',
            'icon': '💸',
            'reward': 1000,
            'requirement': 'Потратить 10,000 звёзд'
        },
        {
            'code': 'mega_spender',
            'title': '💰 Магнат',
            'description': 'Потратьте 100,000 звёзд',
            'icon': '💰',
            'reward': 5000,
            'requirement': 'Потратить 100,000 звёзд'
        },
        {
            'code': 'rich',
            'title': '🤑 Богач',
            'description': 'Накопите 10,000 звёзд',
            'icon': '🤑',
            'reward': 1000,
            'requirement': 'Иметь баланс 10,000 звёзд'
        },
        {
            'code': 'millionaire',
            'title': '👑 Миллионер',
            'description': 'Накопите 100,000 звёзд',
            'icon': '👑',
            'reward': 10000,
            'requirement': 'Иметь баланс 100,000 звёзд'
        },
        {
            'code': 'big_win',
            'title': '🔥 Большой куш',
            'description': 'Выиграйте 500+ звёзд за один спин',
            'icon': '🔥',
            'reward': 500,
            'requirement': 'Выиграть 500+ звёзд за один спин'
        },
        {
            'code': 'dedicated',
            'title': '📅 Преданный',
            'description': 'Играйте 7 дней подряд',
            'icon': '📅',
            'reward': 700,
            'requirement': 'Делать хотя бы 1 спин в день 7 дней подряд'
        },
        {
            'code': 'achievement_hunter',
            'title': '🏆 Охотник за достижениями',
            'description': 'Получите 5 достижений',
            'icon': '🏆',
            'reward': 500,
            'requirement': 'Получить 5 других достижений'
        },
        {
            'code': 'collector',
            'title': '📚 Коллекционер',
            'description': 'Получите все достижения',
            'icon': '📚',
            'reward': 5000,
            'requirement': 'Получить все остальные достижения'
        }
    ]

    def __init__(self, database: Database):
        self.db = database

    def initialize_achievements(self):
        """Инициализация достижений в базе данных"""
        for achievement_data in self.ACHIEVEMENTS:
            existing = self.db.get_achievement_by_code(achievement_data['code'])
            if not existing:
                self.db.create_achievement(
                    code=achievement_data['code'],
                    title=achievement_data['title'],
                    description=achievement_data['description'],
                    icon=achievement_data['icon'],
                    reward=achievement_data['reward'],
                    requirement_description=achievement_data['requirement']
                )
                logger.info(f"Achievement created: {achievement_data['code']}")

    def check_and_unlock_achievements(self, user_id: int, trigger: str, **kwargs) -> List[str]:
        """
        Проверить и разблокировать достижения для пользователя

        Args:
            user_id: ID пользователя
            trigger: Триггер события ('spin', 'win', 'balance_change', etc.)
            **kwargs: Дополнительные параметры

        Returns:
            List[str]: Список кодов разблокированных достижений
        """
        user = self.db.get_user(user_id)
        if not user:
            return []

        unlocked = []

        # Проверяем различные достижения в зависимости от триггера
        if trigger == 'spin':
            # Первый спин
            if user.total_spins == 1 and not self.db.has_achievement(user_id, 'first_spin'):
                if self.db.unlock_achievement(user_id, 'first_spin'):
                    unlocked.append('first_spin')

            # Количество спинов
            if user.total_spins == 10 and not self.db.has_achievement(user_id, 'beginner'):
                if self.db.unlock_achievement(user_id, 'beginner'):
                    unlocked.append('beginner')

            if user.total_spins == 100 and not self.db.has_achievement(user_id, 'experienced'):
                if self.db.unlock_achievement(user_id, 'experienced'):
                    unlocked.append('experienced')

            if user.total_spins == 1000 and not self.db.has_achievement(user_id, 'veteran'):
                if self.db.unlock_achievement(user_id, 'veteran'):
                    unlocked.append('veteran')

            # Потрачено звёзд
            if user.total_wagered >= 10000 and not self.db.has_achievement(user_id, 'big_spender'):
                if self.db.unlock_achievement(user_id, 'big_spender'):
                    unlocked.append('big_spender')

            if user.total_wagered >= 100000 and not self.db.has_achievement(user_id, 'mega_spender'):
                if self.db.unlock_achievement(user_id, 'mega_spender'):
                    unlocked.append('mega_spender')

        elif trigger == 'win':
            win_amount = kwargs.get('win_amount', 0)
            combination = kwargs.get('combination', '')

            # Первая победа
            wins_count = kwargs.get('wins_count', 0)
            if wins_count == 1 and not self.db.has_achievement(user_id, 'first_win'):
                if self.db.unlock_achievement(user_id, 'first_win'):
                    unlocked.append('first_win')

            # Количество побед (нужно считать через транзакции)
            win_transactions = self.db.session.query(self.db.session.query(
                self.db.models.Transaction
            ).filter_by(user_id=user_id, transaction_type='win').count())

            # Упрощённый подсчёт побед
            from models import Transaction
            win_count = self.db.session.query(Transaction).filter_by(
                user_id=user_id,
                transaction_type='win'
            ).count()

            if win_count >= 10 and not self.db.has_achievement(user_id, 'lucky_10'):
                if self.db.unlock_achievement(user_id, 'lucky_10'):
                    unlocked.append('lucky_10')

            if win_count >= 100 and not self.db.has_achievement(user_id, 'lucky_100'):
                if self.db.unlock_achievement(user_id, 'lucky_100'):
                    unlocked.append('lucky_100')

            # Джекпот
            if combination == '7️⃣7️⃣7️⃣' and not self.db.has_achievement(user_id, 'jackpot'):
                if self.db.unlock_achievement(user_id, 'jackpot'):
                    unlocked.append('jackpot')

            # Большой выигрыш
            if win_amount >= 500 and not self.db.has_achievement(user_id, 'big_win'):
                if self.db.unlock_achievement(user_id, 'big_win'):
                    unlocked.append('big_win')

        elif trigger == 'balance_check':
            # Богатство
            if user.balance >= 10000 and not self.db.has_achievement(user_id, 'rich'):
                if self.db.unlock_achievement(user_id, 'rich'):
                    unlocked.append('rich')

            if user.balance >= 100000 and not self.db.has_achievement(user_id, 'millionaire'):
                if self.db.unlock_achievement(user_id, 'millionaire'):
                    unlocked.append('millionaire')

        elif trigger == 'achievement_unlock':
            # Охотник за достижениями
            if user.achievements_unlocked >= 5 and not self.db.has_achievement(user_id, 'achievement_hunter'):
                if self.db.unlock_achievement(user_id, 'achievement_hunter'):
                    unlocked.append('achievement_hunter')

            # Коллекционер (все достижения кроме этого)
            total_achievements = len(self.ACHIEVEMENTS) - 1  # Исключаем само достижение "Коллекционер"
            if user.achievements_unlocked >= total_achievements and not self.db.has_achievement(user_id, 'collector'):
                if self.db.unlock_achievement(user_id, 'collector'):
                    unlocked.append('collector')

        # После разблокировки проверяем мета-достижения
        if unlocked:
            meta_unlocked = self.check_and_unlock_achievements(user_id, 'achievement_unlock')
            unlocked.extend(meta_unlocked)

        return unlocked

    def get_achievement_progress(self, user_id: int) -> dict:
        """
        Получить прогресс по всем достижениям

        Returns:
            dict: Информация о прогрессе
        """
        user = self.db.get_user(user_id)
        if not user:
            return {}

        from models import Transaction
        win_count = self.db.session.query(Transaction).filter_by(
            user_id=user_id,
            transaction_type='win'
        ).count()

        progress = {
            'first_spin': user.total_spins >= 1,
            'beginner': user.total_spins >= 10,
            'experienced': user.total_spins >= 100,
            'veteran': user.total_spins >= 1000,
            'first_win': win_count >= 1,
            'lucky_10': win_count >= 10,
            'lucky_100': win_count >= 100,
            'jackpot': self.db.has_achievement(user_id, 'jackpot'),
            'big_spender': user.total_wagered >= 10000,
            'mega_spender': user.total_wagered >= 100000,
            'rich': user.balance >= 10000,
            'millionaire': user.balance >= 100000,
            'big_win': self.db.has_achievement(user_id, 'big_win'),
            'achievement_hunter': user.achievements_unlocked >= 5,
            'collector': user.achievements_unlocked >= len(self.ACHIEVEMENTS) - 1,
        }

        return progress

    def format_achievement_notification(self, achievement_code: str) -> str:
        """
        Форматировать уведомление о достижении

        Returns:
            str: Отформатированное сообщение
        """
        achievement = self.db.get_achievement_by_code(achievement_code)
        if not achievement:
            return ""

        return f"""
🎊 Новое достижение разблокировано!

{achievement.icon} {achievement.title}
{achievement.description}

💰 Награда: +{achievement.reward} ⭐️
"""
