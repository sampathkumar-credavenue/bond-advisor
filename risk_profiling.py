
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

instruments = pd.read_csv('G:/Shared drives/Data Science/Bond Manager/Data/bonds_live_platform.csv')

def risk_grid_assignor(instruments):
    instruments['duration'] = 0.
    mapper_freq = {'Yearly': 1, 'Half Yearly': 2, 'Quarterly': 4, 'Monthly': 12, 'On Maturity': 0, 'On Redemption': 0}
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

def investor_risk_assingor(

)



########-----------------------

i=61
settlement_date = pd.to_datetime('today')
maturity_date = pd.to_datetime(instruments['maturity_date'][i], format='%d-%m-%Y')
coupon_rate = instruments['coupon_rate'][i]
yield_rate = instruments['yield'][i]
no_of_int_payments_per_year = instruments['no_of_int_payments_per_year'][i]
macaulay_duration(settlement_date, maturity_date, coupon_rate, yield_rate, no_of_int_payments_per_year)

instruments['isin'][i]




def risk_calculator(df):
    ### Estimate the Credit Risk, Interest Rate Risk and Liquidity Risk as per SEBI Guidelines

    {}
    df['credit_risk_value'] =

x, y = macaulay_duration(settlement_date, maturity_date, coupon_rate, yield_rate, no_of_int_payments_per_year)
