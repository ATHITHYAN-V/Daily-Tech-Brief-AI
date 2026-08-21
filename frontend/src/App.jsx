import { useState, useEffect, useRef } from 'react'
import './index.css'

// ── Icons (compact) ──────────────────────────────────────
const I = {
  Play: () => <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>,
  Pause: () => <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>,
  Link: () => <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>,
  Cal: () => <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>,
  Clock: () => <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>,
  Globe: () => <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>,
  Spin: () => <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><line x1="12" y1="2" x2="12" y2="6"/><line x1="12" y1="18" x2="12" y2="22"/><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/><line x1="2" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="22" y2="12"/><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/></svg>,
  Bot: () => <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="12" cy="5" r="2"/><path d="M12 7v4"/><line x1="8" y1="16" x2="8" y2="16"/><line x1="16" y1="16" x2="16" y2="16"/></svg>,
  Warn: () => <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>,
  Refresh: () => <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>,
  Zap: () => <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>,
  Shield: () => <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>,
  Star: () => <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>,
  News: () => <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"/><path d="M18 14h-8"/><path d="M15 18h-5"/><path d="M10 6h8v4h-8V6Z"/></svg>,
}

function catClass(cat = '') {
  const c = cat.toLowerCase()
  if (c.includes('ai') || c.includes('machine') || c.includes('model')) return 'cat-ai'
  if (c.includes('cloud') || c.includes('aws') || c.includes('azure')) return 'cat-cloud'
  if (c.includes('security') || c.includes('privacy')) return 'cat-sec'
  if (c.includes('hardware') || c.includes('chip')) return 'cat-hw'
  return 'cat-def'
}

// ── Kiro-style animated logo ─────────────────────────────
function KiroLogo({ active }) {
  return (
    <div className={`kiro ${active ? 'active' : ''}`}>
      <div className="kiro-ring kiro-r1" />
      <div className="kiro-ring kiro-r2" />
      <div className="kiro-ring kiro-r3" />
      <div className="kiro-core">
        <div className="kiro-inner" />
      </div>
      <div className="kiro-dot kiro-d1" />
      <div className="kiro-dot kiro-d2" />
      <div className="kiro-dot kiro-d3" />
    </div>
  )
}

// ── Audio Player ─────────────────────────────────────────
function AudioPlayer({ src, storiesCount, onPlayState }) {
  const ref = useRef(null)
  const [playing, setPlaying] = useState(false)
  const [prog, setProg] = useState(0)
  const [cur, setCur] = useState(0)
  const [dur, setDur] = useState(0)
  const [spd, setSpd] = useState(1)

  const toggle = () => {
    if (!ref.current) return
    playing ? ref.current.pause() : ref.current.play()
    const n = !playing; setPlaying(n); onPlayState?.(n)
  }

  const onTime = () => { const c = ref.current.currentTime, d = ref.current.duration || 0; setCur(c); setProg(d ? (c/d)*100 : 0) }
  const seek = e => { const r = e.currentTarget.getBoundingClientRect(); ref.current.currentTime = ((e.clientX - r.left) / r.width) * (ref.current.duration || 0) }
  const nextSpd = () => { const n = spd === 1 ? 1.25 : spd === 1.25 ? 1.5 : spd === 1.5 ? 2 : 1; setSpd(n); ref.current.playbackRate = n }
  const fmt = t => (!t || isNaN(t)) ? '0:00' : `${Math.floor(t/60)}:${String(Math.floor(t%60)).padStart(2,'0')}`

  return (
    <div className="player">
      <div className="player-top">
        <KiroLogo active={playing} />
        <div className="player-info">
          <div className="player-label">
            <span className="pl-title">TODAY'S BRIEFING</span>
            {playing && <span className="on-air"><span className="oa-dot"/>ON AIR</span>}
          </div>
          <span className="pl-meta">{storiesCount} stories · {fmt(dur)}</span>
        </div>
      </div>

      <div className="player-ctrls">
        <button className="play-btn" onClick={toggle} id="play-pause-btn">
          {playing ? <I.Pause /> : <I.Play />}
        </button>
        <div className="prog-wrap">
          <div className="prog-track" onClick={seek}>
            <div className="prog-fill" style={{ width: `${prog}%` }} />
          </div>
          <div className="prog-time"><span>{fmt(cur)}</span><span>{fmt(dur)}</span></div>
        </div>
        <button className="spd-btn" onClick={nextSpd} id="speed-btn">{spd}×</button>
      </div>

      <audio ref={ref} src={src} onTimeUpdate={onTime}
        onLoadedMetadata={() => setDur(ref.current.duration)}
        onEnded={() => { setPlaying(false); onPlayState?.(false) }}
      />
    </div>
  )
}

// ── Sidebar ──────────────────────────────────────────────
function Sidebar({ stories, active, onPick }) {
  return (
    <aside className="sidebar">
      <div className="sb-hdr"><I.News /> TOP STORIES</div>
      <ul className="sb-list">
        {stories.map((s, i) => (
          <li key={i} className={`sb-item ${i === active ? 'on' : ''}`} onClick={() => onPick(i)} id={`sb-${i+1}`}>
            <span className="sb-num">{String(i+1).padStart(2,'0')}</span>
            <span className="sb-text">{s.headline}</span>
          </li>
        ))}
      </ul>
    </aside>
  )
}

