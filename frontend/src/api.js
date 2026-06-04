const BASE = import.meta.env.VITE_API_URL || 'http://localhost:5000'

export const fetchSummary    = () => fetch(`${BASE}/api/summary`).then(r => r.json())
export const fetchBranches   = () => fetch(`${BASE}/api/branches`).then(r => r.json())
export const fetchWeekly     = () => fetch(`${BASE}/api/weekly`).then(r => r.json())
export const fetchTreasury   = () => fetch(`${BASE}/api/treasury`).then(r => r.json())
export const fetchExpiry     = () => fetch(`${BASE}/api/expiry`).then(r => r.json())
export const fetchTopProducts= () => fetch(`${BASE}/api/top_products`).then(r => r.json())
export const fetchPurchases  = () => fetch(`${BASE}/api/purchases`).then(r => r.json())
