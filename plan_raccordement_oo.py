#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plan de raccordement électrique post-intempéries (Version Orientée Objet)
-------------------------------------------------------------------------
Lit reseau_en_arbre.csv, infra.csv, batiments.csv et produit :
- plan_raccordement_dommages_oo.csv
- synthese_phases_dommages_oo.csv

Hypothèses et contraintes respectées :
- Seules les infrastructures "a_remplacer" sont planifiées.
- Coûts matériel : aérien 500 €/m, semi-aérien 750 €/m, fourreau 900 €/m
- Rendements : aérien 2 h/m, semi-aérien 4 h/m, fourreau 5 h/m
- Salaire : 300 €/8 h => 37,5 €/h
- Max 4 ouvriers par infra simultanément (parallélisme inter-infra autorisé).
- Phase 0 = hôpital, puis Phase 1 ≈ 40% du coût, Phases 2/3/4 ≈ 20% chacune.
- Vérifie la marge 20% sur les 20h d'autonomie du groupe électrogène.
"""
import argparse
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Set


class Building:
    """Classe représentant un bâtiment."""
    
    def __init__(self, building_id: str, building_type: str, nb_houses: int):
        """
        Initialise un bâtiment.
        
        Args:
            building_id: Identifiant unique du bâtiment
            building_type: Type de bâtiment (habitation, hôpital, etc.)
            nb_houses: Nombre de maisons/logements dans ce bâtiment
        """
        self.building_id = building_id
        self.building_type = building_type
        self.nb_houses = nb_houses
        self.connected_infras = []
    
    def add_connected_infra(self, infra_id: str):
        """Ajoute une infrastructure connectée à ce bâtiment."""
        if infra_id not in self.connected_infras:
            self.connected_infras.append(infra_id)
    
    def is_hospital(self) -> bool:
        """Vérifie si ce bâtiment est un hôpital."""
        return "hôpital" in self.building_type.lower() or "hopital" in self.building_type.lower()
    
    @classmethod
    def load_all_from_data(cls, bat_df: pd.DataFrame, reseau_df: pd.DataFrame) -> Dict[str, 'Building']:
        """
        Charge tous les bâtiments à partir des données.
        
        Args:
            bat_df: DataFrame des bâtiments
            reseau_df: DataFrame du réseau pour établir les connexions
            
        Returns:
            dict: Dictionnaire d'objets Building indexés par building_id
        """
        buildings = {}
        
        # Créer les objets Building
        for _, row in bat_df.iterrows():
            building = cls(
                building_id=row["id_batiment"],
                building_type=row["type_batiment"],
                nb_houses=row["nb_maisons"]
            )
            buildings[building.building_id] = building
        
        # Établir les connexions avec les infrastructures
        for _, row in reseau_df.iterrows():
            building_id = row["id_batiment"]
            infra_id = row["infra_id"]
            if building_id in buildings:
                buildings[building_id].add_connected_infra(infra_id)
        
        return buildings


class Infrastructure:
    """Classe représentant une infrastructure électrique."""
    
    # Paramètres globaux
    UNIT_PRICE = {"aerien": 500.0, "semi-aerien": 750.0, "fourreau": 900.0}
    HOURS_PER_METER = {"aerien": 2.0, "semi-aerien": 4.0, "fourreau": 5.0}
    HOURLY_WAGE = 300.0 / 8.0  # 37.5 €/h
    MAX_WORKERS_PER_INFRA = 4
    
    def __init__(self, infra_id: str, infra_kind: str, longueur: float):
        """
        Initialise une infrastructure.
        
        Args:
            infra_id: Identifiant unique de l'infrastructure
            infra_kind: Type d'infrastructure (aerien, semi-aerien, fourreau)
            longueur: Longueur de l'infrastructure en mètres
        """
        self.infra_id = infra_id
        self.infra_kind = infra_kind if infra_kind else "aerien"  # fallback
        self.longueur = longueur
        self.is_hospital_path = False
        self.phase = None
        self.beneficiaries_proxy = 0
        
        # Calcul des coûts et durées
        self.calculate_costs()
    
    def calculate_costs(self):
        """Calcule les coûts et durées pour cette infrastructure."""
        self.material_cost = self.UNIT_PRICE.get(self.infra_kind, 500.0) * self.longueur
        self.worker_hours = self.HOURS_PER_METER.get(self.infra_kind, 2.0) * self.longueur
        self.labor_cost_continuous = self.worker_hours * self.HOURLY_WAGE
        self.duration_hours_4workers = self.worker_hours / self.MAX_WORKERS_PER_INFRA
        self.total_cost = self.material_cost + self.labor_cost_continuous
    
    def set_beneficiaries(self, count: int):
        """Définit le nombre de bénéficiaires pour cette infrastructure."""
        self.beneficiaries_proxy = count
    
    def mark_as_hospital_path(self):
        """Marque cette infrastructure comme faisant partie du chemin vers l'hôpital."""
        self.is_hospital_path = True
        self.phase = 0  # Phase 0 pour l'hôpital
    
    def assign_phase(self, phase_number: int):
        """Assigne une phase à cette infrastructure."""
        if not self.is_hospital_path:  # Ne pas écraser la phase 0 de l'hôpital
            self.phase = phase_number
    
    def get_benef_per_euro(self) -> float:
        """Calcule le ratio bénéficiaires/coût."""
        if self.total_cost == 0:
            return 0
        return self.beneficiaries_proxy / self.total_cost
    
    def to_dict(self) -> dict:
        """Convertit l'infrastructure en dictionnaire pour l'export."""
        return {
            "infra_id": self.infra_id,
            "infra_kind": self.infra_kind,
            "longueur": self.longueur,
            "material_cost": self.material_cost,
            "labor_cost_continuous": self.labor_cost_continuous,
            "total_cost": self.total_cost,
            "duration_hours_4workers": self.duration_hours_4workers,
            "beneficiaries_proxy": self.beneficiaries_proxy,
            "is_hospital_path": self.is_hospital_path,
            "phase": self.phase
        }
    
    @classmethod
    def load_all_from_data(cls, reseau_df: pd.DataFrame, infra_df: pd.DataFrame, damaged_only: bool = True) -> Dict[str, 'Infrastructure']:
        """
        Charge toutes les infrastructures à partir des données.
        
        Args:
            reseau_df: DataFrame du réseau
            infra_df: DataFrame des infrastructures
            damaged_only: Si True, ne charge que les infrastructures endommagées
            
        Returns:
            dict: Dictionnaire d'objets Infrastructure indexés par infra_id
        """
        # Filtrer les infrastructures endommagées si nécessaire
        if damaged_only:
            damaged_ids = reseau_df.loc[reseau_df["infra_type"] == "a_remplacer", "infra_id"].unique().tolist()
        else:
            damaged_ids = reseau_df["infra_id"].unique().tolist()
        
        # Obtenir les longueurs uniques par infra_id
        infra_lengths = reseau_df.groupby("infra_id", as_index=False)["longueur"].first()
        
        # Fusionner avec les types d'infrastructure
        infra_master = infra_lengths.merge(infra_df, left_on="infra_id", right_on="id_infra", how="left")
        infra_master.drop(columns=["id_infra"], inplace=True)
        infra_master.rename(columns={"type_infra": "infra_kind"}, inplace=True)
        infra_master["infra_kind"].fillna("aerien", inplace=True)  # fallback
        
        # Filtrer si nécessaire
        if damaged_only:
            infra_master = infra_master[infra_master["infra_id"].isin(damaged_ids)].copy()
        
        # Créer les objets Infrastructure
        infrastructures = {}
        for _, row in infra_master.iterrows():
            infra = cls(
                infra_id=row["infra_id"],
                infra_kind=row.get("infra_kind", "aerien"),
                longueur=row["longueur"]
            )
            infrastructures[infra.infra_id] = infra
        
        # Calculer les bénéficiaires pour chaque infrastructure
        benef_proxy = (
            reseau_df[reseau_df["infra_id"].isin(infrastructures.keys())]
            .groupby("infra_id")["nb_maisons"]
            .sum()
        )
        
        # Assigner les bénéficiaires à chaque infrastructure
        for infra_id, count in benef_proxy.items():
            if infra_id in infrastructures:
                infrastructures[infra_id].set_beneficiaries(count)
        
        return infrastructures


