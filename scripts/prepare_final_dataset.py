import sys
import pandas as pd
from pathlib import Path
import subprocess
sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.data.loader import load_config

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    config = load_config()
    
    # Load and combine
    norm_path = Path(config['paths']['interim_data_dir']) / config['data']['normalized_file']
    aug_path = Path(config['paths']['interim_data_dir']) / config['data']['augmented_file']
    
    norm_df = pd.read_csv(norm_path)
    aug_df = pd.read_csv(aug_path)
    final_df = pd.concat([norm_df, aug_df], ignore_index=True)
    
    out_dir = Path(config['paths']['processed_data_dir'])
    out_dir.mkdir(parents=True, exist_ok=True)
    final_path = out_dir / config['data']['final_file']
    final_df.to_csv(final_path, index=False, encoding='utf-8')
    print(f"Final dataset saved to {final_path} with {len(final_df)} records.")
    
    # Run subsequent scripts
    print("Running validation...")
    subprocess.run([sys.executable, "scripts/validate_dataset.py"])
    
    print("Running statistics...")
    subprocess.run([sys.executable, "scripts/dataset_statistics.py"])
    
    print("Running splitting...")
    subprocess.run([sys.executable, "scripts/split_dataset.py"])
    
    print("Pipeline complete.")

if __name__ == '__main__':
    main()
