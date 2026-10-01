"""Create synthetic messages and split by phrase family, never by individual variant."""

import numpy as np
import pandas as pd

from app.schemas import TicketInput
from app.settings import DATA_DIR, LABELS, SEED, VARIANTS_PER_FAMILY
from app.templates import FAMILIES, PREFIXES, SUFFIXES
from app.text import normalize_text


def generate_tickets(seed=SEED):
    rng = np.random.default_rng(seed)
    rows = []
    seen = set()
    for category, families in FAMILIES.items():
        for family_index, phrasings in enumerate(families):
            family_id = f"{category}-{family_index + 1:02d}"
            combinations = [(prefix, core, suffix) for prefix in PREFIXES for core in phrasings for suffix in SUFFIXES]
            rng.shuffle(combinations)
            generated_count = 0
            for prefix, core, suffix in combinations:
                message = f"{prefix} {core} {suffix}"
                canonical = normalize_text(message)
                if canonical in seen:
                    continue
                seen.add(canonical)
                rows.append({"ticket_id": f"REQ-{len(rows) + 1:04d}", "family_id": family_id, "message": message, "category": category})
                generated_count += 1
                if generated_count == VARIANTS_PER_FAMILY[category]:
                    break
    return pd.DataFrame(rows)


def validate_tickets(data):
    required = ["ticket_id", "family_id", "message", "category"]
    if not set(required).issubset(data.columns) or data.empty:
        raise ValueError("The ticket dataset is empty or missing required columns.")
    if data[required].isna().any().any() or data.ticket_id.duplicated().any():
        raise ValueError("Missing values or duplicate ticket IDs.")
    if not data.category.isin(LABELS).all():
        raise ValueError("Unknown category.")
    for message in data.message:
        TicketInput(message=message)
    if data.message.map(normalize_text).duplicated().any():
        raise ValueError("Duplicate normalized messages.")
    if not data.groupby("family_id").category.nunique().eq(1).all():
        raise ValueError("A phrase family has contradictory categories.")


def split_by_family(data, seed=SEED):
    rng = np.random.default_rng(seed)
    assignments = {}
    for category in LABELS:
        families = sorted(data.loc[data.category == category, "family_id"].unique())
        if len(families) < 5:
            raise ValueError("At least five phrase families per category are required.")
        rng.shuffle(families)
        train_count = int(len(families) * 2 / 3)
        validation_count = max(1, (len(families) - train_count) // 2)
        for index, family in enumerate(families):
            assignments[family] = "train" if index < train_count else "validation" if index < train_count + validation_count else "test"
    result = data.copy()
    result["split"] = result.family_id.map(assignments)
    if result.split.isna().any():
        raise ValueError("Every family must be assigned to a partition.")
    return tuple(result[result.split == name].copy() for name in ["train", "validation", "test"])


def main():
    data = generate_tickets()
    validate_tickets(data)
    DATA_DIR.mkdir(exist_ok=True)
    data.to_csv(DATA_DIR / "tickets.csv", index=False)
    for name, part in zip(["train", "validation", "test"], split_by_family(data)):
        part.to_csv(DATA_DIR / f"{name}.csv", index=False)
    print(f"Created {len(data)} synthetic messages in {data.family_id.nunique()} phrase families.")


if __name__ == "__main__":
    main()