class ReconnectionPlanner:
    """Classe pour planifier le raccordement électrique."""
    
    # Paramètres globaux
    PHASE_SHARES = {1: 0.40, 2: 0.20, 3: 0.20, 4: 0.20}
    HOSPITAL_AUTONOMY_HOURS = 20.0
    HOSPITAL_SAFETY_MARGIN = 0.20  # 20%
    
    def __init__(self, infrastructures: Dict[str, Infrastructure], buildings: Dict[str, Building]):
        """
        Initialise le planificateur de raccordement.
        
        Args:
            infrastructures: Dictionnaire d'objets Infrastructure
            buildings: Dictionnaire d'objets Building
        """
        self.infrastructures = infrastructures
        self.buildings = buildings
        self.hospital_buildings = []
        self.hospital_infras = []
        
        # Identifier les bâtiments d'hôpital et leurs infrastructures
        self._identify_hospital_paths()
    
    def _identify_hospital_paths(self):
        """Identifie les chemins vers l'hôpital."""
        # Trouver les bâtiments d'hôpital
        hospital_buildings = [b_id for b_id, building in self.buildings.items() if building.is_hospital()]
        self.hospital_buildings = hospital_buildings
        
        # Trouver les infrastructures connectées aux hôpitaux
        hospital_infras = []
        for b_id in hospital_buildings:
            if b_id in self.buildings:
                hospital_infras.extend(self.buildings[b_id].connected_infras)
        
        # Filtrer pour ne garder que les infrastructures qui sont dans notre ensemble
        self.hospital_infras = [i_id for i_id in hospital_infras if i_id in self.infrastructures]
        
        # Marquer ces infrastructures comme faisant partie du chemin de l'hôpital
        for i_id in self.hospital_infras:
            self.infrastructures[i_id].mark_as_hospital_path()
    
    def assign_phases(self):
        """Assigne les phases aux infrastructures selon le ratio bénéficiaires/coût."""
        # Calculer le coût total
        total_cost = sum(infra.total_cost for infra in self.infrastructures.values())
        
        # Créer un pool d'infrastructures non assignées (hors hôpital)
        pool = [infra for infra in self.infrastructures.values() if infra.phase is None]
        
        # Trier par ratio bénéficiaires/coût décroissant, puis par nombre de bénéficiaires
        pool.sort(key=lambda x: (x.get_benef_per_euro(), x.beneficiaries_proxy), reverse=True)
        
        # Garder trace des infrastructures déjà assignées
        assigned = set(i_id for i_id in self.infrastructures if self.infrastructures[i_id].phase == 0)
        
        # Assigner les phases 1 à 4
        for ph in [1, 2, 3, 4]:
            target_cost = self.PHASE_SHARES[ph] * total_cost
            acc = 0.0
            remaining_pool = []
            
            for infra in pool:
                if infra.infra_id in assigned:
                    continue
                
                if acc < target_cost:
                    infra.assign_phase(ph)
                    assigned.add(infra.infra_id)
                    acc += infra.total_cost
                else:
                    remaining_pool.append(infra)
            
            pool = remaining_pool
        
        # Tout ce qui reste va en phase 4
        for infra in pool:
            if infra.infra_id not in assigned:
                infra.assign_phase(4)
    
    def check_hospital_time(self) -> dict:
        """Vérifie si le temps de raccordement de l'hôpital respecte la contrainte d'autonomie."""
        hospital_infras = [self.infrastructures[i_id] for i_id in self.hospital_infras]
        cost = sum(infra.total_cost for infra in hospital_infras)
        duration_parallel = max([infra.duration_hours_4workers for infra in hospital_infras]) if hospital_infras else 0.0
        target = self.HOSPITAL_AUTONOMY_HOURS * (1.0 - self.HOSPITAL_SAFETY_MARGIN)  # 20h * 0.8 = 16h
        ok = duration_parallel <= target
        
        return {
            "hospital_cost": cost,
            "hospital_duration_parallel": duration_parallel,
            "hospital_target_hours": target,
            "hospital_ok": ok,
        }
    
    def summarize_phases(self) -> pd.DataFrame:
        """Génère un résumé des phases."""
        # Convertir les infrastructures en dictionnaires pour créer un DataFrame
        infra_dicts = [infra.to_dict() for infra in self.infrastructures.values()]
        plan_df = pd.DataFrame(infra_dicts)
        
        total_cost = float(plan_df["total_cost"].sum())
        summary = (
            plan_df.groupby("phase")
            .agg(
                infra_count=("infra_id", "count"),
                phase_cost=("total_cost", "sum"),
                phase_material_cost=("material_cost", "sum"),
                phase_labor_cost=("labor_cost_continuous", "sum"),
                phase_duration_parallel=("duration_hours_4workers", "max"),
                beneficiaries_proxy=("beneficiaries_proxy", "sum"),
            )
            .reset_index()
            .sort_values("phase")
        )
        summary["phase_cost_pct"] = 100.0 * summary["phase_cost"] / total_cost
        return summary
    
    def build_final_plan_table(self) -> pd.DataFrame:
        """Construit le tableau final du plan de raccordement."""
        # Convertir les infrastructures en dictionnaires pour créer un DataFrame
        infra_dicts = [infra.to_dict() for infra in self.infrastructures.values()]
        plan_df = pd.DataFrame(infra_dicts)
        
        cols = [
            "infra_id", "infra_kind", "longueur",
            "material_cost", "labor_cost_continuous", "total_cost",
            "duration_hours_4workers", "beneficiaries_proxy",
            "is_hospital_path", "phase"
        ]
        final = plan_df[cols].sort_values(["phase", "is_hospital_path", "beneficiaries_proxy"], 
                                          ascending=[True, False, False])
        return final


