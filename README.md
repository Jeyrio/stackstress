# StackStress

StackStress is a research prototype for analyzing how much BTC/sBTC can be sold into available Stacks DEX liquidity before price impact exceeds a user-defined tolerance.

The goal is to make large forced-sale scenarios easier to reason about by translating available liquidity into a simple execution-stress analysis.

> **Status:** Working proof of concept / early research prototype.
>
> StackStress is not a production trading, liquidation, or risk-management system.

---

## Problem

Large asset sales can create significant price impact when available liquidity is limited.

This becomes particularly relevant when a lending position is liquidated and the resulting collateral must potentially be sold into a DEX.

For example:

> A position has 10 BTC that may need to be sold.
>
> Instead of assuming that the entire 10 BTC can be sold at the current market price, StackStress estimates how much of that amount can be absorbed before a specified price-impact tolerance is exceeded.

This provides a simple way to reason about market stress caused by large forced flows.

---

## Core Idea

StackStress models a sale against available liquidity levels.

Each liquidity level contains:

- A price
- An amount of BTC/sBTC available at that price

The simulator consumes liquidity from the available levels and calculates:

1. Total amount received
2. Average execution price
3. Price impact
4. Maximum sale amount within a specified price-impact tolerance

Conceptually:

```text
Large potential sale
        ↓
Available DEX liquidity
        ↓
Simulated execution
        ↓
Average execution price
        ↓
Price impact
        ↓
Maximum acceptable sale amount
```

---

## Example

Suppose a market has the following simplified liquidity:

| Price | Available |
|---:|---:|
| $100,000 | 2 BTC |
| $99,500 | 3 BTC |
| $99,000 | 5 BTC |

If 10 BTC is sold across these levels:

- Reference price: $100,000
- Total received: $993,500
- Average execution price: $99,350
- Price impact: 0.65%

If the maximum acceptable price impact is 0.40%, the current proof of concept identifies the liquidity level boundary before the impact exceeds that tolerance.

This is a simplified demonstration of the underlying idea. Real DEX liquidity requires protocol-specific execution and pricing logic.

---

# How StackStress Works

StackStress currently separates the analysis into small components.

### 1. Sale Request

A sale request represents the asset and amount being analyzed.

```python
SaleRequest(
    asset="BTC",
    amount=10
)
```

### 2. Liquidity Levels

Liquidity is represented as a sequence of price/amount levels.

```python
LiquidityLevel(
    price=100000,
    amount=2
)
```

### 3. Sale Simulation

The simulator consumes available liquidity and calculates the total amount received.

### 4. Average Execution Price

The simulator divides the total proceeds by the amount sold.

### 5. Price Impact

Price impact compares the average execution price with the reference price.

### 6. Maximum Sale Analysis

StackStress can estimate the amount that can be sold before a configured price-impact tolerance is exceeded.

---

# Bitflow Integration

StackStress includes an initial adapter for retrieving liquidity data from Bitflow.

The current adapter uses Bitflow's public API to retrieve:

- Pool information
- Active bin information
- Bin reserves
- Bin prices
- Available sBTC-side liquidity

The current research integration focuses on the Bitflow `sBTC-USDCx` DLMM pool.

The adapter converts the retrieved data into StackStress's internal `LiquidityLevel` representation.

```text
Bitflow API
     ↓
Pool information
     ↓
DLMM bins
     ↓
sBTC reserves + prices
     ↓
StackStress LiquidityLevel
     ↓
Stress simulation
```

## Real Liquidity Data

The Bitflow adapter has been tested against live Bitflow API responses.

The retrieved pool data includes the active bin and individual bin reserves/prices.

Because DEX liquidity is dynamic, the active bin and reserves can change between API requests.

Therefore, a liquidity snapshot should be treated as a point-in-time observation rather than permanent market state.

---

# Zest Lending and Liquidation Integration

StackStress is designed to analyze forced-sale pressure that can arise from lending positions on Zest Protocol.

The initial integration research focuses on Zest V2 and the following contracts:

| Contract | Role |
|---|---|
| `v0-market-vault` | Provides lending position, collateral, and debt state |
| `v0-8-market` | Contains lending health and liquidation logic |
| `v0-egroup` | Provides risk-group parameters used by liquidation logic |
| `v0-assets` | Provides asset registry and asset configuration |
| `v0-vault-sbtc` | Provides sBTC vault-related data |

## Position and Liquidation Flow

StackStress's planned Zest integration follows the risk-parameter path used by the Zest V2 contracts:

