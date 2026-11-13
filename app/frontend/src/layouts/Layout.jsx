import { NavLink, Outlet, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search, Heart, Layers, BarChart3, Info,
  Sparkles, ChevronRight
} from 'lucide-react';

const NAV_LINKS = [
  { path: '/', label: 'Ask', icon: Search },
  { path: '/explore', label: 'Explore', icon: Heart },
  { path: '/how-it-works', label: 'Pipeline', icon: Layers },
  { path: '/research', label: 'Research', icon: BarChart3 },
  { path: '/about', label: 'About', icon: Info },
];

function Sidebar() {
  return (
    <aside
      style={{
        position: 'fixed',
        left: 0,
        top: 0,
        bottom: 0,
        width: '88px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        paddingTop: '28px',
        paddingBottom: '28px',
        zIndex: 50,
      }}
    >
      {/* Brand Logo */}
      <NavLink
        to="/"
        style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px', marginBottom: '40px', textDecoration: 'none' }}
      >
        <div
          style={{
            width: '52px',
            height: '52px',
            borderRadius: '18px',
            background: 'linear-gradient(135deg, #7c3aed 0%, #a855f7 50%, #c084fc 100%)',
            boxShadow: '0 8px 24px rgba(124, 58, 237, 0.3)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'transform 0.2s',
          }}
        >
          <Sparkles size={24} color="#fff" strokeWidth={2.5} />
        </div>
        <span
          style={{
            fontSize: '9px',
            fontWeight: 800,
            letterSpacing: '0.15em',
            color: 'var(--text-muted)',
            textTransform: 'uppercase',
            textAlign: 'center',
            lineHeight: 1.3,
          }}
        >
          Medi<br />RAG
        </span>
      </NavLink>

      {/* Navigation */}
      <nav style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '4px', width: '100%', alignItems: 'center' }}>
        {NAV_LINKS.map((link) => (
          <NavLink
            key={link.path}
            to={link.path}
            end={link.path === '/'}
            style={{ textDecoration: 'none', display: 'block' }}
          >
            {({ isActive }) => (
              <div
                style={{
                  width: '64px',
                  height: '56px',
                  borderRadius: '16px',
                  background: isActive
                    ? 'rgba(255,255,255,0.6)'
                    : 'transparent',
                  backdropFilter: isActive ? 'blur(12px)' : 'none',
                  boxShadow: isActive ? 'var(--shadow-md)' : 'none',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '3px',
                  cursor: 'pointer',
                  position: 'relative',
                  transition: 'all 0.25s ease',
                }}
              >
                <link.icon
                  size={20}
                  strokeWidth={2.2}
                  style={{
                    color: isActive ? 'var(--primary)' : 'var(--text-muted)',
                    transition: 'color 0.2s',
                  }}
                />
                <span
                  style={{
                    fontSize: '9px',
                    fontWeight: 700,
                    color: isActive ? 'var(--primary)' : 'var(--text-muted)',
                    letterSpacing: '0.04em',
                    transition: 'color 0.2s',
                  }}
                >
                  {link.label}
                </span>
                {isActive && (
                  <motion.div
                    layoutId="nav-indicator"
                    style={{
                      position: 'absolute',
                      right: '-4px',
                      top: '50%',
                      transform: 'translateY(-50%)',
                      width: '4px',
                      height: '20px',
                      borderRadius: '4px',
                      background: 'var(--primary)',
                    }}
                    transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                  />
                )}
              </div>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Bottom */}
      <div
        style={{
          width: '36px',
          height: '36px',
          borderRadius: '12px',
          background: 'rgba(255,255,255,0.3)',
          backdropFilter: 'blur(10px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <ChevronRight size={16} style={{ color: 'var(--text-muted)' }} />
      </div>
    </aside>
  );
}

const pageVariants = {
  initial: { opacity: 0, y: 12 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -8 },
};

export default function Layout() {
  const location = useLocation();

  return (
    <div style={{ position: 'relative', minHeight: '100vh', overflow: 'hidden' }}>

      {/* ════════════════════════════════════════════
           FULL-VIEWPORT AMBIENT ORBS
           Spread edge-to-edge, large viewport-relative sizes,
           vivid colors — NOT contained in any box.
           ════════════════════════════════════════════ */}
      <div style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        pointerEvents: 'none',
        zIndex: 1,
      }}>
        {/* ── Large center-left purple wash ── */}
        <div
          className="animate-pulse-glow"
          style={{
            position: 'absolute',
            top: '-20%',
            left: '-10%',
            width: '70vw',
            height: '70vh',
            borderRadius: '50%',
            background: 'radial-gradient(ellipse, rgba(168,85,247,0.25) 0%, rgba(139,92,246,0.08) 40%, transparent 70%)',
            filter: 'blur(60px)',
          }}
        />

        {/* ── Right pink blob — bleeds off screen ── */}
        <div
          className="animate-pulse-glow"
          style={{
            position: 'absolute',
            top: '10%',
            right: '-15%',
            width: '65vw',
            height: '65vh',
            borderRadius: '50%',
            background: 'radial-gradient(ellipse, rgba(244,114,182,0.22) 0%, rgba(251,113,133,0.06) 45%, transparent 70%)',
            filter: 'blur(70px)',
            animationDelay: '1.5s',
          }}
        />

        {/* ── Bottom center blue spread ── */}
        <div
          className="animate-pulse-glow"
          style={{
            position: 'absolute',
            bottom: '-25%',
            left: '10%',
            width: '80vw',
            height: '60vh',
            borderRadius: '50%',
            background: 'radial-gradient(ellipse, rgba(96,165,250,0.18) 0%, rgba(59,130,246,0.04) 45%, transparent 70%)',
            filter: 'blur(80px)',
            animationDelay: '3s',
          }}
        />

        {/* ── Center teal accent ── */}
        <div
          className="animate-pulse-glow"
          style={{
            position: 'absolute',
            top: '45%',
            left: '45%',
            width: '40vw',
            height: '40vh',
            borderRadius: '50%',
            background: 'radial-gradient(ellipse, rgba(20,184,166,0.12) 0%, transparent 60%)',
            filter: 'blur(50px)',
            animationDelay: '2s',
          }}
        />

        {/* ── Top center warm subtle orb ── */}
        <div
          style={{
            position: 'absolute',
            top: '0%',
            left: '30%',
            width: '50vw',
            height: '35vh',
            borderRadius: '50%',
            background: 'radial-gradient(ellipse, rgba(251,191,36,0.08) 0%, transparent 60%)',
            filter: 'blur(50px)',
          }}
        />

        {/* ── Bottom-right lavender accent ── */}
        <div
          className="animate-pulse-glow"
          style={{
            position: 'absolute',
            bottom: '5%',
            right: '5%',
            width: '35vw',
            height: '35vh',
            borderRadius: '50%',
            background: 'radial-gradient(ellipse, rgba(167,139,250,0.15) 0%, transparent 60%)',
            filter: 'blur(50px)',
            animationDelay: '4s',
          }}
        />

        {/* ── Floating decorative sphere — top right ── */}
        <div
          className="animate-float"
          style={{
            position: 'absolute',
            top: '8%',
            right: '18%',
            width: '18px',
            height: '18px',
            borderRadius: '50%',
            background: 'linear-gradient(135deg, rgba(255,255,255,0.8), rgba(168,85,247,0.2))',
            boxShadow: '0 4px 12px rgba(0,0,0,0.06)',
          }}
        />

        {/* ── Floating sphere — center left ── */}
        <div
          className="animate-float"
          style={{
            position: 'absolute',
            top: '50%',
            left: '12%',
            width: '12px',
            height: '12px',
            borderRadius: '50%',
            background: 'linear-gradient(135deg, rgba(255,255,255,0.7), rgba(244,114,182,0.25))',
            boxShadow: '0 4px 12px rgba(0,0,0,0.04)',
            animationDelay: '2s',
          }}
        />

        {/* ── Floating sphere — bottom center ── */}
        <div
          className="animate-float"
          style={{
            position: 'absolute',
            bottom: '15%',
            left: '55%',
            width: '14px',
            height: '14px',
            borderRadius: '50%',
            background: 'linear-gradient(135deg, rgba(255,255,255,0.8), rgba(96,165,250,0.25))',
            boxShadow: '0 4px 12px rgba(0,0,0,0.04)',
            animationDelay: '4s',
          }}
        />
      </div>

      <Sidebar />

      {/* Main — open, flowing, no boxy container */}
      <main
        style={{
          marginLeft: '88px',
          position: 'relative',
          zIndex: 10,
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <div
          style={{
            flex: 1,
            padding: '24px 40px 40px',
            width: '100%',
            maxWidth: '1500px',
            margin: '0 auto',
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              variants={pageVariants}
              initial="initial"
              animate="animate"
              exit="exit"
              transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
              style={{ flex: 1, display: 'flex', flexDirection: 'column' }}
            >
              <Outlet />
            </motion.div>
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
}
