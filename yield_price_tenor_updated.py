from datetime import datetime
import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta

live_bonds = pd.read_csv("bonds_live_platform.csv")
fimmda_yld = pd.read_excel("fimmda_yield_curve.xlsx")
my_ptf = pd.read_csv("my_portfolio.csv")

def macaulay_duration(settlement_date, maturity_date, coupon_rate, yield_rate, no_of_int_payments_per_year):

    ### Calculating Macaulay Duration for Bullet Principal Bonds
    if no_of_int_payments_per_year != 0 :

        temp_date = maturity_date
        repayment_dates = []

        while temp_date > settlement_date:
            repayment_dates.append(temp_date)
            temp_date = pd.to_datetime(datetime.date(temp_date) - relativedelta(months=12 / no_of_int_payments_per_year))

        repayment_dates.append(settlement_date)
        repayment_dates.reverse()

        cashflows = pd.DataFrame()
        cashflows['dates'] = repayment_dates
        cashflows['days_diff'] = (cashflows['dates'] - settlement_date).dt.days
        cashflows['days_diff_btn'] = (cashflows['dates'] - cashflows['dates'].shift(1)).dt.days
        cashflows['principal'] = 0
        cashflows.loc[cashflows['dates'] == maturity_date, 'principal'] = 1
        cashflows.loc[0, 'days_diff_btn'] = 0
        cashflows['interest'] = 1*coupon_rate*(cashflows['days_diff_btn']/365)
        cashflows['pv'] = [(cashflows['principal'][i] + cashflows['interest'][i])/np.power(1 + yield_rate, cashflows['days_diff'][i]/365) for i in range(0, cashflows.shape[0])]
        cashflows['time_weight'] = cashflows['pv'] * cashflows['days_diff']/365
        duration = sum(cashflows['time_weight'])/sum(cashflows['pv'])
    else:
        duration = (maturity_date - settlement_date).days/365

    return duration

def yield_curve(segment, maturity_date, rating):
    # maturity_date as string- as per the db
    tenor = (datetime.strptime(maturity_date, '%d-%m-%Y').date() - datetime.now().date()).days / 365
    yld_fimmda = fimmda_yld.loc[(fimmda_yld["segment"] == segment) & (fimmda_yld["rating"] == rating), ["tenor","yield"]].reset_index(drop=True)
    np.searchsorted(yld_fimmda["tenor"], tenor)
    idx = np.searchsorted(yld_fimmda["tenor"], tenor)
    l_yield = yld_fimmda.loc[idx - 1, "yield"]
    u_yield = yld_fimmda.loc[idx, "yield"]
    l_tenor = yld_fimmda.loc[idx - 1, "tenor"]
    u_tenor = yld_fimmda.loc[idx, "tenor"]
    yld = (((tenor - l_tenor) / (u_tenor - l_tenor)) * (u_yield - l_yield)) + l_yield
    return yld, tenor

def indicative_price(m,t,ytm,fv,c):
    # m - no. of interest payments in a year
    # t - tenor
    # ytm - yield
    # fv - face value
    # c - coupon
    return ((fv * c / m * (1 - (1 + ytm / m) ** (-m * t))) / (ytm / m)) + fv * (1 + (ytm / m)) ** (-m * t)

def risk_o_meter(crv, lrv, mrv):
    score = max(((crv + lrv + mrv) / 3), lrv)
    if score <= 1:
        risk_cat = "Low"
    elif (score <= 2) and (score > 1):
        risk_cat = "Low to Moderate"
    elif (score <= 3) and (score > 2):
        risk_cat = "Moderate"
    elif (score <= 4) and (score > 3):
        risk_cat = "Moderately High"
    elif (score <= 5) and (score > 4):
        risk_cat = "High"
    else:
        risk_cat = "Very High"
    return risk_cat

def int_payment_freq(freq):
    if freq == "Half Yearly":
        freq_num = 2
    elif freq == "Monthly":
        freq_num = 12
    elif freq == "Quarterly":
        freq_num = 4
    else:
        freq_num = 1
    return freq_num

# discovery

