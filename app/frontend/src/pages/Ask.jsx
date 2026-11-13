import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search, Activity, Droplet, Heart, Moon,
  Loader2, Wind, Pill, ShieldCheck, Zap,
  Brain, Sparkles
} from 'lucide-react';
import { getSuggestions } from '../services/api';

/* ═══════════════════════════════════════════════
   MINI SVG CHART COMPONENTS
   ═══════════════════════════════════════════════ */

const DnaChart = () => (
  <svg viewBox="0 0 100 40" style={{ width: '100%', height: '48px' }}>
    <path className="chart-path" style={{ color: '#a855f7' }} d="M0 20 Q 25 -10, 50 20 T 100 20" />
    <path className="chart-path" style={{ color: '#f472b6' }} d="M0 20 Q 25 50, 50 20 T 100 20" />
    <circle cx="50" cy="20" r="4" fill="#7c3aed" />
  </svg>
);

const LineChart = () => (
  <svg viewBox="0 0 100 40" style={{ width: '100%', height: '48px' }}>
    <path className="chart-path" style={{ color: '#f43f5e' }} d="M0 30 Q 15 30, 25 15 T 45 35 T 60 10 T 80 25 T 100 20" />
    <circle cx="60" cy="10" r="3" fill="#f43f5e" />
  </svg>
);

const HeartChart = () => (
  <svg viewBox="0 0 100 40" style={{ width: '100%', height: '48px' }}>
    <path className="chart-path" style={{ color: '#ec4899' }} d="M0 20 L 20 20 L 30 5 L 45 35 L 55 10 L 65 25 L 80 20 L 100 20" />
    <path d="M0 40 L 0 20 L 20 20 L 30 5 L 45 35 L 55 10 L 65 25 L 80 20 L 100 20 L 100 40 Z" fill="rgba(236,72,153,0.08)" />
  </svg>
);

const BarChartMini = () => (
  <svg viewBox="0 0 100 40" style={{ width: '100%', height: '48px' }}>
    <rect x="8" y="22" width="6" height="18" rx="3" fill="rgba(96,165,250,0.4)" />
    <rect x="22" y="10" width="6" height="30" rx="3" fill="rgba(96,165,250,0.6)" />
    <rect x="36" y="26" width="6" height="14" rx="3" fill="rgba(96,165,250,0.3)" />
    <rect x="50" y="5" width="6" height="35" rx="3" fill="rgba(59,130,246,0.8)" />
    <rect x="64" y="16" width="6" height="24" rx="3" fill="rgba(96,165,250,0.5)" />
    <rect x="78" y="20" width="6" height="20" rx="3" fill="rgba(96,165,250,0.4)" />
  </svg>
);

const CircularProgress = ({ value = 64, color = '#3b82f6' }) => {
  const circumference = 2 * Math.PI * 28;
  const offset = circumference - (value / 100) * circumference;
  return (
    <div style={{ position: 'relative', width: '56px', height: '56px' }}>
      <svg width="56" height="56" style={{ transform: 'rotate(-90deg)' }}>
        <circle cx="28" cy="28" r="24" stroke="rgba(0,0,0,0.04)" strokeWidth="5" fill="none" />
        <circle cx="28" cy="28" r="24" stroke={color} strokeWidth="5" fill="none"
          strokeDasharray={2 * Math.PI * 24} strokeDashoffset={2 * Math.PI * 24 - (value / 100) * 2 * Math.PI * 24}
          strokeLinecap="round" />
      </svg>
      <span style={{
        position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)',
        fontSize: '11px', fontWeight: 800, color: 'var(--text)'
      }}>
        {value}%
      </span>
    </div>
  );
};

/* ═══════════════════════════════════════════════
   WIDGET CARD COMPONENT
   ═══════════════════════════════════════════════ */

function WidgetCard({ title, value, icon, chart, style }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="glass-widget"
      style={{ padding: '18px 20px', display: 'flex', flexDirection: 'column', gap: '8px', ...style }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <div style={{ color: 'var(--text-muted)', transition: 'transform 0.2s' }}>{icon}</div>
        <span style={{ fontSize: '10px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.12em', color: 'var(--text-muted)' }}>
          {title}
        </span>
      </div>
      {chart && <div style={{ flex: 1, display: 'flex', alignItems: 'center' }}>{chart}</div>}
      <p style={{ fontSize: '18px', fontWeight: 800, color: 'var(--text)', letterSpacing: '-0.02em', margin: 0 }}>
        {value}
      </p>
    </motion.div>
  );
}

