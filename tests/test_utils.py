import pytest
from libximc.highlevel._structure_types import move_settings_t

from fastcs_standa_mirror.utils import patch_move_flags


@pytest.fixture()
def _unpatch_move_flags():
    """Restore original MoveFlags property after test."""
    original_prop = move_settings_t.__dict__["MoveFlags"]
    yield
    move_settings_t.MoveFlags = original_prop


# If this test starts failing this bug may have been fixed upstream in libximc,
# in which case patch_move_flags can be removed
def test_move_flags_rejects_unknown_bits_without_patch():
    """Confirm the underlying bug exists — 0xCC is rejected by the enum."""
    settings = move_settings_t.__new__(move_settings_t)
    with pytest.raises(ValueError, match="MoveFlags"):
        settings.MoveFlags = 0xCC


def test_patch_move_flags_tolerates_unknown_bits():
    """After patching, hardware values with undocumented bits don't crash."""
    patch_move_flags()
    settings = move_settings_t.__new__(move_settings_t)

    settings.MoveFlags = 0xCC  # should not raise
    settings.MoveFlags = 0x01  # valid flag still works
