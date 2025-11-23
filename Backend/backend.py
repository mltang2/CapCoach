import pandas as pd
import numpy as np
import json
from sklearn.preprocessing import StandardScaler
from pmdarima import auto_arima
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX

############################################   Risk Calculation  #######################################################

def calc_risk(df):
    # N > 1.0, indicates cash loss
    avg_burn = (df['expenses'] / df['income']).mean()

    #Debt to Income Ratio, % allocated to debt
    avg_dti = (df['debt_repay'] / df['income']).mean()

    #How long the user could(in theory) survive with no income
    df['cash_liquid'] = df['checking'] + df['savings'] + df['investment']
    current_liquid = df['cash_liquid'].iloc[-1]
    avg_expenses = df['expenses'].mean()
    runaway_months = current_liquid / avg_expenses

    # Overall, are they gaining or losing?
    liquidity_trend = np.polyfit(df.index, pd.to_numeric(df['cash_liquid']), 1)[0]
    debt_trend = np.polyfit(df.index, pd.to_numeric(df['debt']), 1)[0]

    #Risk score is an arbitrary value 0-100 to measure a given users general financial health
    risk_score = 0

    #Burn Rate
    if avg_burn >= 1.0: risk_score += 50 # Spending > Earning
    elif avg_burn > 0.95: risk_score += 30 # Paycheck to Paycheck
    elif avg_burn > 0.90: risk_score += 15
    # DTI
    if avg_dti > 0.5: risk_score += 25 # 50% of portfolio is debt
    elif avg_dti > 0.40: risk_score += 10
    # Runaway
    if runaway_months < 1.0: risk_score += 25 # One month's $
    elif runaway_months < 3.0: risk_score += 10 # Three month's $
    elif runaway_months > 6.0: risk_score -= 10 # Six month's $
    elif runaway_months > 12.0: risk_score -= 20 # 12 month's $
    # Long-Term Gain or Loss
    if debt_trend > 0: risk_score += 15 # Debt growing over time
    if liquidity_trend < 0: risk_score += 15 #Liquidity shrinking over time

    return max(0, min(100, risk_score))

############################################   Model Building  #########################################################

def user_df_gen():
    with open("alex2Ystable.json", 'r') as fp:
        data = json.load(fp)
    month_data = data['monthly_financial_history']

    # Sort 12 month data into a Pandas DataFrame
    user_data_year = pd.DataFrame(
        columns=['month', 'income', 'expenses', 'investment', 'debt', 'debt_repay', 'checking',
                 'savings', 'risk_score', 'fixed', 'variable', 'overall_expense'])
    user_data_year['month'] = range(24)
    user_data_year = user_data_year.set_index('month')
    for i in range(24):
        month = month_data[i]
        month_income = month.get('cash_flow').get('income').get('total')
        month_expense = month.get('cash_flow').get('expenses').get('total_outflow')
        month_debt = month.get('balance_sheet_snapshot').get('debts').get('total_debt')
        month_debt_repay = month.get('cash_flow').get('expenses').get('debt_payments')
        month_investment_total = month.get('balance_sheet_snapshot').get('investments').get('total_investments')

        # Map each value to its respective column
        user_data_year.iat[i, 0] = month_income
        user_data_year.iat[i, 1] = month_expense
        user_data_year.iat[i, 2] = month_investment_total
        user_data_year.iat[i, 3] = month_debt
        user_data_year.iat[i, 4] = month_debt_repay
        user_data_year.iat[i, 5] = month.get('balance_sheet_snapshot').get('liquid_assets').get('checking_account')
        user_data_year.iat[i, 6] = month.get('balance_sheet_snapshot').get('liquid_assets').get('savings_account')
        user_data_year.iat[i, 8] = month.get('cash_flow').get('expenses').get('fixed')
        user_data_year.iat[i, 9] = month.get('cash_flow').get('expenses').get('variable')
        user_data_year.iat[i, 10] = month_expense + month.get('cash_flow').get('expenses').get('variable')

    user_data_year['risk_score'] = calc_risk(user_data_year)

    return user_data_year

df = user_df_gen()
print(df)

df.set_index(pd.date_range(start="2023-01-01", periods=len(df), freq='ME'), inplace=True)
ts = df['cash_liquid'] - df['debt']
#ts_scaled = ts
scaler = StandardScaler()
ts_scaled = scaler.fit_transform(ts.values.reshape(-1, 1)).flatten()

predictor = auto_arima(
    ts_scaled,
    seasonal=True,
    m=12,
    D=1,
    trace=False,
    error_action='ignore',
    suppress_warnings=True
)

next_year = predictor.predict(n_periods=12)
next_year = scaler.inverse_transform(next_year.reshape(-1, 1)).flatten()


#user_percentage_choice = 0.60

#monthly_extra = user_percentage_choice

#intervention = np.arange(1, 13) * monthly_extra


next_months = pd.date_range(start=df.index[-1] + pd.offsets.MonthEnd(), periods=12, freq='ME')

df_predicted = pd.DataFrame({
    "Date": next_months,
    "Future Net Worth": next_year
})

print(df_predicted)
