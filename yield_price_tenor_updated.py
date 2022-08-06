from datetime import datetime
import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta
import math

live_bonds = pd.read_csv("bonds_live_platform.csv")
fimmda_yld = pd.read_excel("fimmda_yield_curve.xlsx")
my_ptf = pd.read_csv("my_portfolio.csv")
dash_df = pd.read_csv("dash_df.csv")
questions = pd.read_excel('Risk assessment.xlsx')
inv_details = pd.read_csv('investor_details_database.csv')
inv_transactions = pd.read_csv('investor_portfolio_database.csv')
instruments = live_bonds

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

# run on a daily basis

# def risk_grid_assignor(instruments):
#     instruments['duration'] = 0.
#     mapper_freq = {np.nan:1, 'Yearly': 1, 'Half Yearly': 2, 'Quarterly': 4, 'Monthly': 12, 'On Maturity': 0, 'On Redemption': 0}
#     instruments['no_of_int_payments_per_year'] = instruments['interest_payment_frequency'].map(mapper_freq)
#
#     for i in range(0, instruments.shape[0]):
#         print(i)
#         #print(instruments['isin'][i])
#         maturity_date = pd.to_datetime(instruments['maturity_date'][i], format='%d-%m-%Y')
#         instruments['duration'][i] = macaulay_duration(pd.to_datetime('today'), maturity_date,
#                           instruments['coupon_rate'][i], instruments['yield'][i],
#                           instruments['no_of_int_payments_per_year'][i])
#
#     instruments['market_risk_value_grid'] = 1
#     instruments.loc[instruments['duration'] > 0.5, 'market_risk_value_grid'] = 2
#     instruments.loc[instruments['duration'] > 1, 'market_risk_value_grid'] = 3
#     instruments.loc[instruments['duration'] > 2, 'market_risk_value_grid'] = 4
#     instruments.loc[instruments['duration'] > 3, 'market_risk_value_grid'] = 5
#     instruments.loc[instruments['duration'] > 4, 'market_risk_value_grid'] = 6
#
#     instruments[['credit_risk_value_grid', 'market_risk_value_grid']]
#
#     instruments['grid_number'] = 0
#     instruments.loc[(instruments['credit_risk_value_grid']>=12) & (instruments['market_risk_value_grid'].isin([1,2])), 'grid_number'] = 1
#     instruments.loc[(instruments['credit_risk_value_grid'].isin([10,11])) & (instruments['market_risk_value_grid'].isin([1,2])), 'grid_number'] = 2
#     instruments.loc[(instruments['credit_risk_value_grid']<=9) & (instruments['market_risk_value_grid'].isin([1,2])), 'grid_number'] = 3
#     instruments.loc[(instruments['credit_risk_value_grid']>=12) & (instruments['market_risk_value_grid'].isin([3,4])), 'grid_number'] = 4
#     instruments.loc[(instruments['credit_risk_value_grid'].isin([10,11])) & (instruments['market_risk_value_grid'].isin([3,4])), 'grid_number'] = 5
#     instruments.loc[(instruments['credit_risk_value_grid']<=9) & (instruments['market_risk_value_grid'].isin([3,4])), 'grid_number'] = 6
#     instruments.loc[(instruments['credit_risk_value_grid']>=12) & (instruments['market_risk_value_grid'] >= 5), 'grid_number'] = 7
#     instruments.loc[(instruments['credit_risk_value_grid'].isin([10,11])) & (instruments['market_risk_value_grid'] >= 5), 'grid_number'] = 8
#     instruments.loc[(instruments['credit_risk_value_grid']<=9) & (instruments['market_risk_value_grid'] >= 5), 'grid_number'] = 9
#
#     return instruments

def investor_grid_estimator(questions):

    # Mapping the Investor the Grid
    credit_risk_option = questions.loc[questions['Q.No'] == 1, 'Option'].values[0]
    market_risk_option = questions.loc[questions['Q.No'] == 2, 'Option'].values[0]
    risk_profile = credit_risk_option + '-' + market_risk_option

    risk_dict = {'a-a' : 1, 'b-a' : 2, 'c-a' : 3,
                 'a-b' : 4, 'b-b' : 5, 'c-b' : 6,
                 'a-c' : 7, 'b-c' : 8, 'c-c' : 9}

    investor_grid_number = risk_dict[risk_profile]
    return investor_grid_number

