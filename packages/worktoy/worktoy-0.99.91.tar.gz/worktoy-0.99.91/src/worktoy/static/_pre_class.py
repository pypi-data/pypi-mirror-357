"""
PreClass provides a stateful class containing the name and hash of a class
about to be created.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from ..parse import maybe
from ..waitaminute import MissingVariable, VariableNotNone, TypeException

from . import AbstractObject

try:
  from typing import TYPE_CHECKING
except ImportError:  # pragma: no cover
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  from typing import Any


class PreClass(type):
  """PreClass provides a stateful class containing the name and hash of a
  class about to be created."""

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  NAMESPACE  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  #  Fallback variables
  __private_fallback__ = '__pre_class__'

  #  Private variables
  __meta_class__ = None
  __hash_value__ = None

  #  Public variables

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  CONSTRUCTORS   # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __new__(mcls, *args, **kwargs) -> type:
    """
    PreClass instances are basically treated as classes, thus 'type' is
    a reasonable base.
    """
    _name, _hash, bases, _meta = None, None, [], None
    for arg in args:
      if isinstance(arg, str):
        if _name is None:
          _name = arg
          continue
      if isinstance(arg, int):
        if _hash is None:
          _hash = arg
          continue
      if isinstance(arg, type):
        if issubclass(arg, type):
          if _meta is None:
            _meta = arg
            continue
        bases.append(arg)

    cls = type.__new__(mcls, _name, (*bases,), {})
    setattr(cls, '__hash_value__', _hash)
    setattr(cls, '__meta_class__', _meta)
    return cls

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  DOMAIN SPECIFIC  # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  Python API   # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __instance_check__(cls, instance: Any) -> bool:
    """
    Checks if the instance is an instance of the PreClass.
    """
    type_ = type(instance)
    return True if hash(type_) == cls.__hash_value__ else False

  def __hash__(cls, ) -> int:
    """
    Returns the explicitly set hash value of the PreClass object.
    """
    if cls.__hash_value__ is None:
      raise MissingVariable('__hash_value__', int)
    if isinstance(cls.__hash_value__, int):
      return cls.__hash_value__
    name, value = '__hash_value__', cls.__hash_value__
    raise TypeException(name, value, int)

  def __getattribute__(cls, key: str, ) -> Any:
    """
    This reimplementation of __getattribute__ was done by a highly skilled
    professional, do not try this at home!
    """
    if key == '__class__':
      return object.__getattribute__(cls, '__meta_class__')
    return object.__getattribute__(cls, key)
