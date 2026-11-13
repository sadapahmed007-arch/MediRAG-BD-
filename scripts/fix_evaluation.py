"""Fix retrieval evaluation and launch verification."""
import sys, os, json, time
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

from src.data.loader import load_config
from src.retrieval.tfidf_retrieval import TFIDFRetriever
from src.retrieval.dense_retrieval import DenseRetriever
from src.retrieval.hybrid_retrieval import HybridRetriever

config = load_config()
IDX_DIR = Path(config['paths']['indexes_dir'])
RESULTS_DIR = Path(config['paths']['experiments_dir']) / 'raw_results'
FIGURES_DIR = Path(config['paths']['experiments_dir']) / 'figures'

# Load retrievers
print("Loading retrievers...")
tfidf_ret = TFIDFRetriever()
tfidf_ret.load(str(IDX_DIR / 'tfidf_vectorizer.pkl'),
               str(IDX_DIR / 'tfidf_matrix.pkl'),
               str(IDX_DIR / 'tfidf_docs.pkl'))

dense_ret = DenseRetriever(config['embeddings']['model_name'])
dense_ret.load(str(IDX_DIR / 'faiss_index.bin'), str(IDX_DIR / 'faiss_docs.pkl'))

hybrid_ret = HybridRetriever(tfidf_ret, dense_ret, alpha=config['retrieval']['hybrid']['alpha'])

# Load splits
train_df = pd.read_csv('data/splits/train.csv', encoding='utf-8')
test_df = pd.read_csv('data/splits/test.csv', encoding='utf-8')
train_df['answer'] = train_df['answer'].fillna('')
test_df['answer'] = test_df['answer'].fillna('')

# Build topic lookup for training docs
train_topics = {row['question_id']: row['topic'] for _, row in train_df.iterrows()}
train_answers = {row['question_id']: row['answer'] for _, row in train_df.iterrows()}

print(f"Train: {len(train_df)}, Test: {len(test_df)}")

# ── EVALUATION 1: Self-retrieval (can the system find its own questions?) ──
print("\n" + "="*60)
print("SELF-RETRIEVAL TEST (training queries → training index)")
print("="*60)

train_sample = train_df.sample(n=min(300, len(train_df)), random_state=42)
self_results = {}

for name, retriever in [('tfidf', tfidf_ret), ('dense', dense_ret), ('hybrid', hybrid_ret)]:
    hits_1, hits_3, hits_5, mrr_sum = 0, 0, 0, 0.0
    latencies = []
    for _, row in train_sample.iterrows():
        t0 = time.time()
        results = retriever.search(row['question'], top_k=5)
        latencies.append(time.time() - t0)
        ret_ids = [r.get('question_id', '') for r in results]
        gt = row['question_id']
        if gt in ret_ids[:1]: hits_1 += 1
        if gt in ret_ids[:3]: hits_3 += 1
        if gt in ret_ids[:5]: hits_5 += 1
        for i, rid in enumerate(ret_ids):
            if rid == gt:
                mrr_sum += 1.0 / (i + 1)
                break

    n = len(train_sample)
    r1, r3, r5, m = hits_1/n, hits_3/n, hits_5/n, mrr_sum/n
    lat = np.mean(latencies) * 1000
    self_results[name] = {'recall_at_1': r1, 'recall_at_3': r3, 'recall_at_5': r5,
                           'mrr': m, 'avg_latency_ms': round(lat, 1)}
    print(f"  {name}: R@1={r1:.3f} R@3={r3:.3f} R@5={r5:.3f} MRR={m:.3f} lat={lat:.0f}ms")

# ── EVALUATION 2: Cross-retrieval (test queries → topic accuracy) ──
print("\n" + "="*60)
print("CROSS-RETRIEVAL TEST (test queries → training index, topic match)")
print("="*60)

test_sample = test_df.sample(n=min(300, len(test_df)), random_state=42)
cross_results = {}

for name, retriever in [('tfidf', tfidf_ret), ('dense', dense_ret), ('hybrid', hybrid_ret)]:
    topic_hits, answer_hits = 0, 0
    top1_scores = []
    for _, row in test_sample.iterrows():
        results = retriever.search(row['question'], top_k=5)
        if results:
            top1 = results[0]
            top1_scores.append(top1['similarity_score'])
            # Topic match
            if top1.get('topic', '') == row['topic']:
                topic_hits += 1
            # Answer overlap (check if answers share significant words)
            ret_ans = str(top1.get('answer', '')).lower().split()
            gt_ans = str(row['answer']).lower().split()
            if ret_ans and gt_ans and len(set(ret_ans) & set(gt_ans)) > 0:
                answer_hits += 1

    n = len(test_sample)
    topic_acc = topic_hits / n
    answer_overlap = answer_hits / n
    avg_score = np.mean(top1_scores) if top1_scores else 0
    cross_results[name] = {
        'topic_accuracy': topic_acc,
        'answer_overlap': answer_overlap,
        'avg_top1_score': round(avg_score, 4),
    }
    print(f"  {name}: topic_acc={topic_acc:.3f} ans_overlap={answer_overlap:.3f} avg_score={avg_score:.3f}")