def grid_based_recommendation(questions, investor_grid_number, instruments):
    grid_instruments = instruments.loc[instruments['grid_number'] == investor_grid_number, :]
    grid_instruments['tenor'] = ((pd.to_datetime(grid_instruments['maturity_date'], format='%d-%m-%Y') - pd.to_datetime('today')).dt.days / 365)

    # Interest Payment Frequency
    desired_int_freq = questions.loc[questions['Q.No'] == 7, 'Answer'].values[0]
    if desired_int_freq != 'Does not matter':
        grid_instruments = grid_instruments.loc[grid_instruments['interest_payment_frequency'] == desired_int_freq, :]

    # Taxation
    if questions.loc[questions['Q.No'] == 7, 'Answer'].values[0] == 'Yes':
        grid_instruments = grid_instruments.loc[grid_instruments['is_tax_free'] == True, :]

    # Investment Amount
    mapper_amount = {'a': 100000, 'b':200000, 'c':500000, 'd':np.nan}
    upper_limit_amount = mapper_amount[questions.loc[questions['Q.No'] == 6, 'Option'].values[0]]
    if questions.loc[questions['Q.No'] == 6, 'Option'].values[0] != 'd':
        grid_instruments = grid_instruments.loc[grid_instruments['face_value'] <= upper_limit_amount, :]

    # Distance Measure
    mapper_tenor = {'a': 0.5, 'b': 2, 'c': 4, 'd': 6}
    desired_tenor = mapper_tenor[questions.loc[questions['Q.No'] == 5, 'Option'].values[0]]

        # Z Score Normalization...
    from scipy.spatial import distance
    from sklearn.preprocessing import StandardScaler
    sc = StandardScaler()
    grid_instruments[['tenor_norm', 'liq_risk_value_norm']] = sc.fit_transform(grid_instruments[['tenor', 'liq_risk_value']])

    if questions.loc[questions['Q.No'] == 4, 'Option'].values[0] == 'a': # Liquidity Check
        desired_liq_risk_value = 1
    elif questions.loc[questions['Q.No'] == 4, 'Option'].values[0] == 'b':
        desired_liq_risk_value = 14

    desired_params = pd.DataFrame([], columns=['tenor', 'liq_risk_value'])
    desired_params.loc[0, :] = [desired_tenor, desired_liq_risk_value]
    desired_params[['desired_tenor_norm', 'desired_liq_risk_value_norm']] = sc.transform(desired_params)

    # Similarity Index
    grid_instruments['euclidean'] = [distance.euclidean(list(grid_instruments.loc[i, ['tenor_norm', 'liq_risk_value_norm']]), list(desired_params.loc[0, ['desired_tenor_norm', 'desired_liq_risk_value_norm']])) for i in grid_instruments.index]
    most_similar_isins = list(grid_instruments.sort_values(['euclidean', 'liq_risk_value'], ascending=[True, True])['isin'])[0:3]
    return most_similar_isins

### PEOPLE SIMILAR TO YOU HAVE INVESTED IN THIS

