# SPDX-License-Identifier: MIT
"""
individual.py - Definition and functionality of evolutionary individuals.

This module defines the `Indiv` class, representing a single individual
within a population used in evolutionary algorithms. Each individual
contains a parameter vector, fitness value, and potentially other
adaptive traits such as mutation rate or strength.

It supports initialization, parameter bounds, fitness assignment,
and cloning operations. The design enables use in both simple and
advanced strategies, including individual-level adaptation and
multi-objective optimization.

Typical use cases include:
- Representation of solution candidates in genetic and evolutionary strategies.
- Adaptive mutation schemes on a per-individual basis.
- Integration into population-level operations (selection, crossover, etc.).

Attributes:
    para (any): Parameter vector.
    fitness (float | None): Fitness value assigned after evaluation.
    mutation_rate (float | None): Optional per-individual mutation rate.
    mutation_strength (float | None): Optional per-individual mutation strength.

Classes:
    Indiv: Core data structure for evolutionary optimization.
"""

from typing import Any, Dict, Optional

from evolib.interfaces.enums import Origin


class Indiv:
    """
    Repräsentiert ein Individuum in einer evolutionären Optimierung.

    Attributes:
        para (Any): Parameter des Individuums (z. B. Liste, Array).
        fitness (float): Fitnesswert des Individuums.
        age (int): Aktuelles Alter des Individuums.
        max_age (Optional[int]): Maximales Alter des Individuums.
        origin (str): Herkunft des Individuums ('parent' oder 'child').
        parent_idx (Optional[int]): Index des Eltern-Individuums.
        mutation_strength (float): Stärke der Mutation.
        mutation_strength_bias (float): Bias für die Mutationsstärke.
        mutation_rate (float): Mutationsrate.
    """

    __slots__ = (
        "para",
        "fitness",
        "age",
        "max_age",
        "origin",
        "parent_idx",
        "mutation_strength",
        "mutation_strengths",
        "mutation_rate",
        "mutation_strength_bias",
        "crossover_rate",
        "tau",
        "extra_metrics",
    )

    extra_metrics: dict[str, float]

    def __init__(self, para: Any = None):
        """
        Initialisiert ein Individuum mit den angegebenen Parametern.

        Args:
            para (Any, optional): Parameter des Individuums. Standard: None.

        Raises:
            ValueError: Wenn max_age negativ oder null ist.
        """

        self.para = para
        self.fitness: float = float("inf")  # Optional[float] = None
        self.age = 0
        self.max_age = 0
        self.origin: Origin = Origin.PARENT
        self.parent_idx: Optional[int] = None

        self.mutation_strength: float | None = None
        self.mutation_strengths: list[float] | None = None
        self.mutation_strength_bias: float | None = None
        self.mutation_rate: float | None = None
        self.crossover_rate: float | None = None

        self.tau = 0.0

        self.extra_metrics = {}

    def __lt__(self, other: "Indiv") -> bool:
        return self.fitness < other.fitness

    def print_status(self) -> None:
        """Prints information about the individual."""
        mutation_rate = getattr(self, "mutation_rate", None)
        mutation_strength = getattr(self, "mutation_strength", None)
        mutation_strength_bias = getattr(self, "mutation_strength_bias", None)
        crossover_rate = getattr(self, "crossover_rate", None)

        print("Individuum:")
        print(f"  Fitness: {self.fitness}")
        print(f"  Age: {self.age}")
        print(f"  Max Age: {self.max_age}")
        print(f"  Origin: {self.origin}")
        print(f"  Parent Index: {self.parent_idx}")
        if mutation_strength is not None:
            print(f"  Mutation Strength: {mutation_strength:.4f}")
        if mutation_strength_bias is not None:
            print(f"  Mutation Strength Bias: {mutation_strength_bias:.4f}")
        if mutation_rate is not None:
            print(f"  Mutation Rate: {mutation_rate:.4f}")
        if crossover_rate is not None:
            print(f"  Crossover Rate: {crossover_rate:.4f}")

    def to_dict(self) -> Dict:
        return {
            "fitness": self.fitness,
            "age": self.age,
            "mutation_strength": self.mutation_strength,
            "mutation_strength_bias": self.mutation_strength_bias,
            "mutation_rate": self.mutation_rate,
        }

    def is_parent(self) -> bool:
        return self.origin == Origin.PARENT

    def is_child(self) -> bool:
        return self.origin == Origin.OFFSPRING
