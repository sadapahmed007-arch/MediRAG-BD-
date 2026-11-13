import pandas as pd
import yaml
from pathlib import Path

def load_config(config_path="configs/config.yaml"):
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_primary_dataset():
    config = load_config()
    raw_dir = Path(config["paths"]["raw_data_dir"])
    primary_file = config["data"]["raw_files"]["primary"]
    return pd.read_csv(raw_dir / primary_file)

def load_secondary_dataset():
    config = load_config()
    raw_dir = Path(config["paths"]["raw_data_dir"])
    secondary_file = config["data"]["raw_files"]["secondary"]
    return pd.read_csv(raw_dir / secondary_file)

def merge_datasets():
    primary_df = load_primary_dataset()
    secondary_df = load_secondary_dataset()
    
    # secondary contains expanded BanglaMedQA answers instead of single letter.
    # also contains MedMCQA, RealMedQA.
    # We should merge intelligently. Let's use question to align or just take all unique records.
    # Assuming primary has BanglaMedQA with single-letter answers. 
    # To replace BanglaMedQA answers from primary with secondary where available:
    # Actually, let's keep all secondary, and then only add primary rows that don't match exactly by 'question' 
    # to avoid duplicates.
    
    # Add data_origin if missing
    if 'data_origin' not in primary_df.columns:
        primary_df['data_origin'] = 'ORIGINAL'
    if 'data_origin' not in secondary_df.columns:
        secondary_df['data_origin'] = 'ORIGINAL'
        
    # Standardize column names if needed
    merged = pd.concat([primary_df, secondary_df], ignore_index=True).drop_duplicates(subset=['question'], keep='last')
    
    # Regenerate question_id uniquely
    merged['question_id'] = [f"Q_{i:06d}" for i in range(len(merged))]
    
    return merged
