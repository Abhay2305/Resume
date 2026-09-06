import { useState, useEffect } from 'react'

const DESKTOP_BREAKPOINT = 1280
const LAPTOP_BREAKPOINT = 1024
const TABLET_BREAKPOINT = 768

function getWidth(): number {
  if (typeof window === 'undefined') return 1280
  return window.innerWidth
}

export function useResponsive() {
  const [width, setWidth] = useState<number>(getWidth)

  useEffect(() => {
    const handleResize = () => setWidth(window.innerWidth)

    const mqlDesktop = window.matchMedia(`(min-width: ${DESKTOP_BREAKPOINT}px)`)
    const mqlLaptop = window.matchMedia(`(min-width: ${LAPTOP_BREAKPOINT}px)`)
    const mqlTablet = window.matchMedia(`(min-width: ${TABLET_BREAKPOINT}px)`)

    mqlDesktop.addEventListener('change', handleResize)
    mqlLaptop.addEventListener('change', handleResize)
    mqlTablet.addEventListener('change', handleResize)

    return () => {
      mqlDesktop.removeEventListener('change', handleResize)
      mqlLaptop.removeEventListener('change', handleResize)
      mqlTablet.removeEventListener('change', handleResize)
    }
  }, [])

  return {
    isDesktop: width >= DESKTOP_BREAKPOINT,
    isLaptop: width >= LAPTOP_BREAKPOINT && width < DESKTOP_BREAKPOINT,
    isTablet: width >= TABLET_BREAKPOINT && width < LAPTOP_BREAKPOINT,
    isMobile: width < TABLET_BREAKPOINT,
    width,
  }
}
