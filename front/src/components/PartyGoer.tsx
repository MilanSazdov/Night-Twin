import { useEffect, useRef } from 'react'

export default function PartyGoer() {
  const ref = useRef<HTMLDivElement | null>(null)
  const posRef = useRef({ x: 0, y: 0 })
  const animRef = useRef<number | null>(null)
  const stopTimer = useRef<number | null>(null)

  useEffect(() => {
    if (typeof document === 'undefined') return
    const el = ref.current!

    // initial position: bottom-left area
    posRef.current.x = window.innerWidth * 0.08
    posRef.current.y = window.innerHeight * 0.78
    el.style.transform = `translate3d(${posRef.current.x}px, ${posRef.current.y}px, 0) translate(-50%, -50%)`

    let target = { x: posRef.current.x, y: posRef.current.y }
    let animating = false

    function getClubCenter() {
      const club = document.getElementById('club')
      if (!club) return { x: window.innerWidth / 2, y: 80 }
      const r = club.getBoundingClientRect()
      return { x: r.left + r.width / 2, y: r.top + r.height / 2 }
    }

    function onPointerMove() {
      // set new target as club center when pointer moves
      target = getClubCenter()
      // start animation loop if not started
      if (!animating) {
        animating = true
        step()
      }

      // reset stop timer so movement continues while user moves the mouse
      if (stopTimer.current) window.clearTimeout(stopTimer.current)
      stopTimer.current = window.setTimeout(() => {
        animating = false
        if (animRef.current) cancelAnimationFrame(animRef.current)
      }, 700)
    }

    function step() {
      const cur = posRef.current
      // move a fraction toward the target (easing)
      const dx = target.x - cur.x
      const dy = target.y - cur.y
      const dist = Math.hypot(dx, dy)
      if (dist > 0.6) {
        // step size proportional to distance but clamped
        const stepSize = Math.max(4, Math.min(40, dist * 0.12))
        cur.x += (dx / dist) * stepSize
        cur.y += (dy / dist) * stepSize
        el.style.transform = `translate3d(${cur.x}px, ${cur.y}px, 0) translate(-50%, -50%)`
        animRef.current = requestAnimationFrame(step)
      } else {
        // close enough; stop animation
        animating = false
        if (animRef.current) cancelAnimationFrame(animRef.current)
      }
    }

    window.addEventListener('pointermove', onPointerMove)

    return () => {
      window.removeEventListener('pointermove', onPointerMove)
      if (animRef.current) cancelAnimationFrame(animRef.current)
      if (stopTimer.current) window.clearTimeout(stopTimer.current)
    }
  }, [])

  return <div ref={ref} className="party-goer" aria-hidden />
}
