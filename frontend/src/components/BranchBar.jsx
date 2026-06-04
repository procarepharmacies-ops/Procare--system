export default function BranchBar({ branch }) {
  const { name, total, tx, share } = branch
  const isElsanta = name?.toLowerCase().includes('els')

  return (
    <div className="mb-3">
      <div className="flex justify-between text-sm mb-1">
        <span className="text-white font-medium">{name}</span>
        <span className="text-slate-400">{tx} tx · {total.toLocaleString('en-EG', { maximumFractionDigits: 0 })} EGP</span>
      </div>
      <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full ${isElsanta ? 'bg-green-500' : 'bg-blue-500'}`}
          style={{ width: `${share}%` }}
        />
      </div>
      <div className="text-right text-xs text-slate-500 mt-0.5">{share}%</div>
    </div>
  )
}
