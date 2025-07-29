# SPDX-FileCopyrightText: 2024 Daniel Biehl <daniel.biehl@imbus.de>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Callable, Optional, TypeVar

__all__ = ["predicate"]

F = TypeVar("F", bound=Callable[..., Any])


def predicate(message: Optional[str] = None, flags: Any = None) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        setattr(func, "__predicate__", True)
        setattr(func, "message", message)
        setattr(func, "flags", flags)
        return func

    return decorator
