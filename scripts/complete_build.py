"""Complete remaining build: FAISS index + experiments + all results."""
import sys, os, json, time
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.metrics import confusion_matrix

from src.data.loader import load_config
from src.evaluation.metrics import batch_recall_at_k, batch_mrr

config = load_config()
MODELS_DIR = Path(config['paths']['models_dir'])
IDX_DIR = Path(config['paths']['indexes_dir'])
RESULTS_DIR = Path(config['paths']['experiments_dir']) / 'raw_results'
FIGURES_DIR = Path(config['paths']['experiments_dir']) / 'figures'
for d in [MODELS_DIR, IDX_DIR, RESULTS_DIR, FIGURES_DIR]:
    d.mkdir(parents=True, exist_ok=True)

splits_dir = Path(config['paths']['splits_dir'])
train_df = pd.read_csv(splits_dir / 'train.csv', encoding='utf-8')
val_df = pd.read_csv(splits_dir / 'validation.csv', encoding='utf-8')
test_df = pd.read_csv(splits_dir / 'test.csv', encoding='utf-8')
for df in [train_df, val_df, test_df]:
    df['answer'] = df['answer'].fillna('')
    df['question'] = df['question'].fillna('')
print(f"Loaded splits: train={len(train_df)}, val={len(val_df)}, test={len(test_df)}")

train_docs = train_df.to_dict('records')

# ── Step 1: Build FAISS index if missing ──
faiss_path = str(IDX_DIR / 'faiss_index.bin')
if not os.path.exists(faiss_path):
    print("\n[1/5] Building FAISS dense index...")
    from src.retrieval.dense_retrieval import DenseRetriever
    dense_ret = DenseRetriever(config['embeddings']['model_name'])
    dense_ret.build_index(train_docs, text_field='question')
    dense_ret.save(faiss_path,
                   str(IDX_DIR / 'faiss_docs.pkl'),
                   str(IDX_DIR / 'faiss_embeddings.npy'))
    print(f"  FAISS index saved: {dense_ret.index.ntotal} vectors")
else:
    print("\n[1/5] FAISS index exists, loading...")
    from src.retrieval.dense_retrieval import DenseRetriever
    dense_ret = DenseRetriever(config['embeddings']['model_name'])
    dense_ret.load(faiss_path, str(IDX_DIR / 'faiss_docs.pkl'))
    print(f"  Loaded FAISS index: {dense_ret.index.ntotal} vectors")

# Load TF-IDF retriever
from src.retrieval.tfidf_retrieval import TFIDFRetriever
tfidf_ret = TFIDFRetriever()
tfidf_ret.load(str(IDX_DIR / 'tfidf_vectorizer.pkl'),
               str(IDX_DIR / 'tfidf_matrix.pkl'),
               str(IDX_DIR / 'tfidf_docs.pkl'))

from src.retrieval.hybrid_retrieval import HybridRetriever
hybrid_ret = HybridRetriever(tfidf_ret, dense_ret, alpha=config['retrieval']['hybrid']['alpha'])

# ── Step 2: Retrieval experiments ──
print("\n[2/5] Running retrieval experiments...")
test_sample = test_df.sample(n=min(400, len(test_df)), random_state=42)
ret_results = {}

for method_name, retriever in [('tfidf', tfidf_ret), ('dense', dense_ret), ('hybrid', hybrid_ret)]:
    print(f"  Evaluating {method_name}...")
    all_ret_ids, all_gt, latencies = [], [], []
    for _, row in test_sample.iterrows():
        t0 = time.time()
        results = retriever.search(row['question'], top_k=10)
        latencies.append(time.time() - t0)
        all_ret_ids.append([r.get('question_id', '') for r in results])
        all_gt.append(row['question_id'])

    r1 = batch_recall_at_k(all_ret_ids, all_gt, 1)
    r3 = batch_recall_at_k(all_ret_ids, all_gt, 3)
    r5 = batch_recall_at_k(all_ret_ids, all_gt, 5)
    m = batch_mrr(all_ret_ids, all_gt)
    lat = np.mean(latencies) * 1000

    ret_results[method_name] = {'recall_at_1': r1, 'recall_at_3': r3, 'recall_at_5': r5,
                                 'mrr': m, 'avg_latency_ms': round(lat, 1)}
    print(f"    R@1={r1:.3f} R@3={r3:.3f} R@5={r5:.3f} MRR={m:.3f} lat={lat:.0f}ms")

# ── Step 3: Per-language experiments ──
print("\n[3/5] Running per-language experiments...")
ml_results = {}
for lang in ['english', 'bangla', 'banglish', 'code_mixed']:
    lang_df = test_df[test_df['language'] == lang]
    if len(lang_df) == 0:
        continue
    sample = lang_df.sample(n=min(80, len(lang_df)), random_state=42)
    all_ret, all_gt = [], []
    for _, row in sample.iterrows():
        res = dense_ret.search(row['question'], top_k=5)
        all_ret.append([r.get('question_id', '') for r in res])
        all_gt.append(row['question_id'])
    r1 = batch_recall_at_k(all_ret, all_gt, 1)
    r3 = batch_recall_at_k(all_ret, all_gt, 3)
    r5 = batch_recall_at_k(all_ret, all_gt, 5)
    m = batch_mrr(all_ret, all_gt)
    ml_results[lang] = {'n': len(sample), 'recall_at_1': r1, 'recall_at_3': r3,
                         'recall_at_5': r5, 'mrr': m}
    print(f"  {lang} (n={len(sample)}): R@1={r1:.3f} R@3={r3:.3f} MRR={m:.3f}")

