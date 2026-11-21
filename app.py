import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime

# ==========================================
# 1. PAGE CONFIG & BLOOMBERG-STYLE DARK UI
# ==========================================
st.set_page_config(
    page_title="NSE/BSE Pro Intelligence Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    /* Global Dark Theme */
    .stApp { background-color: #0b0f19; color: #f1f5f9; }
    .block-container { padding: 1.2rem 1.8rem 2rem 1.8rem; max-width: 100%; }
    
    /* Top Header Banner */
    .top-banner {
        background: linear-gradient(90deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 14px 20px;
        margin-bottom: 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .banner-title { font-size: 1.35rem; font-weight: 800; color: #38bdf8; letter-spacing: 0.5px; }
    .banner-sub { font-size: 0.85rem; color: #94a3b8; }

    /* KPI Cards */
    div[data-testid="stMetric"] {
        background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
        border: 1px solid #1e293b;
        border-top: 3px solid #3b82f6;
        padding: 12px 16px;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    }
    div[data-testid="stMetric"] label { color: #94a3b8 !important; font-size: 0.82rem !important; }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #f8fafc !important; font-size: 1.45rem !important; }

    /* Pro Panel Cards */
    .pro-card {
        background-color: #111827;
        border: 1px solid #1f2937;
        border-radius: 12px;
        padding: 16px 18px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.35);
        height: 100%;
    }
    .card-header {
        font-size: 0.95rem;
        font-weight: 700;
        color: #e2e8f0;
        border-bottom: 1px solid #1f2937;
        padding-bottom: 8px;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }

    /* Action Badges */
    .badge-buy { background: #064e3b; color: #6ee7b7; border: 1px solid #10b981; padding: 4px 10px; border-radius: 6px; font-weight: 800; font-size: 0.85rem; }
    .badge-acc { background: #1e3a8a; color: #93c5fd; border: 1px solid #3b82f6; padding: 4px 10px; border-radius: 6px; font-weight: 800; font-size: 0.85rem; }
    .badge-hold { background: #312e81; color: #c7d2fe; border: 1px solid #6366f1; padding: 4px 10px; border-radius: 6px; font-weight: 800; font-size: 0.85rem; }
    .badge-exit { background: #7f1d1d; color: #fca5a5; border: 1px solid #ef4444; padding: 4px 10px; border-radius: 6px; font-weight: 800; font-size: 0.85rem; }

    /* Progress Bars for Pillars */
    .pillar-row { margin-bottom: 10px; }
    .pillar-label { display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 4px; color: #cbd5e1; }
    .bar-bg { background: #1e293b; height: 8px; border-radius: 4px; overflow: hidden; }
    .bar-fill { height: 100%; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DEFAULT NSE/BSE PORTFOLIO & WATCHLIST
# ==========================================
def get_default_data():
    data = [
        ["HAL", "NSE", "Defence", 4820.0, 4410.0, 45, 31.5, 1.05, 28.0, 22.0, 1.15, 0.00, 0.0, "20>50>200", 62.0, 54.0, 1.7, 16.5, 2.3, 14.0, 1.05, 420.0, 0],
        ["TRENT", "NSE", "Retail", 6450.0, 0.0, 0, 29.0, 0.92, 46.0, 38.0, 1.45, 0.18, 0.0, "20>50>200", 65.0, 58.0, 1.9, 24.0, 2.6, 16.5, 1.12, 380.0, 0],
        ["TATAMOTORS", "NSE", "Auto", 918.0, 880.0, 200, 18.2, 0.88, 22.0, 19.0, 0.85, 0.65, 0.0, "50>200", 56.0, 48.0, 1.3, 6.2, 2.4, 19.0, 1.25, 610.0, 0],
        ["BEL", "NSE", "Defence", 312.0, 275.0, 500, 26.4, 0.96, 24.5, 20.0, 1.10, 0.00, 0.0, "20>50>200", 60.0, 52.0, 1.6, 14.0, 2.5, 15.5, 1.10, 310.0, 0],
        ["KPITTECH", "NSE", "IT", 1540.0, 0.0, 0, 24.8, 0.90, 29.0, 25.0, 1.35, 0.08, 0.0, "20>50>200", 59.0, 49.0, 1.5, 11.5, 2.8, 18.0, 1.18, 145.0, 0],
        ["SUZLON", "NSE", "Energy", 64.5, 72.0, 2000, 14.5, 0.62, 35.0, 18.0, 1.60, 0.25, 0.0, "Below_200", 41.0, 24.0, 2.2, -12.0, 4.8, 36.0, 1.65, 210.0, 1],
        ["IDEA", "NSE", "Telecom", 8.4, 11.2, 10000, -4.0, 0.30, -15.0, -10.0, 5.00, 4.50, 0.0, "Below_200", 33.0, 21.0, 1.1, -28.0, 5.6, 44.0, 1.55, 190.0, 0],
        ["SMALLCAPX", "BSE", "Chemicals", 410.0, 0.0, 0, 19.0, 0.78, 21.0, 17.0, 0.95, 0.45, 32.0, "20>50>200", 67.0, 31.0, 1.8, 12.0, 4.2, 29.0, 1.40, 0.4, 0],
    ]
    cols = [
        "Symbol", "Exchange", "Sector", "LTP", "Buy_Avg", "Qty",
        "ROCE", "CFO_PAT", "Profit_Growth_YoY", "Profit_CAGR_3Y", "PEG", "Debt_Eq", "Pledge_Pct",
        "Price_vs_EMA", "RSI", "Delivery_Pct", "Rel_Vol", "RS_Nifty500",
        "ATR_Pct", "Max_DD_1Y", "Beta", "Daily_Turnover_Cr", "ASM_Stage"
    ]
    return pd.DataFrame(data, columns=cols)

def fetch_live_ltp(df):
    updated_ltps = []
    for _, row in df.iterrows():
        suffix = ".NS" if str(row["Exchange"]).upper() == "NSE" else ".BO"
        ticker = f"{row['Symbol']}{suffix}"
        try:
            hist = yf.Ticker(ticker).history(period="1d")
            if not hist.empty:
                updated_ltps.append(round(float(hist["Close"].tail(1).item()), 2))
            else:
                updated_ltps.append(row["LTP"])
        except Exception:
            updated_ltps.append(row["LTP"])
    df["LTP"] = updated_ltps
    return df

# ==========================================
# 3. INTELLIGENT PARAMETER SCORING ENGINE
# ==========================================
def score_stock_parameters(row, regime="Bull (VIX < 16)"):
    p = {}
    roce = row["ROCE"]
    p["ROCE Quality"] = 95 if roce >= 22 else (75 if roce >= 15 else (45 if roce >= 10 else 15))

    cfo = row["CFO_PAT"]
    p["Cash Flow (CFO/PAT)"] = 95 if cfo >= 0.85 else (65 if cfo >= 0.6 else (35 if cfo >= 0.4 else 10))

    pg = row["Profit_Growth_YoY"]
    base_g = 85 if pg >= 25 else (70 if pg >= 15 else (45 if pg >= 5 else 15))
    accel_bonus = 15 if pg > row["Profit_CAGR_3Y"] and pg > 0 else 0
    p["Earnings Accel"] = min(100, base_g + accel_bonus)

    peg = row["PEG"]
    p["Valuation (PEG)"] = 95 if 0 < peg <= 1.0 else (75 if peg <= 1.5 else (45 if peg <= 2.2 else 15))

    de = row["Debt_Eq"]
    bs_score = 95 if de <= 0.25 else (70 if de <= 0.7 else (40 if de <= 1.2 else 15))
    if row["Pledge_Pct"] > 10:
        bs_score -= min(40, row["Pledge_Pct"])
    p["Balance Sheet"] = max(5, bs_score)

    fund_score = float(np.mean(list(p.values())))

    t = {}
    ema_map = {"20>50>200": 98, "50>200": 75, "Above_200": 55, "Below_200": 15}
    t["EMA Alignment"] = ema_map.get(row["Price_vs_EMA"], 50)

    rsi = row["RSI"]
    if 55 <= rsi <= 68:
        t["RSI Momentum"] = 95
    elif 48 <= rsi < 55 or 68 < rsi <= 75:
        t["RSI Momentum"] = 75
    elif rsi > 75:
        t["RSI Momentum"] = 45
    else:
        t["RSI Momentum"] = 20

    deliv, rvol = row["Delivery_Pct"], row["Rel_Vol"]
    if deliv >= 50 and rvol >= 1.5:
        t["Delivery & Vol"] = 98
    elif deliv >= 40 and rvol >= 1.1:
        t["Delivery & Vol"] = 75
    elif rvol >= 1.8 and deliv < 28:
        t["Delivery & Vol"] = 30
    else:
        t["Delivery & Vol"] = 45

    rs = row["RS_Nifty500"]
    t["Rel Strength"] = 95 if rs >= 15 else (75 if rs >= 5 else (50 if rs >= 0 else 20))

    tech_score = float(np.mean(list(t.values())))

    rk = {}
    atr_pct = row["ATR_Pct"]
    rk["Volatility (ATR)"] = 92 if 1.5 <= atr_pct <= 3.0 else (70 if atr_pct < 1.5 or atr_pct <= 3.8 else 28)

    dd = row["Max_DD_1Y"]
    rk["Drawdown Safety"] = 92 if dd <= 16 else (70 if dd <= 24 else (45 if dd <= 32 else 20))

    turn = row["Daily_Turnover_Cr"]
    liq = 95 if turn >= 10 else (65 if turn >= 2 else 15)
    if row["ASM_Stage"] > 0:
        liq = min(liq, 25)
    rk["Liquidity & ASM"] = liq

    risk_score = float(np.mean(list(rk.values())))
    all_params = {**p, **t, **rk}

    if regime == "Bull (VIX < 16)":
        w_f, w_t, w_r = 0.35, 0.45, 0.20
    elif regime == "High Risk (VIX > 20)":
        w_f, w_t, w_r = 0.45, 0.20, 0.35
    else:
        w_f, w_t, w_r = 0.40, 0.35, 0.25

    raw_master = (fund_score * w_f) + (tech_score * w_t) + (risk_score * w_r)
    confluence_bonus = 5.0 if (fund_score >= 75 and tech_score >= 75 and risk_score >= 75) else 0.0
    master_score = min(100.0, raw_master + confluence_bonus)

    veto_reasons = []
    if row["ASM_Stage"] > 0:
        veto_reasons.append(f"ASM Stage {int(row['ASM_Stage'])}")
    if row["Pledge_Pct"] > 25:
        veto_reasons.append(f"Pledge {row['Pledge_Pct']}%")
    if row["Daily_Turnover_Cr"] < 1.0:
        veto_reasons.append("Low Liquidity")

    if veto_reasons:
        master_score = min(master_score, 45.0)

    riskometer_val = min(100.0, max(5.0, (atr_pct * 10.0) + (dd * 0.7) + (max(0.0, row["Beta"] - 0.8) * 20.0) + (25.0 if veto_reasons else 0.0)))

    return {
        "Fund_Score": round(fund_score, 1),
        "Tech_Score": round(tech_score, 1),
        "Risk_Score": round(risk_score, 1),
        "Master_Score": round(master_score, 1),
        "Confluence": confluence_bonus,
        "Veto": ", ".join(veto_reasons) if veto_reasons else "Clear",
        "Riskometer": round(riskometer_val, 1),
        "Param_Dict": all_params
    }

def compute_trade_plan(row, scores, capital, risk_pct):
    ltp = float(row["LTP"])
    atr_val = ltp * (float(row["ATR_Pct"]) / 100.0)
    stop_loss = round(ltp - (2.0 * atr_val), 2)
    risk_per_share = max(0.01, ltp - stop_loss)

    max_risk_rupees = capital * (risk_pct / 100.0)
    rec_qty = int(max_risk_rupees // risk_per_share)
    max_qty_cap = int((capital * 0.20) // ltp) if ltp > 0 else 0
        
