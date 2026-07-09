"""
Synthetic carbon credit retirement transaction generator.

Strategy:
1. Generate a clean population of internally-consistent transactions.
2. Inject a small, fixed number of realistic discrepancies on top of that
   clean population (one or two per discrepancy type), each derived from
   a real, known carbon-market failure mode.
3. Record ground truth (which row(s), which discrepancy type) in a
   separate answer key, so validator output can be scored automatically.

Discrepancy types modeled:
  - double_count       : same serial number claimed by two different companies
  - vintage_mismatch    : claim_year predates vintage_year (credit claimed
                          for a year before it was even generated)
  - unit_error          : gas_type/unit combination is silently wrong
                          (e.g. CH4 quantity reported as if it were CO2,
                          with no GWP adjustment)
  - double_retirement   : same serial number retired twice (different dates)
  - registry_mismatch   : project_type claimed under a registry that does
                          not actually issue credits for that methodology
"""

import random
from datetime import date, timedelta

import pandas as pd

from reference_data import (
    REGISTRIES,
    PROJECT_TYPE_REGISTRY_MAP,
    PROJECT_TYPES,
    GWP_FACTORS,
    UNITS,
    COMPANIES,
    VINTAGE_YEAR_RANGE,
    CLAIM_YEAR_RANGE,
)

random.seed(42)  # reproducible dataset


def _make_serial_number(registry: str, project_id: int, vintage_year: int, seq: int) -> str:
    """Build a realistic-looking serial number, loosely modeled on Verra's
    real structure: registry prefix + project ID + vintage + sequence block.
    """
    prefix = {
        "Verra": "VCS",
        "Gold Standard": "GS",
        "ACR": "ACR",
        "CAR": "CAR",
        "Puro.earth": "PURO",
    }[registry]
    return f"{prefix}-{project_id:05d}-{vintage_year}-{seq:08d}"


def _random_date_in_year(year: int) -> date:
    start = date(year, 1, 1)
    end = date(year, 12, 31)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def _clean_transaction(txn_id: int, project_id: int, seq_counter: dict) -> dict:
    """Generate one fully self-consistent, valid transaction."""
    project_type = random.choice(PROJECT_TYPES)
    valid_registries = PROJECT_TYPE_REGISTRY_MAP[project_type]
    registry = random.choice(valid_registries)

    vintage_year = random.randint(*VINTAGE_YEAR_RANGE)
    claim_year = random.randint(max(vintage_year, CLAIM_YEAR_RANGE[0]), CLAIM_YEAR_RANGE[1])

    gas_type = random.choices(["CO2", "CH4", "N2O"], weights=[0.85, 0.1, 0.05])[0]
    unit = "tCO2e"  # clean rows always report in proper CO2-equivalent terms
    quantity = round(random.uniform(50, 5000), 2)

    seq_counter[registry] = seq_counter.get(registry, 0) + 1
    serial_number = _make_serial_number(registry, project_id, vintage_year, seq_counter[registry])

    retirement_date = _random_date_in_year(claim_year)

    return {
        "transaction_id": f"T{txn_id:06d}",
        "serial_number": serial_number,
        "registry": registry,
        "project_type": project_type,
        "vintage_year": vintage_year,
        "quantity": quantity,
        "unit": unit,
        "gas_type": gas_type,
        "status": "retired",
        "retirement_date": retirement_date.isoformat(),
        "claimed_by": random.choice(COMPANIES),
        "claim_year": claim_year,
        "claim_id": f"CLAIM-{claim_year}-{random.randint(1000,9999)}",
    }


