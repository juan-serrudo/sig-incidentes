import pandas as pd
import pytest

from app.data import generate_tickets, split_by_family, validate_tickets
from app.settings import LABELS
from app.text import normalize_text


def test_generation_is_reproducible_and_valid():
    data = generate_tickets()
    pd.testing.assert_frame_equal(data, generate_tickets())
    assert len(data) == 720
    assert data.event_group_id.nunique() == 40
    validate_tickets(data)


def test_event_groups_and_duplicate_text_do_not_cross_partitions():
    train, validation, test = split_by_family(generate_tickets())
    for left, right in [(train, validation), (train, test), (validation, test)]:
        assert set(left.event_group_id).isdisjoint(right.event_group_id)
        left_norm = left.apply(lambda r: normalize_text(f"{r.title} {r.initial_description}"), axis=1)
        right_norm = right.apply(lambda r: normalize_text(f"{r.title} {r.initial_description}"), axis=1)
        assert set(left_norm).isdisjoint(set(right_norm))

    assert [len(part) for part in [train, validation, test]] == [450, 90, 180]
    for part in [train, validation, test]:
        assert set(part.category) == set(LABELS)


def test_duplicate_normalized_incidents_are_rejected():
    data = generate_tickets()
    data.loc[1, "title"] = data.loc[0, "title"].upper()
    data.loc[1, "initial_description"] = data.loc[0, "initial_description"].upper()
    with pytest.raises(ValueError, match="Duplicate normalized"):
        validate_tickets(data)


def test_contradictory_labels_within_an_event_group_are_rejected():
    data = generate_tickets()
    data.loc[0, "category"] = "databases" if data.loc[0, "category"] != "databases" else "security_access"
    with pytest.raises(ValueError, match="contradictory"):
        validate_tickets(data)


def test_unknown_categories_are_rejected():
    data = generate_tickets()
    data.loc[0, "category"] = "unknown_category"
    with pytest.raises(ValueError, match="Unknown"):
        validate_tickets(data)


def test_accent_and_whitespace_normalization():
    assert normalize_text("  CONTRASEÑA, sesión! ") == "contrasena sesion"
    assert normalize_text("PostgreSQL: max_connections") == "postgresql max connections"
