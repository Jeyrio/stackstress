from dataclasses import dataclass


@dataclass
class SaleRequest:
    asset: str
    amount: float