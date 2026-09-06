import { useState, useCallback } from 'react'

const STORAGE_KEY = 'procs.sidebar.collapsed'

function getStoredState(): boolean {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    return stored === 'true'
  } catch {
    return false
  }
}

export function useSidebar() {
  const [isCollapsed, setIsCollapsed] = useState<boolean>(getStoredState)

  const toggle = useCallback(() => {
    setIsCollapsed((prev) => {
      const next = !prev
      try {
        localStorage.setItem(STORAGE_KEY, String(next))
      } catch {
        // localStorage unavailable — state still updates in memory
      }
      return next
    })
  }, [])

  return { isCollapsed, toggle }
}
