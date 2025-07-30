# SPDX-License-Identifier: MIT
"""
Provides mutation utilities for evolutionary strategies.

This module defines functions to apply mutations to individuals or entire offspring
populations, based on configurable mutation strategies (e.g., exponential, adaptive).
It delegates actual parameter mutation to user-defined mutation functions.

Functions:
- mutate_indiv: Mutates a single individual based on the population's strategy.
- mutate_offspring: Mutates all individuals in an offspring list.

Expected mutation functions must operate on the parameter level and implement
mutation probability checks internally.
"""

from typing import List

import numpy as np

from evolib.core.population import Indiv, Pop
from evolib.interfaces.enums import MutationStrategy
from evolib.interfaces.structs import MutationParams
from evolib.interfaces.types import (
    MutationFunction,
)
from evolib.utils.math_utils import scaled_mutation_factor


def mutate_indiv(
    pop: Pop,
    indiv: Indiv,
    mutation_function: MutationFunction,
    bounds: tuple[float, float] = (-1, 1),
) -> None:
    """
    Applies mutation to a single individual according to the population's mutation
    strategy.

    Args:
        pop (Pop): The population object holding global mutation parameters.
        indiv (Indiv): The individual to be mutated.
        mutation_function (Callable): The mutation function applied to each parameter.
        bounds (tuple): Lower and upper bounds for parameter values.
    """

    rate, strength = get_mutation_parameters(pop, indiv)

    min_strength = getattr(pop, "min_mutation_strength", strength)
    max_strength = getattr(pop, "max_mutation_strength", strength)
    min_rate = getattr(pop, "min_mutation_rate", rate)
    max_rate = getattr(pop, "max_mutation_rate", rate)

    mutation_function(
        indiv,
        MutationParams(
            strength,
            min_strength,
            max_strength,
            rate,
            min_rate,
            max_rate,
            bounds,
        ),
    )


def mutate_offspring(
    pop: Pop,
    offspring: List[Indiv],
    mutation_function: MutationFunction,
    bounds: tuple[float, float] = (-1, 1),
) -> None:
    """
    Applies mutation to all individuals in the offspring list.

    Args:
        pop (Pop): The population object containing mutation configuration.
        offspring (List[Indiv]): List of individuals to mutate.
        mutation_function (Callable): The mutation function applied to each parameter.
        bounds (tuple): Lower and upper bounds for parameter values.
    """

    # Update global mutation parameters (only if strategy requires it)
    update_mutation_parameters(pop)

    for indiv in offspring:
        mutate_indiv(pop, indiv, mutation_function, bounds)


def get_mutation_parameters(pop: Pop, indiv: Indiv) -> tuple[float, float]:
    strategy = pop.mutation_strategy

    if strategy in {
        MutationStrategy.CONSTANT,
        MutationStrategy.EXPONENTIAL_DECAY,
        MutationStrategy.ADAPTIVE_GLOBAL,
    }:
        return pop.mutation_rate, pop.mutation_strength
    if strategy == MutationStrategy.ADAPTIVE_INDIVIDUAL:
        return indiv.mutation_rate, indiv.mutation_strength

    raise ValueError(f"Unsupported mutation strategy: {strategy}")


def update_mutation_parameters(pop: Pop) -> None:
    if pop.mutation_strategy == MutationStrategy.EXPONENTIAL_DECAY:
        pop.mutation_rate = _exponential_mutation_rate(pop)
        pop.mutation_strength = _exponential_mutation_strength(pop)
    elif pop.mutation_strategy == MutationStrategy.ADAPTIVE_GLOBAL:
        pop.mutation_rate = _adaptive_mutation_rate(pop)
        pop.mutation_strength = _adaptive_mutation_strength(pop)


def _exponential_mutation_strength(pop: Pop) -> float:
    """
    Calculates exponentially decaying mutation strength over generations.

    Args:
        pop (Pop): The population object containing mutation parameters.

    Returns:
        float: The adjusted mutation strength.
    """
    k = (
        np.log(pop.max_mutation_strength / pop.min_mutation_strength)
        / pop.max_generations
    )
    return pop.max_mutation_strength * np.exp(-k * pop.generation_num)


def _exponential_mutation_rate(pop: Pop) -> float:
    """
    Calculates exponentially decaying mutation rate over generations.

    Args:
        pop (Pop): The population object containing mutation parameters.

    Returns:
        float: The adjusted mutation rate.
    """
    k = np.log(pop.max_mutation_rate / pop.min_mutation_rate) / pop.max_generations
    return pop.max_mutation_rate * np.exp(-k * pop.generation_num)