# ── Step 4: Classification results (already trained) ──
print("\n[4/5] Loading classification results...")
from src.classification.classifier import TextClassifier
from src.safety.classifier import SafetyClassifier

cls_results = {}
for task in ['intent', 'topic']:
    clf = TextClassifier()
    clf.load(str(MODELS_DIR / f'{task}_model.pkl'), str(MODELS_DIR / f'{task}_vectorizer.pkl'))
    eval_r = clf.evaluate(test_df['question'].tolist(), test_df[task].tolist())
    cls_results[f'{task}_test'] = {'accuracy': eval_r['accuracy']}
    macro_f1 = eval_r['classification_report'].get('macro avg', {}).get('f1-score', 0)
    cls_results[f'{task}_test']['macro_f1'] = macro_f1
    print(f"  {task}: accuracy={eval_r['accuracy']:.4f}, macro-F1={macro_f1:.4f}")

safety_clf = SafetyClassifier()
safety_clf.load(str(MODELS_DIR / 'safety_model.pkl'), str(MODELS_DIR / 'safety_vectorizer.pkl'))
safety_eval = safety_clf.evaluate(test_df['question'].tolist(), test_df['safety_category'].tolist())
cls_results['safety_test'] = {'accuracy': safety_eval['accuracy']}
print(f"  safety: accuracy={safety_eval['accuracy']:.4f}")

# ── Step 5: Generate all figures and save results ──
print("\n[5/5] Generating figures...")
final_df = pd.read_csv(Path(config['paths']['processed_data_dir']) / config['data']['final_file'], encoding='utf-8')
ds_stats = {
    'total_records': len(final_df),
    'languages': final_df['language'].value_counts().to_dict(),
    'topics': final_df['topic'].value_counts().to_dict(),
    'intents': final_df['intent'].value_counts().to_dict(),
    'safety_categories': final_df['safety_category'].value_counts().to_dict(),
    'data_origins': final_df['data_origin'].value_counts().to_dict(),
    'sources': final_df['source'].value_counts().to_dict(),
    'avg_question_length': round(float(final_df['question'].str.len().mean()), 1),
    'median_question_length': round(float(final_df['question'].str.len().median()), 1),
    'avg_answer_length': round(float(final_df['answer'].dropna().str.len().mean()), 1),
    'unique_variant_groups': int(final_df['variant_group_id'].nunique()),
}

# Distribution charts
for col, title, color in [('language', 'Language Distribution', '#0EA5E9'),
                            ('topic', 'Topic Distribution', '#14B8A6'),
                            ('intent', 'Intent Distribution', '#8B5CF6'),
                            ('safety_category', 'Safety Distribution', '#10B981')]:
    fig, ax = plt.subplots(figsize=(10, 5))
    final_df[col].value_counts().plot(kind='barh', ax=ax, color=color)
    ax.set_title(title, fontsize=14)
    plt.tight_layout()
    plt.savefig(str(FIGURES_DIR / f'{col}_distribution.png'), dpi=150)
    plt.close()

# Retrieval comparison chart
methods = list(ret_results.keys())
metrics_names = ['recall_at_1', 'recall_at_3', 'recall_at_5', 'mrr']
x = np.arange(len(metrics_names))
width = 0.25
fig, ax = plt.subplots(figsize=(10, 6))
colors = ['#0EA5E9', '#14B8A6', '#8B5CF6']
for i, method in enumerate(methods):
    vals = [ret_results[method][m] for m in metrics_names]
    ax.bar(x + i * width, vals, width, label=method.upper(), color=colors[i])
ax.set_xticks(x + width)
ax.set_xticklabels(['Recall@1', 'Recall@3', 'Recall@5', 'MRR'])
ax.set_ylabel('Score')
ax.set_title('Retrieval Method Comparison')
ax.legend()
ax.set_ylim(0, 1.05)
plt.tight_layout()
plt.savefig(str(FIGURES_DIR / 'retrieval_comparison.png'), dpi=150)
plt.close()

# Language comparison chart
if ml_results:
    langs = list(ml_results.keys())
    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(langs))
    width = 0.2
    for i, m in enumerate(metrics_names):
        vals = [ml_results[l][m] for l in langs]
        ax.bar(x + i * width, vals, width, label=m)
    ax.set_xticks(x + 1.5 * width)
    ax.set_xticklabels(langs)
    ax.set_ylabel('Score')
    ax.set_title('Per-Language Retrieval Performance')
    ax.legend()
    ax.set_ylim(0, 1.05)
    plt.tight_layout()
    plt.savefig(str(FIGURES_DIR / 'language_comparison.png'), dpi=150)
    plt.close()

# Save all results
all_results = {
    'dataset_stats': ds_stats,
    'classification': cls_results,
    'retrieval': ret_results,
    'multilingual': ml_results,
}
with open(str(RESULTS_DIR / 'all_experiment_results.json'), 'w', encoding='utf-8') as f:
    json.dump(all_results, f, indent=2, default=str, ensure_ascii=False)

print(f"\n{'='*60}")
print("  ALL BUILD STEPS COMPLETE")
print(f"{'='*60}")
print(f"  Dataset: {ds_stats['total_records']} records")
print(f"  Models: intent, topic, safety classifiers saved")
print(f"  Indexes: TF-IDF + FAISS saved")
print(f"  Results: {RESULTS_DIR / 'all_experiment_results.json'}")
print(f"  Figures: {len(list(FIGURES_DIR.glob('*.png')))} charts generated")
