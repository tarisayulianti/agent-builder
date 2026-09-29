# V3 — Task Optimizer & ML

## Status: 🔲 V3 — Belum mulai (V2 belum dimulai)

## Visi
Task optimizer menggunakan ML untuk memprediksi optimalisasi sub-task decomposition, estimasi durasi, dan priorisasi task queue.

## Environment Setup
```bash
# 1. Install Python ML dependencies
pip install scikit-learn pandas numpy matplotlib

# 2. Pastikan training data tersedia
ls ml/data/  # historical task data

# 3. Run optimizer
python ml/task_optimizer.py --train
python ml/task_optimizer.py --predict "<task description>"
```

## Komponen V3
| Komponen | File | Status |
|---|---|---|
| ML task optimizer | `ml/task_optimizer.py` | 🔲 |
| Model training data | `ml/data/training_data.json` | 🔲 |
| Feature extractor | `ml/feature_extractor.py` | 🔲 |

## Configuration (.env)
```env
# V3 settings
ML_ENABLED=true
ML_MODEL_PATH=ml/models/task_optimizer.pkl
ML_TRAINING_DATA=logs/history/task_history.json
FEATURE_THRESHOLD_COMPLEXITY=5
FEATURE_THRESHOLD_DURATION=600  # 10 menit
```

## Features
- Prediksi durasi sub-task berdasarkan complexity
- Optimasi urutan task di queue
- Priority adjustment berdasarkan historical data

## Test Commands
```bash
# Train model
python ml/task_optimizer.py --train

# Predict task complexity
python ml/task_optimizer.py --predict "Buat script Python fibonacci"

# Show model info
python ml/task_optimizer.py --info
```

## Dependencies
- Python ML libraries (scikit-learn, pandas, numpy, matplotlib)
- Training data dari `logs/history/task_history.json`
- Feature extraction dari `ml/feature_extractor.py`

## File Structure
```
ml/
├── task_optimizer.py       # Main optimizer (train, predict, classify)
├── feature_extractor.py    # Extract features from task descriptions
├── data/
│   ├── training_data.json  # Labeled training data
│   └── features.csv        # Feature vectors
└── models/
    ├── task_optimizer.pkl  # Trained model
    └── feature_scaler.pkl  # Scaler for features
```

## Migration Path (V2 → V3)
1. Install ML dependencies
2. Collect/prepare training data
3. Train initial model
4. Integrate optimizer call di orca.py plan phase
5. Enable ML-based priority adjustment in task queue

## Integration Points
- `ml/task_optimizer.py` ↔ `orca.py` (plan phase — task decomposition)
- `ml/task_optimizer.py` ↔ `logs/history/task_history.json` (training data)
- `ml/feature_extractor.py` ↔ `AGENT2_INSTRUCTION.md` (format parsing)

## Next Action
Implementation setelah V2 selesai.
Lihat juga: [V2 Multi-Agent](V2_MULTI_AGENT.md)
