"""
Master build script: trains all classifiers, builds all indexes, runs all experiments.
This is the single script that takes the project from data -> trained models -> results.
"""
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
from sklearn.metrics import confusion_matrix, classification_report, ConfusionMatrixDisplay

from src.data.loader import load_config
from src.classification.classifier import TextClassifier
from src.safety.classifier import SafetyClassifier
from src.preprocessing.text_processor import preprocess_question
from src.language.detector import detect_language
from src.evaluation.metrics import (
    batch_recall_at_k, batch_mrr, top_k_accuracy, classification_metrics
)

config = load_config()
MODELS_DIR = Path(config['paths']['models_dir'])
RESULTS_DIR = Path(config['paths']['experiments_dir']) / 'raw_results'
FIGURES_DIR = Path(config['paths']['experiments_dir']) / 'figures'
MODELS_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def load_splits():
    splits_dir = Path(config['paths']['splits_dir'])
    train = pd.read_csv(splits_dir / 'train.csv', encoding='utf-8')
    val = pd.read_csv(splits_dir / 'validation.csv', encoding='utf-8')
    test = pd.read_csv(splits_dir / 'test.csv', encoding='utf-8')
    # Fill NaN answers
    for df in [train, val, test]:
        df['answer'] = df['answer'].fillna('')
        df['question'] = df['question'].fillna('')
    return train, val, test


def train_classifiers(train_df, val_df, test_df):
    """Train intent, topic, and safety classifiers."""
    results = {}

    for task in ['intent', 'topic']:
        print(f"\n{'='*60}")
        print(f"Training {task} classifier...")
        print(f"{'='*60}")

        best_acc = 0
        best_type = None

        for clf_type in ['logistic_regression', 'svm']:
            clf = TextClassifier(classifier_type=clf_type, max_features=10000, ngram_range=(1, 2))
            clf.fit(train_df['question'].tolist(), train_df[task].tolist())
            eval_result = clf.evaluate(val_df['question'].tolist(), val_df[task].tolist())
            print(f"  {clf_type}: accuracy={eval_result['accuracy']:.4f}")

            if eval_result['accuracy'] > best_acc:
                best_acc = eval_result['accuracy']
                best_type = clf_type
                best_clf = clf
                best_eval = eval_result

        # Save best model
        best_clf.save(str(MODELS_DIR / f'{task}_model.pkl'),
                      str(MODELS_DIR / f'{task}_vectorizer.pkl'))
        print(f"  Best: {best_type} (accuracy={best_acc:.4f})")

        # Evaluate on test set
        test_eval = best_clf.evaluate(test_df['question'].tolist(), test_df[task].tolist())
        results[f'{task}_val'] = best_eval
        results[f'{task}_test'] = test_eval
        results[f'{task}_best_model'] = best_type

        # Confusion matrix
        preds = best_clf.predict(test_df['question'].tolist())
        labels = sorted(test_df[task].unique())
        cm = confusion_matrix(test_df[task].tolist(), preds, labels=labels)
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', xticklabels=labels, yticklabels=labels,
                   cmap='Blues', ax=ax)
        ax.set_xlabel('Predicted')
        ax.set_ylabel('True')
        ax.set_title(f'{task.title()} Classification Confusion Matrix')
        plt.tight_layout()
        plt.savefig(str(FIGURES_DIR / f'{task}_confusion_matrix.png'), dpi=150)
        plt.close()

    # Safety classifier
    print(f"\n{'='*60}")
    print("Training safety classifier...")
    print(f"{'='*60}")
    safety_clf = SafetyClassifier()
    safety_clf.fit(train_df['question'].tolist(), train_df['safety_category'].tolist())
    safety_clf.save(str(MODELS_DIR / 'safety_model.pkl'),
                    str(MODELS_DIR / 'safety_vectorizer.pkl'))

    safety_val = safety_clf.evaluate(val_df['question'].tolist(), val_df['safety_category'].tolist())
    safety_test = safety_clf.evaluate(test_df['question'].tolist(), test_df['safety_category'].tolist())
    print(f"  Safety val accuracy: {safety_val['accuracy']:.4f}")
    print(f"  Safety test accuracy: {safety_test['accuracy']:.4f}")
    results['safety_val'] = safety_val
    results['safety_test'] = safety_test

    return results


