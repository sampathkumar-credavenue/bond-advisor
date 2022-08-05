
import numpy as np
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta

def macaulay_duration(settlement_date, maturity_date, coupon_rate, yield_rate, no_of_int_payments_per_year):

    ### Calculating Macaulay Duration for Bullet Principal Bonds
    if no_of_int_payments_per_year != 0 :

        temp_date = maturity_date
        repayment_dates = []

        while temp_date > settlement_date:
            repayment_dates.append(temp_date)
            temp_date = pd.to_datetime(datetime.datetime.date(temp_date) - relativedelta(months=12 / no_of_int_payments_per_year))

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

instruments = pd.read_csv('D:/anand.ts/Desktop/Hackathon/bond-advisor/bonds_live_platform.csv')

def risk_grid_assignor(instruments):
    instruments['duration'] = 0.
    mapper_freq = {np.nan:1, 'Yearly': 1, 'Half Yearly': 2, 'Quarterly': 4, 'Monthly': 12, 'On Maturity': 0, 'On Redemption': 0}
    instruments['no_of_int_payments_per_year'] = instruments['interest_payment_frequency'].map(mapper_freq)

    for i in range(0, instruments.shape[0]):
        print(i)
        #print(instruments['isin'][i])
        maturity_date = pd.to_datetime(instruments['maturity_date'][i], format='%d-%m-%Y')
        instruments['duration'][i] = macaulay_duration(pd.to_datetime('today'), maturity_date,
                          instruments['coupon_rate'][i], instruments['yield'][i],
                          instruments['no_of_int_payments_per_year'][i])

    instruments['market_risk_value_grid'] = 1
    instruments.loc[instruments['duration'] > 0.5, 'market_risk_value_grid'] = 2
    instruments.loc[instruments['duration'] > 1, 'market_risk_value_grid'] = 3
    instruments.loc[instruments['duration'] > 2, 'market_risk_value_grid'] = 4
    instruments.loc[instruments['duration'] > 3, 'market_risk_value_grid'] = 5
    instruments.loc[instruments['duration'] > 4, 'market_risk_value_grid'] = 6

    instruments[['credit_risk_value_grid', 'market_risk_value_grid']]

    instruments['grid_number'] = 0
    instruments.loc[(instruments['credit_risk_value_grid']>=12) & (instruments['market_risk_value_grid'].isin([1,2])), 'grid_number'] = 1
    instruments.loc[(instruments['credit_risk_value_grid'].isin([10,11])) & (instruments['market_risk_value_grid'].isin([1,2])), 'grid_number'] = 2
    instruments.loc[(instruments['credit_risk_value_grid']<=9) & (instruments['market_risk_value_grid'].isin([1,2])), 'grid_number'] = 3
    instruments.loc[(instruments['credit_risk_value_grid']>=12) & (instruments['market_risk_value_grid'].isin([3,4])), 'grid_number'] = 4
    instruments.loc[(instruments['credit_risk_value_grid'].isin([10,11])) & (instruments['market_risk_value_grid'].isin([3,4])), 'grid_number'] = 5
    instruments.loc[(instruments['credit_risk_value_grid']<=9) & (instruments['market_risk_value_grid'].isin([3,4])), 'grid_number'] = 6
    instruments.loc[(instruments['credit_risk_value_grid']>=12) & (instruments['market_risk_value_grid'] >= 5), 'grid_number'] = 7
    instruments.loc[(instruments['credit_risk_value_grid'].isin([10,11])) & (instruments['market_risk_value_grid'] >= 5), 'grid_number'] = 8
    instruments.loc[(instruments['credit_risk_value_grid']<=9) & (instruments['market_risk_value_grid'] >= 5), 'grid_number'] = 9

    return instruments

instruments = risk_grid_assignor(instruments)

questions = pd.read_excel('D:/anand.ts/Desktop/Hackathon/Risk assessment.xlsx')

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

investor_grid_number = 8

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
        desired_liquidity_value = 14

    desired_params = pd.DataFrame([], columns=['tenor', 'liq_risk_value'])
    desired_params.loc[0, :] = [desired_tenor, desired_liq_risk_value]
    desired_params[['desired_tenor_norm', 'desired_liq_risk_value_norm']] = sc.transform(desired_params)

    # Similarity Index
    grid_instruments['euclidean'] = [distance.euclidean(list(grid_instruments.loc[i, ['tenor_norm', 'liq_risk_value_norm']]), list(desired_params.loc[0, ['desired_tenor_norm', 'desired_liq_risk_value_norm']])) for i in grid_instruments.index]
    most_similar_isins = list(grid_instruments.sort_values(['euclidean', 'liq_risk_value'], ascending=[True, True])['isin'])[0:2]
    return most_similar_isins

    ########-----------------------


### PEOPLE SIMILAR TO YOU HAVE INVESTED IN THIS
inv_details = pd.read_csv('investor_details_database.csv')
inv_transactions = pd.read_csv('investor_portfolio_database.csv')
current_investor_id = 4

def similar_user_based_recommendation(current_investor_id, inv_details, inv_transactions):

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

    perc_of_inv_in_your_grid =

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

    # % of Transactions in the Same Grid by your Similar Customers [Top 5 Considered to be the most Similar Investors]
    current_inv_transactions = inv_transactions.loc[inv_transactions['investor_id'] == current_investor_id, :]
    if req_db.shape[0] < 5:
        inv_transactions.loc[inv_transactions['investor_id'].isin(list(req_db['investor_id'])), :]
    else:

    # Similar Investor Based Summary on Risk Taking Levels  

    return similar_inv_trade


i=214
settlement_date = pd.to_datetime('today')
maturity_date = pd.to_datetime(instruments['maturity_date'][i], format='%d-%m-%Y')
coupon_rate = instruments['coupon_rate'][i]
yield_rate = instruments['yield'][i]
no_of_int_payments_per_year = instruments['no_of_int_payments_per_year'][i]
macaulay_duration(settlement_date, maturity_date, coupon_rate, yield_rate, no_of_int_payments_per_year)

instruments['isin'][i]



x, y = macaulay_duration(settlement_date, maturity_date, coupon_rate, yield_rate, no_of_int_payments_per_year)
