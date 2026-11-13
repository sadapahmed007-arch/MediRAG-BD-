import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  BarChart2, PieChart, Activity, FileText, Globe,
  Search, RefreshCw, AlertTriangle, ChevronRight,
  X, Database
} from 'lucide-react';
import { getDashboard } from '../services/api';

/* ═══════════════════════════════════════════════
   COMPONENTS
   ═══════════════════════════════════════════════ */

function KPICard({ label, value, icon: Icon, color, lightColor }) {
  return (
    <div
      className="glass-card"
      style={{
        padding: '20px 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}
    >
      <div>
        <p style={{
          fontSize: '10px', fontWeight: 800, textTransform: 'uppercase',
          letterSpacing: '0.12em', color: 'var(--text-muted)', margin: '0 0 6px 0',
        }}>
          {label}
        </p>
        <p style={{
          fontSize: '28px', fontWeight: 800, color: 'var(--text)',
          margin: 0, letterSpacing: '-0.03em',
        }}>
          {value}
        </p>
      </div>
      <div style={{
        width: '48px', height: '48px', borderRadius: '14px',
        background: lightColor || 'var(--primary-light)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}>
        <Icon size={22} style={{ color: color || 'var(--primary)' }} />
      </div>
    </div>
  );
}

function HorizontalBarChart({ data, maxValue, color, label }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '12px' }}>
      {data.map((item, i) => {
        const width = `${Math.max((item.value / maxValue) * 100, 3)}%`;
        return (
          <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{
              width: '80px', flexShrink: 0, fontSize: '13px',
              fontWeight: 600, color: 'var(--text-secondary)',
              overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
            }}>
              {item.label}
            </span>
            <div style={{
              flex: 1, height: '8px', borderRadius: '4px',
              background: 'rgba(0,0,0,0.04)', overflow: 'hidden',
            }}>
              <motion.div
                initial={{ width: 0 }}
                whileInView={{ width }}
                viewport={{ once: true }}
                transition={{ duration: 0.8, delay: i * 0.05 }}
                style={{
                  height: '100%', borderRadius: '4px',
                  background: color || 'var(--primary)',
                }}
              />
            </div>
            <span style={{
              width: '52px', flexShrink: 0, textAlign: 'right',
              fontSize: '13px', fontWeight: 700, color: 'var(--text)',
            }}>
              {label === '%' ? `${(item.value * 100).toFixed(1)}%` : item.value}
            </span>
          </div>
        );
      })}
    </div>
  );
}

function Drawer({ open, onClose, title, content }) {
  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            style={{
              position: 'fixed', inset: 0,
              background: 'rgba(0,0,0,0.3)',
              backdropFilter: 'blur(4px)',
              zIndex: 50,
            }}
          />
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            style={{
              position: 'fixed', top: 0, right: 0, bottom: 0,
              width: '100%', maxWidth: '420px',
              background: 'rgba(255,255,255,0.92)',
              backdropFilter: 'blur(30px)',
              borderLeft: '1px solid var(--border)',
              zIndex: 50,
              display: 'flex', flexDirection: 'column',
            }}
          >
            <div style={{
              padding: '20px 24px',
              borderBottom: '1px solid var(--border-subtle)',
              display: 'flex', justifyContent: 'space-between', alignItems: 'center',
            }}>
              <h3 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text)', margin: 0 }}>{title}</h3>
              <button
                onClick={onClose}
                style={{
                  width: '32px', height: '32px', borderRadius: '10px',
                  background: 'rgba(0,0,0,0.04)', border: 'none',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  cursor: 'pointer', color: 'var(--text-muted)',
                }}
              >
                <X size={16} />
              </button>
            </div>
            <div style={{
              padding: '24px', flex: 1, overflowY: 'auto',
              fontSize: '14px', fontWeight: 500, lineHeight: 1.7,
              color: 'var(--text-secondary)',
            }}>
              {content}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

/* ═══════════════════════════════════════════════
   MAIN RESEARCH PAGE
   ═══════════════════════════════════════════════ */

