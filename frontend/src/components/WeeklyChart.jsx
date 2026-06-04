export default function WeeklyChart({ days, sales }) {
  if (!days?.length) return <p className="text-slate-500 text-sm">No data.</p>

  const max = Math.max(...sales, 1)

  return (
    <div className="flex items-end gap-2 h-32">
      {days.map((day, i) => {
        const pct = (sales[i] / max) * 100
        const label = new Date(day).toLocaleDateString('en-EG', { weekday: 'short' })
        return (
          <div key={i} className="flex-1 flex flex-col items-center gap-1">
            <span className="text-xs text-slate-500">
              {sales[i] >= 1000 ? `${(sales[i]/1000).toFixed(1)}k` : sales[i]}
            </span>
            <div className="w-full bg-slate-700 rounded-t-sm relative" style={{ height: '80px' }}>
              <div
                className="absolute bottom-0 w-full bg-green-500 rounded-t-sm transition-all duration-500"
                style={{ height: `${pct}%` }}
              />
            </div>
            <span className="text-xs text-slate-500">{label}</span>
          </div>
        )
      })}
    </div>
  )
}