```text
Zest lending position
        ↓
Position mask
        ↓
v0-8-market
        ↓
v0-egroup.resolve(mask)
        ↓
Risk-group parameters
        ↓
Liquidation calculation
        ↓
Potential forced-sale amount
        ↓
Bitflow liquidity analysis
```

The Zest V2 liquidation logic uses risk-group parameters including:

- `LTV-BORROW`
- `LTV-LIQ-PARTIAL`
- `LTV-LIQ-FULL`
- `LIQ-PENALTY-MIN`
- `LIQ-PENALTY-MAX`
- `LIQ-CURVE-EXP`

These parameters allow StackStress to model the conditions under which a lending position can enter liquidation and the resulting liquidation flow.

Importantly, the current Zest liquidation model is not being represented as a simple fixed "close factor + liquidation bonus" calculation. The inspected Zest V2 logic uses partial/full liquidation LTV thresholds, a liquidation penalty range, and a liquidation curve.

StackStress will use the resulting liquidation amount as a potential forced-sell flow and evaluate whether available DEX liquidity can absorb that flow within a defined price-impact tolerance.

> **Important:** StackStress is an analytical research prototype. It does not execute Zest liquidations or trades.

---

# Zest Integration Status

The Zest integration is currently at the research and design stage.

The Zest V2 contract structure and liquidation path have been inspected from deployed contract source.

The current prototype does **not** claim to have a complete live Zest position adapter.

The planned implementation is to:

1. Read relevant Zest lending positions.
2. Identify the position's risk-group configuration.
3. Read the applicable liquidation parameters.
4. Determine the potential liquidation debt/collateral amount.
5. Translate that amount into a potential forced-sell flow.
6. Test the flow against available DEX liquidity.
7. Report the resulting price impact and liquidity tolerance.

---

# Forced-Sale Stress Model

The central research question is:

> **How much forced selling can available liquidity absorb before price impact exceeds a defined tolerance?**

For a potential liquidation amount:

```text
Potential liquidation
        ↓
Forced-sale amount
        ↓
DEX liquidity
        ↓
Simulated execution
        ↓
Average execution price
        ↓
Price impact
```

This allows StackStress to distinguish between:

- The amount that may need to be sold
- The amount that available liquidity can absorb within a tolerance
- The portion that may need to remain unsold or be analyzed under another execution scenario

For example:

```text
Potential forced sale: 10 BTC

Maximum sale within tolerance: 7 BTC

Remaining amount: 3 BTC
```

The values above are illustrative. They are not a live market recommendation.

---

# Maximum Sale Analysis

StackStress supports a configurable price-impact tolerance.

For example:

```python
maximum_sale_before_impact(
    liquidity,
    max_impact=0.40,
)
```

The purpose is to answer:

> "How much can be sold before the simulated execution moves beyond the allowed impact?"

The current implementation is intentionally simple and is designed as a proof of concept rather than a production-grade execution engine.

---

# Current Architecture

```text
stackstress/
│
├── stackstress/
│   ├── __init__.py
│   ├── __main__.py
│   ├── models.py
│   ├── liquidity.py
│   └── simulator.py
│
├── adapters/
│   ├── __init__.py
│   └── bitflow.py
│
├── tests/
│   ├── __init__.py
│   └── test_simulator.py
│
├── data/
│
├── docs/
│
├── README.md
├── requirements.txt
└── .gitignore
```

---

# Project Structure

### `stackstress/models.py`

Contains basic data models used by the project.

Currently includes the `SaleRequest` model.

### `stackstress/liquidity.py`

Defines the `LiquidityLevel` data structure used to represent available liquidity at a particular price.

### `stackstress/simulator.py`

Contains the core stress-analysis functions:

- `simulate_sale()`
- `average_execution_price()`
- `price_impact()`
- `maximum_sale_before_impact()`

### `stackstress/__main__.py`

Provides the command-line demonstration of the simulator.

### `adapters/bitflow.py`

Contains the initial Bitflow liquidity adapter.

It retrieves Bitflow pool/bin data and converts usable sBTC liquidity into the internal StackStress representation.

### `tests/test_simulator.py`

Contains automated tests covering the current simulation logic.

### `data/`

Reserved for research datasets and future market snapshots.

### `docs/`

Reserved for technical documentation and research notes.

---

# Current Status

## Built

The current proof of concept includes:

- Core liquidity data model
- Sale simulation
- Average execution-price calculation
- Price-impact calculation
- Maximum-sale analysis
- Automated tests
- Command-line demonstration
- Initial Bitflow API adapter
- Live Bitflow pool/bin retrieval
- Initial investigation of Zest V2 liquidation architecture

