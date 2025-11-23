import data from '../datasets/alex2Ystable.json';
import { Card } from 'react-bootstrap';
import Transactions from './Transactions';

export default function Dashboard(props) {
    // Get the latest month's data (month 24)
    const latestMonth = data.monthly_financial_history[data.monthly_financial_history.length - 1];
    var checkingTotal = latestMonth.balance_sheet_snapshot.liquid_assets.checking_account.toLocaleString('en-US');
    var savingsTotal = latestMonth.balance_sheet_snapshot.liquid_assets.savings_account.toLocaleString('en-US');

    // Generate transactions based on recent months' expense data
    const recentTransactions = [];
    const recentMonths = data.monthly_financial_history.slice(-3); // Last 3 months

    recentMonths.reverse().forEach((month, monthIndex) => {
        const monthDate = new Date(2025, 0 - monthIndex, 1);
        const expenses = month.cash_flow.expenses;

        // Add variable expenses as shopping/dining transactions
        if (expenses.variable > 0) {
            const variableAmount = expenses.variable;
            const numTransactions = Math.min(Math.floor(variableAmount / 100), 3);
            for (let i = 0; i < numTransactions; i++) {
                const merchants = ["Trader Joe's", "Whole Foods", "Starbucks", "Chipotle", "Target", "Amazon"];
                const categories = ["groceries", "dining", "shopping"];
                recentTransactions.push({
                    merchant: merchants[Math.floor(Math.random() * merchants.length)],
                    category: categories[Math.floor(Math.random() * categories.length)],
                    amount: Math.round((variableAmount / numTransactions) * 100) / 100,
                    timestamp: `${monthDate.getFullYear()}-${String(monthDate.getMonth() + 1).padStart(2, '0')}-${String(15 + i * 3).padStart(2, '0')}`
                });
            }
        }
    });

    // Sort by date descending and take first 10
    recentTransactions.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

    return <div className="dashboard-style">
        <br/>
        <h1 style={{fontWeight: 800}}>Welcome to CapCoach Banking</h1>
        <br/>
        <h3 style={{color: '#003E5C'}}>Your Accounts</h3>
        <br/>
        <div className="dashboard-cards">
            <Card>
                <div style={{margin: "10px"}}>
                    <p>360 Checking Account</p>
                    <p style={{fontSize: "32px", color: '#003E5C', fontWeight: 700}}>${checkingTotal}</p>
                    <p style={{fontSize: "10px"}}>Account ending in ****5382</p>
                </div>
            </Card>
            <Card>
                <div style={{margin: "10px"}}>
                    <p>360 Savings Account</p>
                    <p style={{fontSize: "32px", color: '#003E5C', fontWeight: 700}}>${savingsTotal}</p>
                    <p style={{fontSize: "10px"}}>Account ending in ****5383</p>
                </div>
            </Card>
        </div>
        <br/>
        <h3 style={{color: '#003E5C'}}>Recent Activity</h3>
        <br/>
        <div>
            {recentTransactions.slice(0, 10).map((transaction, index) => (
                <Transactions
                    key={index}
                    merchant={transaction.merchant}
                    category={transaction.category}
                    amount={transaction.amount}
                    timestamp={transaction.timestamp}
                />
            ))}
        </div>
    </div>
}
