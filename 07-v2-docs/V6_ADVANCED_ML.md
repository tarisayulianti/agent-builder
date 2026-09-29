# V6 — Advanced ML & Adaptive Optimization

## Status: 🔲 V6 — Belum mulai (V5 belum dimulai)

## Visi
Advanced ML pipeline untuk adaptive task decomposition, anomaly detection, dan predictive maintenance sistem agent.

## Environment Setup
```bash
# 1. Install full ML stack
pip install scikit-learn pandas numpy matplotlib joblib

# 2. Optional: Install deep learning (untuk neural models)
pip install torch --index-url https://download.pytorch.org/whl/cpu

# 3. Train models
python ml/advanced_ml.py --train-all

# 4. Run inference
python ml/advanced_ml.py --decompose "<task description>"
```

## Komponen V6
| Komponen | File | Status |
|---|---|---|
| Advanced ML pipeline | `ml/advanced_ml.py` | 🔲 |
| Model registry | `ml/models/` | 🔲 |
| Anomaly detector | `ml/anomaly_detector.py` | 🔲 |
| Predictive maintainer | `ml/predictive_maintenance.py` | 🔲 |

## Configuration (.env)
```env
# V6 settings
ANOMALY_DETECTION_ENABLED=true
PREDICTIVE_MAINTENANCE=true
ML_MODEL_REGISTRY=ml/models/
ANOMALY_THRESHOLD=0.8
MAINTENANCE_PREDICTION_HORIZON=24h
```

## ML Models
| Model | File | Purpose |
|---|---|---|
| Task decomposition model | `ml/models/decomposer.pkl` | Split task into optimal sub-tasks |
| Duration predictor | `ml/models/duration_predictor.pkl` | Predict task/sub-task duration |
| Anomaly detector | `ml/models/anomaly_detector.pkl` | Detect stuck, timeout, crash |
| Resource predictor | `ml/models/resource_predictor.pkl` | Predict memory/CPU usage |

## Features
- Adaptive task decomposition
- Anomaly detection (stuck, timeout, crash prediction)
- Predictive maintenance (resource usage, cost prediction)
- Self-improving optimizer (retrain on feedback)

## Test Commands
```bash
# Train all models
python ml/advanced_ml.py --train-all

# Decompose task
python ml/advanced_ml.py --decompose "Deploy web app ke cloud"

# Predict anomaly
python ml/anomaly_detector.py --detect task-001 --output logs/recent_output.txt

# Predictive maintenance
python ml/predictive_maintenance.py --predict --window 24h

# Model info
python ml/advanced_ml.py --model-info
```

## Dependencies
- scikit-learn (classification, regression, clustering)
- pandas (data processing)
- numpy (numerical computation)
- matplotlib (visualization)
- joblib (model serialization)
- Optional: torch/tensorflow (for deep learning)

## File Structure
```
ml/
├── advanced_ml.py          # Main pipeline (train, infer, orchestrate)
├── anomaly_detector.py     # Anomaly detection (STUCK, TIMEOUT, CRASH)
├── predictive_maintenance.py # Resource/cost prediction
├── feature_extractor.py    # Feature engineering (V3 — reused)
├── data/
│   ├── training_data.json
│   ├── features.csv
│   └── labels.csv
├── models/
│   ├── decomposer.pkl
│   ├── duration_predictor.pkl
│   ├── anomaly_detector.pkl
│   └── resource_predictor.pkl
└── tests/
    └── test_models.py
```

## Migration Path (V5 → V6)
1. Install full ML stack
2. Collect & label data (from V5 dashboard)
3. Train anomaly detection model
4. Train predictive maintenance model
5. Integrate V6 models into orca.py (orchestrator feedback loop)

## Integration Points
- `ml/anomaly_detector.py` ↔ `orca.py` (failing case detection)
- `ml/predictive_maintenance.py` ↔ `status_tracker.py` (resource monitoring)
- `ml/advanced_ml.py` ↔ `ml/task_optimizer.py` (V3 — feature sharing)
- `ml/advanced_ml.py` ↔ `logs/` (training data source)

## Next Action
Implementation setelah V5 selesai.
Lihat juga: [V5 Web Dashboard](V5_WEB_DASHBOARD.md)
