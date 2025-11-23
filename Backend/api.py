from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import json
from sklearn.preprocessing import StandardScaler
from pmdarima import auto_arima

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

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

# Default to irresponsible data profile
def user_df_gen(json_path="alex2Yirresponsible.json"):
    with open(json_path, 'r') as fp:
        data = json.load(fp)
    month_data = data['monthly_financial_history']

    # Sort 24 month data into a Pandas DataFrame
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

def predict_net_worth(savings_increase_monthly=0):
    """
    Predict net worth for next 12 months
    savings_increase_monthly: additional monthly savings to add
    """
    df = user_df_gen()

    df.set_index(pd.date_range(start="2023-01-01", periods=len(df), freq='M'), inplace=True)
    ts = df['cash_liquid'] - df['debt']

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

    # Apply savings intervention
    if savings_increase_monthly > 0:
        intervention = np.arange(1, 13) * savings_increase_monthly
        next_year = next_year + intervention

    next_months = pd.date_range(start=df.index[-1] + pd.offsets.MonthEnd(), periods=12, freq='M')

    df_predicted = pd.DataFrame({
        "month": range(1, 13),
        "net_worth": next_year.tolist(),
        "date": next_months.strftime('%Y-%m').tolist()
    })

    # Get current net worth
    current_net_worth = (df['cash_liquid'] - df['debt']).iloc[-1]

    # Get final predicted net worth
    final_net_worth = next_year[-1]

    # Calculate growth
    net_worth_growth = final_net_worth - current_net_worth
    growth_percentage = (net_worth_growth / abs(current_net_worth)) * 100

    return {
        "current_net_worth": float(current_net_worth),
        "predicted_net_worth_12mo": float(final_net_worth),
        "net_worth_growth": float(net_worth_growth),
        "growth_percentage": float(growth_percentage),
        "monthly_predictions": df_predicted.to_dict('records'),
        "current_monthly_income": float(df['income'].iloc[-1]),
        "current_variable_expenses": float(df['variable'].iloc[-1])
    }

@app.route('/api/predict', methods=['POST'])
def get_prediction():
    """
    Endpoint to get net worth predictions
    Accepts: { "additional_monthly_savings": 500 }
    """
    data = request.json
    additional_savings = data.get('additional_monthly_savings', 0)

    try:
        result = predict_net_worth(additional_savings)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