## Research / In Development

The following areas are not yet complete:

- Full Zest position adapter
- Complete Zest liquidation-flow calculation
- Protocol-accurate Bitflow execution modeling
- Multi-pool routing
- Fee-aware execution analysis
- Historical liquidity snapshots
- More precise fractional-bin execution
- Comprehensive validation against executable Bitflow quotes

---

# Current Limitations

StackStress is intentionally an early research prototype.

### Simplified Liquidity Model

The initial simulator represents liquidity as ordered price/amount levels.

Actual DEX execution can involve more complex mechanisms.

### Point-in-Time Liquidity

Live DEX liquidity changes over time.

A result based on one liquidity snapshot may differ from a later snapshot.

### Bitflow Routing

The current adapter focuses on a specific Bitflow pool and does not yet model complete multi-pool routing.

### Fees

The current core simulator does not yet incorporate every protocol-specific trading fee into its execution calculation.

### Zest Integration

The Zest integration is currently a research/design component rather than a complete production adapter.

### Execution

StackStress does not execute trades or liquidations.

It is an analytical tool.

---

# Future Development

Planned development includes:

1. Complete the Zest position adapter.
2. Model Zest liquidation amounts using the protocol's risk parameters.
3. Connect liquidation flows to DEX liquidity analysis.
4. Improve Bitflow execution modeling.
5. Account for trading fees.
6. Support multiple liquidity pools and routing paths.
7. Add point-in-time liquidity snapshots.
8. Improve partial-bin/fractional execution calculations.
9. Compare simulated execution with protocol quote results.
10. Expand automated testing using real market snapshots.

---

# Research Direction

StackStress is intended to explore the relationship between:

**Lending risk → liquidation flow → DEX liquidity → market impact**

The project focuses on making this relationship easier to quantify.

Rather than treating a liquidation amount as an isolated number, StackStress aims to ask what happens when that amount reaches the available market liquidity.

```text
Lending Position
       ↓
Liquidation Risk
       ↓
Forced-Sale Flow
       ↓
Available Liquidity
       ↓
Execution Simulation
       ↓
Price Impact
       ↓
Market-Stress Analysis
```

---

# Design Principles

StackStress follows a few simple principles:

### Keep the model understandable

The initial simulator uses straightforward calculations that can be inspected and tested easily.

### Separate protocol adapters from the core simulator

Protocol-specific data retrieval should remain separate from the generic stress-analysis logic.

### Do not assume live data is static

DEX liquidity and market conditions can change continuously.

### Prefer transparent assumptions

Simplified assumptions should be visible rather than hidden inside the model.

### Build incrementally

The project starts with a small simulation engine and adds protocol-specific research components progressively.

---

# Testing

The current simulator has automated tests covering:

- Full liquidity consumption
- Average execution price
- Partial sales
- Price impact
- Maximum sale before a configured impact threshold

Run the test suite with:

```bash
python3 -m pytest
```

The current test suite passes successfully.

---

# Running the Project

From the project root:

```bash
python3 -m stackstress
```

The command-line demonstration produces output similar to:

```text
STACKSTRESS
Market Stress Simulation
------------------------

Asset: BTC
Amount to sell: 10 BTC

Reference price:    $100,000.00
Average execution:  $99,350.00
Total received:     $993,500.00
Price impact:       0.65%
Maximum sale at 0.40% impact: 5 BTC
```

These values use the project's simplified example liquidity data and are not live market results.

---

# Technical Approach

The project is currently implemented in Python.

The architecture intentionally keeps the core simulation independent from external protocols.

```text
                ┌─────────────────────┐
                │   Protocol Adapter  │
                │                     │
                │      Bitflow        │
                │      Zest           │
                └──────────┬──────────┘
                           │
                           ↓
                ┌─────────────────────┐
                │  Normalized Market  │
                │       Data          │
                └──────────┬──────────┘
                           │
                           ↓
                ┌─────────────────────┐
                │  StackStress Core   │
                │                     │
                │ Sale Simulation      │
                │ Execution Price      │
                │ Price Impact         │
                │ Stress Limit         │
                └─────────────────────┘
```

This separation makes it possible to test the simulation independently of protocol-specific APIs.

---

# Scope

StackStress currently focuses on analytical market-stress modeling.

It is **not** intended to:

- Execute trades
- Execute liquidations
- Manage user funds
- Provide financial advice
- Replace protocol risk-management systems
- Guarantee execution prices
- Predict future market prices

---