type Props = {
  onShowLogin: () => void
  onShowRegister: () => void
}

export default function Navbar({ onShowLogin, onShowRegister }: Props) {
  return (
    <header className="nav">
      <div id="club" className="nav-left">
        <span className="brand-small">NightTwin</span>
      </div>
      <nav className="nav-right">
        <button className="nav-btn" onClick={onShowLogin} aria-label="Open login">Login</button>
        <button className="nav-btn primary" onClick={onShowRegister} aria-label="Open register">Register</button>
      </nav>
    </header>
  )
}
