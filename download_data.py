import os
import tidyfinance as tf
import pandas_datareader as pdr
import yfinance as yf
import pandas as pd
from pandas.tseries.offsets import MonthEnd
import numpy as np
from tqdm import tqdm 
import urllib.request
import zipfile
import requests
from dotenv import load_dotenv

start_date = "2000-01-01"
end_date = "2026-06-10"

constituents = tf.download_data(domain="constituents", index="S&P 500")
symbols = constituents["symbol"].tolist()

# ── Prices ──────────────────────────────────────────────────

prices_raw = tf.download_data(
    domain="stock_prices",
    symbols = symbols,
    start_date=start_date,
    end_date=end_date
)

prices = (
    prices_raw
    .assign(date=lambda x: pd.to_datetime(x["date"]))
    .sort_values(["symbol", "date"])
)

prices_monthly = (
    prices
    .groupby("symbol")
    .resample("ME", on="date")
    .agg(
        adj_close=("adjusted_close", "last"),
        volume=("volume", "sum"),
    )
    .reset_index()
)

returns_monthly = (
    prices_monthly
    .assign(returns_monthly = lambda df: df['adj_close'].pct_change())
    .dropna()
)

# ── Market Capitalization ──────────────────────────────────────────────────
shares_list = []

for symbol in tqdm(symbols, desc="Downloading shares outstanding"):
    try:
        ticker = yf.Ticker(symbol)
        shares = ticker.get_shares_full(start=start_date, end=end_date)

        if shares is not None and not shares.empty:
            df = shares.reset_index()
            df.columns = ["date", "shares_outstanding"]
            df["symbol"] = symbol
            shares_list.append(df)

    except Exception as e:
        print(f"Failed for {symbol}: {e}")

shares_df = pd.concat(shares_list, ignore_index=True)

def remove_timezones(d):
    d = pd.to_datetime(d)
    if d.tzinfo is not None: 
        return d.tz_convert(None)
    return d

shares_df["date"] = shares_df["date"].apply(remove_timezones)

shares_monthly = (
    shares_df
    .sort_values(["symbol", "date"])
    .groupby("symbol")
    .resample("ME", on="date")
    .agg(shares_outstanding=("shares_outstanding", "last"))
    .reset_index()
)

# ── Fama French Data ──────────────────────────────────────────────────
url = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_CSV.zip"

zip_path = "data/fama_french.zip"
csv_path = "data/F-F_Research_Data_Factors.CSV"

urllib.request.urlretrieve(url, zip_path)

with zipfile.ZipFile(zip_path, "r") as zf:
    zf.extractall("data")

factor_cols = ["Mkt-RF", "SMB", "HML", "RF"]

ff3_monthly = (
    pd.read_csv(csv_path, skiprows=3)
    .loc[lambda df: df.iloc[:, 0].astype(str).str.match(r"^\d{6}$")]
    .rename(columns=lambda c: "date" if c == "Unnamed: 0" else c)
    .assign(
        date=lambda df: pd.to_datetime(df["date"], format="%Y%m") + MonthEnd(0),
        **{
            col: lambda df, col=col: df[col].astype(float) / 100
            for col in factor_cols
        }
    )
)

# ── Macro data from FRED ──────────────────────────────────────────────────
from fredapi import Fred
FRED_API_KEY = os.getenv("FRED_API_KEY")

if FRED_API_KEY is None:
    raise ValueError(
        "Please set the FRED_API_KEY in environment variable"
    )

fred = Fred(api_key="")

fred_series = {
    "DGS10": "treasury_10y",
    "DGS2":  "treasury_2y",
    "CPIAUCNS": "cpi",
    "UNRATE": "unemployment",
    "INDPRO": "industrial_prod",
}

macro_frames = []
for series, name in fred_series.items():
    df = (
        fred.get_series(series, observation_start=start_date, observation_end=end_date)
        .rename(name)
        .to_frame()
    )
    macro_frames.append(df)

macro = (
    pd.concat(macro_frames, axis=1)
    .reset_index()
    .rename(columns={"index": "date"})
)

macro["term_spread"] = macro["treasury_10y"] - macro["treasury_2y"]
print(macro.head())

(
    macro.isna()
    .sum()
    .rename("n_missing")
    .to_frame()
    .sort_values("n_missing", ascending=False)
)

# ── Save data ───────────────────────────────────────────────────────────────────
os.makedirs("data", exist_ok=True)
shares_monthly.to_parquet("data/shares_monthly.parquet", index=False)
returns_monthly.to_parquet("data/returns_monthly.parquet", index=False)
ff3_monthly.to_parquet("data/ff3_monthly.parquet", index=False)