# ── EVALUATION 3: Per-language (test queries, topic match) ──
print("\n" + "="*60)
print("PER-LANGUAGE RETRIEVAL (dense, topic accuracy)")
print("="*60)

ml_results = {}
for lang in ['english', 'bangla', 'banglish', 'code_mixed']:
    lang_df = test_df[test_df['language'] == lang]
    if len(lang_df) == 0:
        continue
    sample = lang_df.sample(n=min(80, len(lang_df)), random_state=42)
    topic_hits, scores = 0, []
    for _, row in sample.iterrows():
        results = dense_ret.search(row['question'], top_k=5)
        if results:
            scores.append(results[0]['similarity_score'])
            if results[0].get('topic', '') == row['topic']:
                topic_hits += 1
    n = len(sample)
    topic_acc = topic_hits / n
    avg_s = np.mean(scores) if scores else 0
    # Also do self-retrieval for this language from training
    lang_train = train_df[train_df['language'] == lang]
    if len(lang_train) > 0:
        lt_sample = lang_train.sample(n=min(50, len(lang_train)), random_state=42)
        self_hits = 0
        for _, row in lt_sample.iterrows():
            res = dense_ret.search(row['question'], top_k=1)
            if res and res[0].get('question_id') == row['question_id']:
                self_hits += 1
        self_r1 = self_hits / len(lt_sample)
    else:
        self_r1 = 0
    ml_results[lang] = {
        'n': n, 'topic_accuracy': topic_acc,
        'avg_similarity': round(avg_s, 4),
        'self_recall_at_1': self_r1,
    }
    print(f"  {lang} (n={n}): topic_acc={topic_acc:.3f} avg_sim={avg_s:.3f} self_R@1={self_r1:.3f}")

# ── Generate updated figures ──
print("\nGenerating updated figures...")

# Retrieval comparison (self-retrieval)
methods = list(self_results.keys())
metrics_names = ['recall_at_1', 'recall_at_3', 'recall_at_5', 'mrr']
x = np.arange(len(metrics_names))
width = 0.25
fig, ax = plt.subplots(figsize=(10, 6))
colors = ['#0EA5E9', '#14B8A6', '#8B5CF6']
for i, method in enumerate(methods):
    vals = [self_results[method][m] for m in metrics_names]
    ax.bar(x + i * width, vals, width, label=method.upper(), color=colors[i])
ax.set_xticks(x + width)
ax.set_xticklabels(['Recall@1', 'Recall@3', 'Recall@5', 'MRR'])
ax.set_ylabel('Score')
ax.set_title('Retrieval Method Comparison (Self-Retrieval)')
ax.legend()
ax.set_ylim(0, 1.05)
plt.tight_layout()
plt.savefig(str(FIGURES_DIR / 'retrieval_comparison.png'), dpi=150)
plt.close()

# Language comparison
langs = list(ml_results.keys())
fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(len(langs))
vals_topic = [ml_results[l]['topic_accuracy'] for l in langs]
vals_sim = [ml_results[l]['avg_similarity'] for l in langs]
vals_self = [ml_results[l]['self_recall_at_1'] for l in langs]
width = 0.25
ax.bar(x - width, vals_self, width, label='Self Recall@1', color='#0EA5E9')
ax.bar(x, vals_topic, width, label='Topic Accuracy', color='#14B8A6')
ax.bar(x + width, vals_sim, width, label='Avg Similarity', color='#8B5CF6')
ax.set_xticks(x)
ax.set_xticklabels(langs)
ax.set_ylabel('Score')
ax.set_title('Per-Language Retrieval Performance')
ax.legend()
ax.set_ylim(0, 1.05)
plt.tight_layout()
plt.savefig(str(FIGURES_DIR / 'language_comparison.png'), dpi=150)
plt.close()

# ── Save updated results ──
results_path = RESULTS_DIR / 'all_experiment_results.json'
with open(results_path, 'r', encoding='utf-8') as f:
    all_results = json.load(f)

all_results['retrieval'] = self_results
all_results['retrieval_cross'] = cross_results
all_results['multilingual'] = ml_results

with open(results_path, 'w', encoding='utf-8') as f:
    json.dump(all_results, f, indent=2, default=str, ensure_ascii=False)

print(f"\n{'='*60}")
print("  EVALUATION COMPLETE")
print(f"{'='*60}")
print(f"  Self-retrieval (train→train): TF-IDF R@1={self_results['tfidf']['recall_at_1']:.3f}, Dense R@1={self_results['dense']['recall_at_1']:.3f}, Hybrid R@1={self_results['hybrid']['recall_at_1']:.3f}")
print(f"  Cross-retrieval topic accuracy: {cross_results['hybrid']['topic_accuracy']:.3f}")
print(f"  Classification: intent={all_results['classification']['intent_test']['accuracy']:.3f}, topic={all_results['classification']['topic_test']['accuracy']:.3f}, safety={all_results['classification']['safety_test']['accuracy']:.3f}")
