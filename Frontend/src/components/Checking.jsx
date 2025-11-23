import data from '../datasets/alex2Ystable.json';
import { Card } from 'react-bootstrap';
import Transactions from './Transactions';

export default function Checking(props) {
    // Get the latest month's data (month 24)
    const latestMonth = data.monthly_financial_history[data.monthly_financial_history.length - 1];
    var checkingTotal = latestMonth.balance_sheet_snapshot.liquid_assets.checking_account.toLocaleString('en-US');

    const recentTransactions = [];
    const recentMonths = data.monthly_financial_history.slice(-3); 

    recentMonths.reverse().forEach((month, monthIndex) => {
        const monthDate = new Date(2025, 0 - monthIndex, 1); 
        const expenses = month.cash_flow.expenses;

        if (expenses.variable > 0) {
            const variableAmount = expenses.variable;
            const numTransactions = Math.min(Math.floor(variableAmount / 100), 4);
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

        if (month.month === latestMonth.month) {
            recentTransactions.push(
                { merchant: "Rent Payment", category: "rent", amount: Math.round(expenses.fixed * 0.7), timestamp: `${monthDate.getFullYear()}-${String(monthDate.getMonth() + 1).padStart(2, '0')}-01` },
                { merchant: "Verizon", category: "utilities", amount: Math.round(expenses.fixed * 0.15), timestamp: `${monthDate.getFullYear()}-${String(monthDate.getMonth() + 1).padStart(2, '0')}-07` },
                { merchant: "PG&E", category: "utilities", amount: Math.round(expenses.fixed * 0.15), timestamp: `${monthDate.getFullYear()}-${String(monthDate.getMonth() + 1).padStart(2, '0')}-05` }
            );
        }
    });

    recentTransactions.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    const displayTransactions = recentTransactions.slice(0, 12);

    return <div className="dashboard-style">
        <br/>
        <h1 style={{fontWeight: 800}}>360 Checking Account</h1>
        <br/>
        <div className="dashboard-cards">
            <Card>
                <div style={{margin: "10px"}}>
                    <p>Available Balance</p>
                    <p style={{fontSize: "32px", color: '#003E5C', fontWeight: 700}}>${checkingTotal}</p>
                </div>
            </Card>
        </div>
        <br/>
        <h3 style={{color: '#003E5C'}}>Transaction History</h3>
        <br/>
        <div>
            {displayTransactions.map((transaction, index) => (
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