def build_retrieval_indexes(train_df):
    """Build TF-IDF and FAISS indexes from training data."""
    from src.retrieval.tfidf_retrieval import TFIDFRetriever
    from src.retrieval.dense_retrieval import DenseRetriever

    # Prepare documents
    docs = train_df.to_dict('records')

    # TF-IDF index
    print(f"\n{'='*60}")
    print("Building TF-IDF index...")
    print(f"{'='*60}")
    tfidf_ret = TFIDFRetriever(max_features=20000, ngram_range=(1, 2))
    tfidf_ret.build_index(docs, text_field='question')
    idx_dir = Path(config['paths']['indexes_dir'])
    idx_dir.mkdir(parents=True, exist_ok=True)
    tfidf_ret.save(str(idx_dir / 'tfidf_vectorizer.pkl'),
                   str(idx_dir / 'tfidf_matrix.pkl'),
                   str(idx_dir / 'tfidf_docs.pkl'))
    print(f"  TF-IDF index saved ({len(docs)} documents)")

    # Dense index
    print(f"\n{'='*60}")
    print("Building FAISS dense index...")
    print(f"{'='*60}")
    dense_ret = DenseRetriever(config['embeddings']['model_name'])
    dense_ret.build_index(docs, text_field='question')
    dense_ret.save(str(idx_dir / 'faiss_index.bin'),
                   str(idx_dir / 'faiss_docs.pkl'),
                   str(idx_dir / 'faiss_embeddings.npy'))
    print(f"  FAISS index saved ({dense_ret.index.ntotal} vectors)")

    return tfidf_ret, dense_ret


def run_retrieval_experiments(tfidf_ret, dense_ret, test_df):
    """Run all retrieval experiments."""
    from src.retrieval.hybrid_retrieval import HybridRetriever

    hybrid_ret = HybridRetriever(tfidf_ret, dense_ret, alpha=config['retrieval']['hybrid']['alpha'])
    results = {}
    top_k = 10

    # Sample test queries (limit for speed)
    test_sample = test_df.sample(n=min(500, len(test_df)), random_state=42)

    for method_name, retriever in [('tfidf', tfidf_ret), ('dense', dense_ret), ('hybrid', hybrid_ret)]:
        print(f"\n{'='*60}")
        print(f"Evaluating {method_name} retrieval...")
        print(f"{'='*60}")

        all_retrieved_ids = []
        all_ground_truth = []
        latencies = []

        for _, row in test_sample.iterrows():
            query = row['question']
            gt_id = row['question_id']

            t0 = time.time()
            results_list = retriever.search(query, top_k=top_k)
            latencies.append(time.time() - t0)

            retrieved_ids = [r.get('question_id', '') for r in results_list]
            all_retrieved_ids.append(retrieved_ids)
            all_ground_truth.append(gt_id)

        r1 = batch_recall_at_k(all_retrieved_ids, all_ground_truth, 1)
        r3 = batch_recall_at_k(all_retrieved_ids, all_ground_truth, 3)
        r5 = batch_recall_at_k(all_retrieved_ids, all_ground_truth, 5)
        m = batch_mrr(all_retrieved_ids, all_ground_truth)
        avg_lat = np.mean(latencies) * 1000  # ms

        print(f"  Recall@1: {r1:.4f}")
        print(f"  Recall@3: {r3:.4f}")
        print(f"  Recall@5: {r5:.4f}")
        print(f"  MRR: {m:.4f}")
        print(f"  Avg latency: {avg_lat:.1f}ms")

        results[method_name] = {
            'recall_at_1': r1, 'recall_at_3': r3, 'recall_at_5': r5,
            'mrr': m, 'avg_latency_ms': avg_lat,
        }

    return results


