# SPDX-FileCopyrightText: 2024 Daniel Biehl <daniel.biehl@imbus.de>
#
# SPDX-License-Identifier: Apache-2.0

from abc import abstractmethod

from ...core import StrategyBase
from ..orientation import Orientation

__all__ = ["HasOrientation", "Orientation"]


class HasOrientation(StrategyBase):
    strategy_name = "org.platynui.strategies.HasOrientation"

    @property
    @abstractmethod
    def orientation(self) -> Orientation:
        pass
