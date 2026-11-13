import sys
import pandas as pd
import json
import matplotlib.pyplot as plt
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.data.loader import load_config

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    config = load_config()
    
    norm_df = pd.read_csv(Path(config['paths']['interim_data_dir']) / config['data']['normalized_file'])
    aug_df = pd.read_csv(Path(config['paths']['interim_data_dir']) / config['data']['augmented_file'])
    df = pd.concat([norm_df, aug_df], ignore_index=True)
    
    stats = {
        'total_records': len(df),
        'language_dist': df['language'].value_counts().to_dict(),
        'topic_dist': df['topic'].value_counts().to_dict(),
        'intent_dist': df['intent'].value_counts().to_dict(),
        'safety_dist': df['safety_category'].value_counts().to_dict(),
        'origin_dist': df['data_origin'].value_counts().to_dict(),
        'q_len_mean': df['question'].str.len().mean(),
    }
    
    out_dir = Path(config['paths']['experiments_dir']) / 'raw_results'
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / 'dataset_statistics.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=4)
        
    fig_dir = Path(config['paths']['figures_dir'])
    fig_dir.mkdir(parents=True, exist_ok=True)
    
    def plot_dist(col, filename):
        if col in df.columns:
            plt.figure(figsize=(10, 6))
            df[col].value_counts().plot(kind='bar')
            plt.title(f'{col} distribution')
            plt.tight_layout()
            plt.savefig(fig_dir / filename)
            plt.close()
            
    plot_dist('language', 'language_distribution.png')
    plot_dist('topic', 'topic_distribution.png')
    plot_dist('intent', 'intent_distribution.png')
    plot_dist('safety_category', 'safety_distribution.png')
    plot_dist('answer_type', 'answer_type_distribution.png')
    
    print("Statistics and charts generated.")

if __name__ == '__main__':
    main()
