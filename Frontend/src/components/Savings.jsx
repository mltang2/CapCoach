import data from '../datasets/alex2Yirresponsible.json';
import statementData from '../datasets/alex_irresponsible_statement.json';
import { Card } from 'react-bootstrap';

export default function Savings(props) {
    const latestMonth = data.monthly_financial_history[data.monthly_financial_history.length - 1];
    var savingsTotal = latestMonth.balance_sheet_snapshot.liquid_assets.savings_account.toLocaleString('en-US');
    var monthlyIncome = latestMonth.cash_flow.income.total.toLocaleString('en-US');
    var autoTransfer = "1,244";
    var transferFrequency = "monthly";

    // Get only credit transactions (income) from the last 6 months
    const savingsTransactions = [];
    const recentStatements = statementData.statements.slice(-6);

    recentStatements.forEach((statement) => {
        statement.transactions.forEach((transaction) => {
            // Only include credit transactions (income, not expenses)
            if (transaction.type === 'credit') {
                savingsTransactions.push({
                    merchant: transaction.description,
                    category: transaction.category.toLowerCase(),
                    amount: transaction.amount,
                    timestamp: transaction.date
                });
            }
        });
    });

    savingsTransactions.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    const displaySavingsTransactions = savingsTransactions.slice(0, 10);

    return <div className="dashboard-style">
        <br/>
        <h1 style={{fontWeight: 800}}>360 Savings Account</h1>
        <br/>
        <div className="dashboard-cards">
            <Card>
                <div style={{margin: "10px"}}>
                    <p>Available Balance</p>
                    <p style={{fontSize: "32px", color: '#003E5C', fontWeight: 700}}>${savingsTotal}</p>
                </div>
            </Card>
        </div>
        <br/>
        <h3 style={{color: '#003E5C'}}>Income & Savings Information</h3>
        <br/>
        <div className="dashboard-cards">
            <Card>
                <div style={{margin: "10px"}}>
                    <p style={{fontWeight: 600}}>Estimated Monthly Income</p>
                    <p style={{fontSize: "24px", color: '#003E5C', fontWeight: 700}}>${monthlyIncome}</p>
                    <p style={{fontSize: "12px", color: '#666'}}>Net monthly income</p>
                </div>
            </Card>
            <Card>
                <div style={{margin: "10px"}}>
                    <p style={{fontWeight: 600}}>Automatic Savings Transfer</p>
                    <p style={{fontSize: "24px", color: '#003E5C', fontWeight: 700}}>${autoTransfer}</p>
                    <p style={{fontSize: "12px", color: '#666'}}>Transferred {transferFrequency}</p>
                </div>
            </Card>
        </div>
        <br/>
        <h3 style={{color: '#003E5C'}}>Transaction History</h3>
        <br/>
        <div>
            {displaySavingsTransactions.map((transaction, index) => (
                <Card key={index} style={{ marginBottom: '12px', boxShadow: "0 1px 3px rgba(0, 0, 0, 0.15)", border: "none"}}>
                    <div style={{
                        padding: '16px',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center'
                    }}>
                        <div>
                            <p style={{ margin: 0, fontWeight: 600, fontSize: '16px' }}>{transaction.merchant}</p>
                            <p style={{ margin: 0, fontSize: '12px', color: '#666' }}>{transaction.category} • {transaction.timestamp}</p>
                        </div>
                        <div>
                            <p style={{ margin: 0, fontSize: '18px', fontWeight: 700, color: '#28a745' }}>
                                +${transaction.amount.toFixed(2)}
                            </p>
                        </div>
                    </div>
                </Card>
            ))}
        </div>
    </div>
}
