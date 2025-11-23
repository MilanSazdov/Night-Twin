import { useEffect, useRef } from 'react'

export default function CursorLight() {
  const ref = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    const el = ref.current
    if (!el) return

    // Pointermove gives immediate, precise coordinates for mouse and stylus
    function onPointerMove(e: PointerEvent) {
      // Position the center of the spotlight exactly at the pointer
      el.style.transform = `translate3d(${e.clientX}px, ${e.clientY}px, 0) translate(-50%, -50%)`
    }

    window.addEventListener('pointermove', onPointerMove)

    // Also hide the spotlight when pointer leaves window
    function onLeave() {
      el.style.opacity = '0'
    }
    function onEnter() {
      el.style.opacity = '0.92'
    }
    window.addEventListener('pointerleave', onLeave)
    window.addEventListener('pointerenter', onEnter)

    return () => {
      window.removeEventListener('pointermove', onPointerMove)
      window.removeEventListener('pointerleave', onLeave)
      window.removeEventListener('pointerenter', onEnter)
    }
  }, [])

  return <div ref={ref} className="cursor-light" />
}
