"""Create the complete MediRAG-BD project directory structure."""
import os
import shutil

BASE = r"i:\NLP\medirag-bd"

# Directory tree
dirs = [
    "data/raw", "data/interim", "data/processed", "data/splits", "data/indexes",
    "models",
    "configs",
    "src/data", "src/preprocessing", "src/language", "src/classification",
    "src/embeddings", "src/retrieval", "src/safety", "src/evaluation",
    "scripts",
    "app/backend", "app/frontend",
    "experiments/raw_results", "experiments/processed_results",
    "experiments/figures", "experiments/tables",
    "notebooks", "tests", "docs",
]

for d in dirs:
    os.makedirs(os.path.join(BASE, d), exist_ok=True)

# Create __init__.py files for all Python packages
init_dirs = [
    "src", "src/data", "src/preprocessing", "src/language",
    "src/classification", "src/embeddings", "src/retrieval",
    "src/safety", "src/evaluation", "app", "app/backend", "tests",
]
for d in init_dirs:
    path = os.path.join(BASE, d, "__init__.py")
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write("")

# Copy raw data
for fname in ["mediqa_bd_dataset.csv", "1mediqa_bd_dataset.csv"]:
    src = os.path.join(r"i:\NLP", fname)
    dst = os.path.join(BASE, "data", "raw", fname)
    if os.path.exists(src) and not os.path.exists(dst):
        shutil.copy2(src, dst)
        print(f"Copied {fname} to data/raw/")

print("Project structure created successfully!")
print(f"Base directory: {BASE}")
for root, subdirs, files in os.walk(BASE):
    level = root.replace(BASE, "").count(os.sep)
    indent = "  " * level
    print(f"{indent}{os.path.basename(root)}/")
    if level < 3:
        for f in files:
            print(f"{indent}  {f}")
