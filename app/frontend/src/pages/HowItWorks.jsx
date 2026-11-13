import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ArrowDown, ChevronDown, CheckCircle2,
  Database, ShieldCheck, Languages, Stethoscope,
  List, Fingerprint, Search, SortAsc, FileText
} from 'lucide-react';

const NODES = [
  { icon: Languages, title: 'Language Detection', desc: 'Identifies if the query is Bangla, English, Banglish, or Code-Mixed.' },
  { icon: Fingerprint, title: 'Preprocessing', desc: 'Normalizes Banglish variations and cleans the text.' },
  { icon: ShieldCheck, title: 'Safety Check', desc: 'Classifies the query intent to block harmful or out-of-scope requests.' },
  { icon: Stethoscope, title: 'Intent Detection', desc: 'Determines what the user is looking for (e.g., Symptoms, Treatment).' },
  { icon: List, title: 'Topic Detection', desc: 'Categorizes the medical domain (e.g., Cardiology, Nutrition).' },
  { icon: Database, title: 'Embedding', desc: 'Converts text into dense mathematical vectors for semantic understanding.' },
  { icon: Search, title: 'Semantic Retrieval', desc: 'Searches the FAISS vector database and TF-IDF index for matches.' },
  { icon: SortAsc, title: 'Ranking', desc: 'Calculates similarity scores and ranks the best knowledge base hits.' },
  { icon: CheckCircle2, title: 'Validated Answer', desc: 'Extracts the pre-approved answer from the dataset.' },
  { icon: FileText, title: 'Evidence', desc: 'Provides the exact document and section from the original medical source.' },
];

export default function HowItWorks() {
  const [techOpen, setTechOpen] = useState(false);

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', paddingBottom: '48px' }}>

      {/* Hero */}
      <div style={{ textAlign: 'center', marginBottom: '48px' }}>
        <h1 style={{
          fontSize: '2.8rem', fontWeight: 800, color: 'var(--text)',
          letterSpacing: '-0.03em', margin: '0 0 12px 0',
        }}>
          From question to evidence.
        </h1>
        <p style={{
          fontSize: '16px', fontWeight: 500, color: 'var(--text-muted)',
          maxWidth: '520px', margin: '0 auto', lineHeight: 1.6,
        }}>
          MediRAG-BD uses a modular NLP architecture to map natural language to validated medical knowledge.
        </p>
      </div>

      {/* Pipeline Visualization */}
      <section
        className="glass"
        style={{ padding: '36px 40px', marginBottom: '24px', overflow: 'hidden' }}
      >
        <h2 style={{
          fontSize: '11px', fontWeight: 800, textTransform: 'uppercase',
          letterSpacing: '0.12em', color: 'var(--text-muted)',
          margin: '0 0 32px 0', textAlign: 'center',
        }}>
          The Retrieval Pipeline
        </h2>

        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
          {/* User Question badge */}
          <div style={{
            padding: '8px 20px', borderRadius: '9999px',
            background: 'linear-gradient(135deg, #7c3aed, #ec4899)',
            color: '#fff', fontSize: '13px', fontWeight: 700,
            boxShadow: '0 4px 16px rgba(124,58,237,0.3)',
            marginBottom: '8px',
          }}>
            User Question
          </div>

          {NODES.map((node, i) => (
            <div key={i} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <ArrowDown size={18} style={{ color: 'var(--border-subtle)', margin: '6px 0' }} />
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: '-40px' }}
                transition={{ duration: 0.3, delay: 0.05 }}
                className="glass-card"
                style={{
                  width: '100%',
                  maxWidth: '420px',
                  padding: '16px 20px',
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '14px',
                }}
              >
                <div style={{
                  width: '36px', height: '36px', borderRadius: '10px',
                  background: 'var(--primary-light)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  flexShrink: 0,
                }}>
                  <node.icon size={18} style={{ color: 'var(--primary)' }} />
                </div>
                <div>
                  <h3 style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text)', margin: '0 0 4px 0' }}>
                    {node.title}
                  </h3>
                  <p style={{ fontSize: '12px', fontWeight: 500, color: 'var(--text-muted)', margin: 0, lineHeight: 1.5 }}>
                    {node.desc}
                  </p>
                </div>
              </motion.div>
            </div>
          ))}
        </div>
      </section>

      {/* Technical Detail Toggle */}
      <section
        className="glass"
        style={{ overflow: 'hidden' }}
      >
        <button
          onClick={() => setTechOpen(!techOpen)}
          style={{
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '18px 28px',
            background: techOpen ? 'var(--surface-hover)' : 'transparent',
            border: 'none',
            cursor: 'pointer',
            textAlign: 'left',
            transition: 'background 0.2s',
          }}
        >
          <span style={{ fontWeight: 700, fontSize: '15px', color: 'var(--text)' }}>
            Technical Details
          </span>
          <motion.span animate={{ rotate: techOpen ? 180 : 0 }} transition={{ duration: 0.2 }}>
            <ChevronDown size={20} style={{ color: 'var(--text-muted)' }} />
          </motion.span>
        </button>

        <AnimatePresence>
          {techOpen && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3 }}
              style={{ overflow: 'hidden' }}
            >
              <div style={{
                padding: '24px 28px',
                borderTop: '1px solid var(--border-subtle)',
              }}>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
                  gap: '24px',
                }}>
                  {[
                    {
                      title: 'Semantic Representation',
                      desc: 'Uses dense embeddings (e.g., multilingual-e5) combined with TF-IDF for lexical overlap, creating a hybrid retrieval approach.',
                    },
                    {
                      title: 'Vector Indexing',
                      desc: 'FAISS (Facebook AI Similarity Search) is used for extremely fast nearest-neighbor lookups on high-dimensional data.',
                    },
                    {
                      title: 'Classifiers',
                      desc: 'Safety and Intent detection utilize trained Support Vector Machines (SVM) operating on TF-IDF features of the preprocessed text.',
                    },
                    {
                      title: 'Evaluation Metrics',
                      desc: 'The system is evaluated using Recall@K (e.g., Recall@1, Recall@5) and Mean Reciprocal Rank (MRR) to measure retrieval quality.',
                    },
                  ].map((item, i) => (
                    <div key={i}>
                      <h4 style={{
                        fontSize: '14px', fontWeight: 700, color: 'var(--primary)',
                        margin: '0 0 8px 0',
                      }}>
                        {item.title}
                      </h4>
                      <p style={{
                        fontSize: '13px', fontWeight: 500, color: 'var(--text-muted)',
                        margin: 0, lineHeight: 1.6,
                      }}>
                        {item.desc}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </section>
    </div>
  );
}
