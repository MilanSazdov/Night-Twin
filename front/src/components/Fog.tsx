import smokeVideo from '../assets/Smoke_43___4K_res.mp4'

export default function Fog() {
  return (
    <div className="fog" aria-hidden>
      <video className="fog-video" src={smokeVideo} autoPlay muted loop playsInline />
      <div className="fog-layer l1" />
      <div className="fog-layer l2" />
      <div className="fog-layer l3" />
    </div>
  )
}
