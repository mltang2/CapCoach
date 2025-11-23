import { Card } from 'react-bootstrap'

export default function Transactions(props) {
    const { merchant, category, amount, timestamp, type } = props;

    // For dashboard view, type is passed. For checking/savings views, default to debit/credit respectively
    const isCredit = type === 'credit';
    const amountColor = isCredit ? '#28a745' : '#dc3545';
    const sign = isCredit ? '+' : '-';

    return (
        <Card style={{ marginBottom: '12px', boxShadow: "0 1px 3px rgba(0, 0, 0, 0.15)", border: "none"}}>
            <div style={{
                padding: '16px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
            }}>
                <div>
                    <p style={{ margin: 0, fontWeight: 600, fontSize: '16px' }}>{merchant}</p>
                    <p style={{ margin: 0, fontSize: '12px', color: '#666' }}>{category} • {timestamp}</p>
                </div>
                <div>
                    <p style={{ margin: 0, fontSize: '18px', fontWeight: 700, color: amountColor }}>
                        {sign}${Math.abs(amount).toFixed(2)}
                    </p>
                </div>
            </div>
        </Card>
    );
}