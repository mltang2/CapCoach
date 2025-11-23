import { HashRouter, NavLink, Route, Routes } from 'react-router';
import './App.css'
import Dashboard from './components/Dashboard'
import Checking from './components/Checking'
import Savings from './components/Savings'
import Capcoach from './components/Capcoach'
import { useState } from 'react'
import data from './datasets/alex2Ystable.json'

function App() {
  const [navOpen, setNavOpen] = useState(true);
  const toggleNav = () => setNavOpen((open) => !open);

  // Get the latest month's data (month 24)
  const latestMonth = data.monthly_financial_history[data.monthly_financial_history.length - 1];
  const accountTotal = latestMonth.balance_sheet_snapshot.liquid_assets.savings_account + latestMonth.balance_sheet_snapshot.liquid_assets.checking_account;
  const accountTotalFormatted = accountTotal.toLocaleString('en-US');

  return <HashRouter>
    <div className={`layout ${navOpen ? 'nav-open' : 'nav-closed'}`}>
      <aside className={`side-nav ${navOpen ? 'is-open' : 'is-closed'}`}>
        <button className="nav-close" onClick={toggleNav} aria-label="Close navigation">×</button>
        <div className="brand">CapCoach Banking</div>
        <nav>
          <NavLink to="/" end className="nav-link">Dashboard</NavLink>
          <NavLink to="/checking" className="nav-link">Checking Account</NavLink>
          <NavLink to="/savings" className="nav-link">Savings Account</NavLink>
          <NavLink to="/capcoach" className="nav-link">CapCoach</NavLink>
        </nav>
        <hr/>
        <h2 className="summary" style={{fontSize: "20px"}}>Total Balance: ${accountTotalFormatted}</h2>
      </aside>
      <main className="content">
        <button className="nav-open-btn" onClick={toggleNav} aria-label="Open navigation">☰</button>
        <Routes>
          <Route path='/' element={<Dashboard/>}></Route>
          <Route path='/checking' element={<Checking/>}></Route>
          <Route path='/savings' element={<Savings/>}></Route>
          <Route path='/capcoach' element={<Capcoach/>}></Route>
        </Routes>
      </main>
    </div>
  </HashRouter>
}

export default App