def run_multilingual_experiment(dense_ret, test_df):
    """Per-language retrieval evaluation."""
    print(f"\n{'='*60}")
    print("Multilingual retrieval comparison...")
    print(f"{'='*60}")

    results = {}
    for lang in ['english', 'bangla', 'banglish', 'code_mixed']:
        lang_df = test_df[test_df['language'] == lang]
        if len(lang_df) == 0:
            continue
        sample = lang_df.sample(n=min(100, len(lang_df)), random_state=42)

        all_ret = []
        all_gt = []
        for _, row in sample.iterrows():
            res = dense_ret.search(row['question'], top_k=5)
            all_ret.append([r.get('question_id', '') for r in res])
            all_gt.append(row['question_id'])

        r1 = batch_recall_at_k(all_ret, all_gt, 1)
        r3 = batch_recall_at_k(all_ret, all_gt, 3)
        r5 = batch_recall_at_k(all_ret, all_gt, 5)
        m = batch_mrr(all_ret, all_gt)

        print(f"  {lang} (n={len(sample)}): R@1={r1:.3f} R@3={r3:.3f} R@5={r5:.3f} MRR={m:.3f}")
        results[lang] = {'n': len(sample), 'recall_at_1': r1, 'recall_at_3': r3,
                         'recall_at_5': r5, 'mrr': m}

    return results


def generate_figures(cls_results, ret_results, ml_results):
    """Generate all experiment figures from actual data."""
    # Load final dataset for distribution charts
    final_df = pd.read_csv(Path(config['paths']['processed_data_dir']) / config['data']['final_file'],
                          encoding='utf-8')

    # Language distribution
    fig, ax = plt.subplots(figsize=(8, 5))
    final_df['language'].value_counts().plot(kind='bar', ax=ax, color=['#0EA5E9', '#14B8A6', '#8B5CF6', '#F59E0B'])
    ax.set_title('Language Distribution')
    ax.set_ylabel('Count')
    plt.tight_layout()
    plt.savefig(str(FIGURES_DIR / 'language_distribution.png'), dpi=150)
    plt.close()

    # Topic distribution
    fig, ax = plt.subplots(figsize=(10, 5))
    final_df['topic'].value_counts().plot(kind='barh', ax=ax, color='#0EA5E9')
    ax.set_title('Topic Distribution')
    plt.tight_layout()
    plt.savefig(str(FIGURES_DIR / 'topic_distribution.png'), dpi=150)
    plt.close()

    # Intent distribution
    fig, ax = plt.subplots(figsize=(10, 5))
    final_df['intent'].value_counts().plot(kind='barh', ax=ax, color='#14B8A6')
    ax.set_title('Intent Distribution')
    plt.tight_layout()
    plt.savefig(str(FIGURES_DIR / 'intent_distribution.png'), dpi=150)
    plt.close()

    # Safety distribution
    fig, ax = plt.subplots(figsize=(8, 5))
    final_df['safety_category'].value_counts().plot(kind='bar', ax=ax,
        color=['#10B981', '#F59E0B', '#EF4444', '#6B7280'])
    ax.set_title('Safety Category Distribution')
    plt.tight_layout()
    plt.savefig(str(FIGURES_DIR / 'safety_distribution.png'), dpi=150)
    plt.close()

    # Retrieval comparison
    if ret_results:
        methods = list(ret_results.keys())
        metrics_names = ['recall_at_1', 'recall_at_3', 'recall_at_5', 'mrr']
        x = np.arange(len(metrics_names))
        width = 0.25
        fig, ax = plt.subplots(figsize=(10, 6))
        for i, method in enumerate(methods):
            vals = [ret_results[method][m] for m in metrics_names]
            ax.bar(x + i * width, vals, width, label=method.upper())
        ax.set_xticks(x + width)
        ax.set_xticklabels(['Recall@1', 'Recall@3', 'Recall@5', 'MRR'])
        ax.set_ylabel('Score')
        ax.set_title('Retrieval Method Comparison')
        ax.legend()
        ax.set_ylim(0, 1.05)
        plt.tight_layout()
        plt.savefig(str(FIGURES_DIR / 'retrieval_comparison.png'), dpi=150)
        plt.close()

    # Multilingual comparison
    if ml_results:
        langs = list(ml_results.keys())
        fig, ax = plt.subplots(figsize=(8, 5))
        metrics_names = ['recall_at_1', 'recall_at_3', 'recall_at_5', 'mrr']
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