/* ═══════════════════════════════════════════════
   QUICK TOPIC BUTTONS
   ═══════════════════════════════════════════════ */

const QUICK_TOPICS = [
  'Fever symptoms',
  'Blood pressure',
  'Diabetes management',
  'Heart health',
  'Sleep problems',
  'Headache causes',
];

/* ═══════════════════════════════════════════════
   MAIN ASK PAGE
   ═══════════════════════════════════════════════ */

export default function Ask() {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [loading, setLoading] = useState(false);
  const [activeSuggestionIdx, setActiveSuggestionIdx] = useState(-1);
  const navigate = useNavigate();
  const searchRef = useRef(null);
  const debounceRef = useRef(null);

  // Fetch suggestions on typing
  const fetchSuggestions = useCallback(async (q) => {
    if (q.trim().length < 2) {
      setSuggestions([]);
      return;
    }
    try {
      const results = await getSuggestions(q);
      setSuggestions(results);
    } catch {
      setSuggestions([]);
    }
  }, []);

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => fetchSuggestions(query), 250);
    return () => clearTimeout(debounceRef.current);
  }, [query, fetchSuggestions]);

  // Close suggestions on click outside
  useEffect(() => {
    const handler = (e) => {
      if (searchRef.current && !searchRef.current.contains(e.target)) {
        setShowSuggestions(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const handleSubmit = (e) => {
    e?.preventDefault();
    const q = query.trim();
    if (!q) return;
    setShowSuggestions(false);
    navigate('/answer', { state: { question: q } });
  };

  const handleSuggestionClick = (suggestion) => {
    setQuery(suggestion);
    setShowSuggestions(false);
    navigate('/answer', { state: { question: suggestion } });
  };

  const handleKeyDown = (e) => {
    if (!showSuggestions || suggestions.length === 0) return;
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setActiveSuggestionIdx(prev => Math.min(prev + 1, suggestions.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setActiveSuggestionIdx(prev => Math.max(prev - 1, -1));
    } else if (e.key === 'Enter' && activeSuggestionIdx >= 0) {
      e.preventDefault();
      handleSuggestionClick(suggestions[activeSuggestionIdx]);
    }
  };

  const handleQuickTopic = (topic) => {
    setQuery(topic);
    navigate('/answer', { state: { question: topic } });
  };

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', position: 'relative' }}>

      {/* ── Main Content Grid ── */}
      <div style={{
        flex: 1,
        display: 'grid',
        gridTemplateColumns: '1fr minmax(480px, 600px) 1fr',
        gap: '28px',
        alignItems: 'start',
        paddingTop: '16px',
      }}>

        {/* ── Left Widget Column ── */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', paddingTop: '80px' }}>
          <WidgetCard
            title="Sweating"
            value="Good"
            icon={<div style={{ display: 'flex', gap: '2px' }}><div style={{ width: 10, height: 10, borderRadius: '50%', background: '#a855f7' }} /><div style={{ width: 10, height: 10, borderRadius: '50%', background: '#f472b6' }} /></div>}
            chart={<DnaChart />}
          />
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <WidgetCard
              title="Blood"
              value="Normal"
              icon={<Droplet size={15} color="#f43f5e" fill="#f43f5e" />}
              chart={<LineChart />}
              style={{ gridColumn: 'span 2' }}
            />
            <WidgetCard
              title="Pills"
              value="3"
              icon={<Pill size={15} color="#f59e0b" />}
            />
            <WidgetCard
              title="Sports"
              value="2h"
              icon={<Zap size={15} color="#3b82f6" />}
              chart={<CircularProgress value={64} color="#3b82f6" />}
            />
          </div>
        </div>

        {/* ── Center Search Column ── */}
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'flex-start',
          paddingTop: '40px',
        }}>
          {/* Title */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            style={{ textAlign: 'center', marginBottom: '32px' }}
          >
            <h1 style={{
              fontSize: '2.6rem',
              lineHeight: 1.1,
              fontWeight: 800,
              color: 'var(--text)',
              letterSpacing: '-0.03em',
              margin: 0,
            }}>
              What's Up With Your Health,
            </h1>
            <h1 style={{
              fontSize: '3rem',
              fontWeight: 900,
              margin: '4px 0 0 0',
              background: 'linear-gradient(135deg, #7c3aed 0%, #ec4899 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              letterSpacing: '-0.03em',
            }}>
              TODAY! <span style={{ WebkitTextFillColor: 'initial' }}>🧬</span>
            </h1>
          </motion.div>

          {/* Brain Image */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            style={{ 
              position: 'relative', 
              width: '100%', 
              maxWidth: '500px', 
              height: '380px', 
              marginBottom: '16px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {/* Glow behind brain */}
            <div style={{
              position: 'absolute', top: '50%', left: '50%',
              transform: 'translate(-50%, -50%)',
              width: '280px', height: '280px',
              borderRadius: '50%',
              background: 'radial-gradient(circle, rgba(168,85,247,0.25) 0%, transparent 70%)',
              filter: 'blur(40px)',
            }} />
            <img
              src="/brain.jpg"
              alt="3D Brain visualization"
              className="animate-float"
              style={{
                width: '460px',
                height: 'auto',
                objectFit: 'contain',
                mixBlendMode: 'multiply',
                WebkitMaskImage: 'radial-gradient(circle at center, black 50%, transparent 75%)',
                maskImage: 'radial-gradient(circle at center, black 50%, transparent 75%)',
                filter: 'drop-shadow(0 20px 40px rgba(124,58,237,0.15))',
                pointerEvents: 'none',
                position: 'relative',
              }}
            />
          </motion.div>

          {/* Search Bar */}
          <motion.div
            ref={searchRef}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            style={{ width: '100%', maxWidth: '520px', position: 'relative', zIndex: 30 }}
          >
            <form onSubmit={handleSubmit}>
              <div
                className="search-glow"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  padding: '8px 8px 8px 22px',
                  borderRadius: '9999px',
                  background: 'rgba(255,255,255,0.55)',
                  backdropFilter: 'blur(30px)',
                  WebkitBackdropFilter: 'blur(30px)',
                  border: '1px solid rgba(255,255,255,0.7)',
                  boxShadow: 'var(--shadow-lg)',
                  transition: 'all 0.3s ease',
                }}
              >
                <Search size={20} strokeWidth={2.5} style={{ color: 'var(--primary)', marginRight: '12px', flexShrink: 0 }} />
                <input
                  type="text"
                  value={query}
                  onChange={(e) => {
                    setQuery(e.target.value);
                    setShowSuggestions(true);
                    setActiveSuggestionIdx(-1);
                  }}
                  onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
                  onKeyDown={handleKeyDown}
                  placeholder="Search or ask about your health..."
                  disabled={loading}
                  style={{
                    flex: 1,
                    background: 'transparent',
                    border: 'none',
                    outline: 'none',
                    color: 'var(--text)',
                    fontWeight: 600,
                    fontSize: '15px',
                    padding: '8px 0',
                  }}
                />
                <button
                  type="submit"
                  disabled={loading || !query.trim()}
                  style={{
                    width: '44px',
                    height: '44px',
                    borderRadius: '50%',
                    background: 'linear-gradient(135deg, #7c3aed, #ec4899)',
                    color: '#fff',
                    border: 'none',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    cursor: 'pointer',
                    boxShadow: '0 4px 16px rgba(124,58,237,0.3)',
                    transition: 'all 0.2s',
                    opacity: loading || !query.trim() ? 0.5 : 1,
                    marginLeft: '8px',
                    flexShrink: 0,
                  }}
                >
                  {loading
                    ? <Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} />
                    : <Search size={16} strokeWidth={3} />
                  }
                </button>
              </div>
            </form>

            {/* Autocomplete Suggestions Dropdown */}
            <AnimatePresence>
              {showSuggestions && suggestions.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: -4, scaleY: 0.95 }}
                  animate={{ opacity: 1, y: 0, scaleY: 1 }}
                  exit={{ opacity: 0, y: -4, scaleY: 0.95 }}
                  transition={{ duration: 0.2 }}
                  style={{
                    position: 'absolute',
                    top: 'calc(100% + 8px)',
                    left: 0,
                    right: 0,
                    background: 'rgba(255,255,255,0.92)',
                    backdropFilter: 'blur(30px)',
                    WebkitBackdropFilter: 'blur(30px)',
                    borderRadius: '20px',
                    border: '1px solid rgba(255,255,255,0.7)',
                    boxShadow: 'var(--shadow-xl)',
                    overflow: 'hidden',
                    zIndex: 50,
                    transformOrigin: 'top center',
                  }}
                >
                  <div style={{ padding: '8px' }}>
                    <div style={{
                      padding: '6px 14px',
                      fontSize: '10px',
                      fontWeight: 700,
                      textTransform: 'uppercase',
                      letterSpacing: '0.1em',
                      color: 'var(--text-muted)',
                    }}>
                      Suggestions from dataset
                    </div>
                    {suggestions.map((s, i) => (
                      <div
                        key={i}
                        onClick={() => handleSuggestionClick(s)}
                        style={{
                          padding: '10px 14px',
                          fontSize: '13px',
                          fontWeight: 500,
                          color: 'var(--text-secondary)',
                          borderRadius: '12px',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '10px',
                          background: i === activeSuggestionIdx ? 'rgba(124,58,237,0.06)' : 'transparent',
                          transition: 'background 0.15s',
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.background = 'rgba(124,58,237,0.06)';
                          setActiveSuggestionIdx(i);
                        }}
                        onMouseLeave={(e) => {
                          if (i !== activeSuggestionIdx) e.currentTarget.style.background = 'transparent';
                        }}
                      >
                        <Search size={14} style={{ color: 'var(--primary)', flexShrink: 0, opacity: 0.5 }} />
                        <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{s}</span>
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>

          {/* Quick Topics */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6, duration: 0.5 }}
            style={{
              display: 'flex',
              flexWrap: 'wrap',
              gap: '8px',
              justifyContent: 'center',
              marginTop: '20px',
              maxWidth: '520px',
            }}
          >
            {QUICK_TOPICS.map((topic) => (
              <button
                key={topic}
                onClick={() => handleQuickTopic(topic)}
                style={{
                  padding: '6px 14px',
                  borderRadius: '9999px',
                  background: 'rgba(255,255,255,0.5)',
                  backdropFilter: 'blur(10px)',
                  border: '1px solid rgba(255,255,255,0.6)',
                  fontSize: '12px',
                  fontWeight: 600,
                  color: 'var(--text-muted)',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(124,58,237,0.08)';
                  e.currentTarget.style.color = 'var(--primary)';
                  e.currentTarget.style.borderColor = 'rgba(124,58,237,0.2)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'rgba(255,255,255,0.5)';
                  e.currentTarget.style.color = 'var(--text-muted)';
                  e.currentTarget.style.borderColor = 'rgba(255,255,255,0.6)';
                }}
              >
                {topic}
              </button>
            ))}
          </motion.div>
        </div>

        {/* ── Right Widget Column ── */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', paddingTop: '80px' }}>
          <WidgetCard
            title="Breath Activity"
            value="Normal"
            icon={<Wind size={15} color="#14b8a6" />}
          />
          <WidgetCard
            title="Sleep"
            value="7:45h"
            icon={<Moon size={15} color="#6366f1" fill="#6366f1" />}
            chart={<BarChartMini />}
          />
          <WidgetCard
            title="Heart Activity"
            value="84 bpm"
            icon={<Heart size={15} color="#ec4899" fill="#ec4899" />}
            chart={<HeartChart />}
          />
          <div
            className="glass-widget"
            style={{
              padding: '16px 20px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              cursor: 'pointer',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <ShieldCheck size={18} color="#10b981" />
              <div>
                <p style={{ fontSize: '10px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--text-muted)', margin: 0 }}>All Activity</p>
                <p style={{ fontSize: '14px', fontWeight: 800, color: 'var(--text)', margin: 0 }}>Best Performance</p>
              </div>
            </div>
            <div style={{
              width: '28px', height: '28px', borderRadius: '50%',
              background: 'rgba(0,0,0,0.03)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              color: 'var(--text-muted)', fontSize: '14px',
            }}>
              →
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
