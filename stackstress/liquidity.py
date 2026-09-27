from dataclasses import dataclass


@dataclass
class LiquidityLevel:
    price: float
    amount: float