# SPDX-License-Identifier: MIT
"""Common mathematical benchmark functions for optimization tasks."""

import numpy as np


def simple_quadratic(x: np.ndarray) -> np.ndarray:
    """
    Simple 1D benchmark: f(x) = x^2

    Global minimum: f(0) = 0

    Args:
        x (float or np.ndarray): Input value(s).

    Returns:
        float: Function value.
    """
    x = np.asarray(x, dtype=np.float64)
    return np.sum(x**2)


def rastrigin(x: np.ndarray, A: int = 10) -> np.ndarray:
    """
    Rastrigin-Funktion (n-dimensional).

    Globales Minimum: f(0, ..., 0) = 0
    Empfohlener Suchraum: x_i ∈ [-5.12, 5.12]

    Args:
        x (list or np.ndarray): Eingabevektor (beliebige Dimension).
        A (float): Konstante der Rastrigin-Funktion (Standard: 10).

    Returns:
        float: Funktionswert der Rastrigin-Funktion an der Stelle x.
    """
    x = np.asarray(x, dtype=np.float64)

    if x.ndim == 0:  # Skalar → Vektor mit 1 Element
        x = x.reshape(1)
    elif x.ndim > 1:
        raise ValueError("Input x must be 1D or scalar.")

    n = x.size
    return A * n + np.sum(x**2 - A * np.cos(2 * np.pi * x))


def sphere(x: np.ndarray) -> np.ndarray:
    """
    Sphere function (n-dimensional).

    Global minimum: f(0, ..., 0) = 0
    Recommended domain: x_i ∈ [-5.12, 5.12]

    Args:
        x (list or np.ndarray): Input vector.

    Returns:
        float: Function value at x.
    """
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 0:
        x = x.reshape(1)
    elif x.ndim > 1:
        raise ValueError("Input x must be 1D or scalar.")

    return np.sum(x**2)


def rosenbrock(x: np.ndarray) -> np.ndarray:
    """
    Rosenbrock function (n-dimensional).

    Global minimum: f(1, ..., 1) = 0
    Recommended domain: x_i ∈ [-5, 10]

    Args:
        x (list or np.ndarray): Input vector.

    Returns:
        float: Function value at x.
    """
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 0:
        x = x.reshape(1)
    elif x.ndim > 1:
        raise ValueError("Input x must be 1D or scalar.")
    if len(x) < 2:
        raise ValueError("Rosenbrock needs at least 2 dimensions")

    return np.sum(100 * (x[1:] - x[:-1] ** 2) ** 2 + (1 - x[:-1]) ** 2)


def ackley(x: np.ndarray) -> np.ndarray:
    """
    Ackley function (n-dimensional).

    Global minimum: f(0, ..., 0) = 0
    Recommended domain: x_i ∈ [-32.768, 32.768]

    Args:
        x (list or np.ndarray): Input vector.

    Returns:
        float: Function value at x.
    """
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 0:
        x = x.reshape(1)
    elif x.ndim > 1:
        raise ValueError("Input x must be 1D or scalar.")

    n = x.size
    sum_sq = np.sum(x**2)
    sum_cos = np.sum(np.cos(2 * np.pi * x))
    return -20 * np.exp(-0.2 * np.sqrt(sum_sq / n)) - np.exp(sum_cos / n) + 20 + np.e


def griewank(x: np.ndarray) -> np.ndarray:
    """
    Griewank function (n-dimensional).

    Global minimum: f(0, ..., 0) = 0
    Recommended domain: x_i ∈ [-600, 600]

    Args:
        x (list or np.ndarray): Input vector.

    Returns:
        float: Function value at x.
    """
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 0:
        x = x.reshape(1)
    elif x.ndim > 1:
        raise ValueError("Input x must be 1D or scalar.")

    sum_sq = np.sum(x**2) / 4000
    prod_cos = np.prod(np.cos(x / np.sqrt(np.arange(1, x.size + 1))))
    return sum_sq - prod_cos + 1


def schwefel(x: np.ndarray) -> np.ndarray:
    """
    Schwefel function (n-dimensional).

    Global minimum: f(420.9687, ..., 420.9687) = 0
    Recommended domain: x_i ∈ [-500, 500]

    Args:
        x (list or np.ndarray): Input vector.

    Returns:
        float: Function value at x.
    """
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 0:
        x = x.reshape(1)
    elif x.ndim > 1:
        raise ValueError("Input x must be 1D or scalar.")

    return 418.9829 * x.size - np.sum(x * np.sin(np.sqrt(np.abs(x))))