def load_data(path_reseau: Path, path_infra: Path, path_bat: Path) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Charge les données depuis les fichiers CSV."""
    reseau = pd.read_csv(path_reseau)
    infra = pd.read_csv(path_infra)
    bat = pd.read_csv(path_bat)
    return reseau, infra, bat


def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(description="Plan de raccordement – génération des phases et coûts (version OO).")
    parser.add_argument("--reseau", required=True, type=Path, help="Chemin vers reseau_en_arbre.csv")
    parser.add_argument("--infra", required=True, type=Path, help="Chemin vers infra.csv")
    parser.add_argument("--batiments", required=True, type=Path, help="Chemin vers batiments.csv")
    parser.add_argument("--out-plan", default=Path("plan_raccordement_dommages_oo.csv"), type=Path,
                        help="Fichier CSV de sortie pour le plan détaillé")
    parser.add_argument("--out-synthese", default=Path("synthese_phases_dommages_oo.csv"), type=Path,
                        help="Fichier CSV de sortie pour la synthèse des phases")
    args = parser.parse_args()

    # Charger les données
    reseau, infra, bat = load_data(args.reseau, args.infra, args.batiments)
    
    # Créer les objets Building et Infrastructure
    buildings = Building.load_all_from_data(bat, reseau)
    infrastructures = Infrastructure.load_all_from_data(reseau, infra, damaged_only=True)
    
    # Créer le planificateur et exécuter le plan
    planner = ReconnectionPlanner(infrastructures, buildings)
    planner.assign_phases()
    
    # Générer les résultats
    synthese = planner.summarize_phases()
    h_check = planner.check_hospital_time()
    final_plan = planner.build_final_plan_table()
    
    # Sauvegardes
    final_plan.to_csv(args.out_plan, index=False)
    synthese.to_csv(args.out_synthese, index=False)
    
    # Affichage console
    print("=== HÔPITAL (Phase 0) ===")
    print(f"Bâtiment(s) hôpital: {planner.hospital_buildings}")
    print(f"Infras hôpital (endommagées): {planner.hospital_infras}")
    print(f"Coût total hôpital: {h_check['hospital_cost']:.2f} €")
    print(f"Durée critique (4 ouvriers/infra, parallèle): {h_check['hospital_duration_parallel']:.2f} h")
    print(f"Seuil objectif (20h - 20%): {h_check['hospital_target_hours']:.2f} h")
    print(f"Respecte la contrainte ? {'OUI' if h_check['hospital_ok'] else 'NON'}")
    print()
    
    print("=== SYNTHÈSE DES PHASES ===")
    with pd.option_context("display.max_rows", None, "display.max_columns", None, "display.width", 120):
        print(synthese.round(2))
    
    print()
    print(f"Fichiers générés :\n - {args.out_plan}\n - {args.out_synthese}")


if __name__ == "__main__":
    sys.exit(main())