def _adaptive_mutation_rate(pop: Pop, alpha: float = 0.1) -> float:
    """
    Adapts the mutation rate based on smoothed population diversity (EMA).

    Args:
        pop (Pop): The population object with diversity, thresholds and
        mutation settings.
        alpha (float): Smoothing factor for EMA (0 < alpha <= 1).

    Returns:
        float: Adapted mutation rate.
    """
    # Initialisierung bei erster Nutzung
    if not hasattr(pop, "diversity_ema") or pop.diversity_ema is None:
        pop.diversity_ema = pop.diversity  # keine Glättung in der ersten Generation

    # Update EMA für Diversity
    pop.diversity_ema = (1 - alpha) * pop.diversity_ema + alpha * pop.diversity

    # Mutationsrate adaptieren
    rate = pop.mutation_rate
    increased = rate * pop.increase_factor
    decreased = rate * pop.decrease_factor

    if pop.diversity_ema < pop.min_diversity_threshold:
        new_rate = min(pop.max_mutation_rate, increased)
    elif pop.diversity_ema > pop.max_diversity_threshold:
        new_rate = max(pop.min_mutation_rate, decreased)
    else:
        new_rate = rate

    return new_rate


def _adaptive_mutation_strength(pop: Pop, alpha: float = 0.1) -> float:
    """
    Adapts the mutation strength based on smoothed population diversity (EMA).

    Args:
        pop (Pop): The population object with diversity, thresholds and
        mutation settings.
        alpha (float): Smoothing factor for EMA (0 < alpha <= 1).

    Returns:
        float: Adapted mutation strength.
    """
    # Initialisierung bei erster Nutzung
    if not hasattr(pop, "diversity_ema") or pop.diversity_ema is None:
        pop.diversity_ema = pop.diversity  # keine Glättung in der ersten Generation

    # Update EMA für Diversity
    pop.diversity_ema = (1 - alpha) * pop.diversity_ema + alpha * pop.diversity

    # Mutationsstrength adaptieren
    strength = pop.mutation_strength
    increased = strength * pop.increase_factor
    decreased = strength * pop.decrease_factor

    if pop.diversity_ema < pop.min_diversity_threshold:
        new_strength = min(pop.max_mutation_strength, increased)
    elif pop.diversity_ema > pop.max_diversity_threshold:
        new_strength = max(pop.min_mutation_strength, decreased)
    else:
        new_strength = strength

    return new_strength


def mutate_gauss(
    x: np.ndarray,
    mutation_strength: float = 0.05,
    bounds: tuple[float, float] = (-1.0, 1.0),
) -> np.ndarray:
    """
    Mutates a real-valued array by adding Gaussian noise, with clipping to specified
    bounds.

    Args:
        x (np.ndarray): Input array to mutate (e.g., weights of a neural network).
        mutation_strength (float): Standard deviation of the Gaussian noise
        (default: 0.05).
        bounds (tuple): Tuple of (min, max) values to clip the mutated values
        (default: (-1.0, 1.0)).

    Returns:
        np.ndarray: Mutated array with the same shape as x, clipped to bounds.

    Raises:
        ValueError: If mutation_strength is non-positive, bounds are invalid,
        or x is not a NumPy array.
    """
    # Validate inputs
    if not isinstance(x, np.ndarray):
        x = np.asarray(x)
        # raise ValueError("Input x must be a NumPy array")
    if mutation_strength <= 0:
        raise ValueError("mutation_strength must be positive")
    if not (isinstance(bounds, tuple) and len(bounds) == 2 and bounds[0] <= bounds[1]):
        raise ValueError("bounds must be a tuple (min, max) with min <= max")

    # Generate Gaussian noise with the same shape as x
    noise = np.random.normal(0, mutation_strength, size=x.shape)

    # Add noise and clip to bounds
    mutated = x + noise
    mutated = np.clip(mutated, bounds[0], bounds[1])

    return mutated


def adapt_mutation_strength(indiv: Indiv, params: MutationParams) -> float:
    """
    Applies log-normal scaling and clipping to an individual's mutation_strength.

    Args:
        indiv (Indiv): The individual to update.
        params (MutationParams): Contains tau, min/max strength, etc.

    Returns:
        float: The updated mutation strength.
    """
    if indiv.tau > 0:
        indiv.mutation_strength *= scaled_mutation_factor(indiv.tau)
        indiv.mutation_strength = float(
            np.clip(indiv.mutation_strength, params.min_strength, params.max_strength)
        )
    return indiv.mutation_strength


def adapt_mutation_rate(indiv: Indiv, params: MutationParams) -> float:
    """
    Applies log-normal scaling and clipping to an individual's mutation_rate.

    Args:
        indiv (Indiv): The individual to update.
        params (MutationParams): Contains tau, min/max rate, etc.

    Returns:
        float: The updated mutation rate.
    """
    if indiv.tau > 0:
        indiv.mutation_rate *= scaled_mutation_factor(indiv.tau)
        indiv.mutation_rate = float(
            np.clip(indiv.mutation_rate, params.min_rate, params.max_rate)
        )
    return indiv.mutation_rate
