from datetime import datetime
import numpy as np
import pandas as pd

live_bonds = pd.read_csv("bonds_live_platform.csv")
fimmda_yld = pd.read_excel("fimmda_yield_curve.xlsx")

def yield_curve(segment, maturity_date, rating):
    # maturity_date as string- as per the db
    tenor = (datetime.strptime(maturity_date, '%d/%m/%y').date() - datetime.now().date()).days / 365
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

print(yield_curve("Corporates", '20/01/26', "BBB-"))
print(indicative_price(2, yield_curve("Corporates", '20/01/26', "BBB-")[1], yield_curve("Corporates", '20/01/26', "BBB-")[0], 100, 0.1466))
print(risk_o_meter(1,2,3))

# Dashboard

def metrics():


    pass


