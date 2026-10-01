import pandas as pd
import pytest

from app.data import generate_tickets, split_by_family, validate_tickets
from app.settings import LABELS
from app.text import normalize_text


def test_generation_is_reproducible_and_valid():
    data = generate_tickets()
    pd.testing.assert_frame_equal(data, generate_tickets())
    assert len(data) == 1104
    assert data.family_id.nunique() == 60
    validate_tickets(data)


def test_families_and_duplicate_text_do_not_cross_partitions():
    train, validation, test = split_by_family(generate_tickets())
    for left, right in [(train, validation), (train, test), (validation, test)]:
        assert set(left.family_id).isdisjoint(right.family_id)
        assert set(left.message.map(normalize_text)).isdisjoint(right.message.map(normalize_text))
    assert [len(part) for part in [train, validation, test]] == [736, 184, 184]
    for part in [train, validation, test]:
        assert set(part.category) == set(LABELS)


def test_duplicate_normalized_messages_are_rejected():
    data = generate_tickets()
    data.loc[1, "message"] = data.loc[0, "message"].upper()
    with pytest.raises(ValueError, match="Duplicate normalized"):
        validate_tickets(data)


def test_contradictory_labels_within_a_family_are_rejected():
    data = generate_tickets()
    data.loc[0, "category"] = "email"
    with pytest.raises(ValueError, match="contradictory"):
        validate_tickets(data)


def test_unknown_categories_are_rejected():
    data = generate_tickets()
    data.loc[0, "category"] = "unknown"
    with pytest.raises(ValueError, match="Unknown"):
        validate_tickets(data)


def test_accent_and_whitespace_normalization():
    assert normalize_text("  CONTRASEÑA, sesión! ") == "contrasena sesion"

