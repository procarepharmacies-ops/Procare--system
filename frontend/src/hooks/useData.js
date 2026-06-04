import { useState, useEffect, useCallback } from 'react'

export function useData(fetcher, interval = 30000) {
  const [data, setData]     = useState(null)
  const [error, setError]   = useState(null)
  const [loading, setLoading] = useState(true)

  const load = useCallback(() => {
    fetcher()
      .then(d => { setData(d); setError(null) })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [fetcher])

  useEffect(() => {
    load()
    const id = setInterval(load, interval)
    return () => clearInterval(id)
  }, [load, interval])

  return { data, error, loading, refresh: load }
}
