# Strategic vs. Tactical Asset Allocation
Inspired by Faber (2007), a tactical asset allocation (TAA) portfolio is constructed and benchmarked against a strategic 60/40 portfolio (US equities / US bonds) and an equal-weight buy-and-hold portfolio. The TAA signal rotates each asset to cash (SHY) when its price falls below its 10-month simple moving average. Analysis covers 2002–2026 using ETF proxies (SPY, EFA, IEF, GSG, VNQ). Performance is evaluated on annualised excess returns, volatility, Sharpe ratio, and maximum drawdown, reported both over the full period and across five-year subperiods.

## Covered periods:
    2002–2007: Dot-com recovery
    2007–2012: GFC and aftermath
    2012–2017: US equity bull market
    2017–2022: Late cycle, COVID crash, reopening
    2022–2026: Rate shock and AI rally


## Key Results
## Full-period results (2002–2026)

| Strategy       | Ann. Excess Return | Volatility | Sharpe | Max Drawdown |
|----------------|--------------------|------------|--------|--------------|
| TAA            | 6.52%              | 6.33%      | 1.03   | −10.2%       |
| Equal-weighted | 6.82%              | 12.16%     | 0.56   | −46.6%       |
| 60/40          | 8.40%              | 9.13%      | 0.92   | −29.4%       |

> TAA delivers competitive risk-adjusted returns (Sharpe 1.03 vs. 0.92 for 60/40) at roughly half the volatility and a fraction of the drawdown. The cost is modest underperformance in raw returns during US-equity-dominated regimes.

## Methodology 
Stocks are sorted monthly into deciles by 12-2 momentum (cumulative return from T-12 to T-2, skipping the most recent month to avoid short-term reversal). Decile portfolios are value-weighted. The WML factor is constructed as D10 minnus D1. CAPM and FF3 alphas are estimated via OLS. 

## Data
 - CRSP 
 - Ken French FF3 factors via the French data library

 