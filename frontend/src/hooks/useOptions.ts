import { useEffect, useState } from 'react'
import { resource } from '../api/resources'
import type { Option } from '../components/CrudPage'

/**
 * Fetch list endpoint and map records to {label, value} for Select.
 */
export function useOptions(
  endpoint: string,
  labelFn: (row: any) => string,
  valueFn: (row: any) => any = (row) => row.id,
) {
  const [options, setOptions] = useState<Option[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let alive = true
    const api = resource(endpoint)
    ;(async () => {
      setLoading(true)
      setError(null)
      try {
        const rows = await api.list()
        if (!alive) return
        const opts = (Array.isArray(rows) ? rows : []).map((r: any) => ({
          value: valueFn(r),
          label: labelFn(r),
        }))
        setOptions(opts)
      } catch (e: any) {
        if (!alive) return
        setError(e?.response?.data?.detail || 'Failed to load options')
        setOptions([])
      } finally {
        if (alive) setLoading(false)
      }
    })()
    return () => {
      alive = false
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [endpoint])

  return { options, loading, error }
}
