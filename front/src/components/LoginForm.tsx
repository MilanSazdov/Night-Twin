// LoginForm.tsx
import { useEffect, useRef } from 'react'
import { createPortal } from 'react-dom'

type Props = {
  onClose: () => void
}

export default function LoginForm({ onClose }: Props) {
  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const form = e.target as HTMLFormElement
    const data = new FormData(form)
    console.log('Login submit', Object.fromEntries(data.entries()))
    onClose()
  }

  // portal container
  if (typeof document === 'undefined') return null

  const elRef = useRef<HTMLDivElement | null>(null)
  if (!elRef.current) elRef.current = document.createElement('div')
  const el = elRef.current

  useEffect(() => {
    document.body.appendChild(el)
    return () => {
      document.body.removeChild(el)
    }
  }, [el])

  const modal = (
    <div className="modal-overlay" role="dialog" aria-modal="true">
      <div className="modal no-glow">
        <h3>Login</h3>
        <form onSubmit={handleSubmit}>
          <label>
            Email
            <input name="email" type="email" required />
          </label>
          <label>
            Password
            <input name="password" type="password" required />
          </label>
          <div className="modal-actions">
            <button type="button" onClick={onClose}>Cancel</button>
            <button type="submit" className="primary">Sign in</button>
          </div>
        </form>
      </div>
    </div>
  )

  return createPortal(modal, el)
}