def generate_dataset(n_clean: int = 220) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Generate the full dataset.

    Returns:
        transactions_df: the dataset the validator will run on
        answer_key_df:   ground truth of injected discrepancies (NOT passed
                         to the validator — used only to score its output)
    """
    seq_counter: dict = {}
    rows = []
    for i in range(n_clean):
        project_id = random.randint(1000, 9999)
        rows.append(_clean_transaction(i, project_id, seq_counter))

    answer_key = []

    # --- Inject discrepancy 1: double_count ---
    # Same credit serial number claimed by two different companies.
    base = dict(rows[10])
    dup = dict(base)
    dup["transaction_id"] = "T900001"
    dup["claimed_by"] = random.choice([c for c in COMPANIES if c != base["claimed_by"]])
    dup["claim_id"] = f"CLAIM-{base['claim_year']}-{random.randint(1000,9999)}"
    rows.append(dup)
    answer_key.append({
        "transaction_id": dup["transaction_id"],
        "serial_number": dup["serial_number"],
        "discrepancy_type": "double_count",
        "note": f"Serial number also claimed in {base['transaction_id']} by {base['claimed_by']}",
    })

    # --- Inject discrepancy 2: vintage_mismatch ---
    # claim_year set earlier than vintage_year (claiming a credit for a
    # period before the underlying reduction even occurred).
    idx = 30
    bad_row = dict(rows[idx])
    bad_row["transaction_id"] = f"T{idx:06d}"
    bad_row["claim_year"] = bad_row["vintage_year"] - 2
    rows[idx] = bad_row
    answer_key.append({
        "transaction_id": bad_row["transaction_id"],
        "serial_number": bad_row["serial_number"],
        "discrepancy_type": "vintage_mismatch",
        "note": f"claim_year ({bad_row['claim_year']}) predates vintage_year ({bad_row['vintage_year']})",
    })

    # --- Inject discrepancy 3: unit_error ---
    # A methane (CH4) credit reported with unit tCO2 instead of tCO2e —
    # i.e. no GWP adjustment applied, silently understating real impact.
    idx = 55
    bad_row = dict(rows[idx])
    bad_row["transaction_id"] = f"T{idx:06d}"
    bad_row["gas_type"] = "CH4"
    bad_row["unit"] = "tCO2"  # should be tCO2e with GWP_FACTORS["CH4"] applied
    rows[idx] = bad_row
    answer_key.append({
        "transaction_id": bad_row["transaction_id"],
        "serial_number": bad_row["serial_number"],
        "discrepancy_type": "unit_error",
        "note": "CH4 quantity reported in tCO2 without GWP-equivalent conversion to tCO2e",
    })

    # --- Inject discrepancy 4: double_retirement ---
    # Same serial number retired twice, on two different dates.
    base = dict(rows[80])
    second = dict(base)
    second["transaction_id"] = "T900002"
    original_date = date.fromisoformat(base["retirement_date"])
    second["retirement_date"] = (original_date + timedelta(days=120)).isoformat()
    second["claim_id"] = f"CLAIM-{base['claim_year']}-{random.randint(1000,9999)}"
    rows.append(second)
    answer_key.append({
        "transaction_id": second["transaction_id"],
        "serial_number": second["serial_number"],
        "discrepancy_type": "double_retirement",
        "note": f"Same serial number already retired on {base['retirement_date']} in {base['transaction_id']}",
    })

    # --- Inject discrepancy 5: registry_mismatch ---
    # project_type claimed under a registry that doesn't actually issue
    # credits for that methodology (e.g. REDD+ claimed under CAR).
    idx = 105
    bad_row = dict(rows[idx])
    bad_row["transaction_id"] = f"T{idx:06d}"
    bad_row["project_type"] = "REDD+ (VM0048)"  # Verra-only methodology
    bad_row["registry"] = "CAR"  # CAR does not issue VM0048 credits
    rows[idx] = bad_row
    answer_key.append({
        "transaction_id": bad_row["transaction_id"],
        "serial_number": bad_row["serial_number"],
        "discrepancy_type": "registry_mismatch",
        "note": "REDD+ (VM0048) claimed under CAR, which does not issue credits for this methodology",
    })

    transactions_df = pd.DataFrame(rows)
    answer_key_df = pd.DataFrame(answer_key)
    return transactions_df, answer_key_df


if __name__ == "__main__":
    txns, answer_key = generate_dataset()
    txns.to_csv("../data/transactions.csv", index=False)
    answer_key.to_csv("../data/answer_key.csv", index=False)
    print(f"Generated {len(txns)} transactions ({len(answer_key)} seeded discrepancies)")
    print(f"Clean rows: {len(txns) - len(answer_key)}")
    print("\nAnswer key:")
    print(answer_key.to_string(index=False))
