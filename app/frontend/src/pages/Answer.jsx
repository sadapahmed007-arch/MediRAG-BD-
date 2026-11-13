import { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search, ArrowLeft, CheckCircle2, Loader2,
  Activity, Globe, Tag, Shield, Clock,
  FileText, ExternalLink, ChevronRight,
  Sparkles, AlertTriangle, Brain
} from 'lucide-react';
import { askQuestion } from '../services/api';

/* ═══════════════════════════════════════════════
   PROCESSING STAGE INDICATOR
   ═══════════════════════════════════════════════ */

function PipelineStages({ stages, isComplete }) {
  return (
    <div style={{
      display: 'flex',
      flexWrap: 'wrap',
      gap: '8px',
      justifyContent: 'center',
      marginBottom: '24px',
    }}>
      {stages.map((stage, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: i * 0.1, duration: 0.3 }}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '6px 12px',
            borderRadius: '9999px',
            background: stage.status === 'done'
              ? 'rgba(16,185,129,0.08)'
              : 'rgba(124,58,237,0.06)',
            border: `1px solid ${stage.status === 'done' ? 'rgba(16,185,129,0.15)' : 'rgba(124,58,237,0.1)'}`,
            fontSize: '11px',
            fontWeight: 600,
            color: stage.status === 'done' ? '#059669' : 'var(--primary)',
          }}
        >
          {stage.status === 'done'
            ? <CheckCircle2 size={12} />
            : <Loader2 size={12} style={{ animation: 'spin 1s linear infinite' }} />
          }
          <span>{stage.stage}</span>
          {stage.detail && (
            <span style={{
              padding: '1px 6px',
              borderRadius: '6px',
              background: 'rgba(0,0,0,0.04)',
              fontSize: '10px',
              fontWeight: 700,
              color: 'var(--text-muted)',
            }}>
              {stage.detail}
            </span>
          )}
        </motion.div>
      ))}
    </div>
  );
}

/* ═══════════════════════════════════════════════
   META BADGE
   ═══════════════════════════════════════════════ */

function MetaBadge({ icon: Icon, label, value, color }) {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      padding: '8px 14px',
      borderRadius: '14px',
      background: `${color}08`,
      border: `1px solid ${color}18`,
    }}>
      <Icon size={14} style={{ color }} />
      <div>
        <div style={{ fontSize: '9px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-muted)' }}>
          {label}
        </div>
        <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text)' }}>
          {value}
        </div>
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════
   RELATED QUESTION CARD
   ═══════════════════════════════════════════════ */

function RelatedCard({ question, topic, score, onClick }) {
  return (
    <motion.div
      whileHover={{ y: -2 }}
      onClick={onClick}
      style={{
        padding: '16px 20px',
        borderRadius: '18px',
        background: 'rgba(255,255,255,0.6)',
        backdropFilter: 'blur(16px)',
        border: '1px solid rgba(255,255,255,0.7)',
        boxShadow: 'var(--shadow-sm)',
        cursor: 'pointer',
        transition: 'all 0.25s',
        display: 'flex',
        alignItems: 'flex-start',
        gap: '12px',
      }}
    >
      <div style={{
        width: '32px', height: '32px', borderRadius: '10px',
        background: 'var(--primary-light)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        flexShrink: 0,
      }}>
        <Search size={14} style={{ color: 'var(--primary)' }} />
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <p style={{
          fontSize: '13px', fontWeight: 600, color: 'var(--text)',
          margin: 0, lineHeight: 1.5,
          display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical',
          overflow: 'hidden',
        }}>
          {question}
        </p>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '6px' }}>
          {topic && (
            <span style={{
              fontSize: '10px', fontWeight: 700, padding: '2px 8px',
              borderRadius: '6px', background: 'var(--accent-teal-light)',
              color: 'var(--accent-teal)',
            }}>
              {topic}
            </span>
          )}
          <span style={{ fontSize: '10px', fontWeight: 600, color: 'var(--text-muted)' }}>
            {(score * 100).toFixed(1)}% match
          </span>
        </div>
      </div>
      <ChevronRight size={16} style={{ color: 'var(--text-muted)', flexShrink: 0, marginTop: '2px' }} />
    </motion.div>
  );
}