def generate_dataset_stats():
    """Generate dataset statistics."""
    final_df = pd.read_csv(Path(config['paths']['processed_data_dir']) / config['data']['final_file'],
                          encoding='utf-8')
    stats = {
        'total_records': len(final_df),
        'languages': final_df['language'].value_counts().to_dict(),
        'topics': final_df['topic'].value_counts().to_dict(),
        'intents': final_df['intent'].value_counts().to_dict(),
        'safety_categories': final_df['safety_category'].value_counts().to_dict(),
        'data_origins': final_df['data_origin'].value_counts().to_dict(),
        'sources': final_df['source'].value_counts().to_dict(),
        'avg_question_length': float(final_df['question'].str.len().mean()),
        'median_question_length': float(final_df['question'].str.len().median()),
        'avg_answer_length': float(final_df['answer'].dropna().str.len().mean()),
        'unique_variant_groups': int(final_df['variant_group_id'].nunique()),
        'answer_types': final_df['answer_type'].value_counts().to_dict() if 'answer_type' in final_df.columns else {},
    }
    with open(str(RESULTS_DIR / 'dataset_statistics.json'), 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(f"\nDataset statistics saved. Total records: {stats['total_records']}")
    return stats


def main():
    print("="*70)
    print("  MediRAG-BD: COMPLETE BUILD & EXPERIMENT PIPELINE")
    print("="*70)
    start_time = time.time()

    # Load data
    print("\n[1/7] Loading data splits...")
    train_df, val_df, test_df = load_splits()
    print(f"  Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")

    # Dataset stats
    print("\n[2/7] Generating dataset statistics...")
    ds_stats = generate_dataset_stats()

    # Train classifiers
    print("\n[3/7] Training classifiers...")
    cls_results = train_classifiers(train_df, val_df, test_df)

    # Build indexes
    print("\n[4/7] Building retrieval indexes...")
    tfidf_ret, dense_ret = build_retrieval_indexes(train_df)

    # Run retrieval experiments
    print("\n[5/7] Running retrieval experiments...")
    ret_results = run_retrieval_experiments(tfidf_ret, dense_ret, test_df)

    # Run multilingual experiment
    print("\n[6/7] Running multilingual experiment...")
    ml_results = run_multilingual_experiment(dense_ret, test_df)

    # Generate figures
    print("\n[7/7] Generating figures...")
    generate_figures(cls_results, ret_results, ml_results)

    # Save all results
    all_results = {
        'dataset_stats': ds_stats,
        'classification': {k: {kk: vv for kk, vv in v.items() if kk != 'confusion_matrix'}
                          if isinstance(v, dict) else v
                          for k, v in cls_results.items()},
        'retrieval': ret_results,
        'multilingual': ml_results,
        'build_time_seconds': time.time() - start_time,
    }

    with open(str(RESULTS_DIR / 'all_experiment_results.json'), 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, default=str, ensure_ascii=False)

    elapsed = time.time() - start_time
    print(f"\n{'='*70}")
    print(f"  BUILD COMPLETE in {elapsed:.1f}s ({elapsed/60:.1f} min)")
    print(f"{'='*70}")
    print(f"\nResults saved to: {RESULTS_DIR}")
    print(f"Figures saved to: {FIGURES_DIR}")
    print(f"Models saved to: {MODELS_DIR}")


if __name__ == '__main__':
    main()
