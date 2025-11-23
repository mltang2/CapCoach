import data from '../datasets/alex2Yrisky.json';
import statementData from '../datasets/alex_risky_statement.json';
import { Card } from 'react-bootstrap';
import Transactions from './Transactions';

export default function Dashboard(props) {
    const latestMonth = data.monthly_financial_history[data.monthly_financial_history.length - 1];
    var checkingTotal = latestMonth.balance_sheet_snapshot.liquid_assets.checking_account.toLocaleString('en-US');
    var savingsTotal = latestMonth.balance_sheet_snapshot.liquid_assets.savings_account.toLocaleString('en-US');

    // Get all transactions from the last 3 months of statement data
    const recentTransactions = [];
    const recentStatements = statementData.statements.slice(-3);

    recentStatements.forEach((statement) => {
        statement.transactions.forEach((transaction) => {
            recentTransactions.push({
                merchant: transaction.description,
                category: transaction.category.toLowerCase(),
                amount: Math.abs(transaction.amount),
                timestamp: transaction.date,
                type: transaction.type
            });
        });
    });

    // Sort by date in descending order (most recent first)
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
                    type={transaction.type}
                />
            ))}
        </div>
    </div>
}
