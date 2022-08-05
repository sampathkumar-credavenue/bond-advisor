from datetime import datetime
import numpy as np
import pandas as pd
from risk_profiling import macaulay_duration

live_bonds = pd.read_csv("bonds_live_platform.csv")
fimmda_yld = pd.read_excel("fimmda_yield_curve.xlsx")
my_ptf = pd.read_csv("my_portfolio.csv")
duration = pd.read_csv("x.csv")

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


print(yield_curve("Corporates", '20-01-2026', "BBB-"))
print(indicative_price(2, yield_curve("Corporates", '20-01-2026', "BBB-")[1], yield_curve("Corporates", '20-01-2026', "BBB-")[0], 100, 0.1466))
print(risk_o_meter(1,2,3))

# discovery

def isin_fetch(isin_lst):
    issuer_lst = []
    tenor_lst = []
    yield_lst = []
    rom_lst = []
    for i in isin_lst:
        seg = live_bonds.loc[live_bonds["isin"] == isin, ["industry"]].iloc[0, 0]
        issuer = live_bonds.loc[live_bonds["isin"] == isin, ["name"]].iloc[0, 0]
        mat = live_bonds.loc[live_bonds["isin"] == isin, ["maturity_date"]].iloc[0, 0]
        rtng = live_bonds.loc[live_bonds["isin"] == isin, ["rating_yield_curve"]].iloc[0, 0]
        yld, tnr = yield_curve(seg, mat, rtng)
        ipy = live_bonds.loc[live_bonds["isin"] == isin, ["interest_payment_frequency"]].iloc[0, 0]
        fv = live_bonds.loc[live_bonds["isin"] == isin, ["face_value"]].iloc[0, 0]
        cpn = live_bonds.loc[live_bonds["isin"] == isin, ["coupon_rate"]].iloc[0, 0]
        credit = live_bonds.loc[live_bonds["isin"] == isin, ["credit_risk_value_rom"]].iloc[0, 0]
        liq = live_bonds.loc[live_bonds["isin"] == isin, ["liq_risk_value"]].iloc[0, 0]
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

isin_fetch(isin_lst)

# dashboard
#
# def metrics(ptf):
#     isin = ptf.loc[0, "isin"]
#     seg = live_bonds.loc[live_bonds["isin"] == isin, ["industry"]].iloc[0, 0]
#     issuer = live_bonds.loc[live_bonds["isin"] == isin, ["name"]].iloc[0, 0]
#     mat = live_bonds.loc[live_bonds["isin"] == isin, ["maturity_date"]].iloc[0, 0]
#     rtng = live_bonds.loc[live_bonds["isin"] == isin, ["rating_yield_curve"]].iloc[0, 0]
#     yld, tnr = yield_curve(seg, mat, rtng)
#     ipy = live_bonds.loc[live_bonds["isin"] == isin, ["interest_payment_frequency"]].iloc[0, 0]
#     fv = live_bonds.loc[live_bonds["isin"] == isin, ["face_value"]].iloc[0, 0]
#     cpn = live_bonds.loc[live_bonds["isin"] == isin, ["coupon_rate"]].iloc[0, 0]
#     freq = int_payment_freq(ipy)
#     ind_current_price = indicative_price(freq, tnr, yld, fv, cpn)
#
#
#
#
#     return ind_current_price, issuer
#
# metrics(my_ptf)
