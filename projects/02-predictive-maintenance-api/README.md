# Projet 2 — API de maintenance prédictive (ML déployé)

> **Stack :** Python · scikit-learn · Flask · Docker · REST API · pytest

Un pipeline ML **end-to-end** : données capteurs brutes → modèle entraîné →
**API REST** qui prédit la **durée de vie résiduelle** (RUL, *Remaining Useful
Life*) d'un équipement et renvoie une **classification de risque** en temps réel.

## 🎯 Objectif & résultat

| Objectif | Résultat mesuré |
|----------|-----------------|
| Prédire la RUL d'un équipement | ✅ Random Forest, **R² ≈ 0,92** (MAE ~106 h) |
| Classification de risque temps réel | ✅ bandes **LOW / MEDIUM / HIGH** |
| Service consommable par d'autres équipes | ✅ API REST Flask + Docker |
| Latence faible | ✅ réponse < 200 ms |

## 🏗️ Cycle end-to-end

```
model/generate_data.py   → jeu de capteurs synthétique (6 000 machines)
model/features.py        → feature engineering partagé train / serving
model/train.py           → Random Forest, R² ≈ 0,92 → rul_model.pkl
app/api.py               → API Flask : /health, /predict
Dockerfile               → image auto-suffisante (entraîne puis sert le modèle)
```

Le **feature engineering est mutualisé** entre l'entraînement et le serving
(`features.py`) pour éliminer tout *train/serve skew*.

## 🚀 Utilisation

```bash
pip install -r requirements.txt

python model/generate_data.py    # jeu de données capteurs
python model/train.py            # entraîne + évalue -> rul_model.pkl + metrics.json
python -m pytest tests/ -q       # 6 tests (API + logique de risque)

# Lancer l'API
python app/api.py                # http://localhost:8000
#   ...ou en production : gunicorn --chdir app -b 0.0.0.0:8000 api:app
#   ...ou via Docker    : docker build -t pdm-api . && docker run -p 8000:8000 pdm-api
```

## 📡 API

### `GET /health`
```json
{ "status": "ok", "model_loaded": true }
```

### `POST /predict`
Accepte un objet **ou une liste** d'objets (prédiction par lot).

```bash
curl -X POST localhost:8000/predict -H 'Content-Type: application/json' -d '{
  "age_hours": 19000, "temperature_c": 95, "vibration_mm_s": 6.0,
  "pressure_bar": 5.5, "rotational_speed_rpm": 1450, "load_percent": 95
}'
```
```json
{ "predicted_rul_hours": 234.2, "risk": "HIGH" }
```

Une machine saine renvoie `{"predicted_rul_hours": 2154.1, "risk": "LOW"}`.
Champs manquants → `400` avec la liste des champs, modèle absent → `503`.

## 🧠 Points techniques
- **Random Forest** (300 arbres) sur features capteurs + features d'interaction
  (`thermal_load`, `vibration_per_krpm`, `age_khours`).
- **Bruit irréductible calibré** dans les données pour un R² réaliste (~0,92),
  pas un sur-ajustement artificiel.
- **API testable sans modèle** : injection d'un `bundle` stub dans `create_app`.
- **Prêt production** : Dockerfile + entrée gunicorn, validation des entrées.
