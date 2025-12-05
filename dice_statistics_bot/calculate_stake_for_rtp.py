"""
Расчет необходимой ставки для достижения целевого RTP
"""

# Данные из 1000 бросков
total_payout = 6320  # Всего выплачено за 1000 игр
total_rolls = 1000

# Формула: RTP = (total_payout / total_bet) * 100
# total_bet = total_rolls * stake
# RTP = (total_payout / (total_rolls * stake)) * 100
# stake = total_payout / (total_rolls * (RTP / 100))

print("\n" + "="*70)
print("    RASCHET STAVKI DLA CELEVOGO RTP")
print("="*70 + "\n")

print(f"Ishodnie dannie:")
print(f"  Vsego vyplacheno za 1000 igr: {total_payout:,} stars")
print(f"  Kolichestvo igr: {total_rolls:,}")
print(f"\n" + "-"*70 + "\n")

target_rtps = [95, 90, 85, 80, 75, 70]

print("Neobhodimaya stavka dla raznogo RTP:\n")

for target_rtp in target_rtps:
    required_stake = total_payout / (total_rolls * (target_rtp / 100))
    house_edge = 100 - target_rtp

    # Округляем до целых
    stake_rounded = round(required_stake)
    actual_rtp = (total_payout / (total_rolls * stake_rounded)) * 100

    print(f"Celevoj RTP: {target_rtp:2d}% | Nuzhna stavka: {required_stake:.2f} stars (~{stake_rounded} stars)")
    print(f"  -> Pri stavke {stake_rounded} stars: RTP = {actual_rtp:.2f}%, House edge = {100-actual_rtp:.2f}%")
    print()

# Детальный расчет для RTP 90% и 80%
print("\n" + "="*70)
print("    DETALNIJ RASCHET")
print("="*70 + "\n")

for target_rtp in [90, 80]:
    print(f"CELEVOJ RTP: {target_rtp}%")
    print("-" * 70)

    required_stake = total_payout / (total_rolls * (target_rtp / 100))
    stake_rounded = round(required_stake)

    total_bet = total_rolls * stake_rounded
    actual_rtp = (total_payout / total_bet) * 100
    house_edge = 100 - actual_rtp
    profit = total_bet - total_payout

    print(f"Neobhodimaya stavka: {required_stake:.2f} stars")
    print(f"Okruglennaya stavka: {stake_rounded} stars")
    print(f"\nRezultat pri stavke {stake_rounded} stars:")
    print(f"  - Vsego postavleno: {total_bet:,} stars")
    print(f"  - Vsego vyplacheno: {total_payout:,} stars")
    print(f"  - Fakticheskij RTP: {actual_rtp:.2f}%")
    print(f"  - Preimushchestvo kazino: {house_edge:.2f}%")
    print(f"  - Pribyl s 1000 igr: {profit:,} stars")
    print()

    # Прогноз прибыли
    print(f"Prognoz pribyli pri stavke {stake_rounded} stars:")

    games_per_day = [100, 500, 1000, 5000]
    for games in games_per_day:
        daily_bets = games * stake_rounded
        daily_payouts = daily_bets * (actual_rtp / 100)
        daily_profit = daily_bets - daily_payouts
        monthly_profit = daily_profit * 30

        print(f"  {games:,} igr/den: {daily_profit:,.0f} stars/den ({monthly_profit:,.0f} stars/mesyac)")

    print("\n" + "="*70 + "\n")

print("ИТОГОВЫЕ РЕКОМЕНДАЦИИ:")
print("-" * 70)
print()
print("Для RTP 90% (стандарт для слотов):")
print("  -> Ставка: 7 stars")
print("  -> Игроки теряют 10% в долгосрочной перспективе")
print("  -> Хороший баланс между прибылью и удержанием игроков")
print()
print("Для RTP 80% (более выгодно казино):")
print("  -> Ставка: 8 stars")
print("  -> Игроки теряют 20% в долгосрочной перспективе")
print("  -> Выше прибыль, но игроки быстрее потеряют интерес")
print()
print("="*70 + "\n")
