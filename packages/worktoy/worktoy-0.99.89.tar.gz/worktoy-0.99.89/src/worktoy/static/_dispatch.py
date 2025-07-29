"""
The Dispatch class dispatches a function call to the appropriate
function based on the type of the first argument.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

import os
from types import FunctionType as Func
from types import MethodType as Meth

from . import AbstractObject
from ..attr import Field
from ..static import TypeSig
from ..text import typeMsg, monoSpace
from ..waitaminute import HashMismatch, CastMismatch, FlexMismatch
from ..waitaminute import DispatchException, CascadeException
from ..waitaminute import IllegalDispatcher, MissingVariable

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  from typing import Any, Callable, TypeAlias

  Types: TypeAlias = tuple[type, ...]
  Hashes: TypeAlias = list[int]
  HashMap: TypeAlias = dict[int, Callable]
  TypesMap: TypeAlias = dict[Types, Callable]
  CastMap: TypeAlias = dict[Types, Callable]
  CallMap: TypeAlias = dict[TypeSig, Callable]


class Dispatch(AbstractObject):
  """
Dispatch replaces the usual bound method when overloaded function
objects are used. The Dispatch instance serves as a dynamic method
selector, attached to a class attribute in place of the original
function object.

Dispatch achieves this by subclassing AbstractObject, which provides
a full implementation of the descriptor protocol, including
__get__, __set__, and __delete__. This allows Dispatch to operate as
a descriptor that controls method binding and function dispatching.

When called, Dispatch attempts to match the provided arguments to one
of its registered TypeSig signatures. It proceeds in the following stages:

1. Fast dispatch:
   The most performant stage. Arguments must match the expected types
   exactly — even an int will not match a float. If an exact match is
   found, Dispatch immediately invokes the corresponding function.

2. Cast dispatch:
   If fast dispatch fails, Dispatch attempts to cast arguments to the
   required types, proceeding only if all casts succeed.

3. Flex dispatch:
   If casting also fails, Dispatch performs flexible matching. It may
   reorder arguments and unpack iterables as needed to satisfy the
   signature.

