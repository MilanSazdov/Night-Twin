import { useEffect, useRef } from 'react'
import { createPortal } from 'react-dom'

type Props = {
  onClose: () => void
}

export default function RegisterForm({ onClose }: Props) {
  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const form = e.target as HTMLFormElement
    const data = new FormData(form)
    console.log('Register submit', Object.fromEntries(data.entries()))
    onClose()
  }

  if (typeof document === 'undefined') return null

  const elRef = useRef<HTMLDivElement | null>(null)
  if (!elRef.current) elRef.current = document.createElement('div')

  const modal = (
    <div className="modal-overlay" role="dialog" aria-modal="true">
      <div className="modal">
        <h3>Register</h3>
        <form onSubmit={handleSubmit}>
          <label>
            Name
            <input name="name" type="text" required />
          </label>
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
            <button type="submit" className="primary">Create account</button>
          </div>
        </form>
      </div>
    </div>
  )

  const el = elRef.current!

  useEffect(() => {
    document.body.appendChild(el)
    return () => {
      document.body.removeChild(el)
    }
  }, [el])

  return createPortal(modal, el)
}
