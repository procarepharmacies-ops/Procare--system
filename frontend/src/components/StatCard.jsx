export default function StatCard({ title, value, sub, icon, color = 'green', urgent }) {
  const colors = {
    green:  'from-green-500/20 to-green-600/10 border-green-500/30 text-green-400',
    blue:   'from-blue-500/20  to-blue-600/10  border-blue-500/30  text-blue-400',
    yellow: 'from-yellow-500/20 to-yellow-600/10 border-yellow-500/30 text-yellow-400',
    red:    'from-red-500/20   to-red-600/10   border-red-500/30   text-red-400',
    purple: 'from-purple-500/20 to-purple-600/10 border-purple-500/30 text-purple-400',
  }
  const ring = urgent ? 'ring-2 ring-red-500/60' : ''

  return (
    <div className={`bg-gradient-to-br ${colors[color]} border rounded-2xl p-5 ${ring}`}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-slate-400 text-sm font-medium">{title}</span>
        <span className="text-2xl">{icon}</span>
      </div>
      <div className="text-3xl font-bold text-white mb-1">{value}</div>
      {sub && <div className="text-slate-400 text-xs">{sub}</div>}
    </div>
  )
}
