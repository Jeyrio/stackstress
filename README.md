# StackStress

StackStress is a research prototype for analyzing the market impact of large BTC and sBTC sales against available decentralized exchange (DEX) liquidity on the Stacks ecosystem.

The project explores how much of a large sale can be absorbed by available liquidity before execution price impact exceeds a defined tolerance.

StackStress is designed around a simple question:

> **If a large amount of BTC or sBTC needs to be sold, how much can the available market liquidity absorb before the sale causes unacceptable price impact?**

The project is currently an early-stage proof of concept focused on the simulation model and initial integration with real Bitflow liquidity data.

---

## Overview

When a relatively small trade is executed against a liquid market, the available liquidity may be sufficient to fill the order without significantly changing the execution price.

A large sale is different.

If the requested amount is larger than the liquidity available near the current market price, the execution may continue through progressively less favorable price levels. As more liquidity is consumed, the average execution price can move further away from the reference price.

This becomes particularly relevant during market-stress events, including:

- Large BTC or sBTC sales
- Forced exits
- Lending-position liquidations
- Portfolio rebalancing
- Leveraged-position unwinding
- Sudden changes in market conditions

StackStress models this behavior using available liquidity and calculates how execution quality changes as the sale size increases.

---

## The Core Idea

Consider a simplified market with the following liquidity:

| Price | Available Liquidity |
| --- | ---: |
| $100,000 | 2 BTC |
| $99,500 | 3 BTC |
| $99,000 | 5 BTC |

A trader attempting to sell 10 BTC cannot execute the entire sale at $100,000 because only 2 BTC is available at that level.

The simulation therefore consumes liquidity progressively:

```text
2 BTC → $100,000
3 BTC → $99,500
5 BTC → $99,000
```

The resulting execution is different from simply multiplying the entire order by the first available price.

StackStress calculates the resulting:

- Total amount received
- Average execution price
- Price impact
- Maximum sale amount within a specified impact tolerance

This allows the project to analyze the relationship between **sale size, available liquidity, and execution impact**.

---

## Example

The current proof of concept uses a synthetic liquidity scenario:

```text
Amount to sell:       10 BTC
Reference price:      $100,000.00
Average execution:    $99,350.00
Total received:       $993,500.00
Price impact:         0.65%
Maximum at 0.40%:     5 BTC
```

In this scenario, the full 10 BTC sale produces a price impact of 0.65%.

If the defined maximum acceptable impact is 0.40%, the simplified model identifies 5 BTC as the maximum amount that can be sold within that threshold.

The purpose of this example is to demonstrate the simulation methodology.

It is not a live trading recommendation.

---

## How StackStress Works

The current architecture separates the project into three main concepts:

```text
Market Data
    ↓
Liquidity Representation
    ↓
Stress Simulation
    ↓
Execution Analysis
```

### 1. Market Data

Market liquidity can come from an external data source.

The current project includes an initial Bitflow adapter that retrieves pool and DLMM bin information.

### 2. Liquidity Representation

Retrieved market information is converted into a common liquidity representation used by the simulator.

Each liquidity level contains:

- Price
- Available asset amount

This allows the simulation engine to operate independently from the specific API format of an external DEX.

### 3. Stress Simulation

The simulator consumes liquidity levels in sequence according to the simplified execution model.

It calculates the economic result of selling a specified amount against those levels.

### 4. Execution Analysis

The resulting execution is analyzed using:

- Total received
- Average execution price
- Price impact
- Maximum sale before a defined impact threshold

---

## Bitflow Integration

StackStress includes an initial exploratory adapter for Bitflow.

The adapter retrieves information from Bitflow's public API for the sBTC-USDCx liquidity pool.

The current adapter retrieves information including:

- Pool information
- Active bin
- Bin IDs
- Bin prices
- sBTC reserves
- Bin liquidity information

The retrieved sBTC reserves are converted into the project's internal `LiquidityLevel` representation.

The current integration is intended to demonstrate the connection between real DEX liquidity data and the StackStress simulation engine.

It is not yet a complete reproduction of Bitflow's production routing or quote execution logic.

---

## Real Liquidity Data

The project has successfully retrieved live Bitflow pool and DLMM bin data.

The data includes fields such as:

```text
active_bin_id
bin_id
reserve_x
reserve_y
price
liquidity
```

The adapter processes these values and creates liquidity levels that can be passed to the StackStress simulation engine.

