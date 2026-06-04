const typeColors = {
  POS:      'bg-green-500/20 text-green-400',
  Treasury: 'bg-yellow-500/20 text-yellow-400',
  Bank:     'bg-blue-500/20 text-blue-400',
  Other:    'bg-slate-500/20 text-slate-400',
}

export default function TreasuryPanel({ branches, grand_total }) {
  if (!branches?.length) return <p className="text-slate-500 text-sm">No data.</p>

  return (
    <div>
      <div className="text-2xl font-bold text-white mb-4">
        {grand_total?.toLocaleString('en-EG', { maximumFractionDigits: 0 })} EGP
      </div>
      {branches.map(b => (
        <div key={b.branch} className="mb-4">
          <div className="text-green-400 font-semibold text-sm mb-2">{b.branch}</div>
          {b.accounts.map((acc, i) => (
            <div key={i} className="flex items-center justify-between py-1.5 border-b border-slate-700/40">
              <div className="flex items-center gap-2">
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${typeColors[acc.type] || typeColors.Other}`}>
                  {acc.type}
                </span>
                <span className="text-slate-300 text-sm">{acc.name_ar || acc.name}</span>
              </div>
              <span className="text-white font-medium text-sm">
                {acc.balance.toLocaleString('en-EG', { maximumFractionDigits: 0 })}
              </span>
            </div>
          ))}
          <div className="flex justify-between pt-1 text-sm">
            <span className="text-slate-500">Branch total</span>
            <span className="text-white font-semibold">
              {b.total.toLocaleString('en-EG', { maximumFractionDigits: 0 })} EGP
            </span>
          </div>
        </div>
      ))}
    </div>
  )
}
