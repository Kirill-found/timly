"""
Расчет необходимого бюджета для выплат
"""

# Статистика из 1000 реальных бросков
wins = {
    "777": {"count": 15, "payout": 200},
    "BAR BAR BAR": {"count": 21, "payout": 100},
    "Lemon x3": {"count": 16, "payout": 50},
    "Grape x3": {"count": 14, "payout": 30}
}

print("\n" + "="*70)
print("    RASCHET BYUDZHETA DLA VYPLAT")
print("="*70 + "\n")

print("Statistika vyplat na 1000 igr:\n")

total_payout = 0

for combo, data in wins.items():
    count = data["count"]
    payout = data["payout"]
    total = count * payout
    total_payout += total

    print(f"{combo:15s} | {count:2d} vyigryshej x {payout:3d} stars = {total:,} stars")

print("-" * 70)
print(f"{'ИТОГО:':15s} | {sum([d['count'] for d in wins.values()]):2d} vyigryshej = {total_payout:,} stars")

print("\n" + "="*70)
print("    BYUDZHET S ZAPАSOM")
print("="*70 + "\n")

# Добавляем запас на случай удачной серии
safety_margins = [1.0, 1.2, 1.5, 2.0]

for margin in safety_margins:
    budget = int(total_payout * margin)
    extra = budget - total_payout

    print(f"Zapas {int((margin-1)*100):3d}%: {budget:,} stars (+ {extra:,} stars na udachnuyu seriyu)")

print("\n" + "="*70)
print("    DETALNIJ RASCHET")
print("="*70 + "\n")

# Для разных вариантов ставок
stakes = [7, 8]

for stake in stakes:
    total_bet = 1000 * stake
    rtp = (total_payout / total_bet) * 100
    profit = total_bet - total_payout

    print(f"Pri stavke {stake} stars:")
    print(f"  - Vsego postavleno: {total_bet:,} stars")
    print(f"  - Nuzhno na vyplaty: {total_payout:,} stars")
    print(f"  - RTP: {rtp:.2f}%")
    print(f"  - Pribyl: {profit:,} stars")
    print(f"  - Byudzhet s zapasom 50%: {int(total_payout * 1.5):,} stars")
    print()

print("="*70)
print("    REKOMENDACII")
print("="*70 + "\n")

print(f"Minimal'nij byudzhet (bez zapasa): {total_payout:,} stars")
print(f"Rekomenuemyj byudzhet (zapas 20%): {int(total_payout * 1.2):,} stars")
print(f"Bezopasnyj byudzhet (zapas 50%): {int(total_payout * 1.5):,} stars")
print(f"Maksimal'nij byudzhet (zapas 100%): {int(total_payout * 2.0):,} stars")

print("\n" + "="*70)
print("    CHTO OZNACHAET ZAPAS")
print("="*70 + "\n")

print("Zapas nuzhен na sluchaj esli:")
print("  - Vypadet bol'she vyigryshej chem v statistike")
print("  - Podryad vypadet neskol'ko 777 (200 stars kazhdyj)")
print("  - Seriya udachi u igrokov")
print()
print("Bez zapasa:")
print("  - Risku ostat'sya bez sredstv na vyplaty")
print("  - Pridetsya ostanovit' igru chtoby popolnit' balans")
print()
print("S zapasom 50%:")
print("  - Dazhe pri samoj udachnoj serii u vas budut sredstva")
print("  - Igra ne ostanovitsya")
print("  - Bezopasno!")
print()

print("="*70 + "\n")

# Расчет на месяц
print("="*70)
print("    BYUDZHET NA MESYAC")
print("="*70 + "\n")

games_per_day = [100, 500, 1000, 5000]

for games in games_per_day:
    daily_payouts = (games / 1000) * total_payout
    monthly_payouts = daily_payouts * 30
    recommended_budget = monthly_payouts * 1.5

    print(f"{games:,} igr/den:")
    print(f"  - Vyplat v den': {daily_payouts:,.0f} stars")
    print(f"  - Vyplat v mesyac: {monthly_payouts:,.0f} stars")
    print(f"  - Byudzhet s zapasom 50%: {recommended_budget:,.0f} stars")
    print()

print("="*70 + "\n")
