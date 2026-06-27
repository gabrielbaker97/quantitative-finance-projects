import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
load_dotenv()

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical.crypto import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame

# Setup 
API_KEY    = os.environ.get("ALPACA_API_KEY")
API_SECRET = os.environ.get("ALPACA_API_SECRET")
PAPER      = True

UNIVERSE   = ["BTC/USD", "ETH/USD", "SOL/USD", "LINK/USD"]
SMA_WINDOW = 50          
MIN_TRADE  = 1.0         

RESULTS_DIR = "live-taa/results/live_crypto_taa"
os.makedirs(RESULTS_DIR, exist_ok=True)

UTC = ZoneInfo("UTC")

trading_client = TradingClient(API_KEY, API_SECRET, paper=PAPER)
data_client    = CryptoHistoricalDataClient()  

# Data
def fetch_prices(symbols: list[str], lookback_days: int = 80) -> pd.DataFrame:
    """Hent daglige lukkekurser for crypto-symboler."""
    end   = datetime.now(UTC)
    start = end - timedelta(days=lookback_days + 10)

    request = CryptoBarsRequest(
        symbol_or_symbols=symbols,
        timeframe=TimeFrame.Day,
        start=start,
        end=end,
    )

    bars   = data_client.get_crypto_bars(request).df
    prices = (
        bars["close"]
        .unstack(level=0)
        .sort_index()
        .iloc[-lookback_days:]
    )
    return prices


# Signal
def compute_signals(prices: pd.DataFrame, window: int = SMA_WINDOW) -> pd.Series:
    sma      = prices.rolling(window).mean()
    last_px  = prices.iloc[-1]
    last_sma = sma.iloc[-1]
    return last_px > last_sma


def get_portfolio_value() -> float:
    return float(trading_client.get_account().portfolio_value)


def get_current_positions() -> dict[str, float]:
    return {
        p.symbol: float(p.market_value)
        for p in trading_client.get_all_positions()
    }


# Order
def liquidate(symbol: str) -> None:
    # Alpaca bruger "BTCUSD" (uden slash) i positions
    symbol_clean = symbol.replace("/", "")
    try:
        trading_client.close_position(symbol_clean)
        print(f"  LIQUIDATE  {symbol}")
    except Exception as exc:
        print(f"  [!] Kunne ikke lukke {symbol}: {exc}")


def place_order(symbol: str, notional: float, side: OrderSide) -> None:
    if notional < MIN_TRADE:
        return
    order = MarketOrderRequest(
        symbol=symbol,
        notional=round(notional, 2),
        side=side,
        time_in_force=TimeInForce.GTC,   # GTC — ingen lukketid for crypto
    )
    trading_client.submit_order(order)
    direction = "BUY " if side == OrderSide.BUY else "SELL"
    print(f"  {direction}  {symbol:12s}  ${notional:>10,.2f}")


# Rebalance
def rebalance(signals: pd.Series) -> None:
    """
    Equal weight pr. long-aktiv.
    Off-signal coins sælges og lades som USD cash i kontoen.
    """
    portfolio_value = get_portfolio_value()
    current         = get_current_positions()

    long_pairs = [t for t, s in signals.items() if s]

    if not long_pairs:
        print("  Ingen long-signaler — lukker alle positioner, holder USD cash.")
        for sym in list(current.keys()):
            liquidate(sym)
        return

    per_asset = portfolio_value / len(signals)   
    targets   = {t: per_asset for t in long_pairs}

    current_clean = {k.replace("/", ""): (k, v) for k, v in current.items()}
    target_clean  = {k.replace("/", ""): (k, v) for k, v in targets.items()}

    for sym_clean, (sym_orig, _) in current_clean.items():
        if sym_clean not in target_clean:
            liquidate(sym_orig)

    for sym_clean, (sym_orig, target_val) in target_clean.items():
        current_val = current_clean.get(sym_clean, (None, 0.0))[1]
        diff        = target_val - current_val

        if diff > MIN_TRADE:
            place_order(sym_orig, diff, OrderSide.BUY)
        elif diff < -MIN_TRADE:
            place_order(sym_orig, abs(diff), OrderSide.SELL)
        else:
            print(f"  HOLD       {sym_orig:12s}  (Δ${diff:+.0f}, inden for tolerance)")


# Logging
def log_state(signals: pd.Series, prices: pd.DataFrame) -> None:
    account  = trading_client.get_account()
    last_px  = prices[UNIVERSE].iloc[-1]
    last_sma = prices[UNIVERSE].rolling(SMA_WINDOW).mean().iloc[-1]

    row = {
        "timestamp":       datetime.now(UTC).isoformat(),
        "portfolio_value": float(account.portfolio_value),
        "cash":            float(account.cash),
    }
    for t in UNIVERSE:
        row[f"px_{t.replace('/', '_')}"]     = round(last_px[t], 4)
        row[f"sma_{t.replace('/', '_')}"]    = round(last_sma[t], 4)
        row[f"signal_{t.replace('/', '_')}"] = int(signals[t])

    log_path = os.path.join(RESULTS_DIR, "signal_log.csv")
    pd.DataFrame([row]).to_csv(
        log_path,
        mode="a",
        header=not os.path.exists(log_path),
        index=False,
        float_format="%.4f",
    )


# Main
def run() -> None:
    ts = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"\n{'='*60}")
    print(f"  Live Crypto TAA  —  {ts}")
    print(f"{'='*60}")

    all_symbols = UNIVERSE

    print(f"\n[1/4] Henter priser (SMA-{SMA_WINDOW} lookback)...")
    prices = fetch_prices(all_symbols, lookback_days=SMA_WINDOW + 10)
    print(f"      {len(prices)} dage hentet for {len(all_symbols)} coins")

    print(f"\n[2/4] Beregner SMA-{SMA_WINDOW} signaler...")
    signals = compute_signals(prices[UNIVERSE], window=SMA_WINDOW)
    for ticker, sig in signals.items():
        px  = prices[ticker].iloc[-1]
        sma = prices[ticker].rolling(SMA_WINDOW).mean().iloc[-1]
        flag = "LONG ▲" if sig else "CASH  ▼"
        print(f"  {ticker:12s}  {flag}   kurs={px:>10.2f}  SMA={sma:>10.2f}")

    print(f"\n[3/4] Rebalancerer ({signals.sum()} long, {(~signals).sum()} i cash)...")
    rebalance(signals)

    print("\n[4/4] Logger tilstand...")
    log_state(signals, prices)

    account = trading_client.get_account()
    print(f"\n  Porteføljeværdi : ${float(account.portfolio_value):>12,.2f}")
    print(f"  Likvide midler  : ${float(account.cash):>12,.2f}")
    print(f"\nFærdig. Log gemt → {RESULTS_DIR}/signal_log.csv\n")


if __name__ == "__main__":
    run()