import data from '../datasets/capital_one_users.json';
import { Card } from 'react-bootstrap';

export default function Dashboard(props) {
    var checkingTotal = data.users[0].accounts.checking.balance.toLocaleString('en-US');
    var savingsTotal = data.users[0].accounts.savings.balance.toLocaleString('en-US');

    return <div className="dashboard-style">
        <br/>
        <h1>Welcome to CapCoach Banking</h1>
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
    </div>
}
