#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plan de raccordement électrique post-intempéries
------------------------------------------------
Lit reseau_en_arbre.csv, infra.csv, batiments.csv et produit :
- plan_raccordement_dommages.csv
- synthese_phases_dommages.csv

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

# ---- Paramètres globaux ----
UNIT_PRICE = {"aerien": 500.0, "semi-aerien": 750.0, "fourreau": 900.0}
HOURS_PER_METER = {"aerien": 2.0, "semi-aerien": 4.0, "fourreau": 5.0}
HOURLY_WAGE = 300.0 / 8.0  # 37.5 €/h
MAX_WORKERS_PER_INFRA = 4

PHASE_SHARES = {1: 0.40, 2: 0.20, 3: 0.20, 4: 0.20}

HOSPITAL_AUTONOMY_HOURS = 20.0
HOSPITAL_SAFETY_MARGIN = 0.20  # 20%


def load_data(path_reseau: Path, path_infra: Path, path_bat: Path):
    reseau = pd.read_csv(path_reseau)
    infra = pd.read_csv(path_infra)
    bat = pd.read_csv(path_bat)
    return reseau, infra, bat


def compute_infra_master(reseau: pd.DataFrame, infra: pd.DataFrame, damaged_only: bool = True) -> pd.DataFrame:
    """Assemble la table des infras avec longueur unique et type."""
    if damaged_only:
        damaged_ids = reseau.loc[reseau["infra_type"] == "a_remplacer", "infra_id"].unique().tolist()
    else:
        damaged_ids = reseau["infra_id"].unique().tolist()

    infra_lengths = reseau.groupby("infra_id", as_index=False)["longueur"].first()
    infra_master = infra_lengths.merge(infra, left_on="infra_id", right_on="id_infra", how="left")
    infra_master.drop(columns=["id_infra"], inplace=True)
    infra_master.rename(columns={"type_infra": "infra_kind"}, inplace=True)
    infra_master["infra_kind"].fillna("aerien", inplace=True)  # fallback

    if damaged_only:
        infra_master = infra_master[infra_master["infra_id"].isin(damaged_ids)].copy()

    # Coûts et durées
    infra_master["material_cost"] = infra_master.apply(
        lambda r: UNIT_PRICE.get(r["infra_kind"], 500.0) * r["longueur"], axis=1
    )
    infra_master["worker_hours"] = infra_master.apply(
        lambda r: HOURS_PER_METER.get(r["infra_kind"], 2.0) * r["longueur"], axis=1
    )
    infra_master["labor_cost_continuous"] = infra_master["worker_hours"] * HOURLY_WAGE
    infra_master["duration_hours_4workers"] = infra_master["worker_hours"] / MAX_WORKERS_PER_INFRA
    infra_master["total_cost"] = infra_master["material_cost"] + infra_master["labor_cost_continuous"]

    # Bénéficiaires (proxy) : nb_maisons remonté de reseau
    benef_proxy = (
        reseau[reseau["infra_id"].isin(infra_master["infra_id"])]
        .groupby("infra_id")["nb_maisons"]
        .sum()
        .rename("beneficiaries_proxy")
    )
    infra_master = infra_master.merge(benef_proxy, on="infra_id", how="left").fillna({"beneficiaries_proxy": 0})
    return infra_master


def tag_hospital_path(infra_master: pd.DataFrame, reseau: pd.DataFrame, bat: pd.DataFrame) -> pd.DataFrame:
    """Identifie les infras sur le chemin de l'hôpital, limitées aux 'infra_master'."""
    hosp_bats = bat[bat["type_batiment"].str.lower().str.contains("hôpital|hopital", regex=True, na=False)]
    hospital_ids = hosp_bats["id_batiment"].unique().tolist()
    hospital_infras_all = reseau[reseau["id_batiment"].isin(hospital_ids)]["infra_id"].unique().tolist()
    hospital_infras = [iid for iid in hospital_infras_all if iid in set(infra_master["infra_id"])]

    out = infra_master.copy()
    out["is_hospital_path"] = out["infra_id"].isin(hospital_infras)
    return out, hospital_ids, hospital_infras


