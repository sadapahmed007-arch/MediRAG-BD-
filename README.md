# MediRAG-BD

**Multilingual Medical Question Answering and Hybrid Information Retrieval System**

MediRAG-BD is a multilingual medical question-answering system designed to retrieve relevant medical information from a structured knowledge dataset. It supports English, Bangla, Banglish (Romanized Bangla), and code-mixed queries using Natural Language Processing, Machine Learning, and semantic information retrieval techniques.

## Features

- Multilingual medical query processing
- Language detection and text preprocessing
- Medical topic and intent classification
- Safety-aware query classification
- TF-IDF-based information retrieval
- Dense semantic retrieval using Sentence Transformers
- FAISS-based vector similarity search
- Hybrid retrieval and relevance-based ranking
- Evidence and source-based answer retrieval
- Interactive web interface and research dashboard

## Tech Stack

| Category | Technologies |
|---|---|
| Language | Python, JavaScript |
| Machine Learning | Scikit-learn, PyTorch |
| NLP | Sentence Transformers |
| Information Retrieval | TF-IDF, FAISS |
| Backend | FastAPI, Uvicorn |
| Frontend | React.js, Tailwind CSS, Vite |
| Data Processing | Pandas, NumPy |
| Visualization | Matplotlib, Seaborn |

## Project Structure

```text
MediRAG-BD/
│
├── app/
│   ├── backend/
│   └── frontend/
│
├── configs/
│   └── config.yaml
│
├── data/
│   ├── raw/
│   ├── interim/
│   ├── processed/
│   ├── splits/
│   └── indexes/
│
├── docs/
├── experiments/
├── models/
├── scripts/
├── src/
│   ├── classification/
│   ├── data/
│   ├── embeddings/
│   ├── evaluation/
│   ├── language/
│   ├── preprocessing/
│   ├── retrieval/
│   └── safety/
│
├── tests/
├── requirements.txt
└── README.md
```

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/YOUR-USERNAME/MediRAG-BD.git
cd MediRAG-BD
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate:

```bash
# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Frontend Dependencies

```bash
cd app/frontend
npm install
cd ../..
```

### 5. Build Models and Retrieval Indexes

```bash
python scripts/complete_build.py
```

### 6. Run Application

```bash
python scripts/run_app.py
```

## Application URLs

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Documentation | http://localhost:8000/docs |

## Dataset

The project uses a multilingual medical question-answering dataset containing 24,368 records across four language categories.

- English
- Bangla
- Banglish
- Code-Mixed

The dataset includes medical topic, intent, and safety annotations.

For more information, see [Dataset Documentation](docs/dataset_card.md).

## Research & Evaluation

The project includes:

- Dataset analysis and statistics
- Classification evaluation
- Confusion matrix visualization
- Retrieval performance evaluation
- TF-IDF and Dense Retrieval comparison
- Hybrid retrieval experiments

## Safety Disclaimer

MediRAG-BD is developed for academic research and educational purposes. It is not intended to replace professional medical advice, diagnosis, or treatment.

## Author

**YOUR NAME**

GitHub: https://github.com/sadapahmed007-arch

## License

Refer to the licensing conditions of the included datasets and third-party resources before selecting a project license.
