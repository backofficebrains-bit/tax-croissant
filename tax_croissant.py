import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# ====================== KILLER PROFESSIONAL THEME ======================
st.set_page_config(page_title="Tax Croissant", layout="wide", page_icon="🥐")

custom_css = """
<style>
    .stApp { background: linear-gradient(135deg, #0F172A 0%, #1E2937 100%); color: #F1F5F9; font-family: 'Inter', sans-serif; }
    .main-header { background: linear-gradient(90deg, #00D4FF, #00A3CC); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.8rem; font-weight: 700; }
    .stMetric { background: #1E2937; border-radius: 16px; padding: 18px 20px; box-shadow: 0 10px 15px -3px rgba(0, 212, 255, 0.15); border: 1px solid #334155; }
    .stMetric label { color: #94A3B8; font-size: 0.95rem; font-weight: 500; }
    .stMetric [data-testid="stMetricValue"] { color: #F1F5F9; font-size: 1.85rem; font-weight: 700; }
    .pro-card { background: #1E2937; border-radius: 16px; padding: 24px; border: 1px solid #334155; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🥐 Tax Croissant</h1>', unsafe_allow_html=True)
st.markdown("**Professional Tax Awareness Dashboard** • Zero bank upload • 100% private • Built by Partha Sarathi")

# ====================== SESSION STATE ======================
if 'income' not in st.session_state: st.session_state.income = 1200000
if 'other_income' not in st.session_state: st.session_state.other_income = 0
if 'expenses' not in st.session_state: st.session_state.expenses = pd.DataFrame(columns=["Week", "Amount", "Category"])
if 'existing_80c' not in st.session_state: st.session_state.existing_80c = 0
if 'existing_nps' not in st.session_state: st.session_state.existing_nps = 0
if 'existing_80d' not in st.session_state: st.session_state.existing_80d = 0

# ====================== SIDEBAR ======================
with st.sidebar:
    st.markdown("### 📊 Your Financial Snapshot")
    
    st.subheader("Annual Income")
    st.session_state.income = st.number_input("Gross Salary (₹)", min_value=300000, value=st.session_state.income, step=10000)
    st.session_state.other_income = st.number_input("Other Income (₹)", min_value=0, value=st.session_state.other_income, step=1000)
    
    total_income = st.session_state.income + st.session_state.other_income
    st.metric("Total Gross Income This FY", f"₹{total_income:,.0f}")

    st.divider()

    # === NEW: EXISTING INVESTMENTS & INSURANCE ===
    st.subheader("✅ Your Existing Investments & Insurance")
    st.caption("What you have **already** done this year")
    st.session_state.existing_80c = st.number_input("80C already invested (ELSS, PPF, LIC etc.)", min_value=0, value=st.session_state.existing_80c, step=5000, max_value=150000)
    st.session_state.existing_nps = st.number_input("NPS already contributed", min_value=0, value=st.session_state.existing_nps, step=5000, max_value=50000)
    st.session_state.existing_80d = st.number_input("Health Insurance (80D) premium paid", min_value=0, value=st.session_state.existing_80d, step=1000)
    
    st.divider()

    st.subheader("Weekly Expense Tracker")
    week_date = st.date_input("Week ending", value=datetime.today())
    amount = st.number_input("Amount spent this week (₹)", min_value=0, step=100)
    category = st.selectbox("Category", ["Rent/Housing", "Food & Groceries", "Travel & Commute", "Shopping & Lifestyle", "Entertainment", "Bills & Utilities", "Misc"])
    
    if st.button("✅ Log This Week", use_container_width=True):
        new_row = pd.DataFrame({"Week": [week_date.strftime("%d %b %Y")], "Amount": [amount], "Category": [category]})
        st.session_state.expenses = pd.concat([st.session_state.expenses, new_row], ignore_index=True)
        st.toast("Logged!", icon="🥐")

    if not st.session_state.expenses.empty:
        total_exp = st.session_state.expenses["Amount"].sum()
        st.metric("Total Expenses Tracked", f"₹{total_exp:,.0f}")

# ====================== TAX CALCULATION (NOW WITH EXISTING DEDUCTIONS) ======================
def calculate_tax(gross, existing_80c=0, existing_nps=0, existing_80d=0, regime="new"):
    if regime == "new":
        # New regime: very limited deductions
        taxable = max(0, gross - 75000 - existing_nps)   # only standard + employer NPS
        tax = 0
        slabs = [(400000,0),(800000,0.05),(1200000,0.10),(1600000,0.15),(2000000,0.20),(2400000,0.25)]
        prev = 0
        for limit, rate in slabs:
            if taxable > limit:
                tax += (limit - prev) * rate
                prev = limit
            else:
                tax += (taxable - prev) * rate
                break
        if taxable > 2400000: tax += (taxable - 2400000) * 0.30
        return tax + (tax * 0.04)
    
    else:  # Old regime - full deductions
        total_ded = existing_80c + existing_nps + existing_80d
        taxable = max(0, gross - 75000 - total_ded)
        if taxable <= 250000: return 0
        elif taxable <= 500000: return (taxable - 250000) * 0.05
        elif taxable <= 1000000: return 12500 + (taxable - 500000) * 0.20
        else: return 112500 + (taxable - 1000000) * 0.30

# ====================== MAIN DASHBOARD ======================
total_income = st.session_state.income + st.session_state.other_income

col1, col2, col3, col4 = st.columns(4, gap="small")
with col1:
    new_tax = calculate_tax(total_income, st.session_state.existing_80c, st.session_state.existing_nps, st.session_state.existing_80d, "new")
    st.metric("Projected Tax (New Regime)", f"₹{new_tax:,.0f}")
with col2:
    old_tax = calculate_tax(total_income, st.session_state.existing_80c, st.session_state.existing_nps, st.session_state.existing_80d, "old")
    st.metric("Projected Tax (Old Regime)", f"₹{old_tax:,.0f}")
with col3:
    savings = new_tax - old_tax
    st.metric("Maximum Savings Opportunity", f"₹{savings:,.0f}")
with col4:
    st.metric("Effective Tax Rate", f"{(new_tax / total_income * 100):.1f}%")

st.divider()

# What-if Simulator (now includes existing + additional)
st.markdown('<div class="pro-card"><h3>🎛️ What-If Tax Saver Simulator</h3></div>', unsafe_allow_html=True)
colA, colB = st.columns([1, 3])
with colA:
    additional_80c = st.slider("Additional 80C you can still do", 0, 150000 - st.session_state.existing_80c, 0, step=5000)
    additional_nps = st.slider("Additional NPS", 0, 50000 - st.session_state.existing_nps, 0, step=5000)
    
with colB:
    sim_gross = total_income - additional_80c - additional_nps
    sim_new = calculate_tax(sim_gross, st.session_state.existing_80c + additional_80c, st.session_state.existing_nps + additional_nps, st.session_state.existing_80d, "new")
    sim_old = calculate_tax(sim_gross, st.session_state.existing_80c + additional_80c, st.session_state.existing_nps + additional_nps, st.session_state.existing_80d, "old")
    col_new, col_old = st.columns(2)
    with col_new: st.metric("New Regime After Extra Investments", f"₹{sim_new:,.0f}")
    with col_old: st.metric("Old Regime After Extra Investments", f"₹{sim_old:,.0f}")

# Expense & Partha’s Eye (unchanged)
if not st.session_state.expenses.empty:
    st.subheader("Your Spending Reality")
    fig = px.pie(st.session_state.expenses, names="Category", values="Amount", hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

st.markdown('<div class="pro-card"><h3>👁️ Partha’s Eye – Real Talk</h3></div>', unsafe_allow_html=True)
st.info("**At 12 LPA you are already paying tax.** Whatever you have already invested is already reducing your tax — the numbers above are **your real liability**.")
st.info("Old regime usually wins if you max 80C + NPS + 80D. New regime is simpler but costlier if you invest.")

st.caption("Privacy-first • Data stays in your browser only • Professional DNA by Partha Sarathi")

# Download
if st.button("📄 Download Professional Tax Report", type="primary", use_container_width=True):
    report = pd.DataFrame({
        "Item": ["Gross Income", "Existing 80C", "Existing NPS", "Existing 80D", "New Regime Tax", "Old Regime Tax"],
        "Amount (₹)": [total_income, st.session_state.existing_80c, st.session_state.existing_nps, st.session_state.existing_80d, new_tax, old_tax]
    })
    st.download_button("Download Now", report.to_csv(index=False), "Tax_Croissant_Full_Report.csv", type="primary")