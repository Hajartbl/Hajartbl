# 🗂️ Portfolio — Projets Data Engineering / Data Analyst

Quatre projets techniques **reproductibles et testés**, illustrant le passage de
la donnée brute à un livrable utile : pipelines ETL, ML déployé, traitement du
signal et analyse statistique en science cognitive.

| # | Projet | Stack | Résultat clé |
|---|--------|-------|--------------|
| 1 | [**Pipeline ETL multi-format**](01-etl-pipeline/) | Python · pandas · SQL · PyYAML · Docker · CI | 5 000 lignes < 0,5 s, UPSERT idempotent, validation par schéma |
| 2 | [**API de maintenance prédictive**](02-predictive-maintenance-api/) | scikit-learn · Flask · Docker | Random Forest **R² ≈ 0,92**, API REST + risque LOW/MED/HIGH |
| 3 | [**Correction radiométrique IR (NUC)**](03-ir-nuc-correction/) | NumPy · régression · interpolation Newton | Non-uniformité **71 % → 4,7 %**, calibration manquante reconstruite |
| 4 | [**Musique & Dépression**](04-music-and-depression/) | pandas · SciPy · scikit-learn · seaborn | Tests d'hypothèses + tailles d'effet, lien en U écoute↔dépression |

Chaque projet est autonome : son propre `README.md`, `requirements.txt`, suite de
tests et pipeline CI GitHub Actions.

```bash
# Exemple — lancer le projet 1
cd 01-etl-pipeline
pip install -r requirements.txt
python data/generate_samples.py && python run.py
python -m pytest tests/ -q
```

## 🧪 Qualité & reproductibilité
- **Tests** : chaque projet embarque une suite `pytest` (25 tests au total).
- **CI/CD** : workflows GitHub Actions par projet (`.github/workflows/`).
- **Données synthétiques** : générées avec une graine fixe → résultats reproductibles.
- **Docker** : projets 1 et 2 conteneurisés.

---

*Projets décrits dans mon dossier de motivation — **Hajar Toubali**, Data Engineer / Data Analyst.*
