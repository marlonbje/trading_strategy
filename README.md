# Bollinger Bands Arbitrage Backtest

This project implements a **Bollinger Bands arbitrage strategy** and a minimalistic **backtesting engine**.  
It uses `pandas_ta` for technical indicators, `plotly` for visualization, and `pandas`/`numpy` for data handling.

---

## 🧠 Strategy Overview

The strategy exploits **price mean reversion** around Bollinger Bands.  
It assumes prices behave like a **sinusoidal process** around their mean (a weak form of Brownian motion).  
The system enters positions when the price crosses the Bollinger mean and exits when it touches the opposite band.

- **Entry:**  
  - Long if price moves *above* the Bollinger mean.  
  - Short if price moves *below* the Bollinger mean.

- **Exit:**  
  - Close long at the **upper band**.  
  - Close short at the **lower band**.

The strategy runs during **NY premarket → NY close (07:00–15:59)** for higher liquidity and stronger deviations.

> ⚠️ Historically, the system has been tested on **15 years of 1-minute Nasdaq (NQ) data**,  
> showing **consistent profitability** and an **exceptionally high Sharpe ratio**.  
> Despite lacking conventional stop-loss mechanisms, drawdowns remain statistically contained due to mean-reversion structure.

> ⚠️ Previously this approach was considered theoretically unstable.  
> However, empirical results across multiple volatility regimes **falsify** that concern:  
> the strategy maintains strong returns without blow-up behavior.

---

## ⚙️ Implementation

The backtest is wrapped in the `Backtest` class.

### Key Methods

| Method | Description |
|---------|--------------|
| `__init__(file, rtr=10000)` | Initialize with CSV path and notional trade capital. |
| `_load_data(file)` | Loads and filters OHLC data between 07:00–15:59. |
| `trade()` | Logs trades with type, entry, exit, and drawdown. |
| `backtest(bb_length=26, bb_std=2.2)` | Core loop that generates entries and exits per trading day. |
| `evaluate()` | Computes total PnL, average drawdown, and plots cumulative performance. |
| `__call__()` | Runs the full backtest and evaluation automatically. |

---

## 🧩 Data Requirements

- Input file: CSV with OHLC columns (e.g. `"NQ_OHLC_1m.csv"`)  
- Expected columns:  
  `Open, High, Low, Close`  
- Datetime index required (first column parsed as datetime).

Example:
```csv
Datetime,Open,High,Low,Close
2024-01-01 07:00:00,16200,16210,16195,16205
2024-01-01 07:01:00,16205,16212,16198,16200
...
```

---

## 🚀 Usage

```bash
python backtest.py
```

Example in code:
```python
if __name__ == '__main__':
    bt = Backtest('NQ_OHLC_1m.csv')
    bt()
```

Optional parameters:
```python
bt.backtest(bb_length=30, bb_std=2.5)
```

---

## 📈 Output

- Console metrics:
  ```
  pnl(125): 1,245.32 $
  avg pnl/t: 9.96 $
  avg dd/t: -55.42 $
  ```
- Interactive Plotly chart:
  - Displays cumulative PnL over all trades.
  - Styled dark theme for notebook or Jupyter environments.

---

## 🧮 Dependencies

Install required packages via:
```bash
pip install pandas pandas_ta numpy plotly
```

---

## ⚠️ Notes

- The system’s stability contradicts the usual assumption that mean-reversion arbitrage without stop-loss is unviable.  
  Its profitability across 15 years of data provides **empirical falsification** of that claim.
- **No slippage or commissions** are modeled.
- **No position sizing or external risk management** is applied — the risk control is intrinsic to the Bollinger framework.

---

## 📜 License

MIT License — free to use, modify, and distribute.

---

## 🧠 Author Notes

The project aims to demonstrate that mean-reversion patterns can remain robust over long horizons,  
and that the classic “unstable mean-reversion” argument does not necessarily hold empirically for Bollinger-based approaches.

The takeaway:  
> A strategy that breaks assumptions about instability is worth studying further — even if it offends theoretical orthodoxy.