export default function Research() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [drawer, setDrawer] = useState(null);

  useEffect(() => {
    getDashboard().then(res => {
      setData(res);
      setLoading(false);
    }).catch((err) => {
      console.error(err);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return (
      <div style={{ padding: '120px 0', textAlign: 'center', color: 'var(--text-muted)' }}>
        <RefreshCw size={24} style={{ animation: 'spin 1s linear infinite', margin: '0 auto 12px' }} />
        <p style={{ fontWeight: 600 }}>Loading Research Dashboard...</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div style={{ padding: '120px 0', textAlign: 'center', color: 'var(--text-muted)' }}>
        <AlertTriangle size={24} style={{ margin: '0 auto 12px' }} />
        <p style={{ fontWeight: 600 }}>Experiment data unavailable. Please ensure the backend is running.</p>
      </div>
    );
  }

  const stats = data.dataset_stats;
  const retr = data.retrieval_results;
  const cls = data.classification_results;
  const multi = data.multilingual_results;

  return (
    <div style={{ maxWidth: '1100px', margin: '0 auto', paddingBottom: '48px' }}>

      <div style={{ textAlign: 'center', marginBottom: '40px' }}>
        <h1 style={{
          fontSize: '2.4rem', fontWeight: 800, color: 'var(--text)',
          letterSpacing: '-0.03em', margin: '0 0 12px 0',
        }}>
          Research & Evaluation
        </h1>
        <p style={{
          fontSize: '15px', fontWeight: 500, color: 'var(--text-muted)',
          maxWidth: '520px', margin: '0 auto', lineHeight: 1.6,
        }}>
          Explore how MediRAG-BD performs across retrieval methods and languages based on actual evaluation data.
        </p>
      </div>

      {/* KPIs */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))',
        gap: '14px',
        marginBottom: '28px',
      }}>
        <KPICard label="Total Records" value={stats.total_records?.toLocaleString() || '—'} icon={Database} color="#7c3aed" lightColor="var(--primary-light)" />
        <KPICard label="Languages" value={Object.keys(stats.languages || {}).length.toString()} icon={Globe} color="#a855f7" lightColor="var(--accent-purple-light)" />
        <KPICard label="Hybrid Recall@5" value={retr?.hybrid ? `${(retr.hybrid.recall_at_5 * 100).toFixed(1)}%` : '—'} icon={Search} color="#14b8a6" lightColor="var(--accent-teal-light)" />
        <KPICard label="Classifier F1" value={cls?.intent_test ? `${(cls.intent_test.macro_f1 * 100).toFixed(1)}%` : '—'} icon={Activity} color="#10b981" lightColor="var(--accent-emerald-light)" />
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(450px, 1fr))',
        gap: '20px',
      }}>
        {/* Dataset Breakdown */}
        <div className="glass" style={{ padding: '28px 32px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h2 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text)', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <PieChart size={18} style={{ color: 'var(--primary)' }} /> Dataset Overview
            </h2>
            <button
              onClick={() => setDrawer({ title: 'Dataset Configuration', content: 'The dataset consists of QA pairs collected and translated across 4 language variants (English, Bangla, Banglish, Code-Mixed). Data augmentation was used to simulate realistic typos and variations in Banglish.' })}
              style={{
                background: 'none', border: 'none', cursor: 'pointer',
                fontSize: '11px', fontWeight: 800, textTransform: 'uppercase',
                letterSpacing: '0.08em', color: 'var(--primary)',
                display: 'flex', alignItems: 'center', gap: '4px',
              }}
            >
              Details <ChevronRight size={12} />
            </button>
          </div>

          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px', marginBottom: '20px' }}>
            <div style={{
              padding: '10px 16px', borderRadius: '12px',
              background: 'rgba(0,0,0,0.03)',
            }}>
              <span style={{ fontSize: '10px', fontWeight: 700, color: 'var(--text-muted)', display: 'block' }}>Original</span>
              <span style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text)' }}>{stats.data_origins?.ORIGINAL?.toLocaleString() || 'N/A'}</span>
            </div>
            <div style={{
              padding: '10px 16px', borderRadius: '12px',
              background: 'rgba(0,0,0,0.03)',
            }}>
              <span style={{ fontSize: '10px', fontWeight: 700, color: 'var(--text-muted)', display: 'block' }}>Augmented</span>
              <span style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text)' }}>{stats.data_origins?.AUGMENTED?.toLocaleString() || 'N/A'}</span>
            </div>
          </div>

          <h3 style={{ fontSize: '10px', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.12em', color: 'var(--text-muted)', margin: '20px 0 8px 0' }}>
            Top Topics
          </h3>
          {stats.topics && (
            <HorizontalBarChart
              color="#a855f7"
              label="#"
              maxValue={Math.max(...Object.values(stats.topics))}
              data={Object.entries(stats.topics)
                .map(([k, v]) => ({ label: k, value: v }))
                .filter(item => item.label !== 'Other')
                .sort((a, b) => b.value - a.value)
                .slice(0, 5)}
            />
          )}
        </div>

        {/* Retrieval Comparison */}
        <div className="glass" style={{ padding: '28px 32px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h2 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text)', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <BarChart2 size={18} style={{ color: 'var(--primary)' }} /> Retrieval Comparison
            </h2>
            <button
              onClick={() => setDrawer({ title: 'Retrieval Methods', content: 'Compares Sparse (TF-IDF) vs Dense (FAISS Embeddings) vs Hybrid retrieval. Hybrid merges both scores using reciprocal rank fusion for maximum accuracy across lexical and semantic searches.' })}
              style={{
                background: 'none', border: 'none', cursor: 'pointer',
                fontSize: '11px', fontWeight: 800, textTransform: 'uppercase',
                letterSpacing: '0.08em', color: 'var(--primary)',
                display: 'flex', alignItems: 'center', gap: '4px',
              }}
            >
              Details <ChevronRight size={12} />
            </button>
          </div>

          {retr && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <div>
                <h3 style={{ fontSize: '10px', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.12em', color: 'var(--text-muted)', margin: '0 0 8px 0' }}>
                  Recall@1
                </h3>
                <HorizontalBarChart color="#7c3aed" label="%" maxValue={1} data={[
                  { label: 'Hybrid', value: retr.hybrid?.recall_at_1 || 0 },
                  { label: 'Dense', value: retr.dense?.recall_at_1 || 0 },
                  { label: 'TF-IDF', value: retr.tfidf?.recall_at_1 || 0 },
                ]} />
              </div>
              <div>
                <h3 style={{ fontSize: '10px', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.12em', color: 'var(--text-muted)', margin: '0 0 8px 0' }}>
                  Recall@5
                </h3>
                <HorizontalBarChart color="#14b8a6" label="%" maxValue={1} data={[
                  { label: 'Hybrid', value: retr.hybrid?.recall_at_5 || 0 },
                  { label: 'Dense', value: retr.dense?.recall_at_5 || 0 },
                  { label: 'TF-IDF', value: retr.tfidf?.recall_at_5 || 0 },
                ]} />
              </div>
            </div>
          )}
        </div>

        {/* Language Performance */}
        <div className="glass" style={{ padding: '28px 32px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h2 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text)', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Globe size={18} style={{ color: 'var(--primary)' }} /> Language Performance
            </h2>
            <button
              onClick={() => setDrawer({ title: 'Language Support', content: 'Evaluates the Hybrid retrieval pipeline on individual language sets. Note that Code-Mixed and Banglish naturally have higher variance.' })}
              style={{
                background: 'none', border: 'none', cursor: 'pointer',
                fontSize: '11px', fontWeight: 800, textTransform: 'uppercase',
                letterSpacing: '0.08em', color: 'var(--primary)',
                display: 'flex', alignItems: 'center', gap: '4px',
              }}
            >
              Details <ChevronRight size={12} />
            </button>
          </div>

          {multi && (
            <>
              <h3 style={{ fontSize: '10px', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.12em', color: 'var(--text-muted)', margin: '0 0 8px 0' }}>
                Recall@1 (Self)
              </h3>
              <HorizontalBarChart color="#f59e0b" label="%" maxValue={1} data={
                Object.entries(multi)
                  .map(([lang, perf]) => ({ label: lang.replace('_', ' '), value: perf.self_recall_at_1 }))
                  .sort((a, b) => b.value - a.value)
              } />
            </>
          )}
        </div>

        {/* Classification Accuracy */}
        <div className="glass" style={{ padding: '28px 32px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h2 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text)', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <FileText size={18} style={{ color: 'var(--primary)' }} /> Classification Accuracy
            </h2>
            <button
              onClick={() => setDrawer({ title: 'Classification Models', content: 'Shows the accuracy of the SVM-based intent, topic, and safety classifiers.' })}
              style={{
                background: 'none', border: 'none', cursor: 'pointer',
                fontSize: '11px', fontWeight: 800, textTransform: 'uppercase',
                letterSpacing: '0.08em', color: 'var(--primary)',
                display: 'flex', alignItems: 'center', gap: '4px',
              }}
            >
              Details <ChevronRight size={12} />
            </button>
          </div>

          {cls && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <div>
                <h3 style={{ fontSize: '10px', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.12em', color: 'var(--text-muted)', margin: '0 0 8px 0' }}>
                  Safety & Intent
                </h3>
                <HorizontalBarChart color="#a855f7" label="%" maxValue={1} data={[
                  { label: 'Safety', value: cls.safety_test?.accuracy || 0 },
                  { label: 'Intent', value: cls.intent_test?.accuracy || 0 },
                ]} />
              </div>
              {multi && (
                <div>
                  <h3 style={{ fontSize: '10px', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.12em', color: 'var(--text-muted)', margin: '0 0 8px 0' }}>
                    Topic Routing
                  </h3>
                  <HorizontalBarChart color="#10b981" label="%" maxValue={1} data={[
                    { label: 'English', value: multi.english?.topic_accuracy || 0 },
                    { label: 'Bangla', value: multi.bangla?.topic_accuracy || 0 },
                    { label: 'Banglish', value: multi.banglish?.topic_accuracy || 0 },
                    { label: 'Code-Mix', value: multi.code_mixed?.topic_accuracy || 0 },
                  ]} />
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      <Drawer open={!!drawer} onClose={() => setDrawer(null)} title={drawer?.title} content={drawer?.content} />
    </div>
  );
}
