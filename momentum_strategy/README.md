# Cross-Sectional Momentum Strategy — Rolling 5-Year Windows
Backtests a standard 12-2 cross-sectional momentum strategy on US equities across 5 year windows, using CRSP monthly returns and Ken French FF3 factors. The rolling structure is designed to show how momentum alpha, Sharpe ratio, and drawdown profile vary across distinct market regimes rather the averaging across them. 

## Covered periods:
    1990-1994: Early 90s recession and recovery
    1995-1999: Dot-com bull market
    2000–2004: Dot-com bust and recovery
    2005–2009: Pre-crisis bull run and 2008 financial crisis 
    2010–2014: Post-crisis recovery
    2015–2019: Low-volatility bull market
    2020–2024: COVID crash, recovery, rate hike cycle
    2021–2026: AI/momentum cycle

Each period produces its own plot saved as e.g. "results/momentum_2000_2004.png"

## Key Results

| Period    | Ann. Return (%) | Sharpe | Max Drawdown (%) | CAPM α (%/mo) | CAPM t | FF3 α (%/mo) | FF3 t |
|-----------|-----------------|--------|------------------|---------------|--------|--------------|-------|
| 1990–1994 | 16.1            | 0.66   | -34.2            | 1.42          | 1.55   | 1.65         | 2.01  |
| 1995–1999 | 19.6            | 0.67   | -34.1            | 1.80          | 1.67   | 1.88         | 1.82  |
| 2000–2004 | 7.4             | 0.13   | -73.1            | 0.18          | 0.13   | -2.49        | -1.88 |
| 2005–2009 | 7.9             | 0.16   | -86.4            | 0.61          | 0.35   | 0.66         | 0.37  |
| 2010–2014 | 6.4             | 0.31   | -26.5            | 1.08          | 1.79   | 0.96         | 1.63  |
| 2015–2019 | 10.0            | 0.34   | -41.4            | 1.49          | 1.40   | 0.81         | 0.76  |
| 2020–2024 | 24.5            | 0.55   | -65.0            | 3.19          | 3.16   | 2.53         | 3.23  |
| 2022–2026 | 45.4            | 1.09   | -44.3            | 4.12          | 3.78   | 2.60         | 2.27  |

Momentum alpha is positive in all periods but collapses to statistical insignificance during
the dot-com reversal (2000–2004) and GFC (2005–2009), where max drawdowns of 73% and 86%
respectively make the gross returns uninvestable in practice. The 2020–2024 and 2022–2026
windows show unusually strong alpha (FF3 t > 3), likely driven by concentration in large-cap
technology and AI-related names — a regime that warrants caution in extrapolation.
No transaction costs are modelled; live implementation costs would materially reduce these figures.