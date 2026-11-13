import sys
import pandas as pd
import yaml
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.data.loader import merge_datasets, load_config

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    config = load_config()
    df = merge_datasets()
    
    # Normalize schema
    required_cols = ['question_id', 'variant_group_id', 'question', 'language', 'topic', 'intent', 
                     'question_type', 'safety_category', 'answer', 'answer_type', 'evidence_text', 
                     'evidence_id', 'document_id', 'section', 'source', 'subject', 'difficulty', 
                     'data_origin', 'annotation_status']
    
    for col in required_cols:
        if col not in df.columns:
            df[col] = None
            
    # Derive question_type
    df.loc[df['question'].str.len() > 300, 'question_type'] = 'clinical_vignette'
    df.loc[df['question'].str.len() <= 300, 'question_type'] = 'direct_question'
    if 'source' in df.columns:
        df.loc[df['source'] == 'BanglaMedQA', 'question_type'] = 'mcq'
    
    # Ensure safety category
    df['safety_category'] = df['safety_category'].fillna('SAFE_GENERAL_INFORMATION')
    
    # Derive answer type
    def get_ans_type(ans):
        if pd.isna(ans): return 'short_answer'
        ans = str(ans)
        if len(ans) == 1 and ans.upper() in ['A', 'B', 'C', 'D', 'E']: return 'mcq_letter'
        if len(ans) < 50: return 'short_answer'
        return 'explanatory'
    
    df['answer_type'] = df['answer'].apply(get_ans_type)
    
    # Defaults
    df['data_origin'] = df['data_origin'].fillna('ORIGINAL')
    df['annotation_status'] = 'auto_labeled'
    
    # Keep only schema cols
    df = df[required_cols]
    
    out_dir = Path(config['paths']['interim_data_dir'])
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / config['data']['normalized_file']
    
    df.to_csv(out_path, index=False, encoding='utf-8')
    print(f"Normalized dataset saved to {out_path} with {len(df)} records.")

if __name__ == '__main__':
    main()
