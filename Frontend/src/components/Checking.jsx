import data from '../datasets/alex2Ystable.json';
import statementData from '../datasets/alex_stable_statement.json';
import { Card } from 'react-bootstrap';
import Transactions from './Transactions';

export default function Checking(props) {
    // Get the latest month's data (month 24)
    const latestMonth = data.monthly_financial_history[data.monthly_financial_history.length - 1];
    var checkingTotal = latestMonth.balance_sheet_snapshot.liquid_assets.checking_account.toLocaleString('en-US');

    // Get only debit transactions (expenses) from the last 3 months
    const recentTransactions = [];
    const recentStatements = statementData.statements.slice(-3);

    recentStatements.forEach((statement) => {
        statement.transactions.forEach((transaction) => {
            // Only include debit transactions (expenses, not income)
            if (transaction.type === 'debit') {
                recentTransactions.push({
                    merchant: transaction.description,
                    category: transaction.category.toLowerCase(),
                    amount: Math.abs(transaction.amount),
                    timestamp: transaction.date
                });
            }
        });
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
