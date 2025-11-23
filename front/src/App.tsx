import { useState } from 'react'
// removed logo imports; showing app name instead
import './App.css'
import Navbar from './components/Navbar'
import LoginForm from './components/LoginForm'
import RegisterForm from './components/RegisterForm'
import CursorLight from './components/CursorLight'
import PartyGoer from './components/PartyGoer'
import Fog from './components/Fog'
import Gallery from './components/Gallery'
import OptionPage from './components/OptionPage'
import { useEffect } from 'react'

function App() {
  const [showLogin, setShowLogin] = useState(false)
  const [showRegister, setShowRegister] = useState(false)
  const [showCards, setShowCards] = useState(false)
  const [view, setView] = useState<'home' | 'gallery' | 'option'>('home')
  const [optionId, setOptionId] = useState<number | null>(null)

  // Navigate helper: prefer history API, fallback to hash
  function navigate(path: string) {
    try {
      if (window.history && window.history.pushState) {
        window.history.pushState({}, '', path)
      } else {
        window.location.hash = `#${path}`
      }
    } catch (e) {
      // ignore
    }
    // update view immediately
    if (path === '/findnight' || path === '#/findnight' || path === '#findnight') {
      setView('gallery')
      setOptionId(null)
    } else if (path.startsWith('/option/') || path.startsWith('#/option/')) {
      // extract id
      const id = parseInt(path.split('/').pop() || '', 10) || null
      setOptionId(id)
      setView('option')
    } else {
      setView('home')
      setOptionId(null)
    }
  }

  useEffect(() => {
    // initial routing: check pathname or hash
    const p = window.location.pathname
    const h = window.location.hash
    if (p === '/findnight' || h === '#/findnight' || h === '#findnight') {
      setView('gallery')
      setOptionId(null)
    } else if (h.startsWith('#/option/') || p.startsWith('/option/')) {
      const raw = h.startsWith('#/option/') ? h.replace('#/option/', '') : p.replace('/option/', '')
      const id = parseInt(raw.split('/')[0] || '', 10) || null
      setOptionId(id)
      setView('option')
    }

    function onPop() {
      const p2 = window.location.pathname
      const h2 = window.location.hash
      if (p2 === '/findnight' || h2 === '#/findnight' || h2 === '#findnight') {
        setView('gallery')
        setOptionId(null)
      } else if (h2.startsWith('#/option/') || p2.startsWith('/option/')) {
        const raw = h2.startsWith('#/option/') ? h2.replace('#/option/', '') : p2.replace('/option/', '')
        const id = parseInt(raw.split('/')[0] || '', 10) || null
        setOptionId(id)
        setView('option')
      } else {
        setView('home')
        setOptionId(null)
      }
    }

    window.addEventListener('popstate', onPop)
    return () => window.removeEventListener('popstate', onPop)
  }, [])

  return (
    <>
      <CursorLight />
      <Fog />
      <PartyGoer />
      <Navbar onShowLogin={() => setShowLogin(true)} onShowRegister={() => setShowRegister(true)} />

      {showLogin && <LoginForm onClose={() => setShowLogin(false)} />}
      {showRegister && <RegisterForm onClose={() => setShowRegister(false)} />}

      {view === 'gallery' ? (
        <Gallery onBack={() => navigate('/')} />
      ) : view === 'option' && optionId ? (
        <OptionPage id={optionId} onBack={() => navigate('/findnight')} />
      ) : (
        <main className="app-content">
          <div className="app-hero full-center">
            <div className="brand" role="button" tabIndex={0} onClick={() => setShowCards(s => !s)} onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') setShowCards(s => !s) }}>
              NightTwin
            </div>

            <div className="hero-actions">
              <button className="find-btn" onClick={() => navigate('/findnight')}>Find perfect night</button>
            </div>

            {showCards && (
              <div className="cards" role="dialog" aria-modal onClick={() => setShowCards(false)}>
                <div className="cards-inner" onClick={(e) => e.stopPropagation()}>
                  <div className="info-card">
                    <h3>Find your night</h3>
                    <p>Search and discover the best night events nearby.</p>
                  </div>  
                  <div className="info-card">
                    <h3>Reserve Spot</h3>
                    <p>Book a table or reserve entry quickly.</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </main>
      )}
    </>
  )
}

export default App
