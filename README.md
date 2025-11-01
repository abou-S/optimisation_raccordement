# Projet de Raccordement Électrique

## Contexte
Une petite ville a été touchée par des intempéries, entraînant la destruction de plusieurs infrastructures permettant le raccordement des maisons au réseau électrique. Ce projet vise à proposer une planification optimale pour reconnecter les citoyens au réseau électrique tout en minimisant les coûts et en respectant les contraintes de temps et de ressources.

## Objectifs
- Rétablir rapidement la connexion électrique pour le plus grand nombre d'habitants.
- Minimiser les coûts de raccordement.
- Prioriser les bâtiments critiques (comme l'hôpital) et respecter les contraintes de phases de construction.
- Optimiser l'utilisation des ressources humaines et matérielles.

## Architecture du Projet

### Structure des Fichiers
```
projet_optimisation/
├── README.md                         # Documentation du projet
├── plan_raccordement_oo.py           # Script principal d'optimisation (version orientée objet)
├── requirements.txt                  # Dépendances du projet
├── .gitignore                        # Configuration des fichiers à ignorer dans Git
└── docs/                             # Documentation supplémentaire
    ├── Rapport Optimisation Opérationnelle.pdf
    └── carte 23.pdf                  # Carte du réseau électrique
```

### Fichiers de données (non inclus dans le dépôt Git)
```
├── batiments.csv                     # Données des bâtiments
├── infra.csv                         # Données des infrastructures
├── reseau_en_arbre.csv               # Données du réseau électrique
├── plan_raccordement_dommages_oo.csv # Résultat: plan détaillé par infrastructure
└── synthese_phases_dommages_oo.csv   # Résultat: synthèse des phases
```

### Flux de Traitement
1. Chargement des données (batiments.csv, infra.csv, reseau_en_arbre.csv)
2. Identification des infrastructures endommagées
3. Calcul des coûts et durées pour chaque infrastructure
4. Identification du chemin de l'hôpital (Phase 0)
5. Calcul du ratio bénéficiaires/coût pour chaque infrastructure
6. Affectation des infrastructures aux phases 1-4 selon leur ratio
7. Génération des fichiers de résultats

## Données Fournies
Le projet utilise les fichiers suivants :
1. **`batiments.csv`** : Contient les informations sur les bâtiments (coordonnées, nombre d'habitants, etc.).
2. **`infra.csv`** : Contient les informations sur les infrastructures existantes ou à construire.
3. **`reseau_en_arbre.csv`** : Décrit les connexions possibles entre les bâtiments et le réseau électrique, ainsi que les coûts associés. /!\ ce fichier a été corrigé en amout dans un autre notebook 

## Contraintes
- **Coûts du matériel** :
  - Aérien : 500 €/m
  - Semi-aérien : 750 €/m
  - Fourreau : 900 €/m
- **Durée par ouvrier** :
  - Aérien : 2h/m
  - Semi-aérien : 4h/m
  - Fourreau : 5h/m
- **Coût des ouvriers** : 300 € pour 8h de travail.
- **Limite d'ouvriers** : Maximum 4 ouvriers par infrastructure en simultané.
- **Autonomie de l'hôpital** : 20h avec une marge de sécurité de 20 %.

## Phases de Construction
1. **Phase 0** : Priorité à l'hôpital.
2. **Phase 1** : 40 % du coût total.
3. **Phases 2, 3, 4** : 20 % du coût total pour chaque phase.

# Rapport Détaillé

## 1. Description de la Métrique de Priorisation

Notre métrique principale de priorisation est le **ratio bénéficiaires/coût**, qui représente le nombre de maisons desservies par euro investi. Cette métrique est calculée comme suit :

```
Métrique de Priorisation = Nombre de Bénéficiaires / Coût Total de l'Infrastructure
```

Cette approche présente plusieurs avantages :

- **Maximisation de l'impact social** : En priorisant les infrastructures avec le meilleur ratio bénéficiaires/coût, nous maximisons le nombre de foyers raccordés pour chaque euro investi.
- **Équité et efficience** : Cette métrique permet d'équilibrer l'équité (desservir un maximum de personnes) et l'efficience économique (minimiser les coûts).
- **Adaptabilité aux contraintes budgétaires** : La métrique s'adapte naturellement aux différentes phases du projet et à leurs contraintes budgétaires respectives.

En cas d'égalité du ratio, nous utilisons le nombre absolu de bénéficiaires comme critère secondaire, favorisant ainsi les infrastructures desservant le plus grand nombre de foyers.

## 2. Plan de Raccordement avec Ordre de Priorité

Notre plan de raccordement est structuré en 5 phases distinctes, chacune avec ses propres priorités :

### Phase 0 : Infrastructures Critiques (Hôpital)
- **Nombre d'infrastructures** : 3
- **Coût total** : 21 405,13 €
- **Bénéficiaires** : 24
- **Durée critique** : 9,35 heures (avec 4 ouvriers par infrastructure)
- **Pourcentage du coût total** : 1,47%

Cette phase prioritaire garantit que l'hôpital est raccordé bien avant l'épuisement de son autonomie de 20 heures (avec une marge de sécurité de 20%).

### Phase 1 : Raccordement Massif Initial
- **Nombre d'infrastructures** : 108
- **Coût total** : 592 227,91 €
- **Bénéficiaires** : 1 928
- **Durée critique** : 38,17 heures
- **Pourcentage du coût total** : 40,64%

Cette phase représente le plus grand nombre de bénéficiaires (1 928 foyers), conformément à l'objectif de 40% du budget total.

### Phase 2 : Premier Complément
- **Nombre d'infrastructures** : 41
- **Coût total** : 323 498,05 €
- **Bénéficiaires** : 167
- **Durée critique** : 37,66 heures
- **Pourcentage du coût total** : 22,20%

### Phase 3 : Deuxième Complément
- **Nombre d'infrastructures** : 28
- **Coût total** : 292 542,54 €
- **Bénéficiaires** : 78
- **Durée critique** : 32,23 heures
- **Pourcentage du coût total** : 20,07%

### Phase 4 : Finalisation
- **Nombre d'infrastructures** : 17
- **Coût total** : 227 589,93 €
- **Bénéficiaires** : 25
- **Durée critique** : 43,26 heures
- **Pourcentage du coût total** : 15,62%

## 3. Analyse des Coûts et Bénéfices

### Analyse Globale
- **Nombre total d'infrastructures réparées** : 197
- **Coût total du projet** : 1 457 263,57 €
- **Nombre total de bénéficiaires** : 2 222
- **Coût moyen par bénéficiaire** : 655,83 €

### Répartition des Coûts
- **Coûts matériels** : 1 235 335,55 € (84,77% du total)
- **Coûts de main-d'œuvre** : 221 928,02 € (15,23% du total)

### Efficacité par Phase
- **Phase 0** : 892 € par bénéficiaire (priorité à la sécurité)
- **Phase 1** : 307 € par bénéficiaire (phase la plus efficiente)
- **Phase 2** : 1 937 € par bénéficiaire
- **Phase 3** : 3 750 € par bénéficiaire
- **Phase 4** : 9 104 € par bénéficiaire (phase la moins efficiente)

Cette analyse démontre l'efficacité de notre métrique de priorisation, avec un coût par bénéficiaire qui augmente progressivement à travers les phases. La Phase 1 présente le meilleur rapport coût-bénéfice, tandis que les phases ultérieures concernent des infrastructures moins efficientes mais nécessaires pour compléter le raccordement de l'ensemble de la communauté.

### Bénéfices Sociaux et Économiques
- **Rétablissement rapide pour la majorité** : 87,67% des bénéficiaires sont raccordés dès les phases 0 et 1.
- **Équité territoriale** : Toutes les zones sont progressivement couvertes, même celles moins densément peuplées.
- **Respect des contraintes temporelles** : Le raccordement de l'hôpital est assuré en 9,35 heures, bien en-deçà de la limite de 16 heures (20h avec marge de sécurité).

## 4. Visualisation du Réseau

![Carte du réseau électrique](docs/carte%2023.pdf)

La carte du réseau électrique (disponible dans le dossier `docs`) illustre la distribution spatiale des infrastructures et leur priorisation par phases. Cette visualisation permet de mieux comprendre la logique de déploiement et l'impact territorial du plan de raccordement.

En conclusion, notre plan de raccordement offre un équilibre optimal entre efficacité économique et impact social, en priorisant les infrastructures selon leur ratio bénéficiaires/coût tout en respectant les contraintes techniques et budgétaires du projet.

# Rapport Détaillé

## 1. Description de la Métrique de Priorisation

Notre métrique principale de priorisation est le **ratio bénéficiaires/coût**, qui représente le nombre de maisons desservies par euro investi. Cette métrique est calculée comme suit :

```
Métrique de Priorisation = Nombre de Bénéficiaires / Coût Total de l'Infrastructure
```

Cette approche présente plusieurs avantages :

- **Maximisation de l'impact social** : En priorisant les infrastructures avec le meilleur ratio bénéficiaires/coût, nous maximisons le nombre de foyers raccordés pour chaque euro investi.
- **Équité et efficience** : Cette métrique permet d'équilibrer l'équité (desservir un maximum de personnes) et l'efficience économique (minimiser les coûts).
- **Adaptabilité aux contraintes budgétaires** : La métrique s'adapte naturellement aux différentes phases du projet et à leurs contraintes budgétaires respectives.

En cas d'égalité du ratio, nous utilisons le nombre absolu de bénéficiaires comme critère secondaire, favorisant ainsi les infrastructures desservant le plus grand nombre de foyers.

## 2. Plan de Raccordement avec Ordre de Priorité

Notre plan de raccordement est structuré en 5 phases distinctes, chacune avec ses propres priorités :

### Phase 0 : Infrastructures Critiques (Hôpital)
- **Nombre d'infrastructures** : 3
- **Coût total** : 21 405,13 €
- **Bénéficiaires** : 24
- **Durée critique** : 9,35 heures (avec 4 ouvriers par infrastructure)
- **Pourcentage du coût total** : 1,47%

Cette phase prioritaire garantit que l'hôpital est raccordé bien avant l'épuisement de son autonomie de 20 heures (avec une marge de sécurité de 20%).

### Phase 1 : Raccordement Massif Initial
- **Nombre d'infrastructures** : 108
- **Coût total** : 592 227,91 €
- **Bénéficiaires** : 1 928
- **Durée critique** : 38,17 heures
- **Pourcentage du coût total** : 40,64%

Cette phase représente le plus grand nombre de bénéficiaires (1 928 foyers), conformément à l'objectif de 40% du budget total.

### Phase 2 : Premier Complément
- **Nombre d'infrastructures** : 41
- **Coût total** : 323 498,05 €
- **Bénéficiaires** : 167
- **Durée critique** : 37,66 heures
- **Pourcentage du coût total** : 22,20%

### Phase 3 : Deuxième Complément
- **Nombre d'infrastructures** : 28
- **Coût total** : 292 542,54 €
- **Bénéficiaires** : 78
- **Durée critique** : 32,23 heures
- **Pourcentage du coût total** : 20,07%

### Phase 4 : Finalisation
- **Nombre d'infrastructures** : 17
- **Coût total** : 227 589,93 €
- **Bénéficiaires** : 25
- **Durée critique** : 43,26 heures
- **Pourcentage du coût total** : 15,62%

## 3. Analyse des Coûts et Bénéfices

### Analyse Globale
- **Nombre total d'infrastructures réparées** : 197
- **Coût total du projet** : 1 457 263,57 €
- **Nombre total de bénéficiaires** : 2 222
- **Coût moyen par bénéficiaire** : 655,83 €

### Répartition des Coûts
- **Coûts matériels** : 1 235 335,55 € (84,77% du total)
- **Coûts de main-d'œuvre** : 221 928,02 € (15,23% du total)

### Efficacité par Phase
- **Phase 0** : 892 € par bénéficiaire (priorité à la sécurité)
- **Phase 1** : 307 € par bénéficiaire (phase la plus efficiente)
- **Phase 2** : 1 937 € par bénéficiaire
- **Phase 3** : 3 750 € par bénéficiaire
- **Phase 4** : 9 104 € par bénéficiaire (phase la moins efficiente)

Cette analyse démontre l'efficacité de notre métrique de priorisation, avec un coût par bénéficiaire qui augmente progressivement à travers les phases. La Phase 1 présente le meilleur rapport coût-bénéfice, tandis que les phases ultérieures concernent des infrastructures moins efficientes mais nécessaires pour compléter le raccordement de l'ensemble de la communauté.

### Bénéfices Sociaux et Économiques
- **Rétablissement rapide pour la majorité** : 87,67% des bénéficiaires sont raccordés dès les phases 0 et 1.
- **Équité territoriale** : Toutes les zones sont progressivement couvertes, même celles moins densément peuplées.
- **Respect des contraintes temporelles** : Le raccordement de l'hôpital est assuré en 9,35 heures, bien en-deçà de la limite de 16 heures (20h avec marge de sécurité).

En conclusion, notre plan de raccordement offre un équilibre optimal entre efficacité économique et impact social, en priorisant les infrastructures selon leur ratio bénéficiaires/coût tout en respectant les contraintes techniques et budgétaires du projet.