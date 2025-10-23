# BollingerBands Arbitrage Strategy Backtest

## Overview

This repository implements a **Bollinger Bands Arbitrage Strategy**,
designed to exploit short-term mean reversion patterns in high-frequency
market data.\
The strategy assumes that price tends to oscillate around its
statistical mean --- modeled by Bollinger Bands --- and aims to capture
these deviations intraday.

Unlike conventional trend-following or breakout systems, this approach
takes a *contrarian* position: it anticipates that extreme short-term
deviations will revert to the mean. The strategy is purely systematic
and executes trades based on quantitative signals without discretionary
overrides.

## Methodology

### Core Idea

The underlying hypothesis is that intraday price dynamics approximate
**Brownian motion** with bounded volatility, behaving roughly like a
noisy sine wave around the mean.\
Thus, when price crosses the Bollinger midline, a position is opened in
the direction of the deviation, expecting a reversion toward the
opposite band.

-   **Entry Condition:**
    -   Long if price crosses above the middle band.\
    -   Short if price crosses below the middle band.
-   **Exit Condition:**
    -   Longs close when price touches or exceeds the upper band.\
    -   Shorts close when price touches or drops below the lower band.

This design leads to high win rates, as most trades eventually revert to
the mean --- but at the cost of potentially extreme drawdowns. There is
no stop-loss mechanism, only dynamic exits based on price normalization.

## Implementation Details

The code loads high-frequency (1-minute) OHLC data, applies Bollinger
Bands via `pandas_ta`, and simulates trades per trading day between
**07:00--15:59** (NY pre-market to close), where volume and volatility
are highest.

Each trade tracks: - **Time** - **Direction** (long/short) - **Entry and
Exit Prices** - **Profit/Loss (PnL)** - **Maximum Drawdown (DD)**

Evaluation summarizes: - Total Profit/Loss\
- Number of Trades\
- Average Drawdown\
- Average PnL per Trade

## Code Structure

``` python
class Backtest:
    def __init__(self, file, rtr=10000):
        ...
    def _load_data(self, file):
        ...
    def trade(self, time, type, entry, exit, dd):
        ...
    def backtest(self, bb_length=26, bb_std=2.2):
        ...
    def evaluate(self):
        ...
    def __call__(self):
        ...
```

To run:

``` bash
python backtest.py
```

The script will: 1. Load data (`NQ_OHLC_1m.csv`) 2. Execute trades day
by day 3. Print evaluation metrics

## Important Notes

-   **No Commission, Spread, or Swap Costs** are modeled. In real-world
    arbitrage, these significantly impact profitability.\
-   **No Stop Losses**: drawdowns can be extremely high compared to
    realized returns.\
-   **Data Tested:** 15 years of 1-minute **NASDAQ (NQ)** data.\
-   **Performance:** Extremely high **Sharpe ratio** and consistent
    profitability under historical backtest conditions --- though such
    results may not generalize under live trading conditions.\
-   **Interpretation:** The results falsify some conventional
    assumptions about market efficiency in intraday mean reversion
    contexts, though caution is warranted --- profits can disappear
    quickly when costs, slippage, and execution latency are introduced.

## Example Usage

``` python
if __name__ == '__main__':
    bt = Backtest('NQ_OHLC_1m.csv')
    bt()
```

## Conclusion

This backtest illustrates that even a simple statistical arbitrage
mechanism can produce seemingly extraordinary results over long
historical datasets --- but at the cost of high latent risk.\
Its profitability likely depends on data characteristics that may not
persist in live markets. Treat this not as a trading system, but as an
**empirical exploration of market microstructure and mean-reversion
behavior.**