def isin_fetch(isin_lst):
    issuer_lst = []
    tenor_lst = []
    yield_lst = []
    rom_lst = []
    for i in isin_lst:
        seg = live_bonds.loc[live_bonds["isin"] == i, ["industry"]].iloc[0, 0]
        issuer = live_bonds.loc[live_bonds["isin"] == i, ["name"]].iloc[0, 0]
        mat = live_bonds.loc[live_bonds["isin"] == i, ["maturity_date"]].iloc[0, 0]
        rtng = live_bonds.loc[live_bonds["isin"] == i, ["rating_yield_curve"]].iloc[0, 0]
        yld, tnr = yield_curve(seg, mat, rtng)
        ipy_str = live_bonds.loc[live_bonds["isin"] == i, ["interest_payment_frequency"]].iloc[0, 0]
        ipy = int_payment_freq(ipy_str)
        cpn = live_bonds.loc[live_bonds["isin"] == i, ["coupon_rate"]].iloc[0, 0]
        credit = live_bonds.loc[live_bonds["isin"] == i, ["credit_risk_value_rom"]].iloc[0, 0]
        liq = live_bonds.loc[live_bonds["isin"] == i, ["liq_risk_value"]].iloc[0, 0]
        maturity_date = pd.to_datetime(mat, format='%d-%m-%Y')
        mrv = macaulay_duration(pd.to_datetime('today'), maturity_date, cpn, yld,ipy)
        rom = risk_o_meter(credit, liq, mrv)
        issuer_lst.append(issuer)
        tenor_lst.append(tnr)
        yield_lst.append(yld)
        rom_lst.append(rom)
    discovery_df = pd.DataFrame({"ISIN": isin_lst, "Issuer": issuer_lst, "Tenor": tenor_lst, "Yield": yield_lst, "Risk-O-Meter": rom_lst})
    return discovery_df

isin_lst = ["INE01YL07102", "INE06E507058"]
disc_df = isin_fetch(isin_lst)

# dashboard

def metrics(ptf):
    isin_lst = ptf["isin"].tolist()
    issuer_lst = []
    current_inv_amt_lst = []
    p_and_l_lst = []
    rom_lst = []
    for i in isin_lst:
        isin = i
        qty = ptf.loc[ptf["isin"] == isin, "qty"]
        buy_price = ptf.loc[ptf["isin"] == isin, "buy_price"]
        seg = live_bonds.loc[live_bonds["isin"] == isin, ["industry"]].iloc[0, 0]
        issuer = live_bonds.loc[live_bonds["isin"] == isin, ["name"]].iloc[0, 0]
        mat = live_bonds.loc[live_bonds["isin"] == isin, ["maturity_date"]].iloc[0, 0]
        rtng = live_bonds.loc[live_bonds["isin"] == isin, ["rating_yield_curve"]].iloc[0, 0]
        yld, tnr = yield_curve(seg, mat, rtng)
        ipy_str = live_bonds.loc[live_bonds["isin"] == isin, ["interest_payment_frequency"]].iloc[0, 0]
        ipy = int_payment_freq(ipy_str)
        fv = live_bonds.loc[live_bonds["isin"] == isin, ["face_value"]].iloc[0, 0]
        cpn = live_bonds.loc[live_bonds["isin"] == isin, ["coupon_rate"]].iloc[0, 0]
        freq = int_payment_freq(ipy)
        ind_current_price = indicative_price(freq, tnr, yld, fv, cpn)
        current_inv_amt = ind_current_price * qty
        p_and_l = current_inv_amt - (buy_price * qty)
        credit = live_bonds.loc[live_bonds["isin"] == isin, ["credit_risk_value_rom"]].iloc[0, 0]
        liq = live_bonds.loc[live_bonds["isin"] == isin, ["liq_risk_value"]].iloc[0, 0]
        maturity_date = pd.to_datetime(mat, format='%d-%m-%Y')
        mrv = macaulay_duration(pd.to_datetime('today'), maturity_date, cpn, yld, ipy)
        rom = risk_o_meter(credit, liq, mrv)
        issuer_lst.append(issuer)
        current_inv_amt_lst.append(current_inv_amt)
        p_and_l_lst.append(p_and_l)
        rom_lst.append(rom)

    return isin_lst, issuer_lst, current_inv_amt_lst, p_and_l_lst, rom_lst

def portfolio_rom():
    pass

print(metrics(my_ptf))

disc_df.to_csv("disc_df.csv", index = False)