def assign_phases(plan: pd.DataFrame) -> pd.DataFrame:
    """Affecte phase 0 (hôpital), puis 1..4 selon le ratio bénéficiaires/€ jusqu'à atteindre les parts cibles."""
    total_cost = float(plan["total_cost"].sum())
    plan = plan.copy()
    # Phase 0 déjà taguée par 'is_hospital_path'
    plan["phase"] = np.where(plan["is_hospital_path"], 0, np.nan)

    pool = plan[plan["phase"].isna()].copy()
    pool["benef_per_euro"] = pool["beneficiaries_proxy"] / pool["total_cost"].replace(0, np.nan)
    pool_sorted = pool.sort_values(by=["benef_per_euro", "beneficiaries_proxy"], ascending=False).copy()

    assigned = set(plan.loc[plan["phase"] == 0, "infra_id"].tolist())

    for ph in [1, 2, 3, 4]:
        target_cost = PHASE_SHARES[ph] * total_cost
        acc = 0.0
        selected = []
        remaining_rows = []
        for _, row in pool_sorted.iterrows():
            if row["infra_id"] in assigned:
                continue
            if acc < target_cost:
                selected.append(row["infra_id"])
                assigned.add(row["infra_id"])
                acc += float(row["total_cost"])
            else:
                remaining_rows.append(row)
        plan.loc[plan["infra_id"].isin(selected), "phase"] = ph
        pool_sorted = pd.DataFrame(remaining_rows) if remaining_rows else pd.DataFrame(columns=pool_sorted.columns)

    # Tout ce qui reste va en phase 4
    if not pool_sorted.empty:
        plan.loc[plan["infra_id"].isin(pool_sorted["infra_id"]), "phase"] = 4

    return plan


def summarize_phases(plan: pd.DataFrame) -> pd.DataFrame:
    total_cost = float(plan["total_cost"].sum())
    summary = (
        plan.groupby("phase")
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


def check_hospital_time(plan: pd.DataFrame) -> dict:
    hospital_df = plan[plan["is_hospital_path"]].copy()
    cost = float(hospital_df["total_cost"].sum())
    duration_parallel = float(hospital_df["duration_hours_4workers"].max()) if len(hospital_df) else 0.0
    target = HOSPITAL_AUTONOMY_HOURS * (1.0 - HOSPITAL_SAFETY_MARGIN)  # 20h * 0.8 = 16h
    ok = duration_parallel <= target
    return {
        "hospital_cost": cost,
        "hospital_duration_parallel": duration_parallel,
        "hospital_target_hours": target,
        "hospital_ok": ok,
    }


def build_final_plan_table(plan: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "infra_id", "infra_kind", "longueur",
        "material_cost", "labor_cost_continuous", "total_cost",
        "duration_hours_4workers", "beneficiaries_proxy",
        "is_hospital_path", "phase"
    ]
    final = plan[cols].sort_values(["phase", "is_hospital_path", "beneficiaries_proxy"], ascending=[True, False, False])
    return final


def main():
    parser = argparse.ArgumentParser(description="Plan de raccordement – génération des phases et coûts.")
    parser.add_argument("--reseau", required=True, type=Path, help="Chemin vers reseau_en_arbre.csv")
    parser.add_argument("--infra", required=True, type=Path, help="Chemin vers infra.csv")
    parser.add_argument("--batiments", required=True, type=Path, help="Chemin vers batiments.csv")
    parser.add_argument("--out-plan", default=Path("plan_raccordement_dommages.csv"), type=Path,
                        help="Fichier CSV de sortie pour le plan détaillé")
    parser.add_argument("--out-synthese", default=Path("synthese_phases_dommages.csv"), type=Path,
                        help="Fichier CSV de sortie pour la synthèse des phases")
    args = parser.parse_args()

    reseau, infra, bat = load_data(args.reseau, args.infra, args.batiments)

    infra_master = compute_infra_master(reseau, infra, damaged_only=True)
    plan0, hospital_bids, hospital_iids = tag_hospital_path(infra_master, reseau, bat)
    plan = assign_phases(plan0)
    synthese = summarize_phases(plan)
    h_check = check_hospital_time(plan)
    final_plan = build_final_plan_table(plan)

    # Sauvegardes
    final_plan.to_csv(args.out_plan, index=False)
    synthese.to_csv(args.out_synthese, index=False)

    # Affichage console
    print("=== HÔPITAL (Phase 0) ===")
    print(f"Bâtiment(s) hôpital: {hospital_bids}")
    print(f"Infras hôpital (endommagées): {hospital_iids}")
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
