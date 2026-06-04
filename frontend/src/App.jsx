import { useCallback } from 'react'
import { useData } from './hooks/useData'
import {
  fetchSummary, fetchBranches, fetchWeekly,
  fetchTreasury, fetchExpiry, fetchTopProducts
} from './api'
import StatCard      from './components/StatCard'
import SectionCard   from './components/SectionCard'
import BranchBar     from './components/BranchBar'
import ExpiryTable   from './components/ExpiryTable'
import WeeklyChart   from './components/WeeklyChart'
import TreasuryPanel from './components/TreasuryPanel'

function fmt(n) {
  if (!n && n !== 0) return '...'
  if (n >= 1_000_000) return `${(n/1_000_000).toFixed(1)}M`
  if (n >= 1_000)     return `${(n/1_000).toFixed(1)}k`
  return n.toLocaleString('en-EG')
}

export default function App() {
  const summary     = useData(useCallback(fetchSummary,     []), 30_000)
  const branches    = useData(useCallback(fetchBranches,    []), 60_000)
  const weekly      = useData(useCallback(fetchWeekly,      []), 60_000)
  const treasury    = useData(useCallback(fetchTreasury,    []), 60_000)
  const expiry      = useData(useCallback(fetchExpiry,      []), 120_000)
  const topProducts = useData(useCallback(fetchTopProducts, []), 60_000)

  const s = summary.data || {}
  const connected = !summary.error

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      {/* Header */}
      <header className="bg-slate-800/80 border-b border-slate-700/50 backdrop-blur sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center text-white font-bold text-sm">P</div>
            <div>
              <div className="text-white font-semibold text-sm">ProCare Intelligence</div>
              <div className="text-slate-500 text-xs">Elsanta · Mashala</div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`} />
            <span className="text-xs text-slate-400">
              {connected ? `Live · ${s.generated_at || ''}` : 'Offline'}
            </span>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6 space-y-6">

        {/* KPI Row */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <StatCard title="Today Sales"     value={`${fmt(s.today_sales)} EGP`}     icon="💰" color="green"  />
          <StatCard title="Transactions"    value={fmt(s.today_tx)}                  icon="🧾" color="blue"   />
          <StatCard title="Yesterday Sales" value={`${fmt(s.yesterday_sales)} EGP`} icon="📅" color="purple" />
          <StatCard title="Yesterday Tx"    value={fmt(s.yesterday_tx)}              icon="📊" color="blue"   />
          <StatCard title="Expiry Alerts"   value={fmt(s.expiry_alerts)}             icon="⚠️" color="yellow"
                    urgent={s.expiry_alerts > 0} />
          <StatCard title="Treasury"        value={`${fmt(s.treasury_total)} EGP`}  icon="🏦" color="green"  />
        </div>

        {/* Row 2: Weekly + Branches */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <SectionCard title="7-Day Sales">
            <WeeklyChart days={weekly.data?.days} sales={weekly.data?.sales} />
            {weekly.data && (
              <div className="mt-3 flex gap-4 text-sm text-slate-400">
                <span>Week total: <strong className="text-white">{fmt(weekly.data.week_total)} EGP</strong></span>
                <span>Tx: <strong className="text-white">{weekly.data.week_tx}</strong></span>
              </div>
            )}
          </SectionCard>

          <SectionCard title="Branch Comparison">
            {branches.data?.branches?.map(b => <BranchBar key={b.name} branch={b} />)}
            {branches.data && (
              <div className="text-xs text-slate-500 mt-2">Yesterday · {branches.data.date}</div>
            )}
          </SectionCard>
        </div>

        {/* Row 3: Treasury + Expiry */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <SectionCard title="Treasury Breakdown">
            <TreasuryPanel branches={treasury.data?.branches} grand_total={treasury.data?.grand_total} />
          </SectionCard>

          <SectionCard title="Expiring Soon (60 days)">
            <ExpiryTable items={expiry.data?.items} />
          </SectionCard>
        </div>

        {/* Row 4: Top Products */}
        <SectionCard title="Top Products Yesterday">
          {topProducts.data?.products?.length ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
              {topProducts.data.products.map((p, i) => (
                <div key={i} className="bg-slate-700/40 rounded-xl p-3">
                  <span className="text-slate-500 text-xs font-bold">#{i+1}</span>
                  <div className="text-white text-sm font-medium truncate mt-1">{p.name}</div>
                  <div className="text-green-400 text-sm font-semibold mt-1">{fmt(p.revenue)} EGP</div>
                  <div className="text-slate-500 text-xs">Qty: {p.qty}</div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-slate-500 text-sm">No data for yesterday.</p>
          )}
        </SectionCard>

      </main>
    </div>
  )
}
