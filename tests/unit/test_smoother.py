"""Tests for Exponential Moving Average filter and deadzone suppression."""

import pytest

from facepong.vision.smoother import EMASmoother


def test_smoother_parameter_validation() -> None:
    """Ensure invalid alpha or negative deadzone raises ValueError."""
    with pytest.raises(ValueError):
        EMASmoother(alpha=0.0)

    with pytest.raises(ValueError):
        EMASmoother(alpha=1.5)

    with pytest.raises(ValueError):
        EMASmoother(deadzone=-0.1)


def test_smoother_initialization_and_filtering() -> None:
    """First sample initializes state; subsequent samples smooth signal."""
    smoother = EMASmoother(alpha=0.5, deadzone=0.01)

    # First sample sets initial value directly
    assert smoother.filter(10.0) == 10.0

    # Second sample: 0.5 * 20 + 0.5 * 10 = 15.0
    assert smoother.filter(20.0) == 15.0


def test_smoother_deadzone_suppression() -> None:
    """Small fluctuations below deadzone must be ignored."""
    smoother = EMASmoother(alpha=0.5, deadzone=0.05)
    smoother.filter(1.0)

    # Fluctuation of 0.02 is under 0.05 deadzone
    assert smoother.filter(1.02) == 1.0


def test_smoother_reset() -> None:
    """Verify reset clears current value memory."""
    smoother = EMASmoother(alpha=0.5, deadzone=0.01)
    smoother.filter(10.0)
    smoother.reset()
    assert smoother.current_value is None