def similar_user_based_recommendation(current_investor_id, investor_grid_number, inv_details, inv_transactions):

    inv_transactions['market_risk_value_grid'] = 1
    inv_transactions.loc[inv_transactions['duration'] > 0.5, 'market_risk_value_grid'] = 2
    inv_transactions.loc[inv_transactions['duration'] > 1, 'market_risk_value_grid'] = 3
    inv_transactions.loc[inv_transactions['duration'] > 2, 'market_risk_value_grid'] = 4
    inv_transactions.loc[inv_transactions['duration'] > 3, 'market_risk_value_grid'] = 5
    inv_transactions.loc[inv_transactions['duration'] > 4, 'market_risk_value_grid'] = 6

    inv_transactions['grid_number'] = 0
    inv_transactions.loc[(inv_transactions['credit_risk_value_grid'] >= 12) & (inv_transactions['market_risk_value_grid'].isin([1, 2])), 'grid_number'] = 1
    inv_transactions.loc[(inv_transactions['credit_risk_value_grid'].isin([10, 11])) & (inv_transactions['market_risk_value_grid'].isin([1, 2])), 'grid_number'] = 2
    inv_transactions.loc[(inv_transactions['credit_risk_value_grid'] <= 9) & (inv_transactions['market_risk_value_grid'].isin([1, 2])), 'grid_number'] = 3
    inv_transactions.loc[(inv_transactions['credit_risk_value_grid'] >= 12) & (inv_transactions['market_risk_value_grid'].isin([3, 4])), 'grid_number'] = 4
    inv_transactions.loc[(inv_transactions['credit_risk_value_grid'].isin([10, 11])) & (inv_transactions['market_risk_value_grid'].isin([3, 4])), 'grid_number'] = 5
    inv_transactions.loc[(inv_transactions['credit_risk_value_grid'] <= 9) & (inv_transactions['market_risk_value_grid'].isin([3, 4])), 'grid_number'] = 6
    inv_transactions.loc[(inv_transactions['credit_risk_value_grid'] >= 12) & (inv_transactions['market_risk_value_grid'] >= 5), 'grid_number'] = 7
    inv_transactions.loc[(inv_transactions['credit_risk_value_grid'].isin([10, 11])) & (inv_transactions['market_risk_value_grid'] >= 5), 'grid_number'] = 8
    inv_transactions.loc[(inv_transactions['credit_risk_value_grid'] <= 9) & (inv_transactions['market_risk_value_grid'] >= 5), 'grid_number'] = 9

    # Finding the Similarity
    current_inv_details = inv_details.loc[inv_details['investor_id'] == current_investor_id, :]
    current_inv_details.index = [0]
    req_db = inv_details.loc[(inv_details['state'] == current_inv_details['state'].values[0]) &
                             (inv_details['marital_status'] == current_inv_details['marital_status'].values[0]), :]
    req_db = req_db.loc[req_db['investor_id']!=current_investor_id, :]

    # Z Score Normalization...
    from scipy.spatial import distance
    from sklearn.preprocessing import StandardScaler
    sc = StandardScaler()
    req_db[['age_norm', 'salary_norm']] = sc.fit_transform(req_db[['age', 'salary']])
    current_inv_details[['age_norm', 'salary_norm']] = sc.transform(current_inv_details[['age', 'salary']])
    req_db['euclidean'] = [distance.euclidean(list(req_db.loc[i, ['age_norm', 'salary_norm']]), list(current_inv_details.loc[0, ['age_norm', 'salary_norm']])) for i in req_db.index]
    req_db = req_db.sort_values(['euclidean'], ascending=[True])
    req_db.index = range(0, req_db.shape[0])

    # Similar Investor's Trade
    similar_inv_trade = inv_transactions.loc[inv_transactions['investor_id'] == req_db.loc[0, 'investor_id'], :]

    # % of Transactions in the Same Grid by your Similar Investors [Top 5 Considered to be the most Similar Investors]
    current_inv_transactions = inv_transactions.loc[inv_transactions['investor_id'] == current_investor_id, :]
    if req_db.shape[0] < 5:
        x = inv_transactions.loc[inv_transactions['investor_id'].isin(list(req_db['investor_id'])), 'grid_number']
        perc_of_trans_in_same_grid_by_sim_inv = sum(x == investor_grid_number) / x.shape[0]
    else:
        top_5_sim_inv = list(req_db['investor_id'][0:5])
        x = inv_transactions.loc[inv_transactions['investor_id'].isin(top_5_sim_inv), 'grid_number']
        perc_of_trans_in_same_grid_by_sim_inv = sum(x == investor_grid_number) / x.shape[0]

    # Similar Investor Based Summary on Risk Taking Levels
    sim_inv_grid_number = x.mode().values[0]

    # Credit Risk and Market Risk Summary based on Similar Investors...
    y = [1, 4, 7, 2, 5, 8, 3, 6, 9]

    if math.ceil(y.index(sim_inv_grid_number) / 3) > math.ceil(y.index(investor_grid_number) / 3):
        credit_risk_summary = 'Similar Investors are taking more credit risk than you'
    elif math.ceil(sim_inv_grid_number / 3) == math.ceil(investor_grid_number / 3):
        credit_risk_summary = 'Similar Investors are taking same credit risk as you'
    else:
        credit_risk_summary = 'Similar Investors are taking less credit risk than you'

    if math.ceil(sim_inv_grid_number / 3) > math.ceil(investor_grid_number / 3):
        market_risk_summary = 'Similar Investors are taking more market risk than you'
    elif math.ceil(sim_inv_grid_number / 3) == math.ceil(investor_grid_number / 3):
        market_risk_summary = 'Similar Investors are taking same market risk as you'
    else:
        market_risk_summary = 'Similar Investors are taking less market risk than you'

    return similar_inv_trade, perc_of_trans_in_same_grid_by_sim_inv, credit_risk_summary, market_risk_summary

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

