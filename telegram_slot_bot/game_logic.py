from typing import Dict, Optional
from database import Database
import logging

logger = logging.getLogger(__name__)


class GameLogic:
    """Игровая логика слот-машины"""

    # Таблица выплат (в игровых звёздах)
    # RTP 57.8% при цене спина 20 Stars
    # Используем только UNLIMITED подарки (доступны всегда!)
    PAYOUTS = {
        "🍒🍒🍒": 25,   # 1.25x - Малый приз
        "🍋🍋🍋": 50,   # 2.5x - Хороший приз
        "🍇🍇🍇": 50,   # 2.5x - Хороший приз
        "7️⃣7️⃣7️⃣": 100, # 5x - ДЖЕКПОТ!
    }

    # Соответствие dice_value и комбинаций
    # ВАЖНО: Эти значения примерные и требуют тестирования!
    # Telegram Dice API возвращает значения от 1 до 64
    # Точную таблицу нужно определить через тестирование
    DICE_TO_COMBO = {
        1: "🍒🍒🍒",      # Три вишни (предположительно)
        22: "🍋🍋🍋",     # Три лимона (предположительно)
        43: "🍇🍇🍇",     # Три винограда (предположительно)
        64: "7️⃣7️⃣7️⃣",    # Три семёрки - джекпот (предположительно)
    }

    def __init__(self, database: Database):
        self.db = database

    def check_win(self, dice_value: int) -> Dict:
        """
        Проверка выигрыша по значению dice

        Args:
            dice_value: значение от Telegram Dice API (1-64)

        Returns:
            dict: {
                'win': bool,
                'combination': str or None,
                'payout': int,
                'combo_emoji': str or None
            }
        """
        combination = self.DICE_TO_COMBO.get(dice_value)

        # Записываем dice_value в БД для статистики
        self.db.record_dice_value(
            dice_value=dice_value,
            combination=combination,
            is_win=combination is not None,
            payout_multiplier=self.PAYOUTS.get(combination, 0) / 35 if combination else 0
        )

        if combination:
            payout = self.PAYOUTS[combination]
            logger.info(f"Win! dice_value={dice_value}, combo={combination}, payout={payout}")
            return {
                'win': True,
                'combination': combination,
                'payout': payout,
                'combo_emoji': combination
            }
        else:
            logger.debug(f"No win. dice_value={dice_value}")
            return {
                'win': False,
                'combination': None,
                'payout': 0,
                'combo_emoji': None
            }

    def calculate_theoretical_rtp(self) -> Optional[float]:
        """
        Расчёт теоретического RTP на основе собранной статистики

        Returns:
            float: RTP в процентах или None если недостаточно данных
        """
        dice_stats = self.db.get_dice_statistics()

        if not dice_stats:
            return None

        total_occurrences = sum(stat.occurrence_count for stat in dice_stats)

        if total_occurrences < 100:  # Минимум 100 спинов для расчёта
            return None

        # Расчёт expected value
        expected_return = 0
        for stat in dice_stats:
            probability = stat.occurrence_count / total_occurrences
            payout = self.PAYOUTS.get(stat.combination, 0)
            expected_return += probability * payout

        # RTP = (expected return / spin cost) * 100
        spin_cost = 35
        rtp = (expected_return / spin_cost) * 100

        logger.info(f"Theoretical RTP calculated: {rtp:.2f}% (based on {total_occurrences} spins)")
        return rtp

    def get_payout_table(self) -> Dict[str, int]:
        """Получить таблицу выплат"""
        return self.PAYOUTS.copy()

    def get_win_combinations_count(self) -> int:
        """Получить количество выигрышных комбинаций"""
        return len(self.DICE_TO_COMBO)

    def get_max_payout(self) -> int:
        """Получить максимальный выигрыш"""
        return max(self.PAYOUTS.values())

    def get_min_payout(self) -> int:
        """Получить минимальный выигрыш"""
        return min(self.PAYOUTS.values())
