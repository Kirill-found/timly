"""
Проверка прогресса сбора статистики
"""

import os
import glob
from datetime import datetime

print("\n" + "="*60)
print("    ПРОВЕРКА ПРОГРЕССА")
print("="*60 + "\n")

# Ищем CSV файлы
csv_files = glob.glob("dice_stats_*.csv")

if csv_files:
    latest_csv = max(csv_files, key=os.path.getctime)
    print(f"Найден файл: {latest_csv}")

    # Читаем файл
    with open(latest_csv, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    total_lines = len(lines) - 1  # минус заголовок
    print(f"Собрано бросков: {total_lines}")

    if total_lines > 0:
        # Показываем последние 5 строк
        print("\nПоследние 5 бросков:")
        for line in lines[-5:]:
            print("  " + line.strip())

        # Время
        created = datetime.fromtimestamp(os.path.getctime(latest_csv))
        print(f"\nФайл создан: {created.strftime('%H:%M:%S')}")
        print(f"Текущее время: {datetime.now().strftime('%H:%M:%S')}")

        # Оценка оставшегося времени
        target = 1000
        if total_lines < target:
            remaining = target - total_lines
            elapsed = (datetime.now() - created).total_seconds()
            if total_lines > 0:
                time_per_roll = elapsed / total_lines
                remaining_time = remaining * time_per_roll
                print(f"\nОсталось примерно: {remaining_time/60:.1f} минут")
else:
    print("CSV файлы не найдены")
    print("Возможно сбор еще не начался")

print("\n" + "="*60 + "\n")