Classes derived from BaseMeta can decorate methods with @overload([TYPES])
to indicate that the decorated object should be dispatched when receiving
arguments matching the given types. The custom metaclass control flow then
instantiates Dispatch during class creation.
  """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  NAMESPACE  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  #  Class variables
  __latest_dispatch__ = None  # The latest dispatch that was made
  __running_tests__ = None  # Whether the class is running tests
  __overload_dispatcher__ = True  # Required flag for all dispatchers!

  #  Private variables
  __call_map__ = None

  #  Public variables
  __name__ = Field()

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  GETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def getTypeSigs(self) -> list[TypeSig]:
    """
    Getter-function for the type signatures supported.
    """
    return [*self.__call_map__.keys(), ]

  @classmethod
  def getLatestDispatch(cls) -> Func:
    """
    Getter-function for the most recently successful dispatch.
    """
    if cls.__latest_dispatch__ is None:
      raise MissingVariable('__latest_dispatch__', Meth)
    return cls.__latest_dispatch__.__func__

  @classmethod
  def _createTestFlag(cls) -> None:
    """
    Create the test flag for the class.
    """
    value = os.environ.get('RUNNING_TESTS', '')
    cls.__running_tests__ = True if value else False

  @classmethod
  def getTestFlag(cls, **kwargs) -> bool:
    """
    Get the test flag.
    """
    if cls.__running_tests__ is None:
      if kwargs.get('_recursion', False):
        raise RecursionError
      cls._createTestFlag()
      return cls.getTestFlag(_recursion=True)
    return cls.__running_tests__

  @__name__.GET
  def _getName(self, ) -> str:
    """
    Get the name of the function.
    """
    return self.getFieldName()

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  SETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  @classmethod
  def _resetLatestDispatch(cls) -> None:
    """
    Reset the latest dispatch to None.
    """
    cls.__latest_dispatch__ = None

  @classmethod
  def _setLatestDispatch(cls, dispatch: Callable) -> None:
    """
    Set the latest dispatch to the given dispatch.
    """
    cls.__latest_dispatch__ = dispatch

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  CONSTRUCTORS   # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __init__(self, callMap: CallMap) -> None:
    self.__call_map__ = callMap

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  Python API   # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __set_name__(self, owner: type, name: str, **kwargs) -> None:
    """
    When the owning class is created, Python calls this method to allowing
    the type signatures to be updated with the owner class. This is
    necessary as the type signatures are able to reference the owning
    class before it is created by using the 'THIS' token object in place
    of it.
    """
    AbstractObject.__set_name__(self, owner, name, **kwargs)

    for sig, call in self.__call_map__.items():
      if not isinstance(sig, TypeSig):
        raise TypeError(typeMsg('sig', sig, TypeSig))
      if not callable(call):
        raise TypeError(typeMsg('call', call, Func))
      TypeSig.replaceTHIS(sig, owner)

  def __init_subclass__(cls, **kwargs) -> None:
    """
    This method checks that subclasses retain the token flag to indicate
    their use as dispatchers. See the 'IllegalDispatcher' documentation
    for more details.
    """
    try:
      _ = cls.__overload_dispatcher__
    except Exception as exception:
      raise IllegalDispatcher(cls, ) from exception

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  DOMAIN SPECIFIC  # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def _fastDispatch(self, *args, **kwargs) -> Any:
    """
    Fast dispatch the function call.
    """
    exceptions = []
    for sig, call in self.__call_map__.items():
      try:
        posArgs = sig.fast(*args)
      except HashMismatch as hashMismatch:
        exceptions.append(hashMismatch)
        continue
      else:
        if hasattr(call, '__func__'):
          return call.__func__(self.instance, *posArgs, **kwargs)
        return call(self.instance, *posArgs, **kwargs)
    else:
      if exceptions:
        raise exceptions[-1]  # Will be caught by control flow
      raise RuntimeError("""No signatures defined!""")

  def _castDispatch(self, *args, **kwargs) -> Any:
    """
    Dispatches the function call with arguments casted to the expected
    types.
    """
    exceptions = []
    for sig, call in self.__call_map__.items():
      try:
        posArgs = sig.cast(*args)
      except CastMismatch as castMismatch:
        exceptions.append(castMismatch)
        continue
      else:
        return call(self.instance, *posArgs, **kwargs)
    else:
      if exceptions:
        raise exceptions[-1]  # Will be caught by control flow
      raise RuntimeError("""No signatures defined!""")

  def _flexDispatch(self, *args, **kwargs) -> Any:
    """
    The most flexible attempt to dispatch the function call.
    """
    exceptions = []
    for sig, call in self.__call_map__.items():
      try:
        posArgs = sig.flex(*args)
      except Exception as exception:
        exceptions.append(exception)
        continue
      else:
        return call(self.instance, *posArgs, **kwargs)
    else:
      if exceptions:
        raise exceptions[-1]  # Will be caught by control flow
      raise RuntimeError("""No signatures defined!""")

  def _dispatch(self, *args: Any, **kwargs: Any) -> Any:
    """
    Dispatches the function call by trying fast, cast and flex in that
    order.
    """
    testFlag = self.getTestFlag()
    if testFlag:
      self._setLatestDispatch(self._fastDispatch)
    exceptions = []
    try:
      out = self._fastDispatch(*args, **kwargs)
    except HashMismatch as hashMismatch:
      exceptions.append(hashMismatch)
    else:
      return out
    try:
      out = self._castDispatch(*args, **kwargs)
    except CastMismatch as castMismatch:
      exceptions.append(castMismatch)
    else:
      if testFlag:
        self._setLatestDispatch(self._castDispatch)
      return out
    try:
      out = self._flexDispatch(*args, **kwargs)
    except FlexMismatch as flexMismatch:
      exceptions.append(flexMismatch)
    else:
      if testFlag:
        self._setLatestDispatch(self._flexDispatch)
      return out
    if testFlag:
      self._resetLatestDispatch()
    try:
      raise CascadeException(*exceptions)
    except CascadeException as cascadeException:
      raise DispatchException(self, *args) from cascadeException

  def __call__(self, *args: Any, **kwargs: Any) -> Any:
    """
    Tries fast, cast and flex dispatches in that order before raising
    'DispatchException'.
    """
    if self.getTestFlag():
      self._resetLatestDispatch()
    return self._dispatch(*args, **kwargs)

  def __str__(self, ) -> str:
    """Get the string representation of the function."""
    sigStr = [str(sig) for sig in self.getTypeSigs()]
    info = """%s object supporting type signatures: \n%s"""
    sigLines = '<br><tab>'.join(sigStr)
    return monoSpace(info % (self.__field_name__, sigLines))

  def __repr__(self, ) -> str:
    """Get the string representation of the function."""
    return object.__repr__(self)
