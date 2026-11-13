"""Group-aware train/validation/test split for MediRAG-BD."""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import GroupShuffleSplit
from src.data.loader import load_config


def main():
    config = load_config()
    final_path = Path(config['paths']['processed_data_dir']) / config['data']['final_file']
    df = pd.read_csv(final_path, encoding='utf-8')
    print(f"Loaded final dataset: {len(df)} records")

    seed = config['project']['random_seed']
    train_r = config['splitting']['train_ratio']
    val_r = config['splitting']['validation_ratio']
    group_col = config['splitting']['group_column']

    # Fill missing variant_group_id with question_id
    df[group_col] = df[group_col].fillna(df['question_id'])

    groups = df[group_col].values

    # First split: train+val vs test
    gss1 = GroupShuffleSplit(n_splits=1, test_size=1 - train_r, random_state=seed)
    train_idx, temp_idx = next(gss1.split(df, groups=groups))

    train_df = df.iloc[train_idx]
    temp_df = df.iloc[temp_idx]
    temp_groups = temp_df[group_col].values

    # Second split: val vs test from temp
    test_ratio_of_temp = config['splitting']['test_ratio'] / (val_r + config['splitting']['test_ratio'])
    gss2 = GroupShuffleSplit(n_splits=1, test_size=test_ratio_of_temp, random_state=seed)
    val_idx_local, test_idx_local = next(gss2.split(temp_df, groups=temp_groups))

    val_df = temp_df.iloc[val_idx_local]
    test_df = temp_df.iloc[test_idx_local]

    # Save splits
    splits_dir = Path(config['paths']['splits_dir'])
    splits_dir.mkdir(parents=True, exist_ok=True)

    train_df.to_csv(splits_dir / 'train.csv', index=False, encoding='utf-8')
    val_df.to_csv(splits_dir / 'validation.csv', index=False, encoding='utf-8')
    test_df.to_csv(splits_dir / 'test.csv', index=False, encoding='utf-8')

    print(f"\nSplit results:")
    print(f"  Train: {len(train_df)} ({len(train_df)/len(df)*100:.1f}%)")
    print(f"  Validation: {len(val_df)} ({len(val_df)/len(df)*100:.1f}%)")
    print(f"  Test: {len(test_df)} ({len(test_df)/len(df)*100:.1f}%)")

    # Leakage check
    train_groups = set(train_df[group_col].unique())
    val_groups = set(val_df[group_col].unique())
    test_groups = set(test_df[group_col].unique())

    tv_leak = train_groups & val_groups
    tt_leak = train_groups & test_groups
    vt_leak = val_groups & test_groups

    print(f"\nLeakage check:")
    print(f"  Train-Val group overlap: {len(tv_leak)}")
    print(f"  Train-Test group overlap: {len(tt_leak)}")
    print(f"  Val-Test group overlap: {len(vt_leak)}")

    if len(tv_leak) == 0 and len(tt_leak) == 0 and len(vt_leak) == 0:
        print("  ✓ No group leakage detected!")
    else:
        print("  ⚠ Group leakage detected!")

    # Per-split distribution
    for name, split_df in [('Train', train_df), ('Val', val_df), ('Test', test_df)]:
        print(f"\n{name} distribution:")
        print(f"  Languages: {split_df['language'].value_counts().to_dict()}")
        print(f"  Safety: {split_df['safety_category'].value_counts().to_dict()}")
        print(f"  Origins: {split_df['data_origin'].value_counts().to_dict()}")


if __name__ == '__main__':
    main()
