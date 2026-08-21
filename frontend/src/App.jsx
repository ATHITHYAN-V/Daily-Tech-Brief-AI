import { useState, useEffect, useRef } from 'react'

const AudioPlayer = ({ src, date, storiesCount }) => {
  const audioRef = useRef(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [progress, setProgress] = useState(0)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [playbackRate, setPlaybackRate] = useState(1)

  const togglePlay = () => {
    if (isPlaying) {
      audioRef.current.pause()
    } else {
      audioRef.current.play()
    }
    setIsPlaying(!isPlaying)
  }

  const handleTimeUpdate = () => {
    const current = audioRef.current.currentTime
    const dur = audioRef.current.duration
    setCurrentTime(current)
    setProgress((current / dur) * 100 || 0)
  }

  const handleLoadedMetadata = () => {
    setDuration(audioRef.current.duration)
  }

  const handleProgressClick = (e) => {
    const bar = e.currentTarget
    const rect = bar.getBoundingClientRect()
    const percent = (e.clientX - rect.left) / rect.width
    audioRef.current.currentTime = percent * audioRef.current.duration
  }

  const toggleSpeed = () => {
    const nextSpeed = playbackRate === 1 ? 1.25 : playbackRate === 1.25 ? 1.5 : 1
    setPlaybackRate(nextSpeed)
    audioRef.current.playbackRate = nextSpeed
  }

  const formatTime = (time) => {
    if (!time || isNaN(time)) return "00:00"
    const mins = Math.floor(time / 60)
    const secs = Math.floor(time % 60)
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="player-container fade-in">
      <div className="player-header">
        <div className="player-title">
          <span>🎙️</span> TODAY'S BRIEFING
        </div>
        <div className="player-stats">
          {formatTime(duration)} · {storiesCount} stories
        </div>
      </div>
      
      <div className="audio-controls">
        <button className="play-btn" onClick={togglePlay}>
          {isPlaying ? (
            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
              <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
            </svg>
          ) : (
            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" style={{marginLeft: '4px'}}>
              <path d="M8 5v14l11-7z"/>
            </svg>
          )}
        </button>
        
        <div className="progress-bar-container" onClick={handleProgressClick}>
          <div className="progress-bar" style={{ width: `${progress}%` }}></div>
        </div>
        
        <div className="time-display">
          {formatTime(currentTime)}
        </div>

        <button className="playback-rate" onClick={toggleSpeed}>
          {playbackRate}x
        </button>
      </div>
      
      <audio 
        ref={audioRef} 
        src={src} 
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onEnded={() => setIsPlaying(false)}
      />
    </div>
  )
}

function App() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [latest, setLatest] = useState(null)
  const [stories, setStories] = useState([])

  useEffect(() => {
    // Determine base URL depending on if we are running locally or deployed.
    // In production (Amplify), the S3 bucket URL should be configured via env var or CORS proxy.
    // For local demo, we fetch from the public folder.
    const baseUrl = import.meta.env.VITE_S3_BASE_URL || ''

    fetch(`${baseUrl}/latest.json`)
      .then(res => {
        if (!res.ok) throw new Error("Could not find latest episode.")
        return res.json()
      })
      .then(data => {
        setLatest(data)
        return fetch(`${baseUrl}/${data.stories}`)
      })
      .then(res => res.json())
      .then(storiesData => {
        setStories(storiesData.stories || [])
        setLoading(false)
      })
      .catch(err => {
        console.error(err)
        setError("Failed to load today's briefing. Please try again later.")
        setLoading(false)
      })
  }, [])

  if (loading) {
    return <div className="loading-spinner"></div>
  }

  if (error) {
    return <div className="error-message">{error}</div>
  }

  const baseUrl = import.meta.env.VITE_S3_BASE_URL || ''

  return (
    <>
      <header className="header fade-in">
        <h1>DAILY TECH BRIEF</h1>
        <div className="tagline">While you were away, technology changed.</div>
        <div className="date">{new Date(latest.date).toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</div>
      </header>

      <main>
        {latest.audio ? (
          <AudioPlayer src={`${baseUrl}/${latest.audio}`} date={latest.date} storiesCount={stories.length} />
        ) : (
          <div className="error-message">Audio briefing is unavailable for today.</div>
        )}

        <div className="stories-section">
          <div className="section-title" style={{marginTop: '2rem'}}>
            TODAY'S TOP STORIES
          </div>
          
          {stories.map((story, idx) => (
            <div key={idx} className="story-card fade-in" style={{animationDelay: `${0.1 * (idx + 1)}s`}}>
              <div className="story-header">
                <span className="story-rank">{(idx + 1).toString().padStart(2, '0')}</span>
                <span className="story-category">{story.category}</span>
              </div>
              <div className="story-title">{story.headline}</div>
              <div className="story-why">{story.why_it_matters}</div>
              <div className="story-source">
                <span>Source: {story.source}</span>
                <a href={story.url} target="_blank" rel="noopener noreferrer" className="story-link">Read original →</a>
              </div>
            </div>
          ))}
        </div>
      </main>

      <footer className="footer fade-in">
        Generated automatically at 06:00 UTC<br/>
        An autonomous AI radio station built for the AWS Builder Challenge.
      </footer>
    </>
  )
}

export default App
