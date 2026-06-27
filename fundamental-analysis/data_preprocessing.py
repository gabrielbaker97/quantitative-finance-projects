import pandas as pd

def preprocess_data(file):
    # ── Load ──────────────────────────────────────────────────────────────────
    pl_group = pd.read_excel(file, sheet_name="Group P&L", header=2, nrows=31)

    fy_cols = ["(DKKm)"] + [c for c in pl_group.columns if str(c).startswith("FY")]

    # ── PL Group ──────────────────────────────────────────────────────────────
    pl_group = (pl_group[fy_cols]
        .set_index("(DKKm)")
        .dropna(how="all")
        .rename(columns=lambda c: str(c)[-4:])
        .T
    )
    pl_group.index = pl_group.index.astype(int)

    # ── PL Simple ─────────────────────────────────────────────────────────────
    pl_simple = (pl_group[['Revenue', 'Gross profit', 'EBITDA before special items',
                            'EBIT before special items', 'Profit for the period']]
        .rename(columns={'EBITDA before special items': 'EBITDA',
                         'EBIT before special items':   'EBIT',
                         'Profit for the period':       'Net profit'})
        .assign(EBIT_margin=lambda df: df['EBIT'] / df['Revenue'] * 100)
    )[['Revenue', 'Gross profit', 'EBITDA', 'EBIT', 'EBIT_margin', 'Net profit']]

    # ── PL Growth ─────────────────────────────────────────────────────────────
    pl_growth = (pl_simple[['Revenue', 'Gross profit', 'EBITDA', 'EBIT', 'Net profit']]
        .pct_change()
        .dropna(how='all')
        .multiply(100)
        .assign(EBIT_margin=pl_simple['EBIT_margin'].diff().dropna())
    )[['Revenue', 'Gross profit', 'EBITDA', 'EBIT', 'EBIT_margin', 'Net profit']]

    # ── Margin Trends ─────────────────────────────────────────────────────────
    margin_trends = (pl_simple[['Gross profit', 'EBITDA', 'EBIT', 'Net profit']]
        .divide(pl_simple['Revenue'], axis=0)
        .multiply(100)
        .rename(columns={'Gross profit': 'Gross margin', 'EBITDA': 'EBITDA margin',
                         'EBIT':         'EBIT margin',  'Net profit': 'Net margin'})
    )

    return pl_simple, pl_growth, margin_trends
