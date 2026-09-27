from typing import List

from .liquidity import LiquidityLevel


def simulate_sale(
    amount: float,
    liquidity: List[LiquidityLevel],
) -> float:
    remaining = amount
    total_received = 0.0

    for level in liquidity:
        if remaining <= 0:
            break

        amount_sold = min(remaining, level.amount)
        total_received += amount_sold * level.price
        remaining -= amount_sold

    return total_received


def average_execution_price(
    amount: float,
    liquidity: List[LiquidityLevel],
) -> float:
    total_received = simulate_sale(amount, liquidity)

    return total_received / amount


def price_impact(
    amount: float,
    liquidity: List[LiquidityLevel],
) -> float:
    reference_price = liquidity[0].price
    average_price = average_execution_price(amount, liquidity)

    return ((reference_price - average_price) / reference_price) * 100



def maximum_sale_before_impact(
    liquidity: List[LiquidityLevel],
    max_impact: float,
) -> float:
    cumulative_amount = 0.0

    for level in liquidity:
        cumulative_amount += level.amount

        impact = price_impact(cumulative_amount, liquidity)

        if impact > max_impact:
            return cumulative_amount - level.amount

    return cumulative_amount