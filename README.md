# Bollinger Bands Arbitrage Backtest

This repository contains a **fully-automated backtest** implementation
of a *Bollinger Bands Arbitrage Strategy* written in Python.\
It uses `pandas_ta` for indicator computation and `matplotlib` for
visual performance evaluation.

------------------------------------------------------------------------

## 📖 Strategy Overview

The **Bollinger Bands Arbitrage Strategy** assumes mean-reverting price
behavior.\
The model trades **toward the mean** when volatility (ATR) is
sufficiently high, using **Bollinger Bands** as reference zones.

### Core Idea

Prices fluctuate like a *noisy sine wave* around their mean. The middle
Bollinger Band represents this mean, while outer bands capture
statistical extremes.

**Entry Logic:** - Long when price crosses **above the middle band**
with sufficient ATR\
- Short when price crosses **below the middle band** with sufficient ATR

**Exit Logic:** - Long exits at the **upper band** - Short exits at the
**lower band**

------------------------------------------------------------------------

## ⚙️ Features

-   Clean, class-based architecture (`BollingerBandsBacktest`)
-   Built-in data loading and trade recording
-   Daily segmented execution for 1-minute OHLC data
-   ATR-based volatility filter
-   Full trade statistics and graphical evaluation
-   Automated performance report with:
    -   Win rate
    -   Average drawdown
    -   Average duration
    -   Cumulative performance plots

------------------------------------------------------------------------

## 🧠 Notes & Insights

This model is **highly profitable** on long historical backtests (15
years of 1-minute NQ data), showing an *extremely high Sharpe ratio*.\
However, it also demonstrates why **statistical arbitrage is fragile**:

> Small deviations in execution cost assumptions (spread, fees,
> slippage) can destroy returns.

No stop-loss is used --- exits are **price-adjusted** through the outer
Bollinger Bands.\
While this keeps the win rate high, it creates **large floating
drawdowns** and **poor risk-adjusted efficiency** in real-world
conditions.

------------------------------------------------------------------------

## 🧩 Usage

``` bash
pip install pandas pandas_ta numpy matplotlib
```

Then execute:

``` bash
python main.py
```

The script automatically runs the full process: 1. Load data from
`NQ_OHLC_1m.csv` 2. Backtest with BB(26, 2.2) and ATR(14) 3. Evaluate
and save plots as `eval_BB26_2.2.png`

------------------------------------------------------------------------

## 📊 Output Example

Performance metrics printed to console:

    ==================================================
    BACKTEST EVALUATION
    ==================================================
    Total PnL:          3,520,000 USD  (4872 trades)
    Risk per Trade:        25,000 USD
    Avg PnL:                  722 USD
    Avg Drawdown:           4,830 USD
    Avg Duration:            38 min
    Win Rate:               68.3 %
    ==================================================

------------------------------------------------------------------------

## ⚠️ Disclaimer

This project is a **research backtest** and not financial advice.\
Market conditions, fees, latency, and data quality have **major impact**
on real-world performance.

Use this as an **educational experiment** in statistical arbitrage and
volatility modeling.

------------------------------------------------------------------------

© 2025 --- Quantitative Strategy Prototype
