# CapCoach - AI-Powered Financial Planning

CapCoach is a banking application with AI-powered financial predictions that help users plan their financial future.

## Features

- **Dashboard**: View account balances and recent transactions
- **Checking & Savings**: Detailed account views with transaction history
- **CapCoach AI**: Machine learning-powered net worth predictions with personalized savings recommendations

## Setup Instructions

### Backend (Flask API)

1. Navigate to the Backend directory:
   ```bash
   cd Backend
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the Flask server:
   ```bash
   python api.py
   ```

   The API will run on `http://localhost:5001`

### Frontend (React)

1. Navigate to the Frontend directory:
   ```bash
   cd Frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open your browser to the URL shown (typically `http://localhost:5173`)

## Using CapCoach AI

1. Navigate to the CapCoach page in the app
2. View your AI-predicted net worth for the next 12 months
3. Choose whether you're satisfied with the prediction or want higher/lower growth
4. For higher growth targets:
   - Use the slider to set your target growth percentage
   - Click "Calculate Savings Plan"
   - Get personalized recommendations on how much to save and which spending categories to reduce

## Technology Stack

- **Frontend**: React, React Router, React Bootstrap, Vite
- **Backend**: Flask, Flask-CORS
- **ML Model**: ARIMA time series forecasting with pmdarima
- **Data Processing**: pandas, numpy, scikit-learn

## API Endpoints

- `GET /api/health` - Health check endpoint
- `POST /api/predict` - Get net worth predictions
  - Request body: `{"additional_monthly_savings": 0}`
  - Returns current net worth, 12-month prediction, growth percentage, and monthly breakdown

## Notes

- Port 5000 may be used by macOS Control Center, so the Flask API runs on port 5001
- The ML model uses 24 months of historical financial data
- Predictions account for liquid assets, investments, debts, income, and expenses
