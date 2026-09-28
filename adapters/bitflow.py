import json
import urllib.request

from stackstress.liquidity import LiquidityLevel


POOL_URL = "https://bff.bitflowapis.finance/api/quotes/v1/pools/dlmm_1"
BINS_URL = "https://bff.bitflowapis.finance/api/quotes/v1/bins/dlmm_1"

SBTC_DECIMALS = 8
PRICE_DECIMALS = 8


def load_bitflow_liquidity():
    with urllib.request.urlopen(POOL_URL) as response:
        pool = json.loads(response.read())

    with urllib.request.urlopen(BINS_URL) as response:
        data = json.loads(response.read())

    active_bin = data["active_bin_id"]

    bins = [
        bin_data
        for bin_data in data["bins"]
        if int(bin_data["bin_id"]) >= active_bin
        and int(bin_data["reserve_x"]) > 0
    ]

    bins.sort(
        key=lambda bin_data: int(bin_data["bin_id"]),
        reverse=False,
    )

    liquidity = []

    for bin_data in bins:
        price = int(bin_data["price"]) / (10 ** PRICE_DECIMALS)
        amount = int(bin_data["reserve_x"]) / (10 ** SBTC_DECIMALS)

        liquidity.append(
            LiquidityLevel(
                price=price,
                amount=amount,
            )
        )

    return pool, liquidity