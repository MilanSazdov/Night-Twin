import React from 'react'
import imglasta from '../assets/download.jpg'
import img2 from '../assets/ChatGPT Image Nov 22, 2025, 08_58_07 PM.png'
import img3 from '../assets/ChatGPT Image Nov 22, 2025, 08_59_30 PM.png'

type Props = {
  id: number
  onBack: () => void
}

const IMAGES: Record<number, { src: string; title: string; desc: string }> = {
  1: { src: imglasta, title: 'Lasta', desc: 'A popular spot matching your preferences — late start, mid-budget, non-alcohol friendly options.' },
  2: { src: img2, title: 'Afterparty', desc: 'Late-night afterparty vibes.' },
  3: { src: img3, title: 'Vibe', desc: 'Chill areas and lounge vibes.' },
}

export default function OptionPage({ id, onBack }: Props) {
  const info = IMAGES[id] || IMAGES[1]
  return (
    <div className="gallery-page">
      <button className="gallery-back" onClick={onBack} aria-label="Back">← Back</button>
      <div style={{ display: 'flex', gap: '1.25rem', alignItems: 'flex-start', justifyContent: 'center', width: '100%' }}>
        <div style={{ maxWidth: 720 }}>
          <img src={info.src} alt={info.title} style={{ width: '100%', borderRadius: 12, objectFit: 'cover' }} />
          <h3 style={{ marginTop: '0.75rem' }}>{info.title}</h3>
          <p style={{ color: 'var(--muted)' }}>{info.desc}</p>
        </div>
        <aside style={{ minWidth: 260 }}>
          <div style={{ background: 'linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.02))', padding: '1rem', borderRadius: 10, border: '1px solid rgba(255,255,255,0.04)' }}>
            <h4>Match score</h4>
            <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--accent)' }}>9/10</div>
            <p style={{ marginTop: '0.6rem', color: 'var(--muted)' }}>This result matches your preferences closely.</p>
          </div>
        </aside>
      </div>
    </div>
  )
}
