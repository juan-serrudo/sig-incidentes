"""Generate synthetic UOIT incident dataset and partition by event group.

Strictly groups variants by event_group_id to prevent data leakage between
training, validation, and test partitions.
"""

import numpy as np
import pandas as pd

from app.schemas import IncidentInput
from app.settings import DATA_DIR, LABELS, SEED, VARIANTS_PER_FAMILY
from app.templates import FAMILIES, PREFIXES, SUFFIXES
from app.text import normalize_text


def generate_tickets(seed=SEED):
    rng = np.random.default_rng(seed)
    rows = []
    seen = set()
    base_time = pd.Timestamp("2026-01-15 08:00:00", tz="UTC")

    for category, families in FAMILIES.items():
        for family in families:
            family_id = family["family_id"]
            titles = family["titles"]
            descriptions = family["descriptions"]

            combinations = [
                (title, prefix, core, suffix)
                for title in titles
                for prefix in PREFIXES
                for core in descriptions
                for suffix in SUFFIXES
            ]
            rng.shuffle(combinations)

            generated_count = 0
            for title, prefix, core, suffix in combinations:
                initial_description = f"{prefix} {core} {suffix}"
                combined = f"{title}. {initial_description}"
                canonical = normalize_text(combined)

                if canonical in seen:
                    continue
                seen.add(canonical)

                # Assign realistic chronological timestamp
                incident_number = len(rows) + 1
                created_at = base_time + pd.Timedelta(
                    hours=incident_number * 8,
                    minutes=int(rng.integers(0, 59)),
                    seconds=int(rng.integers(0, 59)),
                )

                rows.append({
                    "incident_id": f"INC-2026-{incident_number:04d}",
                    "event_group_id": family_id,
                    "created_at": created_at.isoformat(),
                    "title": title,
                    "initial_description": initial_description,
                    "category": category,
                })
                generated_count += 1
                if generated_count == VARIANTS_PER_FAMILY[category]:
                    break

    data = pd.DataFrame(rows)
    # Sort chronologically while preserving deterministic IDs
    data = data.sort_values("created_at").reset_index(drop=True)
    # Re-assign sequential incident_id following chronological order
    data["incident_id"] = [f"INC-2026-{i + 1:04d}" for i in range(len(data))]
    return data


def validate_tickets(data):
    required = ["incident_id", "event_group_id", "created_at", "title", "initial_description", "category"]
    if not set(required).issubset(data.columns) or data.empty:
        raise ValueError("The incident dataset is empty or missing required columns.")
    if data[required].isna().any().any():
        raise ValueError("Missing values found in required columns.")
    if data.incident_id.duplicated().any():
        raise ValueError("Duplicate incident IDs found.")
    if not data.category.isin(LABELS).all():
        raise ValueError("Unknown category found in dataset.")

    for _, row in data.iterrows():
        IncidentInput(title=row["title"], initial_description=row["initial_description"])

    normalized = data.apply(lambda r: normalize_text(f"{r['title']} {r['initial_description']}"), axis=1)
    if normalized.duplicated().any():
        raise ValueError("Duplicate normalized incident texts found.")

    if not data.groupby("event_group_id").category.nunique().eq(1).all():
        raise ValueError("An event group contains contradictory categories.")


def split_by_family(data, seed=SEED):
    rng = np.random.default_rng(seed)
    assignments = {}

    for category in LABELS:
        groups = sorted(data.loc[data.category == category, "event_group_id"].unique())
        if len(groups) < 5:
            raise ValueError("At least five event groups per category are required.")
        rng.shuffle(groups)

        # 8 families per category -> 5 train, 1 validation, 2 test
        train_count = int(len(groups) * 2 / 3)  # 5
        validation_count = max(1, (len(groups) - train_count) // 2)  # 1

        for index, group_id in enumerate(groups):
            if index < train_count:
                assignments[group_id] = "train"
            elif index < train_count + validation_count:
                assignments[group_id] = "validation"
            else:
                assignments[group_id] = "test"

    result = data.copy()
    result["split"] = result.event_group_id.map(assignments)
    if result.split.isna().any():
        raise ValueError("Every event group must be assigned to a partition.")

    return tuple(result[result.split == name].copy() for name in ["train", "validation", "test"])


def main():
    data = generate_tickets()
    validate_tickets(data)
    DATA_DIR.mkdir(exist_ok=True)
    data.to_csv(DATA_DIR / "tickets.csv", index=False)

    train, validation, test = split_by_family(data)
    for name, part in zip(["train", "validation", "test"], [train, validation, test]):
        part.to_csv(DATA_DIR / f"{name}.csv", index=False)

    print(
        f"Created {len(data)} synthetic incidents in {data.event_group_id.nunique()} event groups."
    )
    print(
        f"Partition distribution: Train={len(train)} ({train.event_group_id.nunique()} groups), "
        f"Val={len(validation)} ({validation.event_group_id.nunique()} groups), "
        f"Test={len(test)} ({test.event_group_id.nunique()} groups)."
    )


if __name__ == "__main__":
    main()
