import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime

# ==========================================
# 1. PAGE CONFIG & COMPACT TERMINAL STYLING
# ==========================================
st.set_page_config(
    page_title="NSE/BSE Intelligence Command Center",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; max-width: 98%; }
    div[data-testid="stMetric"] {
        background-color: #111827;
        border: 1px solid #1f2937;
        padding: 10px 14px;
        border-radius: 8px;
    }
    .trade-box {
        background-color: #111827;
        border: 1px solid #374151;
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 10px;
    }
    .badge-buy { background: #065f46; color: #a7f3d0; padding: 3px 8px; border-radius: 4px; font-weight: 700; }
    .badge-hold { background: #1e40af; color: #bfdbfe; padding: 3px 8px; border-radius: 4px; font-weight: 700; }
    .badge-exit { background: #991b1b; color: #fecaca; padding: 3px 8px; border-radius: 4px; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DEFAULT NSE/BSE DATASET (SAMPLE + LIVE HOOK)
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
    """Fetches live LTP from Yahoo Finance for NSE/BSE symbols."""
    updated_ltps = []
    for _, row in df.iterrows():
        suffix = ".NS" if str(row["Exchange"]).upper() == "NSE" else ".BO"
        ticker = f"{row['Symbol']}{suffix}"
        try:
            hist = yf.Ticker(ticker).history(period="1d")
            if not hist.empty:
                updated_ltps.append(round(float(hist["Close"].iloc[-1]), 2))
            else:
                updated_ltps.append(row["LTP"])
        except Exception:
            updated_ltps.append(row["LTP"])
    df["LTP"] = updated_ltps
    return df

# ==========================================
# 3. INTELLIGENT PARAMETER-WISE SCORING ENGINE
# ==========================================
def score_stock_parameters(row, regime="Bull (VIX < 16)"):
    p = {}

    # --- A. FUNDAMENTAL PARAMETERS (0-100 each) ---
    roce = row["ROCE"]
    p["ROCE"] = 95 if roce >= 22 else (75 if roce >= 15 else (45 if roce >= 10 else 15))

    cfo = row["CFO_PAT"]
    p["Cash Flow"] = 95 if cfo >= 0.85 else (65 if cfo >= 0.6 else (35 if cfo >= 0.4 else 10))

    pg = row["Profit_Growth_YoY"]
    base_g = 85 if pg >= 25 else (70 if pg >= 15 else (45 if pg >= 5 else 15))
    accel_bonus = 15 if pg > row["Profit_CAGR_3Y"] and pg > 0 else 0
    p["Earnings Growth"] = min(100, base_g + accel_bonus)

    peg = row["PEG"]
    p["Valuation (PEG)"] = 95 if 0 < peg <= 1.0 else (75 if peg <= 1.5 else (45 if peg <= 2.2 else 15))

    de = row["Debt_Eq"]
    bs_score = 95 if de <= 0.25 else (70 if de <= 0.7 else (40 if de <= 1.2 else 15))
    if row["Pledge_Pct"] > 10:
        bs_score -= min(40, row["Pledge_Pct"])
    p["Balance Sheet"] = max(5, bs_score)

    fund_score = float(np.mean([p["ROCE"], p["Cash Flow"], p["Earnings Growth"], p["Valuation (PEG)"], p["Balance Sheet"]]))

    # --- B. TECHNICAL PARAMETERS (0-100 each) ---
    ema_map = {"20>50>200": 98, "50>200": 75, "Above_200": 55, "Below_200": 15}
    p["EMA Trend"] = ema_map.get(row["Price_vs_EMA"], 50)

    rsi = row["RSI"]
    if 55 <= rsi <= 68:
        p["RSI Momentum"] = 95
    elif 48 <= rsi < 55 or 68 < rsi <= 75:
        p["RSI Momentum"] = 75
    elif rsi > 75:
        p["RSI Momentum"] = 45
    else:
        p["RSI Momentum"] = 20

    deliv, rvol = row["Delivery_Pct"], row["Rel_Vol"]
    if deliv >= 50 and rvol >= 1.5:
        p["Delivery & Vol"] = 98
    elif deliv >= 40 and rvol >= 1.1:
        p["Delivery & Vol"] = 75
    elif rvol >= 1.8 and deliv < 28:
        p["Delivery & Vol"] = 30
    else:
        p["Delivery & Vol"] = 45

    rs = row["RS_Nifty500"]
    p["Rel Strength"] = 95 if rs >= 15 else (75 if rs >= 5 else (50 if rs >= 0 else 20))

    tech_score = float(np.mean([p["EMA Trend"], p["RSI Momentum"], p["Delivery & Vol"], p["Rel Strength"]]))

    # --- C. RISK & LIQUIDITY PARAMETERS (0-100 each) ---
    atr_pct = row["ATR_Pct"]
    p["Volatility (ATR)"] = 92 if 1.5 <= atr_pct <= 3.0 else (70 if atr_pct < 1.5 or atr_pct <= 3.8 else 28)

    dd = row["Max_DD_1Y"]
    p["Drawdown Safety"] = 92 if dd <= 16 else (70 if dd <= 24 else (45 if dd <= 32 else 20))

    turn = row["Daily_Turnover_Cr"]
    liq = 95 if turn >= 10 else (65 if turn >= 2 else 15)
    if row["ASM_Stage"] > 0:
        liq = min(liq, 25)
    p["Liquidity & ASM"] = liq

    risk_score = float(np.mean([p["Volatility (ATR)"], p["Drawdown Safety"], p["Liquidity & ASM"]]))

    # --- D. DYNAMIC MARKET REGIME WEIGHTING ---
    if regime == "Bull (VIX < 16)":
        w_f, w_t, w_r = 0.35, 0.45, 0.20
    elif regime == "High Risk (VIX > 20)":
        w_f, w_t, w_r = 0.45, 0.20, 0.35
    else:
        w_f, w_t, w_r = 0.40, 0.35, 0.25

    raw_master = (fund_score * w_f) + (tech_score * w_t) + (risk_score * w_r)

    # --- E. CONFLUENCE BONUS & HARD RISK CIRCUIT-BREAKERS ---
    confluence_bonus = 5.0 if (fund_score >= 75 and tech_score >= 75 and risk_score >= 75) else 0.0
    master_score = min(100.0, raw_master + confluence_bonus)

    veto_reasons = []
    if row["ASM_Stage"] > 0:
        veto_reasons.append(f"ASM Stage {int(row['ASM_Stage'])}")
    if row["Pledge_Pct"] > 25:
        veto_reasons.append(f"High Pledge ({row['Pledge_Pct']}%)")
    if row["Daily_Turnover_Cr"] < 1.0:
        veto_reasons.append("Illiquid (<₹1Cr/day)")

    if veto_reasons:
        master_score = min(master_score, 45.0)

    # --- F. RISKOMETER RATING (0-100 Risk Index) ---
    riskometer_val = min(100.0, max(5.0, (atr_pct * 10.0) + (dd * 0.7) + (max(0.0, row["Beta"] - 0.8) * 20.0) + (25.0 if veto_reasons else 0.0)))

    return {
        "Fund_Score": round(fund_score, 1),
        "Tech_Score": round(tech_score, 1),
        "Risk_Score": round(risk_score, 1),
        "Master_Score": round(master_score, 1),
        "Confluence": confluence_bonus,
        "Veto": ", ".join(veto_reasons) if veto_reasons else "Clear",
        "Riskometer": round(riskometer_val, 1),
        "Param_Dict": p
    }

def compute_trade_plan(row, scores, capital, risk_pct):
    ltp = float(row["LTP"])
    atr_val = ltp * (float(row["ATR_Pct"]) / 100.0)
    stop_loss = round(ltp - (2.0 * atr_val), 2)
    risk_per_share = max(0.01, ltp - stop_loss)

    max_risk_rupees = capital * (risk_pct / 100.0)
    rec_qty = int(max_risk_rupees // risk_per_share)
    max_qty_cap = int((capital * 0.20) // ltp) if ltp > 0 else 0
    rec_qty = min(rec_qty, max_qty_cap)

    target_1 = round(ltp + (3.0 * atr_val), 2)
    target_2 = round(ltp + (5.0 * atr_val), 2)

    qty_held = float(row["Qty"])
    buy_avg = float(row["Buy_Avg"])
    invested = qty_held * buy_avg
    current_val = qty_held * ltp
    pnl_rs = current_val - invested
    pnl_pct = ((ltp - buy_avg) / buy_avg * 100.0) if buy_avg > 0 else 0.0

    ms = scores["Master_Score"]
    if qty_held > 0:
        if ms < 55 or scores["Veto"] != "Clear" or ltp <= stop_loss:
            action = "EXIT NOW"
        elif ms >= 75:
            action = f"HOLD (Trail SL ₹{stop_loss})"
        else:
            action = f"HOLD / TIGHTEN SL ₹{stop_loss}"
    else:
        if ms >= 80 and scores["Veto"] == "Clear":
            action = "STRONG BUY"
        elif ms >= 68 and scores["Veto"] == "Clear":
            action = "ACCUMULATE (50%)"
        else:
            action = "AVOID / WATCH"

    return {
        "Entry_Zone": f"₹{round(ltp*0.99, 1)} - ₹{round(ltp*1.005, 1)}",
        "Stop_Loss": stop_loss,
        "Target_1": target_1,
        "Target_2": target_2,
        "Rec_Qty": rec_qty,
        "Invested": round(invested, 2),
        "Current_Val": round(current_val, 2),
        "PnL_Rs": round(pnl_rs, 2),
        "PnL_Pct": round(pnl_pct, 2),
        "Action": action
    }

# ==========================================
# 4. SIDEBAR CONTROLS (DATA & RISK SETTINGS)
# ==========================================
with st.sidebar:
    st.header("⚙️ Terminal Controls")
    
