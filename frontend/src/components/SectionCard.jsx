export default function SectionCard({ title, children, action }) {
  return (
    <div className="bg-slate-800/60 border border-slate-700/50 rounded-2xl p-5">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-white font-semibold text-base">{title}</h2>
        {action}
      </div>
      {children}
    </div>
  )
}
