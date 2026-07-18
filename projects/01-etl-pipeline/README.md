# Projet 1 — Pipeline ETL production multi-format

> **Stack :** Python · pandas · SQLite / PostgreSQL · PyYAML · pytest · Docker · CI/CD

Un pipeline ETL robuste qui **ingère, nettoie, valide et charge** des données
hétérogènes (**CSV, Excel, JSON, XML**) dans une base, avec validation par schéma
déclaratif, déduplication et pattern **UPSERT** idempotent.

## 🎯 Objectif & résultat

| Objectif | Résultat mesuré |
|----------|-----------------|
| Traiter 5 000 lignes en < 0,5 s | ✅ **~310 ms** (~16 000 lignes/s) |
| Zéro régression | ✅ 6 tests unitaires + test d'idempotence |
| Aucune donnée invalide chargée | ✅ lignes rejetées isolées dans un fichier d'erreurs |

## 🏗️ Architecture

```
sources (CSV/XLSX/JSON/XML)
        │
        ▼
   extract.py        ── lecture multi-format (dispatch sur l'extension)
        ▼
   validate.py       ── schéma YAML : types, plages, valeurs autorisées
        │                 ├─ lignes valides ─┐
        │                 └─ lignes rejetées → rejected_rows.csv
        ▼                                     │
   transform.py      ── déduplication (clé primaire) + KPIs métier
        ▼
   load.py           ── UPSERT (INSERT ... ON CONFLICT DO UPDATE)
        ▼
   warehouse.db      ── tables sales_orders + sales_kpis
```

Les règles métier vivent dans **`config/schema.yaml`** — on change une contrainte
sans toucher au code. L'UPSERT est écrit en SQL standard (`ON CONFLICT`), donc le
même code cible **SQLite en local et PostgreSQL en production**.

## 🚀 Utilisation

```bash
pip install -r requirements.txt

python data/generate_samples.py   # crée 4 fichiers sources (avec doublons + erreurs volontaires)
python run.py                      # exécute le pipeline -> warehouse.db
python benchmark.py                # vérifie la cible de performance
python -m pytest tests/ -q         # lance la suite de tests

# ...ou tout via Docker :
docker build -t etl-pipeline . && docker run --rm etl-pipeline
```

### Exemple de sortie
```
read=408 valid=405 rejected=3 deduped=400 kpis=117 in 145.4 ms
db: {'orders_in_db': 400, 'kpis_in_db': 117}
```
→ 3 lignes invalides écartées, 5 doublons résolus par UPSERT, 117 KPIs agrégés.

## 🧠 Points techniques
- **Validation déclarative** (types, `min`/`max`, `allowed`, `max_length`, dates).
- **UPSERT idempotent** : relancer le pipeline ne crée jamais de doublon (testé).
- **Déduplication `keep=last`** : un envoi corrigé remplace l'ancien.
- **Observabilité** : chaque run renvoie un `RunReport` (compteurs + timing).
- **Gate de performance** en CI : le build échoue si on dépasse 0,5 s / 5 000 lignes.
