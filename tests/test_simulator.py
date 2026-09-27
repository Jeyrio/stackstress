from stackstress.liquidity import LiquidityLevel
from stackstress.simulator import (
    average_execution_price,
    maximum_sale_before_impact,
    price_impact,
    simulate_sale,
)  


def test_simulate_sale():
    liquidity = [
        LiquidityLevel(price=100000, amount=2),
        LiquidityLevel(price=99500, amount=3),
        LiquidityLevel(price=99000, amount=5),
    ]

    result = simulate_sale(10, liquidity)

    expected = (
        (2 * 100000)
        + (3 * 99500)
        + (5 * 99000)
    )

    assert result == expected


def test_average_execution_price():
    liquidity = [
        LiquidityLevel(price=100000, amount=2),
        LiquidityLevel(price=99500, amount=3),
        LiquidityLevel(price=99000, amount=5),
    ]

    result = average_execution_price(10, liquidity)

    assert result == 99350


def test_partial_sale():
    liquidity = [
        LiquidityLevel(price=100000, amount=2),
        LiquidityLevel(price=99500, amount=3),
        LiquidityLevel(price=99000, amount=5),
    ]

    result = simulate_sale(4, liquidity)

    expected = (
        (2 * 100000)
        + (2 * 99500)
    )

    assert result == expected



def test_price_impact():
    liquidity = [
        LiquidityLevel(price=100000, amount=2),
        LiquidityLevel(price=99500, amount=3),
        LiquidityLevel(price=99000, amount=5),
    ]

    result = price_impact(10, liquidity)

    assert result == 0.65



def test_maximum_sale_before_impact():
    liquidity = [
        LiquidityLevel(price=100000, amount=2),
        LiquidityLevel(price=99500, amount=3),
        LiquidityLevel(price=99000, amount=5),
    ]

    result = maximum_sale_before_impact(
        liquidity,
        max_impact=0.4,
    )

    assert result == 5