# dashboard
def metrics(ptf):
    isin_lst = ptf["isin"].tolist()
    issuer_lst = []
    current_inv_amt_lst = []
    p_and_l_lst = []
    rom_lst = []
    invt_amt_lst = []
    for i in isin_lst:
        isin = i
        qty = ptf.loc[ptf["isin"] == isin, "qty"].iloc[0]
        buy_price = ptf.loc[ptf["isin"] == isin, "buy_price"].iloc[0]
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
        invested_amt = buy_price * qty
        credit = live_bonds.loc[live_bonds["isin"] == isin, ["credit_risk_value_rom"]].iloc[0, 0]
        liq = live_bonds.loc[live_bonds["isin"] == isin, ["liq_risk_value"]].iloc[0, 0]
        maturity_date = pd.to_datetime(mat, format='%d-%m-%Y')
        mrv = macaulay_duration(pd.to_datetime('today'), maturity_date, cpn, yld, ipy)
        rom = risk_o_meter(credit, liq, mrv)
        issuer_lst.append(issuer)
        current_inv_amt_lst.append(current_inv_amt)
        p_and_l_lst.append(p_and_l)
        rom_lst.append(rom)
        invt_amt_lst.append(invested_amt)
    dashboard_df = pd.DataFrame(
        {"isin": isin_lst, "issuer": issuer_lst, "invt_amt": invt_amt_lst, "current_invt_amt": current_inv_amt_lst, "pl": p_and_l_lst, "rom": rom_lst})
    return dashboard_df

def portfolio_metrics(dashboard_df):
    rom_values = {"Low": 1, "Low to Moderate": 2, "Moderate": 3, "Moderately High": 4, "High": 5, "Very High": 6}
    invest_amt = dashboard_df["invt_amt"].sum()
    pl = dashboard_df["pl"].sum()
    cur_invst_amt = dashboard_df["current_invt_amt"].sum()
    rom_values_list = []
    for i in dashboard_df["rom"].to_list():
        rom_values_list.append(rom_values[i])
    ptf_rom = int(sum(rom_values_list)/len(rom_values_list))
    sector_df = pd.merge(dashboard_df, live_bonds[["isin", "sector"]], how="left", on="isin").groupby(["sector"]).agg({"current_invt_amt":sum}).reset_index()
    sector_df["current_invt_amt"] = sector_df[['current_invt_amt']].apply(lambda x: (x/sum(x)*100)**2)
    sector_hhi = sector_df["current_invt_amt"].sum()
    if sector_hhi > 4500:
        diversification_flag = "Low Diversification"
    elif (sector_hhi > 3500) and (sector_hhi <= 4500):
        diversification_flag = "Moderate Diversification"
    else:
        diversification_flag = "High Diversification"
    return pd.DataFrame({"params": ["Invested Amt", "Unrealized P/L", "Current Invst Amt", "Sector Diversification", "Risk-o-Meter"], "values": [invest_amt, pl, cur_invst_amt, diversification_flag, ptf_rom]})

# code flow
# instruments = risk_grid_assignor(instruments)
investor_grid_number = investor_grid_estimator(questions)
current_investor_id = 4
investor_grid_number = investor_grid_estimator(questions)
instruments = pd.read_csv("instruments.csv")
isins_reco = grid_based_recommendation(questions, investor_grid_number, instruments)
isin_lst = isins_reco
disc_df = isin_fetch(isin_lst)
dash_df = metrics(my_ptf)
metrics_df = portfolio_metrics(dash_df)
similar_bonds, sim_inv_grid, credit_risk_sum, mkt_risk_sum = similar_user_based_recommendation(current_investor_id, investor_grid_number, inv_details, inv_transactions)
