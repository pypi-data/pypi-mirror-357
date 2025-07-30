# SPDX-License-Identifier: MIT

import copy
from typing import Any


def copy_indiv(individual: Any) -> Any:
    """
    Erstellt eine tiefe Kopie eines Individuums.

    Args:
        individual: Zu kopierendes Individuum.

    Returns:
        Kopiertes Individuum.
    """
    # Optimierte Kopie, falls Individual eine copy-Methode hat
    if hasattr(individual, "copy"):
        return individual.copy()
    return copy.deepcopy(individual)
