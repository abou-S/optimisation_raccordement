# Projet de Raccordement Électrique

## Contexte
Une petite ville a été touchée par des intempéries, entraînant la destruction de plusieurs infrastructures permettant le raccordement des maisons au réseau électrique. Ce projet vise à proposer une planification optimale pour reconnecter les citoyens au réseau électrique tout en minimisant les coûts et en respectant les contraintes de temps et de ressources.

## Objectifs
- Rétablir rapidement la connexion électrique pour le plus grand nombre d'habitants.
- Minimiser les coûts de raccordement.
- Prioriser les bâtiments critiques (comme l'hôpital) et respecter les contraintes de phases de construction.
- Optimiser l'utilisation des ressources humaines et matérielles.

## Données Fournies
Le projet utilise les fichiers suivants :
1. **`batiments.csv`** : Contient les informations sur les bâtiments (coordonnées, nombre d'habitants, etc.).
2. **`infra.csv`** : Contient les informations sur les infrastructures existantes ou à construire.
3. **`reseau_en_arbre.csv`** : Décrit les connexions possibles entre les bâtiments et le réseau électrique, ainsi que les coûts associés.

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

## Solution Proposée

### Approche Générale
La solution repose sur la modélisation du problème sous forme de graphe pondéré, où :
- Les **nœuds** représentent les bâtiments et les points de connexion.
- Les **arêtes** représentent les lignes électriques possibles, avec un poids correspondant au coût total (matériel + main-d'œuvre).

L'objectif est de construire un **arbre couvrant minimal** (Minimum Spanning Tree, MST) pour connecter tous les bâtiments au réseau électrique tout en respectant les contraintes de coûts, de temps et de priorités.

### Étapes de la Solution
1. **Modélisation des Données** :
   - Les données du fichier `reseau_en_arbre.csv` sont utilisées pour construire le graphe.
   - Les coûts des infrastructures (aérien, semi-aérien, fourreau) et les durées de travail sont calculés pour chaque connexion.

2. **Priorisation des Connexions** :
   - Les connexions sont priorisées en fonction de leur **coût par prise raccordée**. Cette métrique est calculée comme suit :
     \[
     \text{Métrique de Priorisation} = \frac{\text{Coût Total de la Connexion}}{\text{Nombre de Prises Raccordées}}
     \]
   - Les connexions avec le coût par prise le plus faible sont traitées en premier.

3. **Phases de Construction** :
   - **Phase 0** : L'hôpital est priorisé pour garantir sa connexion dans les 20 heures disponibles, avec une marge de sécurité de 20 %.
   - **Phase 1** : 40 % du budget total est alloué pour connecter un maximum de bâtiments après l'hôpital.
   - **Phases 2, 3, 4** : Les 60 % restants sont répartis équitablement (20 % par phase) pour compléter le raccordement.

4. **Optimisation des Ressources** :
   - La mutualisation des lignes électriques est prise en compte pour minimiser les coûts.
   - Un maximum de 4 ouvriers est affecté par infrastructure, et les durées sont ajustées en conséquence.

5. **Validation des Contraintes** :
   - Les coûts et durées sont vérifiés pour chaque phase afin de respecter les limites budgétaires et temporelles.
   - Une marge de sécurité est appliquée pour les infrastructures critiques comme l'hôpital.

### Résultats
- Le plan de raccordement est optimisé pour minimiser les coûts tout en maximisant le nombre de prises raccordées.
- Les bâtiments critiques (comme l'hôpital) sont raccordés en priorité.
- Les phases de construction sont équilibrées pour respecter les contraintes budgétaires et temporelles.

### Métrique de Priorisation
La métrique de priorisation utilisée est essentielle pour garantir une optimisation efficace. Elle permet de :
- Maximiser l'impact (nombre de prises raccordées) pour chaque euro dépensé.
- Prioriser les connexions les plus simples et les moins coûteuses.
- Garantir une progression rapide du raccordement tout en respectant les contraintes.

En résumé, cette approche garantit un raccordement rapide, efficace et optimisé pour tous les citoyens, tout en respectant les contraintes imposées par le projet.