import os
from fredapi import Fred
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

start_date = "1960-02-01"
end_date = "2024-12-01"

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
FRED_API_KEY = os.getenv("FRED_API_KEY")

if FRED_API_KEY is None:
    raise ValueError(
        "Please set the FRED_API_KEY in environment variable"
    )

fred = Fred(api_key=FRED_API_KEY)

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
ff3_monthly.to_parquet("data/ff3_monthly.parquet", index=False)
macro.to_parquet("data/macro.parquet", index=False)



