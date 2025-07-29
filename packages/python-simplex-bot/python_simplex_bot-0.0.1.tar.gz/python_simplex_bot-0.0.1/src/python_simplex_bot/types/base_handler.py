from typing import Callable, Any
from .base_context import BaseContext
from .update import Update

BaseHandler = Callable[[Update, BaseContext], Any]

__all__ = ["BaseHandler"]