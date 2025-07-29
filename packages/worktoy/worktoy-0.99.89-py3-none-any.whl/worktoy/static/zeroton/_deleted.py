"""DELETED provides a value used to indicate that an attribute is to be
treated as having been deleted. For example, after a call to __delete__,
subsequent calls to __get__ should raise AttributeError until a call to
__set__ provides a new value. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from . import Zeroton

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  pass


class DELETED(metaclass=Zeroton):
  """DELETED is a singleton class that is used to indicate that an
  attribute has been deleted. It covers an edge case where a deleted
  attribute is accessed, and this singleton is present to indicate that
  the attribute has been deleted with 'del <attr>' or similar."""
  pass
