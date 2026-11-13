import sys
import pandas as pd
import json
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.data.loader import load_config

def validate(df):
    report = {
        'total': len(df),
        'missing_q': df['question'].isna().sum().item(),
        'missing_a': df['answer'].isna().sum().item(),
        'duplicates': df['question'].duplicated().sum().item(),
        'single_letter_a': df['answer'].astype(str).apply(lambda x: len(x.strip()) == 1).sum().item(),
        'invalid_label': 0 # simplified
    }
    return report

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    config = load_config()
    
    norm_df = pd.read_csv(Path(config['paths']['interim_data_dir']) / config['data']['normalized_file'])
    aug_df = pd.read_csv(Path(config['paths']['interim_data_dir']) / config['data']['augmented_file'])
    
    report = {
        'normalized': validate(norm_df),
        'augmented': validate(aug_df)
    }
    
    out_dir = Path(config['paths']['experiments_dir']) / 'raw_results'
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / 'validation_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=4)
        
    print("Validation complete. Report saved.")

if __name__ == '__main__':
    main()
