import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings
import fundamental_functions as fct
import data_preprocessing as preprocess
%load_ext autoreload
%autoreload 2
warnings.filterwarnings("ignore")

file = "fundamental-analysis/DSV Financial details 2020-2025.xlsx"

pl_simple, pl_growth, margin_trends = preprocess.preprocess_data(file)

print("Revenue CAGRs:")
for period, (s, e) in [("2010-2025", (2010, 2025)),
                        ("2010-2019", (2010, 2019)),
                        ("2019-2022", (2019, 2022)),
                        ("2022-2025", (2022, 2025))]:
    print(f"  {period}: {fct.cagr(pl_simple['Revenue'], s, e):.1f}%")

fct.bar_chart(pl_simple, 'DSV — Annual Revenue (DKKbn)', 'Revenue', 'DKKbn')

print("EBIT CAGRs:")
for period, (s, e) in [("2010-2025", (2010, 2025)),
                        ("2010-2019", (2010, 2019)),
                        ("2019-2022", (2019, 2022)),
                        ("2022-2025", (2022, 2025))]:
    print(f"  {period}: {fct.cagr(pl_simple['EBIT'], s, e):.1f}%")

fct.bar_chart(pl_simple, 'DSV — Annual EBIT (DKKbn)', 'EBIT', 'DKKbn')

fct.bar_chart(pl_growth, 'DSV — EBIT-margin Growth YoY (%-pts)', 'EBIT_margin', '%', conditional_colors=True)

print("Margin trends:")
margin_trends.tail(5)
fct.line_chart(margin_trends, pl_simple, 'DSV — Margin Trends (%)', '%')