Because DEX pool state changes continuously, retrieved values represent a snapshot of the market at the time of the request.

For example:

```text
Pool state at time T1
        ↓
Liquidity snapshot
        ↓
StackStress simulation
```

A later request can produce different:

- Active bin
- Reserves
- Liquidity distribution
- Available execution levels

This is an important consideration for future versions of the model.

---

## Core Components

The project currently consists of four primary components.

### Liquidity Model

The liquidity model represents an available execution level:

```text
Price + Available Amount
```

This provides a simple abstraction that allows the simulation engine to work with liquidity data without being tightly coupled to one external API.

### Sale Simulation

The sale simulation determines how a requested amount is consumed across available liquidity levels.

The simulator tracks:

- Remaining amount
- Amount consumed at each level
- Total value received

### Execution Price

The average execution price is calculated from the total value received divided by the amount sold.

This provides a single measure of the effective price received across the entire simulated sale.

### Price Impact

Price impact measures how far the average execution price moves away from the reference price.

The current simplified calculation uses the first liquidity level as the reference price.

The formula is:

```text
Price Impact =
((Reference Price - Average Execution Price)
 / Reference Price) × 100
```

This produces a percentage representing the difference between the reference price and the simulated average execution price.

---

## Maximum Sale Analysis

One of the core functions of StackStress is identifying how much of a sale can be executed before a defined price-impact threshold is exceeded.

For example:

```text
Requested sale:       10 BTC
Maximum impact:       0.40%
```

The simulator evaluates the available liquidity and determines the maximum amount that remains within the specified threshold.

Conceptually:

```text
Large Sale
    ↓
Consume Available Liquidity
    ↓
Calculate Execution Price
    ↓
Calculate Price Impact
    ↓
Compare With Allowed Threshold
    ↓
Determine Maximum Sale Amount
```

This is the foundation of the project's market-stress analysis.

---

## Current Project Status

StackStress is currently a **working proof of concept**.

The repository contains:

- A core liquidity model
- A sale simulation engine
- Average execution-price calculations
- Price-impact calculations
- Maximum-sale analysis
- Automated tests
- A command-line demonstration
- An initial Bitflow liquidity adapter
- Real Bitflow pool and DLMM bin data retrieval

The project is intentionally kept small at this stage.

The current focus is validating the underlying simulation approach before introducing additional protocol integrations or a larger user interface.

---

## Current Limitations

StackStress currently uses a simplified liquidity model.

It does not yet reproduce every detail involved in executing a real DEX transaction.

Important areas that require further development include:

### DEX Routing

The current simulator does not reproduce complete production routing logic across multiple pools.

### Trading Fees

Trading fees are not currently incorporated into the core simulation model.

### Partial Bin Execution

The current maximum-sale calculation operates on the available liquidity levels and does not yet model every possible fractional execution step.

### Dynamic Pool State

A real DEX pool can change while a transaction is being prepared or executed.

The current prototype treats retrieved liquidity as a snapshot.

### Quote Validation

The current model has not yet been fully validated against Bitflow's production quote and routing behavior.

### Lending Integration

Zest lending-position data and liquidation logic are not currently integrated into the simulator.

These limitations define areas for future research and development rather than features the current prototype claims to have completed.

---

## Future Development

Potential future development includes:

- More accurate DEX routing simulation
- Trading-fee calculations
- Fractional bin execution
- Multi-pool liquidity analysis
- Historical liquidity snapshots
- Dynamic pool-state analysis
- Comparison against live DEX quotes
- Lending-position analysis
- Liquidation-event modeling
- Forced-sale estimation
- Cross-protocol liquidity stress analysis
- Visualization of liquidity depth and price impact
- A web interface for interactive scenarios

The project is intentionally starting with the core simulation model before expanding into these additional capabilities.

---

## Testing

The project includes automated tests for the core simulation engine.

Current tests cover:

- Full liquidity consumption
- Partial sales
- Average execution price
- Price impact
- Maximum sale before an impact threshold

Run the test suite with:

```bash
python3 -m pytest
```

The current test suite contains five tests.

Expected result:

```text
5 passed
```

---

## Running the Project

### Requirements

- Python 3
- `pytest` for running the test suite
- Internet access for the Bitflow adapter

### Install Dependencies

From the project root:

```bash
pip install -r requirements.txt
```

### Run Tests

