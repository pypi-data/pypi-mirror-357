# 🧠 README_ACTION.md – IA Affiliée : Plan d'action automatique

Ce document t’explique **chaque action de ton IA affiliée**, ligne par ligne, avec une **explication concrète**.  
Objectif : gagner de l’argent en postant du contenu **automatisé mais naturel**, sans que ça se voie.

---

## ✅ Pipeline d'actions de l’IA (1 ligne = 1 action)

### 🟩 Étape 1 : Recherche produit

- `fetch_products("mot-clé")`  
  ➜ Cherche les produits Amazon pertinents selon une niche.

> Exemple : “support ordinateur portable” → Amazon renvoie 5 liens valides

---

### 🟩 Étape 2 : Génération d’avis

- `generate_review(product_title)`  
  ➜ Crée un avis IA positif, crédible, au ton **neutre et sincère**, pas "pub".

> Exemple : “Ce support s’est avéré plus utile que je ne le pensais, notamment pour mes longues sessions de travail.”

---

### 🟩 Étape 3 : Ajout du lien affilié

- `build_affiliate_link(url, "tonid-21")`  
  ➜ Convertit l’URL brute en lien affilié traqué (tu touches commission).

> Résultat : `https://www.amazon.fr/dp/B08XYZ?tag=tonid-21`

---

### 🟩 Étape 4 : Publication

- `publish_to_medium(title, content)`  
- `publish_to_reddit(title, content)`  
  ➜ Poste l’avis + lien sur Medium, Reddit ou d’autres plateformes.

> ✍️ L’IA signe sous un pseudo. Le style est conversationnel, pas vendeur.

---

### 🟩 Étape 5 : Logging

- `log_event(...)`  
  ➜ Archive tout : titre, date, plateforme, statut

- `log_revenue(...)`  
  ➜ Permet d’ajouter les revenus gagnés manuellement (ou via API Amazon dans une future version)

---

### 🟩 Étape 6 : Analyse revenus

- `revenus.py`  
  ➜ Affiche :
  - Total cumulé
  - Revenus par jour
  - Revenus par plateforme
  - Graphique matplotlib

---

## 🤑 Es-tu payé au clic ou à l’achat ?

- **Amazon Affiliates France** : tu es **payé à l’achat**, **dans les 24h** suivant le clic sur ton lien.
- Tu gagnes un **% (3% à 10%)** selon la catégorie de produit.

> Donc ton but : inciter au **clic**, puis à **l’achat dans la foulée**.

---

## 🎯 Comment faire cliquer sans faire "marketing" ?

Voici les **3 règles d’or** intégrées dans les avis IA :

1. **Parler d’expérience personnelle**
   - “J’ai essayé ce support pendant 3 jours…”

2. **Ne pas mettre d’emoji tapageur**
   - ✅ “J’ai été surpris”  
   - ❌ “🔥🔥 C’EST LE MEILLEUR SUPPORT 🔥🔥”

3. **Contextualiser le lien Amazon**
   - “Voici le modèle que j’utilise → [Lien Amazon]”

---

## 🧑‍💻 Bonus : optimiser ton CTR

- Poste sur des subreddits **adaptés à ta niche**
  - Ex : `r/Productivity`, `r/TechWearables`, `r/HomeOfficeSetups`
- Intègre une image (dans version future)
- Pose une question à la fin : “Vous utilisez quoi, vous ?”

---

Ce fichier peut être mis à jour à chaque ajout de fonctionnalité.
