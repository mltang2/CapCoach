import { useState } from 'react';
import data from '../datasets/alex2Ystable.json';
import statementData from '../datasets/alex_stable_statement.json';
import { Card } from 'react-bootstrap';

export default function Capcoach({ prediction, loading, fetchPrediction }) {
    const [userChoice, setUserChoice] = useState(null); // 'satisfied', 'higher', 'lower'
    const [targetGrowthPercent, setTargetGrowthPercent] = useState(null);

    const latestMonth = data.monthly_financial_history[data.monthly_financial_history.length - 1];

    const avgMonthlyIncome = latestMonth.cash_flow.income.total;

    // Calculate average spending by category from statement data
    const calculateSpendingByCategory = () => {
        const categoryTotals = {};
        const recentStatements = statementData.statements.slice(-3); // Last 3 months

        recentStatements.forEach((statement) => {
            statement.transactions.forEach((transaction) => {
                if (transaction.type === 'debit' && transaction.category === 'Variable') {
                    // Categorize variable expenses based on merchant
                    const merchant = transaction.description.toLowerCase();
                    let category = 'other';

                    if (merchant.includes('restaurant') || merchant.includes('bar') || merchant.includes('grill') ||
                        merchant.includes('eats') || merchant.includes("valentine's")) {
                        category = 'dining';
                    } else if (merchant.includes('concert') || merchant.includes('gaming') ||
                               merchant.includes('entertainment') || merchant.includes('ticket')) {
                        category = 'entertainment';
                    } else if (merchant.includes('target') || merchant.includes('purchase') || merchant.includes('electronics')) {
                        category = 'shopping';
                    } else if (merchant.includes('uber') || merchant.includes('shell') || merchant.includes('gas')) {
                        category = 'transportation';
                    }

                    if (!categoryTotals[category]) {
                        categoryTotals[category] = 0;
                    }
                    categoryTotals[category] += Math.abs(transaction.amount);
                }
            });
        });

        // Calculate monthly averages
        const monthlyAverages = {};
        Object.keys(categoryTotals).forEach(category => {
            monthlyAverages[category] = categoryTotals[category] / 3;
        });

        return monthlyAverages;
    };

    const spendingByCategory = calculateSpendingByCategory();

    const handleUserChoice = (choice) => {
        setUserChoice(choice);
        if (choice === 'adjust') {
            setTargetGrowthPercent(0);
        }
    };

    const calculateSavingsForTarget = () => {
        if (targetGrowthPercent === null || !prediction) return null;

        // Target is based on PREDICTED net worth with percentage adjustment
        const baselinePredicted = prediction.predicted_net_worth_12mo;
        const targetNetWorth = baselinePredicted * (1 + targetGrowthPercent / 100);

        // Additional growth needed beyond baseline prediction
        const additionalGrowthNeeded = targetNetWorth - baselinePredicted;
        const additionalSavingsNeeded = additionalGrowthNeeded / 12;

        // Calculate maximum possible cuts from variable spending
        const totalVariableSpending = Object.values(spendingByCategory).reduce((sum, val) => sum + val, 0);
        const maxPossibleCutsFromVariable = totalVariableSpending * 0.45; // Average of 40-50% caps

        // Check if achievable - comparing against what can actually be cut from variable expenses
        // For negative adjustments (decreasing target), always achievable
        // For positive adjustments, need to check if additional savings is within cuttable capacity
        const isAchievable = additionalSavingsNeeded <= maxPossibleCutsFromVariable;

        // Calculate what percentage of income this represents
        const percentageOfIncome = (additionalSavingsNeeded / avgMonthlyIncome) * 100;

        // Calculate maximum possible adjustment based on variable spending cuts
        const maxAdditionalGrowth = maxPossibleCutsFromVariable * 12;
        const maxTargetNetWorth = baselinePredicted + maxAdditionalGrowth;
        const maxAdjustmentPercent = ((maxTargetNetWorth - baselinePredicted) / Math.abs(baselinePredicted)) * 100;

        return {
            targetNetWorth,
            additionalGrowthNeeded,
            additionalSavingsNeeded,
            isAchievable,
            percentageOfIncome,
            maxMonthlySavings: maxPossibleCutsFromVariable,
            maxAdditionalGrowth,
            maxAdjustmentPercent,
            baselinePredicted
        };
    };

    const applyTargetSavings = () => {
        // No need to fetch - we calculate everything client-side
        // The calculation is already done and displayed via calculateSavingsForTarget()
    };

    return <div className="dashboard-style">
        <br/>
        <h1 style={{fontWeight: 800}}>CapCoach - AI Financial Planner</h1>
        <br/>

        {loading && (
            <Card style={{ padding: '40px', textAlign: 'center', boxShadow:"0 1px 3px rgba(0, 0, 0, 0.15)", border: "none" }}>
                <h3 style={{color: '#003E5C'}}>Loading AI Predictions...</h3>
                <p style={{color: '#666'}}>Analyzing your financial data with machine learning...</p>
                <div className="loading-spinner" role="status" aria-label="Loading predictions"></div>
            </Card>
        )}

        {!loading && prediction && (
            <>
                {/* Current vs Predicted Net Worth */}
                <h3 style={{color: '#003E5C'}}>AI-Powered Net Worth Prediction</h3>
                <br/>
                <div className="dashboard-cards">
                    <Card>
                        <div style={{margin: "10px"}}>
                            <p style={{fontWeight: 600}}>Current Net Worth</p>
                            <p style={{fontSize: "28px", color: '#003E5C', fontWeight: 700}}>
                                ${prediction.current_net_worth.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}
                            </p>
                            <p style={{fontSize: "12px", color: '#666'}}>As of now</p>
                        </div>
                    </Card>
                    <Card>
                        <div style={{margin: "10px"}}>
                            <p style={{fontWeight: 600}}>Predicted Net Worth (12 months)</p>
                            <p style={{fontSize: "28px", color: '#28a745', fontWeight: 700}}>
                                ${prediction.predicted_net_worth_12mo.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}
                            </p>
                            <p style={{fontSize: "12px", color: '#666'}}>AI Forecast</p>
                        </div>
                    </Card>
                    <Card>
                        <div style={{margin: "10px"}}>
                            <p style={{fontWeight: 600}}>Expected Growth</p>
                            <p style={{fontSize: "28px", color: prediction.growth_percentage >= 0 ? '#28a745' : '#dc3545', fontWeight: 700}}>
                                {prediction.growth_percentage >= 0 ? '+' : ''}{prediction.growth_percentage.toFixed(1)}%
                            </p>
                            <p style={{fontSize: "12px", color: '#666'}}>
                                ${Math.abs(prediction.net_worth_growth).toLocaleString('en-US', {minimumFractionDigits: 2})}
                            </p>
                        </div>
                    </Card>
                </div>

                <br/>

                {/* User Satisfaction Question */}
                {!userChoice && (
                    <>
                        <Card style={{ padding: '30px', textAlign: 'center', backgroundColor: '#f8f9fa' }}>
                            <h3 style={{color: '#003E5C', marginBottom: '20px'}}>
                                Are you satisfied with this projected growth?
                            </h3>
                            <div style={{display: 'flex', gap: '16px', justifyContent: 'center', flexWrap: 'wrap'}}>
                                <button
                                    onClick={() => handleUserChoice('satisfied')}
                                    style={{
                                        backgroundColor: '#28a745',
                                        color: 'white',
                                        border: 'none',
                                        padding: '16px 40px',
                                        borderRadius: '8px',
                                        fontSize: '16px',
                                        fontWeight: 600,
                                        cursor: 'pointer',
                                        minWidth: '200px'
                                    }}
                                >
                                    Yes, I'm satisfied
                                </button>
                                <button
                                    onClick={() => handleUserChoice('adjust')}
                                    style={{
                                        backgroundColor: '#ffc107',
                                        color: 'white',
                                        border: 'none',
                                        padding: '16px 40px',
                                        borderRadius: '8px',
                                        fontSize: '16px',
                                        fontWeight: 600,
                                        cursor: 'pointer',
                                        minWidth: '200px'
                                    }}
                                >
                                    No, I want to adjust it
                                </button>
                            </div>
                        </Card>
                    </>
                )}

                {/* Satisfied Response */}
                {userChoice === 'satisfied' && (
                    <>
                        <br/>
                        <Card style={{ padding: '30px', backgroundColor: '#d4edda', border: '1px solid #c3e6cb' }}>
                            <div style={{textAlign: 'center'}}>
                                <h2 style={{color: '#155724', marginBottom: '16px'}}>Great! Keep up the good work!</h2>
                                <p style={{fontSize: '18px', color: '#155724', lineHeight: '1.6'}}>
                                    Based on your current spending and saving habits, you're on track to grow your net worth by{' '}
                                    <strong>${Math.abs(prediction.net_worth_growth).toLocaleString('en-US', {minimumFractionDigits: 2})}</strong>{' '}
                                    over the next year.
                                </p>
                            </div>
                        </Card>
                        <br/>
                        <Card style={{ padding: '20px', backgroundColor: '#e7f3ff' }}>
                            <h4 style={{color: '#003E5C', marginBottom: '12px'}}>Tips to Stay on Track</h4>
                            <ul style={{color: '#004879', lineHeight: '1.8', paddingLeft: '20px'}}>
                                <li>Continue your current saving habits</li>
                                <li>Review your budget monthly to catch any overspending early</li>
                                <li>Consider automating your savings to make it effortless</li>
                                <li>Build an emergency fund if you haven't already (3-6 months of expenses)</li>
                            </ul>
                        </Card>
                    </>
                )}

                {/* Adjust Target */}
                {userChoice === 'adjust' && (
                    <>
                        <br/>
                        <h3 style={{color: '#003E5C'}}>Adjust Your Net Worth Target</h3>
                        <br/>
                        <Card style={{ padding: '24px', marginBottom: '24px' }}>
                            <div>
                                <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px'}}>
                                    <label style={{fontSize: '16px', fontWeight: 600, margin: 0}}>
                                        Adjustment from Baseline: <span style={{color: targetGrowthPercent >= 0 ? '#28a745' : '#dc3545', fontSize: '20px'}}>
                                            {targetGrowthPercent >= 0 ? '+' : ''}{targetGrowthPercent}%
                                        </span>
                                    </label>
                                    <div style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
                                        <input
                                            type="number"
                                            min="-100"
                                            max="100"
                                            step="0.1"
                                            value={targetGrowthPercent}
                                            onChange={(e) => {
                                                const val = Number(e.target.value);
                                                if (val >= -100 && val <= 100) {
                                                    setTargetGrowthPercent(val);
                                                }
                                            }}
                                            style={{
                                                width: '80px',
                                                padding: '8px',
                                                borderRadius: '4px',
                                                border: '1px solid #ccc',
                                                fontSize: '14px',
                                                textAlign: 'right'
                                            }}
                                        />
                                        <span style={{fontSize: '14px', color: '#666'}}>%</span>
                                    </div>
                                </div>
                                <p style={{fontSize: '14px', color: '#666', marginBottom: '12px'}}>
                                    Baseline prediction: {prediction ? prediction.predicted_net_worth_12mo.toLocaleString('en-US', {style: 'currency', currency: 'USD'}) : '...'}
                                </p>
                                <input
                                    type="range"
                                    min="-100"
                                    max="100"
                                    step="0.1"
                                    value={targetGrowthPercent}
                                    onChange={(e) => setTargetGrowthPercent(Number(e.target.value))}
                                    style={{
                                        width: '100%',
                                        height: '8px',
                                        borderRadius: '5px',
                                        background: 'linear-gradient(to right, #dc3545 0%, #ffc107 50%, #28a745 100%)',
                                        outline: 'none',
                                        marginBottom: '20px'
                                    }}
                                />
                                <div style={{display: 'flex', justifyContent: 'space-between', color: '#666', fontSize: '12px'}}>
                                    <span>-100%</span>
                                    <span>0%</span>
                                    <span>+100%</span>
                                </div>
                            </div>
                            <br/>
                            <button
                                onClick={applyTargetSavings}
                                style={{
                                    backgroundColor: '#003E5C',
                                    color: 'white',
                                    border: 'none',
                                    padding: '12px 32px',
                                    borderRadius: '8px',
                                    fontSize: '16px',
                                    fontWeight: 600,
                                    cursor: 'pointer',
                                    width: '100%'
                                }}
                            >
                                Calculate Savings Plan
                            </button>
                        </Card>

                        {targetGrowthPercent !== null && (() => {
                            const calculation = calculateSavingsForTarget();
                            if (!calculation) return null;

                            // If adjustment is 0 or negative, it's always achievable (reducing spending)
                            const isReducingTarget = targetGrowthPercent <= 0;

                            return (
                                <>
                                    {isReducingTarget ? (
                                        <>
                                            <Card style={{ padding: '24px', marginBottom: '16px', backgroundColor: '#fff3cd', border: '1px solid #ffc107' }}>
                                                <div style={{textAlign: 'center'}}>
                                                    <h2 style={{color: '#856404', marginBottom: '16px'}}>Lower Target Selected</h2>
                                                    <p style={{fontSize: '18px', color: '#856404', marginBottom: '12px'}}>
                                                        Your adjusted target: {calculation.targetNetWorth.toLocaleString('en-US', {style: 'currency', currency: 'USD'})}
                                                        {' '}({targetGrowthPercent}% adjustment)
                                                    </p>
                                                    <p style={{fontSize: '16px', color: '#856404'}}>
                                                        This is {Math.abs(calculation.additionalSavingsNeeded).toLocaleString('en-US', {style: 'currency', currency: 'USD'})}/month less than your baseline trajectory. You'll have more spending flexibility!
                                                    </p>
                                                </div>
                                            </Card>
                                            <Card style={{ padding: '20px', backgroundColor: '#e7f3ff' }}>
                                                <h4 style={{color: '#003E5C', marginBottom: '12px'}}>Enjoying Life While Building Wealth</h4>
                                                <ul style={{color: '#004879', lineHeight: '1.8', paddingLeft: '20px'}}>
                                                    <li>It's okay to prioritize current lifestyle and experiences</li>
                                                    <li>You can still build wealth at a comfortable pace</li>
                                                    <li>Consider allocating the extra funds to things that bring you joy</li>
                                                    <li>Keep an eye on your spending to ensure you stay on track</li>
                                                </ul>
                                            </Card>
                                        </>
                                    ) : calculation.isAchievable ? (
                                        <>
                                            <Card style={{ padding: '24px', marginBottom: '16px', backgroundColor: '#d4edda', border: '1px solid #c3e6cb' }}>
                                                <div style={{textAlign: 'center'}}>
                                                    <h2 style={{color: '#155724', marginBottom: '16px'}}>Goal is Achievable!</h2>
                                                    <p style={{fontSize: '18px', color: '#155724', marginBottom: '8px'}}>
                                                        To reach {calculation.targetNetWorth.toLocaleString('en-US', {style: 'currency', currency: 'USD'})} in 12 months
                                                    </p>
                                                    <p style={{fontSize: '14px', color: '#155724'}}>
                                                        ({targetGrowthPercent >= 0 ? '+' : ''}{targetGrowthPercent}% from baseline: {calculation.baselinePredicted.toLocaleString('en-US', {style: 'currency', currency: 'USD'})})
                                                    </p>
                                                </div>
                                            </Card>

                                            <div className="dashboard-cards">
                                                <Card>
                                                    <div style={{margin: "10px", textAlign: 'center'}}>
                                                        <p style={{fontWeight: 600, color: '#666'}}>Additional Savings/Month</p>
                                                        <p style={{fontSize: "32px", color: '#28a745', fontWeight: 700}}>
                                                            ${calculation.additionalSavingsNeeded.toLocaleString('en-US', {minimumFractionDigits: 2})}
                                                        </p>
                                                    </div>
                                                </Card>
                                                <Card>
                                                    <div style={{margin: "10px", textAlign: 'center'}}>
                                                        <p style={{fontWeight: 600, color: '#666'}}>% of Income</p>
                                                        <p style={{fontSize: "32px", color: '#003E5C', fontWeight: 700}}>
                                                            {calculation.percentageOfIncome.toFixed(1)}%
                                                        </p>
                                                    </div>
                                                </Card>
                                                <Card>
                                                    <div style={{margin: "10px", textAlign: 'center'}}>
                                                        <p style={{fontWeight: 600, color: '#666'}}>Target Net Worth</p>
                                                        <p style={{fontSize: "32px", color: '#28a745', fontWeight: 700}}>
                                                            ${calculation.targetNetWorth.toLocaleString('en-US', {minimumFractionDigits: 2})}
                                                        </p>
                                                    </div>
                                                </Card>
                                            </div>
                                            {calculation.additionalSavingsNeeded > 0.01 && (
                                                <>
                                                    <Card style={{ padding: '20px', backgroundColor: '#e7f3ff', marginTop: '16px' }}>
                                                        <p style={{color: '#004879', marginBottom: '8px'}}>
                                                            Save an <strong>additional ${calculation.additionalSavingsNeeded.toLocaleString('en-US', {minimumFractionDigits: 2})}/month</strong> beyond your current trajectory to reach this goal
                                                        </p>
                                                    </Card>

                                                    <Card style={{ padding: '20px', backgroundColor: '#fff3cd', border: '1px solid #ffc107', marginTop: '16px' }}>
                                                        <h4 style={{color: '#856404', marginBottom: '16px'}}>Ways to Bridge the Gap</h4>
                                                        <p style={{color: '#856404', marginBottom: '16px'}}>
                                                            Here's how to save an additional <strong>${calculation.additionalSavingsNeeded.toLocaleString('en-US', {minimumFractionDigits: 2})}/month</strong>:
                                                        </p>

                                                        <div style={{backgroundColor: 'white', padding: '16px', borderRadius: '8px'}}>
                                                            <h5 style={{color: '#003E5C', marginBottom: '12px'}}>Recommended Spending Adjustments:</h5>

                                                            {(() => {
                                                                const gap = calculation.additionalSavingsNeeded;
                                                                const totalVariableSpending = Object.values(spendingByCategory).reduce((sum, val) => sum + val, 0);

                                                                // Two-pass algorithm to ensure cuts sum to exactly the gap
                                                                const categories = [];

                                                                if (spendingByCategory.dining > 0) {
                                                                    categories.push({
                                                                        category: 'Dining & Restaurants',
                                                                        current: spendingByCategory.dining,
                                                                        maxCap: 0.5,
                                                                        tip: 'Cook at home more, limit takeout to 2-3 times/week'
                                                                    });
                                                                }

                                                                if (spendingByCategory.shopping > 0 || spendingByCategory.entertainment > 0) {
                                                                    const totalShopEnt = (spendingByCategory.shopping || 0) + (spendingByCategory.entertainment || 0);
                                                                    categories.push({
                                                                        category: 'Shopping & Entertainment',
                                                                        current: totalShopEnt,
                                                                        maxCap: 0.5,
                                                                        tip: 'Limit impulse purchases, use 24-hour rule'
                                                                    });
                                                                }

                                                                if (spendingByCategory.transportation > 0) {
                                                                    categories.push({
                                                                        category: 'Transportation',
                                                                        current: spendingByCategory.transportation,
                                                                        maxCap: 0.4,
                                                                        tip: 'Carpool, public transit, combine errands'
                                                                    });
                                                                }

                                                                if (spendingByCategory.other > 0) {
                                                                    categories.push({
                                                                        category: 'Other Variable Expenses',
                                                                        current: spendingByCategory.other,
                                                                        maxCap: 0.4,
                                                                        tip: 'Review and reduce non-essential spending'
                                                                    });
                                                                }

                                                                // First pass: calculate proportional cuts with caps
                                                                const recommendations = categories.map(cat => {
                                                                    const proportionalCut = (cat.current / totalVariableSpending) * gap;
                                                                    const maxCut = cat.current * cat.maxCap;
                                                                    const actualCut = Math.min(proportionalCut, maxCut);

                                                                    return {
                                                                        ...cat,
                                                                        cut: actualCut,
                                                                        hitCap: proportionalCut > maxCut,
                                                                        availableRoom: maxCut - actualCut
                                                                    };
                                                                });

                                                                // Calculate shortfall
                                                                const totalCuts = recommendations.reduce((sum, rec) => sum + rec.cut, 0);
                                                                const shortfall = gap - totalCuts;

                                                                // Second pass: distribute shortfall to categories that haven't hit caps
                                                                if (shortfall > 0.01) {
                                                                    const uncappedCategories = recommendations.filter(rec => !rec.hitCap && rec.availableRoom > 0);

                                                                    if (uncappedCategories.length > 0) {
                                                                        const totalAvailableRoom = uncappedCategories.reduce((sum, rec) => sum + rec.availableRoom, 0);

                                                                        uncappedCategories.forEach(rec => {
                                                                            const additionalCut = Math.min(
                                                                                (rec.availableRoom / totalAvailableRoom) * shortfall,
                                                                                rec.availableRoom
                                                                            );
                                                                            rec.cut += additionalCut;
                                                                        });
                                                                    }
                                                                }

                                                                // Calculate final total
                                                                const finalTotal = recommendations.reduce((sum, rec) => sum + rec.cut, 0);

                                                                return (
                                                                    <>
                                                                        {recommendations.map((rec, idx) => (
                                                                            <div key={idx} style={{
                                                                                marginBottom: '10px',
                                                                                paddingLeft: '12px',
                                                                                borderLeft: '3px solid #ffc107'
                                                                            }}>
                                                                                <div style={{display: 'flex', justifyContent: 'space-between'}}>
                                                                                    <span style={{fontWeight: 600}}>{rec.category}</span>
                                                                                    <span style={{color: '#dc3545', fontWeight: 600}}>
                                                                                        -${rec.cut.toFixed(2)}
                                                                                    </span>
                                                                                </div>
                                                                                <p style={{fontSize: '12px', color: '#999', margin: '2px 0'}}>
                                                                                    Current: ${rec.current.toFixed(2)}/mo
                                                                                </p>
                                                                                <p style={{fontSize: '13px', color: '#666', margin: '4px 0 0 0'}}>
                                                                                    {rec.tip}
                                                                                </p>
                                                                            </div>
                                                                        ))}
                                                                        <div style={{
                                                                            marginTop: '16px',
                                                                            paddingTop: '12px',
                                                                            borderTop: '2px solid #ffc107',
                                                                            display: 'flex',
                                                                            justifyContent: 'space-between',
                                                                            fontWeight: 700,
                                                                            fontSize: '16px'
                                                                        }}>
                                                                            <span>Total Monthly Savings:</span>
                                                                            <span style={{color: '#dc3545'}}>
                                                                                -${finalTotal.toFixed(2)}
                                                                            </span>
                                                                        </div>
                                                                    </>
                                                                );
                                                            })()}
                                                        </div>
                                                    </Card>
                                                </>
                                            )}
                                        </>
                                    ) : (
                                        <>
                                            <Card style={{ padding: '24px', marginBottom: '16px', backgroundColor: '#f8d7da', border: '1px solid #f5c6cb' }}>
                                                <div style={{textAlign: 'center'}}>
                                                    <h2 style={{color: '#721c24', marginBottom: '16px'}}>Goal Exceeds Maximum Capacity</h2>
                                                    <p style={{fontSize: '16px', color: '#721c24', marginBottom: '12px'}}>
                                                        This target requires ${calculation.additionalSavingsNeeded.toLocaleString('en-US', {minimumFractionDigits: 2})}/month in additional savings,
                                                        but your maximum capacity (after essential expenses) is ${calculation.maxMonthlySavings.toLocaleString('en-US', {minimumFractionDigits: 2})}/month.
                                                    </p>
                                                    <p style={{fontSize: '16px', color: '#721c24', marginBottom: '8px'}}>
                                                        You would need to reduce spending by an additional <strong>${(calculation.additionalSavingsNeeded - calculation.maxMonthlySavings).toLocaleString('en-US', {minimumFractionDigits: 2})}/month</strong> beyond your variable expenses.
                                                    </p>
                                                    <p style={{fontSize: '14px', color: '#721c24'}}>
                                                        Maximum achievable adjustment: <strong>{calculation.maxAdjustmentPercent.toFixed(1)}%</strong>
                                                        ({(calculation.baselinePredicted + calculation.maxAdditionalGrowth).toLocaleString('en-US', {style: 'currency', currency: 'USD'})})
                                                    </p>
                                                </div>
                                            </Card>

                                            <Card style={{ padding: '20px', backgroundColor: '#e7f3ff', marginTop: '16px' }}>
                                                <h4 style={{color: '#003E5C', marginBottom: '12px'}}>Consider These Options Instead</h4>
                                                <ul style={{color: '#004879', lineHeight: '1.8', paddingLeft: '20px'}}>
                                                    <li><strong>Lower your target</strong> to a more realistic percentage using the slider above</li>
                                                    <li><strong>Increase your income</strong> through a side hustle, freelance work, or raise</li>
                                                    <li><strong>Extend your timeline</strong> to 18-24 months for more gradual growth</li>
                                                    <li><strong>Reduce fixed expenses</strong> by negotiating bills or refinancing debts</li>
                                                </ul>
                                            </Card>
                                        </>
                                    )}
                                </>
                            );
                        })()}
                    </>
                )}

                {userChoice && (
                    <>
                        <br/>
                        <button
                            onClick={() => {
                                setUserChoice(null);
                                setTargetGrowthPercent(null);
                                fetchPrediction(0);
                            }}
                            style={{
                                backgroundColor: '#6c757d',
                                color: 'white',
                                border: 'none',
                                padding: '12px 24px',
                                borderRadius: '8px',
                                fontSize: '14px',
                                cursor: 'pointer'
                            }}
                        >
                            Start Over
                        </button>
                    </>
                )}
            </>
        )}
    </div>
}
