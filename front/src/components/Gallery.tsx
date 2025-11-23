import React from 'react'
import img3 from '../assets/ChatGPT Image Nov 22, 2025, 08_59_30 PM.png'
import img1 from '../assets/ChatGPT Image Nov 22, 2025, 08_52_27 PM.png'
import img2 from '../assets/ChatGPT Image Nov 22, 2025, 08_58_07 PM.png'
import imglasta from '../assets/download.jpg'
import imgkucica from '../assets/images.jpg'
import zapp from '../assets/214263.jpg'
import res1 from '../assets/res1.jpg'
import res2 from '../assets/res2.jpg'
import res3 from '../assets/res3.jpg'
import res4 from '../assets/res4.png'
import res5 from '../assets/res5.png'
import res6 from '../assets/res6.png'
import res11 from '../assets/res11.jpg'
import res12 from '../assets/res12.png'
import res13 from '../assets/res13.jpg'

type Props = {
  onBack: () => void
}

type ClubOption = {
  id: number
  title: string
  desc: string
  img: string
}

export default function Gallery({ onBack }: Props) {
  const [query, setQuery] = React.useState('')
  const [showSecond, setShowSecond] = React.useState(false)
  const [showThird, setShowThird] = React.useState(false)
  const [showSuggestions, setShowSuggestions] = React.useState(false)
  const [searchSubmitted, setSearchSubmitted] = React.useState(false)
  const [hoveredSuggestion, setHoveredSuggestion] = React.useState<number | null>(null)
  const [lastSearch, setLastSearch] = React.useState('')
  const [selectedClub, setSelectedClub] = React.useState<ClubOption | null>(null)

  const suggestions: ClubOption[] = [
    { id: 1, title: 'Option 1', desc: '', img: imglasta },
    { id: 2, title: 'Option 2', desc: '', img: imgkucica },
    { id: 3, title: 'Option 3', desc: '', img: zapp },
  ]
const clubDetails = {
  bg1: {
  1: {
    city: 'Belgrade',
    place: 'Blue Wave kafe restoran',
    area: 'Dorcol',
    day: 'Saturday',
    groupSize: 2,
    budget: 1,
    start_time: '20:00',
    end_time: '23:30',
    party_level: 1,
    vibe_tags: ['date', 'chill', 'quiet'],
    description: 'It was a low-key date in Dorcol (Belgrade), with wine and small plates in a cozy bar, followed by a short walk by the river before going home. There were 2 of us and the night lasted around 3.5 hours, with a date, chill, quiet vibe.',
    img: res4
  },
  2: {
    city: 'Belgrade',
    place: 'Baristocratia coffee',
    area: 'Vracar',
    day: 'Saturday',
    groupSize: 2,
    budget: 2,
    start_time: '19:30',
    end_time: '23:00',
    party_level: 1,
    vibe_tags: ['date', 'chill', 'fancy'],
    description: 'It was a quiet date in Vracar (Belgrade), starting with dinner at a small bistro and then a couple of cocktails at a stylish bar before heading home around 11pm. There were 2 of us and the night lasted about 3.5 hours, with a date, chill, fancy vibe.',
    img: res5
  },
  3: {
    city: 'Belgrade',
    place: 'Quens pub',
    area: 'Centar',
    day: 'Saturday',
    groupSize: 2,
    budget: 2,
    start_time: '20:30',
    end_time: '23:30',
    party_level: 2,
    vibe_tags: ['date', 'chill', 'quiet'],
    description: 'We spent a relaxed Friday evening in a rock bar in the center of Belgrade, mostly sitting and talking while a quieter band played in the background. There were 2 of us and the night lasted about 3.0 hours, with a rock, chill vibe.',
    img: res6
  }
},
  bg2: {
  1: {
    city: 'Belgrade',
    place: 'Dorcol Bar',
    area: 'Dorcol',
    day: 'Friday',
    groupSize: 5,
    budget: 2,
    description: 'We met in a small bar in Dorcol (Belgrade) around 10:30pm, then moved to a small underground techno club and stayed on the dance floor until about 3am. There were 5 of us and the whole night lasted around 4.5 hours, with a techno, student night, crowded vibe.',
    img: res11
  },
  2: {
    city: 'Belgrade',
    place: 'Pukni Zoro',
    area: 'Zemun',
    day: 'Friday',
    groupSize: 4,
    budget: 2,
    description: 'We celebrated a friend s birthday in a pub in Zemun (Belgrade), with a live band, rakija, and dancing on chairs until 2am. There were 4 of us and the night lasted about 5 hours, with a kafana, live music, birthday vibe.',
    
  },
  3: {
    city: 'Belgrade',
    place: 'BeerWood',
    area: 'Dorcol',
    day: 'Friday',
    groupSize: 4,
    budget: 1,
    description: 'We started the night in a pub in Dorcol (Belgrade) with beers and shots, then moved to a bar in the same area as the night got louder and more crowded. There were 4 of us and the night lasted about 2 hours, with a pub, crowded, student night vibe.',
    img: res13
  }
}
,
  'novi sad': {
  1: {
    city: 'Novi Sad',
    place: 'Dva Galeba',
    area: 'Limani',
    day: 'Friday',
    groupSize: 5,
    budget: 3,
    start_time: '23:00',
    end_time: '03:30',
    party_level: 3,
    vibe_tags: ['birthday', 'crowded'],
    description: 'On Friday nights, Limani comes alive, and the floating club Dva Galeba is a great spot to celebrate a birthday with a small group of friends. From 11 PM until the early hours, enjoy a mix of popular music and a lively crowd that adds to the energy.',
    img: res1
  },
  2: {
    city: 'Novi Sad',
    place: 'London Pub',
    area: 'Centar',
    day: 'Friday',
    groupSize: 5,
    budget: 2,
    start_time: '22:00',
    end_time: '02:30',
    party_level: 3,
    vibe_tags: ['crowded', 'rock'],
    description: 'We had a great Friday night in Center (Novi Sad), with beers, great EX-yu rock music, and nice people. Very energetic atmosphere, you must go sometimes there!',
    img: res2
  },
  3: {
    city: 'Novi Sad',
    place: 'Tata Brada',
    area: 'Centar',
    day: 'Friday',
    groupSize: 5,
    budget: 3,
    start_time: '22:30',
    end_time: '03:00',
    party_level: 3,
    vibe_tags: ['fancy', 'pub', 'crowded'],
    description: 'We went to a busy downtown pub in the center of Novi Sad for drinks and snacks, standing at the bar and chatting in a loud but friendly atmosphere. There were 5 of us and the night lasted around 4.0 hours, with a cool, pub, crowded vibe.',
    img: res3
  },
  4:{
   'mistake': {
  1: {
    city: 'Čačak',
    place: 'Njegovo',
    area: 'Center',
    day: 'Saturday',
    groupSize: 5,
    budget: 2,
    start_time: '22:00',
    end_time: '03:00',
    party_level: 4,
    vibe_tags: ['pop', 'crowded', 'casual'],
    description: 'We started the night in the city center of Čačak with drinks at a popular local bar, then moved to a lively club with pop music and dancing. There were 5 of us and the whole night lasted around 5 hours, with a pop, crowded, casual vibe.',
    
  },
  2: {
    city: 'Novi Sad',
    place: 'Tocionica',
    area: 'Limani',
    day: 'Thursday',
    groupSize: 4,
    budget: 2,
    start_time: '12:00',
    end_time: '15:00',
    party_level: 4,
    vibe_tags: ['techno', 'student night'],
    description: 'We met in a student bar in Limani (Novi Sad) a bit after 10pm and then moved to a small techno club popular with students, staying until around 2am. There were 4 of us and the whole night lasted about 4.0 hours, with a techno, student night vibe.',
    
  },
  3: {
    city: 'Niš',
    place: 'Pauza Cafe',
    area: 'Centar',
    day: 'Saturday',
    groupSize: 3,
}
}

}
    }    }
  const specialText =
    "I want to have fun in belgrade, me and 3 friends. We dont like alcohol that much, and we want to spend middle budget range. Today is friday, and we will go out about 22:00."

  const specialText2 = "I have 4 friends, and this friday we just finishedMe and girlfriend want to go out for a drink on saturday night but we dont have much money. It should be casual and romantic night out. year on college. We want to party tonight, and celebrate this. Suggest me any place, any budget, just long fun night"
  const specialText3 = ""
  const specialText4 = "where can I go out?"

  const secondDelay = '220ms'
  const thirdDelay = '360ms'

  React.useEffect(() => {
    if (query.trim().length > 0 && !searchSubmitted) {
      setShowSecond(false)
      setShowThird(false)
      const t = window.setTimeout(() => setShowSecond(true), 300)
      return () => window.clearTimeout(t)
    }

    if (!searchSubmitted) {
      setShowSecond(false)
      setShowThird(false)
    }
  }, [query, searchSubmitted])

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setShowThird(true)
    setLastSearch(query)
    setShowSuggestions(true)
    setSearchSubmitted(true)
  }

  return (
    <div className="gallery-page">
      <button className="gallery-back" onClick={onBack} aria-label="Back to home">← Back</button>
      <h2 className="gallery-title">Find your perfect night</h2>

      <div className="strip">
        <figure className={`strip-item visible`}>
          <img src={img1} alt="Night scene 1" />
          <figcaption>Crowd</figcaption>
        </figure>

        <div className={`connector connector-first`} aria-hidden>
          <svg className="connector-svg" viewBox="0 0 140 24" preserveAspectRatio="none">
            <defs>
              <linearGradient id="g-arrow-1" x1="0" x2="1">
                <stop offset="0" stopColor="#7C3AED" stopOpacity="0.95" />
                <stop offset="1" stopColor="#FF2D95" stopOpacity="0.95" />
              </linearGradient>
              <marker id="arrowhead-1" markerWidth="10" markerHeight="10" refX="10" refY="5" orient="auto">
                <path d="M0,0 L10,5 L0,10 z" fill="url(#g-arrow-1)" />
              </marker>
            </defs>
            <path d="M4 12 L136 12" stroke="url(#g-arrow-1)" strokeWidth="4" fill="none" markerEnd="url(#arrowhead-1)" strokeLinecap="round" />
          </svg>
        </div>

        <figure className={`strip-item ${showSecond ? 'visible' : 'hidden'}`} style={{ transitionDelay: showSecond ? secondDelay : '0ms' }}>
          <img src={img2} alt="Night scene 2" />
          <figcaption>Afterparty</figcaption>
        </figure>

        <div className={`connector ${showSecond ? 'active' : 'hidden'}`} aria-hidden style={{ transitionDelay: showSecond ? secondDelay : '0ms' }}>
          <svg className="connector-svg" viewBox="0 0 140 24" preserveAspectRatio="none">
            <defs>
              <linearGradient id="g-arrow-2" x1="0" x2="1">
                <stop offset="0" stopColor="#7C3AED" stopOpacity="0.95" />
                <stop offset="1" stopColor="#FF2D95" stopOpacity="0.95" />
              </linearGradient>
              <marker id="arrowhead-2" markerWidth="10" markerHeight="10" refX="10" refY="5" orient="auto">
                <path d="M0,0 L10,5 L0,10 z" fill="url(#g-arrow-2)" />
              </marker>
            </defs>
            <path d="M4 12 L136 12" stroke="url(#g-arrow-2)" strokeWidth="4" fill="none" markerEnd="url(#arrowhead-2)" strokeLinecap="round" />
          </svg>
        </div>

        <figure className={`strip-item ${showThird ? 'visible' : 'hidden'}`} style={{ transitionDelay: showThird ? thirdDelay : '0ms' }}>
          <img src={img3} alt="Night scene 3" />
          <figcaption>Vibe</figcaption>
        </figure>
      </div>

      <form className="gallery-input" onSubmit={handleSubmit}>
        <label className="input-window">
          <div className="input-label">Describe the night you expect</div>
          <textarea value={query} onChange={(e) => setQuery(e.target.value)} placeholder="E.g. lively crowd, techno, late afterparty..." rows={4} />
        </label>
        <div className="input-actions">
          <button type="submit" className="find-btn">Search</button>
        </div>
      </form>

      {showSuggestions && (
        <div className="suggestions-wrap">
          <ul className="suggestions" role="list">
            {suggestions.map((s, idx) => (
              <li
                key={s.id}
                className="suggestion-item"
                onMouseEnter={() => setHoveredSuggestion(idx)}
                onMouseLeave={() => setHoveredSuggestion(null)}
                onFocus={() => setHoveredSuggestion(idx)}
                onBlur={() => setHoveredSuggestion(null)}
                onClick={() => setSelectedClub(s)} // OVDE POSTAVLJAMO MODAL
              >
                {s.title}

                {hoveredSuggestion === idx && (
                  <div className="suggestion-card suggestion-card-large" role="note">
                    {lastSearch.trim().toLowerCase().includes("middle")  ? (
                      idx === 0 ? (
                        <>
                          <img src={imglasta} alt="Match preview" />
                          <div className="match-badge">Match 9/10</div>
                          <h4>Lasta</h4>
                          <p>{s.desc}</p>
                        </>
                      ) : idx === 1 ? (
                        <>
                          <img src={imgkucica} alt="Match preview" />
                          <div className="match-badge">Match 7/10</div>
                          <h4>Kucica</h4>
                          <p>{s.desc}</p>
                        </>
                      ) : (
                        <>
                          <img src={zapp} alt="Match preview" />
                          <div className="match-badge">Match 5/10</div>
                          <h4>Zapa barka</h4>
                          <p>{s.desc}</p>
                        </>
                      )
                    ) : lastSearch.trim().toLowerCase() .includes("college") ? (
                      idx === 0 ? (
                        <>
                          <img src={res1} alt="Match preview" />
                          <div className="match-badge">Match 8/10</div>
                          <h4>Dva galeba</h4>
                          <p>{s.desc}</p>
                        </>
                      ) : idx === 1 ? (
                        <>
                          <img src={res2} alt="Match preview" />
                          <div className="match-badge">Match 6/10</div>
                          <h4>London pub</h4>
                          <p>{s.desc}</p>
                        </>
                      ) : (
                        <>
                          <img src={res3} alt="Match preview" />
                          <div className="match-badge">Match 5/10</div>
                          <h4>Tata brada</h4>
                          <p>{s.desc}</p>
                        </>
                      )
                    ) : lastSearch.trim().toLowerCase().includes("girlfriend") ? (
                      idx === 0 ? (
                        <>
                          <img src={res4} alt="Match preview" />
                          <div className="match-badge">Match 10/10</div>
                          <h4>Blue wave restaurant</h4>
                          <p>{s.desc}</p>
                        </>
                      ) : idx === 1 ? (
                        <>
                          <img src={res5} alt="Match preview" />
                          <div className="match-badge">Match 8/10</div>
                          <h4>Baristocratia coffe</h4>
                          <p>{s.desc}</p>
                        </>
                      ) : (
                        <>
                          <img src={res6} alt="Match preview" />
                          <div className="match-badge">Match 7/10</div>
                          <h4>Queens pub</h4>
                          <p>{s.desc}</p>
                        </>
                      )
                    ) : lastSearch.trim().toLowerCase().includes("where can i go") ? (
                      idx === 0 ? (
                        <>
                          <img src={res11} alt="Match preview" />
                          <div className="match-badge">Match 8/10</div>
                          <h4>Dzon Beer</h4>
                          <p>{s.desc}</p>
                        </>
                      ) : idx === 1 ? (
                        <>
                          <img src={res12} alt="Match preview" />
                          <div className="match-badge">Match 8/10</div>
                          <h4>Kafic</h4>
                          <p>{s.desc}</p>
                        </>
                      ) : (
                        <>
                          <img src={res13} alt="Match preview" />
                          <div className="match-badge">Match 7/10</div>
                          <h4>Kafic2</h4>
                          <p>{s.desc}</p>
                        </>
                      )
                    ) : (
                      <>
                        <h4>{s.title}</h4>
                        <p>{s.desc}</p>
                      </>
                    )}
                  </div>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
 {/* MODAL ZA DETALJNE INFORMACIJE */}
{selectedClub && (
  <div
    onClick={() => setSelectedClub(null)}
    style={{
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100%',
      height: '100%',
      backgroundColor: 'rgba(0,0,0,0.85)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
    }}
  >
    <div
      onClick={(e) => e.stopPropagation()}
      style={{
        background: '#1f1f1f',
        color: '#f1f1f1',
        padding: '30px',
        borderRadius: '15px',
        maxWidth: '90%',
        width: '800px',
        textAlign: 'center',
        position: 'relative',
        boxShadow: '0 0 40px rgba(0,0,0,0.8)',
      }}
    >
      <button
        onClick={() => setSelectedClub(null)}
        style={{
          position: 'absolute',
          top: '10px',
          right: '20px',
          fontSize: '28px',
          background: 'none',
          border: 'none',
          color: '#f1f1f1',
          cursor: 'pointer',
        }}
      >
        ×
      </button>

      <h2 style={{ marginBottom: '20px' }}>{selectedClub.title}</h2>

      {/* Slika zavisi od grada i odabrane opcije */}
      <img
        src={
          lastSearch.trim().toLowerCase().includes('where can')
            ? selectedClub.id === 1
              ? res11
              : selectedClub.id === 2
              ? res12
              : res13
            : lastSearch.trim().toLowerCase().includes('girlfriend')
            ? selectedClub.id === 1
              ? res4
              : selectedClub.id === 2
              ? res5
              : res6
            : lastSearch.trim().toLowerCase().includes('college')
            ? selectedClub.id === 1
              ? res1
              : selectedClub.id === 2
              ? res2
              : res3
            : selectedClub.img
        }
        alt={selectedClub.title}
        style={{ width: '100%', maxWidth: '700px', margin: '20px 0', borderRadius: '10px' }}
      />

      <p style={{ marginBottom: '20px' }}>{selectedClub.desc}</p>

      {/* Detalji zavise od grada i opcije */}
      <ul style={{ textAlign: 'left', marginTop: '20px', lineHeight: '1.6' }}>
        {lastSearch.trim().toLowerCase().includes("where can") ? (
          <>

          <ul>
  <li>City: Čačak</li>
  <li>Place: Njegovo</li>
  <li>Area: Center</li>
  <li>Day: Saturday</li>
  <li>Group Size: 5</li>
  <li>Budget: 2</li>
  <li>Start Time: 22:00</li>
  <li>End Time: 03:00</li>
  <li>Party Level: 4</li>
  <li>Vibe Tags: pop, crowded, casual</li>
  <li>Description: We started the night in the city center of Čačak with drinks at a popular local bar, then moved to a lively club with pop music and dancing. There were 5 of us and the whole night lasted around 5 hours, with a pop, crowded, casual vibe.</li>
</ul>

   
          </>
        ) : lastSearch.trim().toLowerCase().includes("girlfriend") ? (
          <>
                 <ul>
  <li>City: Belgrade</li>
  <li>Place: Baristocratia coffee</li>
  <li>Area: Vracar</li>
  <li>Day: Saturday</li>
  <li>Group Size: 2</li>
  <li>Budget: 2</li>
  <li>Start Time: 19:30</li>
  <li>End Time: 23:00</li>
  <li>Party Level: 1</li>
  <li>Vibe Tags: date, chill, fancy</li>
  <li>Description: It was a quiet date in Vracar (Belgrade), starting with dinner at a small bistro and then a couple of cocktails at a stylish bar before heading home around 11pm. There were 2 of us and the night lasted about 3.5 hours, with a date, chill, fancy vibe.</li>
</ul>


          </>
        ) : lastSearch.trim().toLowerCase().includes('middle') ? (
          <>
            <ul>
                <li>City: Belgrade</li>
  <li>Zapa barka</li>
  <li>Area: Sajam</li>
  <li>Day: Saturday</li>
  <li>Group Size: 2</li>
  <li>Budget: 2</li>
  <li>Start Time: 19:30</li>
  <li>End Time: 23:00</li>
  <li>Party Level: 1</li>
  <li>Vibe Tags: date, chill, fancy</li>
  <li>We danced nonstop at a packed club, with booming music, flashing lights, and an electric crowd that kept the energy soaring all night long.</li>
</ul>
  

          </>
        ) : (
          <>
            <ul>
  <li>City: Novi Sad</li>
  <li>Place: Dva Galeba</li>
  <li>Area: Limani</li>
  <li>Day: Friday</li>
  <li>Group Size: 5</li>
  <li>Budget: 3</li>
  <li>Start Time: 23:00</li>
  <li>End Time: 03:30</li>
  <li>Party Level: 3</li>
  <li>Vibe Tags: birthday, crowded</li>
  <li>Description: On Friday nights, Limani comes alive, and the floating club Dva Galeba is a great spot to celebrate a birthday with a small group of friends. From 11 PM until the early hours, enjoy a mix of popular music and a lively crowd that adds to the energy.</li>
</ul>

          </>
        )}
      </ul>
    </div>
  </div>
)}


     
    </div>
  )
  }