```bash
python3 -m pytest
```

### Run the CLI Demo

```bash
python3 -m stackstress
```

Example output:

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

---

## Project Structure

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

## File and Directory Description

### `stackstress/`

Contains the core StackStress simulation package.

### `stackstress/__init__.py`

Marks the `stackstress` directory as a Python package.

### `stackstress/__main__.py`

Provides the command-line entry point.

Running:

```bash
python3 -m stackstress
```

executes the demonstration defined in this file.

### `stackstress/models.py`

Contains basic data models used by the project.

The current implementation includes the `SaleRequest` model, which represents:

- Asset
- Amount

### `stackstress/liquidity.py`

Contains the `LiquidityLevel` model.

Each liquidity level represents:

```text
Price
Available Amount
```

### `stackstress/simulator.py`

Contains the core simulation logic.

Current functions include:

```text
simulate_sale()
average_execution_price()
price_impact()
maximum_sale_before_impact()
```

This is currently the central component of StackStress.

---

## `adapters/`

Contains integrations that retrieve external market data and convert it into the format expected by the simulation engine.

### `adapters/bitflow.py`

Contains the initial Bitflow adapter.

Its responsibilities include:

1. Requesting Bitflow pool information
2. Requesting DLMM bin information
3. Identifying the active bin
4. Reading available sBTC reserves
5. Reading bin prices
6. Converting the retrieved information into `LiquidityLevel` objects

This separation keeps external data retrieval independent from the core simulation logic.

---

## `tests/`

Contains automated tests for the StackStress simulation engine.

### `tests/test_simulator.py`

Tests the main simulation functions against controlled synthetic liquidity scenarios.

The tests help verify that changes to the simulation logic do not unintentionally break existing behavior.

---

## `data/`

Reserved for project data and future research datasets.

Potential future uses include:

- Historical liquidity snapshots
- Simulation inputs
- Research datasets
- Exported market-state observations

---

## `docs/`

Reserved for additional technical documentation and research notes.

Potential future documentation includes:

- Simulation methodology
- DEX integration notes
- Data-source documentation
- Mathematical assumptions
- Research findings
- Validation results

---

## `requirements.txt`

Contains the Python dependencies required by the project.

---

## `.gitignore`

Specifies files and directories that should not be committed to the repository.

---

## Design Principles

StackStress currently follows several simple design principles.

### Keep the Core Model Independent

The simulation engine should not depend directly on a specific DEX API.

External data should first be converted into the common liquidity representation.

```text
External DEX
     ↓
Adapter
     ↓
LiquidityLevel
     ↓
Simulation Engine
```

This makes it possible to add additional liquidity sources without rewriting the core simulation logic.

### Start With a Small, Testable Model

The project begins with a simple simulation model that can be tested using controlled liquidity scenarios.

This makes it easier to identify assumptions and validate individual components before introducing more complex protocol behavior.

### Separate Research From Production Claims

The current implementation is explicitly a research prototype.

Results depend on:

- Data quality
- Liquidity snapshots
- Simulation assumptions
- Routing behavior
- Fees
- Pool state

The project therefore avoids treating the current model as a production trading or liquidation system.

---

## Research Direction

The broader research direction is to connect two pieces of information:

```text
Potential Forced-Sale Size
            +
Available DEX Liquidity
            ↓
     Market Stress Analysis
```

A future version could use lending-position information to estimate the amount of an asset that may need to be sold during a liquidation event.

That amount could then be evaluated against current DEX liquidity to estimate how much execution pressure the market may experience.

The long-term research question is whether this combination can provide a useful view of market resilience during large forced flows.

---

## Scope

The current scope is deliberately limited to:

- Liquidity representation
- Sale simulation
- Execution-price analysis
- Price-impact analysis
- Maximum-sale analysis
- Initial Bitflow data retrieval

The following are outside the current proof-of-concept scope:

- Executing trades
- Executing liquidations
- Managing user funds
- Providing financial advice
- Acting as a production risk-management system
- Guaranteeing execution prices

---

## Disclaimer

StackStress is an experimental research prototype.

It does not execute trades, manage funds, or provide financial advice.

Simulation results are dependent on the liquidity data and assumptions used by the model and should not be treated as guaranteed real-world execution results.

The project is intended for research, experimentation, and validation of the underlying market-stress analysis approach.

---

## License

This project is currently under development as a Stacks ecosystem research and development project.