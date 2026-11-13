import { motion } from 'framer-motion';
import {
  Globe, Languages, Sparkles, ArrowRight,
  MessageCircle, Stethoscope, Activity, Heart,
  Shield, BookOpen, Pill, Thermometer,
} from 'lucide-react';

const fade = {
  initial: { opacity: 0, y: 20 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true },
  transition: { duration: 0.4 },
};

const TOPICS = [
  { icon: Thermometer, name: 'Fever & Temperature', desc: 'Common fever causes, symptoms, and management' },
  { icon: Activity, name: 'Heart & Circulation', desc: 'Blood pressure, heart health, and circulation' },
  { icon: Pill, name: 'Medication Info', desc: 'General medication information and usage' },
  { icon: Heart, name: 'General Wellness', desc: 'Daily health, hydration, nutrition basics' },
  { icon: Shield, name: 'Prevention', desc: 'Preventive health measures and practices' },
  { icon: BookOpen, name: 'Common Conditions', desc: 'Diabetes, asthma, allergies, and more' },
];

const LANGS = [
  { label: 'English', native: 'English', example: 'What are the symptoms of dehydration?', color: '#7c3aed' },
  { label: 'বাংলা', native: 'Bangla', example: 'পানিশূন্যতার লক্ষণ কী কী?', color: '#a855f7' },
  { label: 'Banglish', native: 'Banglish', example: 'Pani shunnotar symptoms ki ki?', color: '#14b8a6' },
  { label: 'Code-Mixed', native: 'Mixed', example: 'Dehydration er লক্ষণ ki ki?', color: '#f59e0b' },
];

export default function Explore() {
  return (
    <div style={{ maxWidth: '960px', margin: '0 auto', paddingBottom: '48px' }}>

      {/* Hero */}
      <motion.div {...fade} style={{ textAlign: 'center', marginBottom: '56px' }}>
        <h1 style={{
          fontSize: '2.8rem', fontWeight: 800, color: 'var(--text)',
          letterSpacing: '-0.03em', margin: '0 0 12px 0',
        }}>
          Explore the Knowledge
        </h1>
        <p style={{
          fontSize: '16px', fontWeight: 500, color: 'var(--text-muted)',
          maxWidth: '520px', margin: '0 auto', lineHeight: 1.6,
        }}>
          Browse the topics and questions represented in the MediRAG-BD knowledge dataset.
        </p>
      </motion.div>

      {/* Topic Cards */}
      <motion.section {...fade} style={{ marginBottom: '64px' }}>
        <h2 style={{
          fontSize: '11px', fontWeight: 800, textTransform: 'uppercase',
          letterSpacing: '0.12em', color: 'var(--text-muted)', margin: '0 0 20px 0',
        }}>
          Topics in the Dataset
        </h2>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
          gap: '14px',
        }}>
          {TOPICS.map((t, i) => (
            <motion.div
              key={i}
              whileHover={{ y: -3 }}
              className="glass-card"
              style={{
                padding: '20px',
                display: 'flex',
                alignItems: 'flex-start',
                gap: '14px',
                cursor: 'pointer',
              }}
            >
              <div style={{
                width: '40px', height: '40px', borderRadius: '12px',
                background: 'var(--primary-light)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                flexShrink: 0,
              }}>
                <t.icon size={20} style={{ color: 'var(--primary)' }} />
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <h3 style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text)', margin: '0 0 4px 0' }}>
                  {t.name}
                </h3>
                <p style={{ fontSize: '12px', fontWeight: 500, color: 'var(--text-muted)', margin: 0, lineHeight: 1.5 }}>
                  {t.desc}
                </p>
              </div>
              <ArrowRight size={16} style={{ color: 'var(--text-muted)', flexShrink: 0, marginTop: '2px' }} />
            </motion.div>
          ))}
        </div>
      </motion.section>

      {/* Multilingual Showcase */}
      <motion.section {...fade} style={{ marginBottom: '64px' }}>
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <h2 style={{
            fontSize: '2rem', fontWeight: 800, color: 'var(--text)',
            letterSpacing: '-0.02em', margin: '0 0 10px 0',
          }}>
            Ask the way you naturally speak.
          </h2>
          <p style={{
            fontSize: '15px', fontWeight: 500, color: 'var(--text-muted)',
            maxWidth: '480px', margin: '0 auto', lineHeight: 1.6,
          }}>
            Different language forms → Same intent → Same knowledge
          </p>
        </div>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
          gap: '14px',
        }}>
          {LANGS.map((l, i) => (
            <div
              key={i}
              className="glass-card"
              style={{
                padding: '20px',
                borderLeft: `3px solid ${l.color}`,
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                <Globe size={14} style={{ color: l.color }} />
                <span style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.1em', color: l.color }}>
                  {l.native}
                </span>
              </div>
              <p style={{
                fontSize: '15px', fontWeight: 600, color: 'var(--text)',
                margin: 0, lineHeight: 1.5, fontStyle: 'italic',
              }}>
                "{l.example}"
              </p>
            </div>
          ))}
        </div>
      </motion.section>

      {/* Banglish Showcase */}
      <motion.section {...fade}>
        <div
          className="glass"
          style={{
            padding: '40px 32px',
            textAlign: 'center',
          }}
        >
          <div style={{
            display: 'inline-flex', alignItems: 'center', gap: '6px',
            padding: '5px 14px', borderRadius: '9999px',
            background: 'var(--accent-teal-light)', color: 'var(--accent-teal)',
            fontSize: '11px', fontWeight: 700, marginBottom: '16px',
          }}>
            <Languages size={13} /> Built for Banglish
          </div>
          <h2 style={{
            fontSize: '1.8rem', fontWeight: 800, color: 'var(--text)',
            letterSpacing: '-0.02em', margin: '0 0 12px 0',
          }}>
            Banglish has spelling variation and code-mixing.
          </h2>
          <p style={{
            fontSize: '14px', fontWeight: 500, color: 'var(--text-muted)',
            maxWidth: '480px', margin: '0 auto 28px auto', lineHeight: 1.6,
          }}>
            MediRAG-BD handles the natural variation in Romanized Bangla through semantic understanding rather than exact matching.
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px' }}>
            {[
              { label: 'User types', value: '"Pani shunnota ki?"' },
              { label: 'Language', value: 'Banglish detected' },
              { label: 'Semantic match', value: 'Dehydration symptoms' },
              { label: 'Answer', value: 'Retrieved from knowledge base' },
            ].map((step, i) => (
              <div key={i} style={{
                display: 'flex', alignItems: 'center', gap: '10px',
                fontSize: '14px',
              }}>
                <span style={{
                  width: '24px', height: '24px', borderRadius: '8px',
                  background: 'var(--primary-light)', color: 'var(--primary)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '11px', fontWeight: 800, flexShrink: 0,
                }}>
                  {i + 1}
                </span>
                <span style={{ fontWeight: 600, color: 'var(--text-muted)' }}>{step.label}:</span>
                <span style={{ fontWeight: 700, color: 'var(--text)' }}>{step.value}</span>
              </div>
            ))}
          </div>
        </div>
      </motion.section>
    </div>
  );
}
