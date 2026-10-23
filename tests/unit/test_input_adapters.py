"""Tests for InputAdapter implementations."""

from unittest.mock import MagicMock

import pygame

from facepong.input.face_input import FaceInputAdapter
from facepong.input.keyboard_input import KeyboardInputAdapter


def test_face_input_adapter() -> None:
    """Verify face input adapter updates and returns target position."""
    adapter = FaceInputAdapter(player_id=1)
    assert not adapter.is_detected()

    adapter.update_from_vision(position=0.75, detected=True)
    assert adapter.is_detected()
    assert adapter.get_normalized_position() == 0.75
    assert adapter.get_delta_y(0.016) == 0.0


def test_keyboard_input_adapter() -> None:
    """Verify keyboard input adapter reacts to key events and produces displacement."""
    adapter = KeyboardInputAdapter(key_up=pygame.K_w, key_down=pygame.K_s, speed=500.0)
    assert adapter.is_detected()
    assert adapter.get_normalized_position() is None

    # Key down W (move up -> negative delta Y)
    event_w_down = MagicMock(type=pygame.KEYDOWN, key=pygame.K_w)
    adapter.handle_event(event_w_down)
    assert adapter.get_delta_y(dt=0.1) == -50.0

    # Key up W
    event_w_up = MagicMock(type=pygame.KEYUP, key=pygame.K_w)
    adapter.handle_event(event_w_up)
    assert adapter.get_delta_y(dt=0.1) == 0.0

    # Key down S (move down -> positive delta Y)
    event_s_down = MagicMock(type=pygame.KEYDOWN, key=pygame.K_s)
    adapter.handle_event(event_s_down)
    assert adapter.get_delta_y(dt=0.1) == 50.0