/* ═══════════════════════════════════════════════
   ANSWER PAGE
   ═══════════════════════════════════════════════ */

export default function Answer() {
  const location = useLocation();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const question = location.state?.question || '';

  useEffect(() => {
    if (!question) {
      navigate('/');
      return;
    }
    let cancelled = false;
    setLoading(true);
    setResult(null);
    setError(null);

    askQuestion(question)
      .then((res) => {
        if (!cancelled) {
          setResult(res);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          console.error(err);
          setError('Failed to process your question. Please ensure the backend is running.');
          setLoading(false);
        }
      });

    return () => { cancelled = true; };
  }, [question, navigate]);

  const handleRelatedClick = (q) => {
    navigate('/answer', { state: { question: q }, replace: true });
    // Force re-run by changing key
    window.location.reload();
  };

  // Loading state
  if (loading) {
    return (
      <div style={{
        flex: 1, display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center',
        minHeight: '60vh', gap: '24px',
      }}>
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
          style={{
            width: '64px', height: '64px', borderRadius: '20px',
            background: 'linear-gradient(135deg, #7c3aed, #ec4899)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 8px 32px rgba(124,58,237,0.3)',
          }}
        >
          <Brain size={28} color="#fff" />
        </motion.div>
        <div style={{ textAlign: 'center' }}>
          <p style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text)', margin: '0 0 4px 0' }}>
            Analyzing your question...
          </p>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)', margin: 0 }}>
            Running through the MediRAG pipeline
          </p>
        </div>
        <div style={{
          display: 'flex', gap: '6px', marginTop: '8px',
        }}>
          {['Language', 'Safety', 'Processing', 'Retrieval', 'Answer'].map((stage, i) => (
            <motion.div
              key={stage}
              initial={{ opacity: 0.3 }}
              animate={{ opacity: [0.3, 1, 0.3] }}
              transition={{ duration: 1.5, delay: i * 0.3, repeat: Infinity }}
              style={{
                padding: '4px 10px', borderRadius: '8px',
                background: 'var(--primary-light)',
                fontSize: '10px', fontWeight: 700,
                color: 'var(--primary)',
              }}
            >
              {stage}
            </motion.div>
          ))}
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div style={{
        flex: 1, display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center',
        minHeight: '60vh', gap: '16px',
      }}>
        <AlertTriangle size={48} style={{ color: 'var(--accent-amber)' }} />
        <p style={{ fontSize: '16px', fontWeight: 600, color: 'var(--text)' }}>{error}</p>
        <button
          onClick={() => navigate('/')}
          style={{
            padding: '10px 24px', borderRadius: '12px',
            background: 'var(--primary)', color: '#fff',
            border: 'none', fontWeight: 700, cursor: 'pointer',
            fontSize: '14px',
          }}
        >
          Go Back
        </button>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto', width: '100%' }}>

      {/* Back Button + Query */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
        <button
          onClick={() => navigate('/')}
          style={{
            width: '40px', height: '40px', borderRadius: '14px',
            background: 'rgba(255,255,255,0.6)', backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255,255,255,0.7)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            cursor: 'pointer', color: 'var(--text-muted)',
            transition: 'all 0.2s', boxShadow: 'var(--shadow-sm)',
            flexShrink: 0,
          }}
        >
          <ArrowLeft size={18} />
        </button>
        <div>
          <p style={{ fontSize: '10px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.12em', color: 'var(--text-muted)', margin: 0 }}>
            Your Question
          </p>
          <h2 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text)', margin: '2px 0 0 0', lineHeight: 1.4 }}>
            {question}
          </h2>
        </div>
      </div>

      {/* Processing Stages */}
      {result?.processing_stages && (
        <PipelineStages stages={result.processing_stages} isComplete={true} />
      )}

      {/* Meta Badges */}
      {result && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          style={{
            display: 'flex', flexWrap: 'wrap', gap: '10px',
            marginBottom: '24px', justifyContent: 'center',
          }}
        >
          {result.language && <MetaBadge icon={Globe} label="Language" value={result.language} color="#6366f1" />}
          {result.topic && <MetaBadge icon={Tag} label="Topic" value={result.topic} color="#14b8a6" />}
          {result.intent && <MetaBadge icon={Activity} label="Intent" value={result.intent} color="#f59e0b" />}
          {result.safety_category && <MetaBadge icon={Shield} label="Safety" value={result.safety_category} color="#10b981" />}
          {result.latency_ms > 0 && <MetaBadge icon={Clock} label="Latency" value={`${result.latency_ms.toFixed(0)}ms`} color="#8b5cf6" />}
        </motion.div>
      )}

      {/* Answer Card */}
      {result && (
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, type: 'spring', stiffness: 200, damping: 25 }}
          style={{
            borderRadius: '28px',
            background: 'rgba(255,255,255,0.85)',
            backdropFilter: 'blur(30px)',
            WebkitBackdropFilter: 'blur(30px)',
            border: '1px solid rgba(255,255,255,0.6)',
            boxShadow: 'var(--shadow-lg)',
            overflow: 'hidden',
            marginBottom: '28px',
          }}
        >
          {/* Gradient top bar */}
          <div style={{
            height: '4px',
            background: result.abstained
              ? 'linear-gradient(90deg, #f59e0b, #ef4444)'
              : 'linear-gradient(90deg, #7c3aed, #ec4899, #6366f1)',
          }} />

          <div style={{ padding: '32px' }}>
            {/* Answer Header */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '14px', marginBottom: '20px' }}>
              <div style={{
                width: '48px', height: '48px', borderRadius: '16px',
                background: result.abstained ? 'var(--accent-amber-light)' : 'var(--primary-light)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                flexShrink: 0,
              }}>
                {result.abstained
                  ? <AlertTriangle size={22} style={{ color: 'var(--accent-amber)' }} />
                  : <Sparkles size={22} style={{ color: 'var(--primary)' }} />
                }
              </div>
              <div>
                <p style={{ fontSize: '10px', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.15em', color: result.abstained ? 'var(--accent-amber)' : 'var(--primary)', margin: 0 }}>
                  {result.abstained ? 'No Confident Match' : 'Analysis Result'}
                </p>
                {result.matched_question && (
                  <p style={{ fontSize: '12px', fontWeight: 500, color: 'var(--text-muted)', margin: '2px 0 0 0' }}>
                    Matched: "{result.matched_question.slice(0, 100)}{result.matched_question.length > 100 ? '...' : ''}"
                  </p>
                )}
                {result.similarity_score > 0 && (
                  <div style={{
                    display: 'inline-flex', alignItems: 'center', gap: '4px',
                    marginTop: '4px', padding: '2px 8px', borderRadius: '6px',
                    background: result.similarity_score >= 0.8 ? 'rgba(16,185,129,0.08)' : 'rgba(245,158,11,0.08)',
                    fontSize: '11px', fontWeight: 700,
                    color: result.similarity_score >= 0.8 ? '#059669' : '#d97706',
                  }}>
                    {(result.similarity_score * 100).toFixed(1)}% similarity
                  </div>
                )}
              </div>
            </div>

            {/* Answer Text */}
            <div style={{
              fontSize: '15px',
              fontWeight: 500,
              lineHeight: 1.8,
              color: 'var(--text-secondary)',
              whiteSpace: 'pre-wrap',
            }}>
              {result.answer}
            </div>

            {/* Evidence Section */}
            {result.evidence && result.evidence.length > 0 && (
              <div style={{
                marginTop: '28px',
                paddingTop: '20px',
                borderTop: '1px solid rgba(0,0,0,0.05)',
              }}>
                <h4 style={{
                  fontSize: '10px', fontWeight: 800, textTransform: 'uppercase',
                  letterSpacing: '0.12em', color: 'var(--text-muted)', margin: '0 0 12px 0',
                }}>
                  Evidence
                </h4>
                {result.evidence.map((ev, i) => (
                  <div key={i} style={{
                    padding: '14px 16px', borderRadius: '14px',
                    background: 'rgba(124,58,237,0.03)',
                    border: '1px solid rgba(124,58,237,0.06)',
                    marginBottom: '8px',
                  }}>
                    <p style={{ fontSize: '13px', fontWeight: 500, color: 'var(--text-secondary)', margin: 0, lineHeight: 1.6 }}>
                      {ev.text}
                    </p>
                    {(ev.document_id || ev.section) && (
                      <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
                        {ev.document_id && (
                          <span style={{ fontSize: '10px', fontWeight: 600, color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                            <FileText size={10} /> {ev.document_id}
                          </span>
                        )}
                        {ev.section && (
                          <span style={{ fontSize: '10px', fontWeight: 600, color: 'var(--text-muted)' }}>
                            § {ev.section}
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* Sources Section */}
            {result.sources && result.sources.length > 0 && (
              <div style={{
                marginTop: '20px',
                paddingTop: '16px',
                borderTop: '1px solid rgba(0,0,0,0.05)',
              }}>
                <h4 style={{
                  fontSize: '10px', fontWeight: 800, textTransform: 'uppercase',
                  letterSpacing: '0.12em', color: 'var(--text-muted)', margin: '0 0 10px 0',
                }}>
                  Sources
                </h4>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {result.sources.map((src, i) => (
                    <div key={i} style={{
                      display: 'flex', alignItems: 'center', gap: '6px',
                      padding: '6px 12px', borderRadius: '10px',
                      background: 'rgba(255,255,255,0.6)',
                      border: '1px solid rgba(0,0,0,0.04)',
                      fontSize: '12px', fontWeight: 600,
                      color: 'var(--text-secondary)',
                    }}>
                      <span style={{
                        width: '18px', height: '18px', borderRadius: '6px',
                        background: 'var(--primary-light)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontSize: '10px', fontWeight: 800, color: 'var(--primary)',
                      }}>
                        {i + 1}
                      </span>
                      <span>{typeof src === 'string' ? src : (src.metadata?.title || 'Medical Source')}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </motion.div>
      )}

      {/* Related Questions */}
      {result?.related_questions && result.related_questions.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          style={{ marginBottom: '40px' }}
        >
          <h3 style={{
            fontSize: '11px', fontWeight: 800, textTransform: 'uppercase',
            letterSpacing: '0.12em', color: 'var(--text-muted)',
            margin: '0 0 14px 0', paddingLeft: '4px',
          }}>
            Related Questions
          </h3>
          <div style={{ display: 'grid', gap: '10px' }}>
            {result.related_questions.map((rq, i) => (
              <RelatedCard
                key={i}
                question={rq.question}
                topic={rq.topic}
                score={rq.similarity_score}
                onClick={() => handleRelatedClick(rq.question)}
              />
            ))}
          </div>
        </motion.div>
      )}

      {/* Ask Another Button */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        style={{ textAlign: 'center', paddingBottom: '32px' }}
      >
        <button
          onClick={() => navigate('/')}
          style={{
            padding: '12px 28px',
            borderRadius: '9999px',
            background: 'linear-gradient(135deg, #7c3aed, #ec4899)',
            color: '#fff',
            border: 'none',
            fontWeight: 700,
            fontSize: '14px',
            cursor: 'pointer',
            boxShadow: '0 4px 20px rgba(124,58,237,0.3)',
            transition: 'all 0.2s',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
          }}
        >
          <Search size={16} />
          Ask Another Question
        </button>
      </motion.div>
    </div>
  );
}
