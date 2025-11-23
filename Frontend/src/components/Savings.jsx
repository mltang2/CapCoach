import data from '../datasets/alex2Ystable.json';
import { Card } from 'react-bootstrap';

export default function Savings(props) {
    const latestMonth = data.monthly_financial_history[data.monthly_financial_history.length - 1];
    var savingsTotal = latestMonth.balance_sheet_snapshot.liquid_assets.savings_account.toLocaleString('en-US');
    var monthlyIncome = latestMonth.cash_flow.income.total.toLocaleString('en-US');
    var autoTransfer = "1,244"; 
    var transferFrequency = "monthly";

    const savingsTransactions = [];
    const recentMonths = data.monthly_financial_history.slice(-6);

    recentMonths.reverse().forEach((month, monthIndex) => {
        const monthDate = new Date(2025, 0 - monthIndex, 1); 
        const income = month.cash_flow.income;

        if (income.salary > 0) {
            savingsTransactions.push({
                merchant: `Salary Deposit - ${data.personal_info.occupation}`,
                category: "salary",
                amount: income.salary,
                timestamp: `${monthDate.getFullYear()}-${String(monthDate.getMonth() + 1).padStart(2, '0')}-15`
            });
        }

        if (income.freelance > 0) {
            savingsTransactions.push({
                merchant: "Freelance Payment",
                category: "freelance",
                amount: income.freelance,
                timestamp: `${monthDate.getFullYear()}-${String(monthDate.getMonth() + 1).padStart(2, '0')}-${20 + monthIndex}`
            });
        }

        const monthIdx = data.monthly_financial_history.findIndex(m => m.month === month.month);
        if (monthIdx > 0) {
            const prevMonth = data.monthly_financial_history[monthIdx - 1];
            const savingsGrowth = month.balance_sheet_snapshot.liquid_assets.savings_account - prevMonth.balance_sheet_snapshot.liquid_assets.savings_account;
            if (savingsGrowth > 100) {
                savingsTransactions.push({
                    merchant: "Automatic Transfer from Checking",
                    category: "transfer",
                    amount: Math.round(savingsGrowth * 0.6 * 100) / 100,
                    timestamp: `${monthDate.getFullYear()}-${String(monthDate.getMonth() + 1).padStart(2, '0')}-22`
                });
            }
        }

        savingsTransactions.push({
            merchant: "Interest Payment",
            category: "interest",
            amount: Math.round((month.balance_sheet_snapshot.liquid_assets.savings_account * 0.0003) * 100) / 100,
            timestamp: `${monthDate.getFullYear()}-${String(monthDate.getMonth() + 1).padStart(2, '0')}-${25 + monthIndex}`
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