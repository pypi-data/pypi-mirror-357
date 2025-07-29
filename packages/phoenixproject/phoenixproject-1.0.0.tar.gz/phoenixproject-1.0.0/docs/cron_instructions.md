# ⏰ Planification Automatique - Analyse Hebdomadaire des Revenus

## 📅 Objectif
Analyser automatiquement les revenus et publications **chaque dimanche à 2h** du matin.

---

## 🧠 Activation manuelle (Linux/macOS)

Ajoutez cette ligne à votre crontab :
```bash
0 2 * * 0 python3 /chemin/vers/affiliate_ai/modules/analyse_revenus.py >> /chemin/vers/data/logs/analyse_revenus.log 2>&1
```

Remplacez `/chemin/vers/` par le chemin absolu du projet.

---

## ⚙️ Détection automatique possible ?

✅ Oui, si :
- Le système est Linux/macOS
- `crontab` est installé
- L'utilisateur a les droits

⚠️ Sinon, l’option dans le menu sera **grisée** ou désactivée automatiquement.

---

## 🔒 Sécurité

- Aucun accès réseau requis
- Données locales uniquement
- Journalisation dans `data/logs/`

---

## ✅ Activation via code (détection automatique)

Vous pouvez utiliser la commande :
```bash
python3 affiliate_ai/scripts/activer_cron.py
```

---

## ❌ Désactivation
Supprimez la tâche via :
```bash
crontab -e
```
Et supprimez la ligne liée à `analyse_revenus.py`.

---
