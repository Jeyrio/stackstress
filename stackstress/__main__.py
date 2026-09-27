from stackstress.liquidity import LiquidityLevel
from stackstress.simulator import (
    average_execution_price,
    maximum_sale_before_impact,
    price_impact,
    simulate_sale,
)


def main():
    liquidity = [
        LiquidityLevel(price=100000, amount=2),
        LiquidityLevel(price=99500, amount=3),
        LiquidityLevel(price=99000, amount=5),
    ]

    amount = 10

    total_received = simulate_sale(amount, liquidity)
    average_price = average_execution_price(amount, liquidity)
    impact = price_impact(amount, liquidity)

    max_sale = maximum_sale_before_impact(
    liquidity,
    max_impact=0.4,
)

    print("STACKSTRESS")
    print("Market Stress Simulation")
    print("------------------------")
    print()
    print("Asset: BTC")
    print("Amount to sell: {} BTC".format(amount))
    print()
    print("Reference price:    ${:,.2f}".format(liquidity[0].price))
    print("Average execution:  ${:,.2f}".format(average_price))
    print("Total received:     ${:,.2f}".format(total_received))
    print("Price impact:       {:.2f}%".format(impact))
    print("Maximum sale at 0.40% impact: {:.0f} BTC".format(max_sale))


if __name__ == "__main__":
    main()