// ── Story Card ───────────────────────────────────────────
function Card({ story, idx, on, cRef }) {
  return (
    <article className={`card ${on ? 'card-on' : ''}`} ref={cRef} style={{ animationDelay: `${idx * 0.06}s` }} id={`story-${idx+1}`}>
      <div className="c-top">
        <span className="c-rank">{String(idx+1).padStart(2,'0')}</span>
        <span className={`c-cat ${catClass(story.category)}`}>{story.category}</span>
        {story.importance_score > 0 && (
          <span className="c-imp"><span className="c-imp-bar" style={{width:`${story.importance_score}%`}}/>{story.importance_score}</span>
        )}
      </div>
      <h3 className="c-hl">{story.headline}</h3>
      <p className="c-why">{story.why_it_matters}</p>
      <div className="c-foot">
        <span className="c-src"><I.Globe />{story.source}</span>
        <a href={story.url} target="_blank" rel="noopener noreferrer" className="c-link" id={`link-${idx+1}`}>Read original <I.Link /></a>
      </div>
    </article>
  )
}

// ── App ──────────────────────────────────────────────────
export default function App() {
  const [status, setStatus] = useState('LOADING')
  const [latest, setLatest] = useState(null)
  const [stories, setStories] = useState([])
  const [playing, setPlaying] = useState(false)
  const [active, setActive] = useState(0)
  const refs = useRef([])

  useEffect(() => {
    (async () => {
      const base = import.meta.env.VITE_S3_BASE_URL || ''
      try {
        const r = await fetch(`${base}/latest.json`)
        if (r.status === 404 || r.status === 403) { setStatus('NO_EPISODE'); return }
        if (!r.ok) throw new Error()
        const d = await r.json()
        if (!d?.date || !d?.audio || !d?.stories) { setStatus('NO_EPISODE'); return }
        const sr = await fetch(`${base}/${d.stories}`)
        if (!sr.ok) { setStatus('NO_EPISODE'); return }
        const sd = await sr.json()
        if (!sd?.stories) { setStatus('NO_EPISODE'); return }
        setLatest(d); setStories(sd.stories); setStatus('READY')
      } catch { setStatus('ERROR') }
    })()
  }, [])

  const pick = i => { setActive(i); refs.current[i]?.scrollIntoView({ behavior: 'smooth', block: 'center' }) }
  const base = import.meta.env.VITE_S3_BASE_URL || ''
  const fmtD = d => { try { return new Date(d+'T12:00:00Z').toLocaleDateString('en-US',{weekday:'long',year:'numeric',month:'long',day:'numeric'}) } catch { return d } }

  return (
    <div className="root">
      {/* Header */}
      <header className="hdr">
        <h1 className="hdr-t">Daily Tech Brief</h1>
        <p className="hdr-sub">While you were away, technology changed.</p>
        {status === 'READY' && latest && <div className="hdr-date"><I.Cal />{fmtD(latest.date)}</div>}
      </header>

      {/* States */}
      {status === 'LOADING' && (
        <div className="state"><div className="st-ico loading"><I.Spin /></div><h2>Tuning in…</h2><p>Checking for today's briefing.</p></div>
      )}
      {status === 'NO_EPISODE' && (
        <div className="state">
          <div className="st-ico waiting"><I.Bot /></div>
          <h2>Today's briefing is being prepared.</h2>
          <p>Our AI editor scans 9 sources, curates Top 10 stories, writes the script and generates audio — hands-free.</p>
          <div className="pills"><span className="pill"><I.Zap />No signup</span><span className="pill"><I.Shield />No login</span><span className="pill"><I.Star />Free</span></div>
          <div className="badge-g"><span className="p-dot"/>Agent is active</div>
          <div className="sch"><I.Clock />Next: 06:00 UTC daily</div>
        </div>
      )}
      {status === 'ERROR' && (
        <div className="state"><div className="st-ico err"><I.Warn /></div><h2>Couldn't reach today's briefing.</h2><p>Please try again shortly.</p><button className="retry" onClick={() => window.location.reload()}><I.Refresh />Try Again</button></div>
      )}

      {/* Main content */}
      {status === 'READY' && latest && (
        <div className="layout">
          <Sidebar stories={stories} active={active} onPick={pick} />
          <div className="main">
            <AudioPlayer src={`${base}/${latest.audio}`} storiesCount={stories.length} onPlayState={setPlaying} />
            <div className="sec-hdr"><I.News />TODAY'S TOP STORIES<span className="sec-count">{stories.length}</span></div>
            <div className="cards">
              {stories.map((s, i) => <Card key={i} story={s} idx={i} on={i === active} cRef={el => refs.current[i] = el} />)}
            </div>
          </div>
        </div>
      )}

      <footer className="ftr">Generated autonomously at 06:00 UTC · Powered by Amazon Nova Pro &amp; Polly</footer>
    </div>
  )
}
