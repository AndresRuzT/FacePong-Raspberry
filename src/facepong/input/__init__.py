"""Input abstraction and adapter system."""

from facepong.input.base import InputAdapter
from facepong.input.face_input import FaceInputAdapter
from facepong.input.keyboard_input import KeyboardInputAdapter

__all__ = ["FaceInputAdapter", "InputAdapter", "KeyboardInputAdapter"]
