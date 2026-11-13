import { ShieldAlert, BookOpen, Globe, Code, CheckCircle, Info } from 'lucide-react';

export default function About() {
  return (
    <div style={{ maxWidth: '720px', margin: '0 auto', paddingBottom: '48px' }}>

      <div style={{ textAlign: 'center', marginBottom: '48px' }}>
        <h1 style={{
          fontSize: '2.8rem', fontWeight: 800, color: 'var(--text)',
          letterSpacing: '-0.03em', margin: '0 0 16px 0',
        }}>
          About MediRAG-BD
        </h1>
        <p style={{
          fontSize: '16px', fontWeight: 500, color: 'var(--text-muted)',
          maxWidth: '480px', margin: '0 auto', lineHeight: 1.6,
        }}>
          Bridging the language gap in medical information access through semantic search.
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>

        {/* Project Description */}
        <section
          className="glass"
          style={{
            padding: '28px 32px',
            borderLeft: '4px solid var(--primary)',
            overflow: 'hidden',
          }}
        >
          <h2 style={{
            fontSize: '18px', fontWeight: 700, color: 'var(--text)',
            margin: '0 0 14px 0',
            display: 'flex', alignItems: 'center', gap: '8px',
          }}>
            <BookOpen size={20} style={{ color: 'var(--primary)' }} /> Project Description
          </h2>
          <p style={{
            fontSize: '14px', fontWeight: 500, color: 'var(--text-secondary)',
            margin: 0, lineHeight: 1.8,
          }}>
            MediRAG-BD is a research initiative aimed at solving a critical problem: the vast majority of high-quality, verified medical information is available only in English, while millions of users search for health information using Bangla, Banglish (Romanized Bangla), and Code-Mixed (Bangla-English) text.
            By utilizing a Retrieval-Augmented Generation (RAG) architecture without relying on unpredictable LLM generation, this system acts as a highly accurate, multilingual semantic search engine over a validated medical dataset.
          </p>
        </section>

        {/* Supported Languages */}
        <section className="glass" style={{ padding: '28px 32px' }}>
          <h2 style={{
            fontSize: '18px', fontWeight: 700, color: 'var(--text)',
            margin: '0 0 18px 0',
            display: 'flex', alignItems: 'center', gap: '8px',
          }}>
            <Globe size={20} style={{ color: 'var(--primary)' }} /> Supported Languages
          </h2>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(4, 1fr)',
            gap: '10px',
          }}>
            {['Bangla', 'English', 'Banglish', 'Code-Mixed'].map((l) => (
              <div
                key={l}
                className="glass-card"
                style={{
                  padding: '14px',
                  textAlign: 'center',
                  fontWeight: 700,
                  fontSize: '13px',
                  color: 'var(--text-secondary)',
                }}
              >
                {l}
              </div>
            ))}
          </div>
        </section>

        {/* Safety & Limitations */}
        <section
          className="glass"
          style={{
            padding: '28px 32px',
            borderLeft: '4px solid #f59e0b',
            overflow: 'hidden',
          }}
        >
          <h2 style={{
            fontSize: '18px', fontWeight: 700, color: 'var(--text)',
            margin: '0 0 14px 0',
            display: 'flex', alignItems: 'center', gap: '8px',
          }}>
            <ShieldAlert size={20} style={{ color: '#f59e0b' }} /> Safety & Limitations
          </h2>
          <p style={{
            fontSize: '14px', fontWeight: 500, color: 'var(--text-secondary)',
            margin: '0 0 16px 0', lineHeight: 1.7,
          }}>
            This system is designed strictly as an information retrieval tool. It is <strong>not</strong> a diagnostic system, a digital doctor, or a treatment recommender.
          </p>
          <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {[
              'Does not generate clinical advice or personalize treatments.',
              'Answers are exact matches from the pre-approved dataset.',
              'Intentionally abstains from answering if similarity falls below the safety threshold.',
              'Classifies and blocks harmful or deeply personal medical requests.',
            ].map((item, i) => (
              <li
                key={i}
                style={{
                  display: 'flex', alignItems: 'flex-start', gap: '10px',
                  fontSize: '13px', fontWeight: 500, color: 'var(--text-muted)', lineHeight: 1.5,
                }}
              >
                <CheckCircle size={15} style={{ color: '#10b981', flexShrink: 0, marginTop: '2px' }} />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </section>

        {/* Technology Stack */}
        <section className="glass" style={{ padding: '28px 32px' }}>
          <h2 style={{
            fontSize: '18px', fontWeight: 700, color: 'var(--text)',
            margin: '0 0 14px 0',
            display: 'flex', alignItems: 'center', gap: '8px',
          }}>
            <Code size={20} style={{ color: 'var(--primary)' }} /> Technology Stack
          </h2>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {['React', 'Tailwind v4', 'Framer Motion', 'FastAPI', 'Python', 'scikit-learn', 'FAISS', 'Sentence Transformers'].map((t) => (
              <span
                key={t}
                className="badge"
                style={{
                  background: 'var(--primary-light)',
                  color: 'var(--primary)',
                }}
              >
                {t}
              </span>
            ))}
          </div>
        </section>
      </div>

      {/* Disclaimer */}
      <div style={{ paddingTop: '32px', textAlign: 'center' }}>
        <div style={{
          display: 'inline-flex', alignItems: 'flex-start', gap: '10px',
          padding: '16px 20px', borderRadius: '16px', textAlign: 'left',
          maxWidth: '560px',
          background: 'rgba(255,255,255,0.5)',
          backdropFilter: 'blur(10px)',
          border: '1px solid var(--border)',
        }}>
          <Info size={16} style={{ color: 'var(--text-muted)', flexShrink: 0, marginTop: '2px' }} />
          <p style={{
            fontSize: '12px', fontWeight: 500, color: 'var(--text-muted)',
            margin: 0, lineHeight: 1.6,
          }}>
            <strong>Disclaimer:</strong> MediRAG-BD provides general health information from its knowledge dataset. It is not a diagnostic or treatment system. Always consult a qualified healthcare provider for medical advice.
          </p>
        </div>
      </div>
    </div>
  );
}
