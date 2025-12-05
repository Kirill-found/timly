"""
Расчет RTP с разными параметрами
"""

# Данные из 1000 бросков
statistics = {
    1: 21,   # BAR BAR BAR
    22: 16,  # Lemon
    43: 14,  # Grape
    64: 15   # 777
}

# Текущие выплаты
payouts = {
    1: 100,   # BAR BAR BAR
    22: 50,   # Lemon
    43: 30,   # Grape
    64: 200   # 777
}

symbols = {
    1: "BAR BAR BAR",
    22: "Lemon x3",
    43: "Grape x3",
    64: "777"
}

total_rolls = 1000
total_wins = sum(statistics.values())
win_rate = (total_wins / total_rolls) * 100

print("\n" + "="*70)
print("    ANALIZ VYGRYSHNYH KOMBINACIJ (1000 BROSKOV)")
print("="*70 + "\n")

print("VYGRYSHNIE KOMBINACII:")
print("-" * 70)

total_payout = 0

for value in [64, 1, 22, 43]:
    count = statistics[value]
    payout = payouts[value]
    symbol = symbols[value]
    probability = (count / total_rolls) * 100
    total_value = count * payout
    total_payout += total_value

    print(f"{symbol:15s} | Vypalo: {count:3d} raz | Veroyatnost: {probability:5.2f}% | Vyplata: {payout:3d} stars")
    print(f"{' ':15s} | Vsego vyplacheno: {total_value:,} stars")
    print("-" * 70)

print(f"\nITOGO:")
print(f"  Vsego vyigryshej: {total_wins} iz {total_rolls} ({win_rate:.2f}%)")
print(f"  Vsego vyplacheno: {total_payout:,} stars")
print(f"  Proigrushej: {total_rolls - total_wins} ({100-win_rate:.2f}%)")

# RTP с разными ставками
print("\n" + "="*70)
print("    RTP ANALIZ S RAZNYMI STAVKAMI")
print("="*70 + "\n")

stakes = [35, 25, 20, 15, 10, 7]

for stake in stakes:
    total_bet = total_rolls * stake
    rtp = (total_payout / total_bet) * 100
    house_edge = 100 - rtp

    print(f"Stavka: {stake:2d} stars | Total bet: {total_bet:,} | RTP: {rtp:6.2f}% | House edge: {house_edge:6.2f}%", end="")

    if rtp > 100:
        print("  <- Igroki v plyuse!")
    elif rtp > 95:
        print("  <- Vysokij RTP (vydgodno igrokam)")
    elif rtp > 85:
        print("  <- OPTIMAL!")
    elif rtp > 75:
        print("  <- Nizkij RTP")
    else:
        print("  <- Slishkom nizkij!")

# Детальный расчет для ставки 15 звезд
print("\n" + "="*70)
print("    DETALNIJ RASCHET DLA STAVKI 15 STARS")
print("="*70 + "\n")

stake = 15
total_bet = total_rolls * stake
rtp = (total_payout / total_bet) * 100
house_edge = 100 - rtp

print(f"Srednyaya stavka: {stake} stars")
print(f"Vsego postavleno (1000 igr): {total_bet:,} stars")
print(f"Vsego vyplacheno: {total_payout:,} stars")
print(f"RTP (Return to Player): {rtp:.2f}%")
print(f"Preimushchestvo kazino: {house_edge:.2f}%")

print("\n" + "="*70)
print("    REKOMENDACII")
print("="*70 + "\n")

if rtp > 100:
    print("WARNING: RTP > 100% - igroki v plyuse! Nuzhno snizit vyplaty")
elif rtp > 95:
    print("OK: RTP vysokij (>95%) - vygodno igrokam, no dopustimo")
elif rtp > 85:
    print("OTLICHNO: RTP optimalnyj (85-95%) - balans mezhdu igrokom i domom")
elif rtp > 75:
    print("WARNING: RTP nizkij (<85%) - igroki bystro poteryayut interes")
else:
    print("ERROR: RTP slishkom nizkij (<75%) - nikto ne budet igrat")

# Прогноз прибыли
print("\n" + "="*70)
print("    PROGNOZ PRIBYLI")
print("="*70 + "\n")

games_per_day = [100, 500, 1000, 5000]

print(f"Pri stavke {stake} stars i RTP {rtp:.2f}%:\n")

for games in games_per_day:
    daily_bets = games * stake
    daily_payouts = daily_bets * (rtp / 100)
    daily_profit = daily_bets - daily_payouts
    monthly_profit = daily_profit * 30

    print(f"  {games:,} igr/den: Stavki {daily_bets:,} | Vyplaty {daily_payouts:,.0f} | Pribyl {daily_profit:,.0f} stars/den ({monthly_profit:,.0f} stars/mesyac)")

print("\n" + "="*70 + "\n")
