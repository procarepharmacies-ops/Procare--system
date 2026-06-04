export default function ExpiryTable({ items }) {
  if (!items?.length) return <p className="text-slate-500 text-sm">No expiring items.</p>

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-slate-500 text-xs border-b border-slate-700">
            <th className="text-left pb-2 font-medium">Product</th>
            <th className="text-center pb-2 font-medium">Exp Date</th>
            <th className="text-center pb-2 font-medium">Days</th>
            <th className="text-right pb-2 font-medium">Qty</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item, i) => (
            <tr key={i} className="border-b border-slate-700/40 hover:bg-slate-700/20">
              <td className="py-2 text-white">{item.name_ar || item.name_en}</td>
              <td className="py-2 text-center text-slate-400">{item.exp_date}</td>
              <td className="py-2 text-center">
                <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                  item.urgent ? 'bg-red-500/20 text-red-400' : 'bg-yellow-500/20 text-yellow-400'
                }`}>
                  {item.days_left}d
                </span>
              </td>
              <td className="py-2 text-right text-slate-400">{item.qty}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
