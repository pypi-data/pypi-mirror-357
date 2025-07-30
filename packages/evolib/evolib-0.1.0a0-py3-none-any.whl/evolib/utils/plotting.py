# SPDX-License-Identifier: MIT
"""
Plotting utilities for visualizing evolutionary progress.

This module provides functions for visualizing:
- Fitness statistics (best, mean, median, std)
- Diversity over time
- Mutation rate and strength trends
- Fitness comparison
"""

from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd


def plot_fitness(
    history: pd.DataFrame,
    title: str = "Fitness over Generations",
    show: bool = True,
    log: bool = False,
    save_path: str | None = None,
) -> None:
    """
    Plots best, mean, and median fitness with standard deviation shading.

    Args:
        history (pd.DataFrame): The logged history DataFrame.
        title (str): Title of the plot.
    """
    plt.figure(figsize=(10, 6))

    if log is True:
        plt.yscale("log")

    plt.plot(
        history["generation"], history["best_fitness"], label="Best", color="green"
    )
    plt.plot(history["generation"], history["mean_fitness"], label="Mean", color="blue")
    plt.plot(
        history["generation"], history["median_fitness"], label="Median", color="orange"
    )

    if "std_fitness" in history.columns:
        lower = history["mean_fitness"] - history["std_fitness"]
        upper = history["mean_fitness"] + history["std_fitness"]
        plt.fill_between(
            history["generation"],
            lower,
            upper,
            color="blue",
            alpha=0.2,
            label="Std Dev",
        )

    plt.xlabel("Generation")
    plt.ylabel("Fitness")
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    if save_path is not None:
        plt.savefig(save_path, dpi=300)
        print(f"Plot saved to '{save_path}'")

    if show:
        plt.show()
    else:
        plt.close()


def plot_diversity(
    history: pd.DataFrame,
    show: bool = True,
    log: bool = False,
    save_path: str | None = None,
) -> None:
    """
    Plots the diversity of the population over generations.

    Args:
        history (pd.DataFrame): The logged history DataFrame.
    """
    if "diversity" not in history.columns:
        print("No 'diversity' column found in history.")
        return

    plt.figure(figsize=(10, 4))

    if log is True:
        plt.yscale("log")

    plt.plot(
        history["generation"], history["diversity"], color="purple", label="Diversity"
    )
    plt.xlabel("Generation")
    plt.ylabel("Diversity")
    plt.title("Population Diversity")
    plt.grid(True)
    plt.tight_layout()

    if save_path is not None:
        plt.savefig(save_path, dpi=300)
        print(f"Plot saved to '{save_path}'")

    if show:
        plt.show()
    else:
        plt.close()


def plot_mutation_trends(
    history: pd.DataFrame,
    show: bool = True,
    log: bool = False,
    save_path: str | None = None,
) -> None:
    """
    Plots mutation rate and strength trends over time, if present.

    Args:
        history (pd.DataFrame): The logged history DataFrame.
    """
    plt.figure(figsize=(10, 4))

    if log is True:
        plt.yscale("log")

    has_rate = "mutation_rate_mean" in history.columns
    has_strength = "mutation_strength_mean" in history.columns

    if has_rate:
        plt.plot(
            history["generation"],
            history["mutation_rate_mean"],
            label="Mutation Rate",
            color="red",
        )
    if has_strength:
        plt.plot(
            history["generation"],
            history["mutation_strength_mean"],
            label="Mutation Strength",
            color="brown",
        )

    if not (has_rate or has_strength):
        print("No mutation-related columns in history.")
        return

    plt.xlabel("Generation")
    plt.ylabel("Value")
    plt.title("Mutation Parameter Trends")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    if save_path is not None:
        plt.savefig(save_path, dpi=300)
        print(f"Plot saved to '{save_path}'")

    if show:
        plt.show()
    else:
        plt.close()


def plot_fitness_comparison(
    histories: list[pd.DataFrame],
    *,
    labels: Optional[list[str]] = None,
    metric: str = "best_fitness",
    title: str = "Fitness Comparison over Generations",
    show: bool = True,
    log: bool = False,
    save_path: str | None = None,
) -> None:
    """
    Plots a fitness metric from multiple runs for comparison.

    Args:
        histories (list[pd.DataFrame]): List of history dataframes from different runs.
        labels (list[str]): Optional list of labels for each run.
        metric (str): Which metric to compare (e.g., 'best_fitness', 'mean_fitness').
        title (str): Title of the plot.
    """
    if labels is None:
        labels = [f"Run {i+1}" for i in range(len(histories))]

    plt.figure(figsize=(10, 6))

    if log is True:
        plt.yscale("log")

    for hist, label in zip(histories, labels):
        if metric not in hist.columns:
            print(f"Metric '{metric}' not in history for {label}. Skipping.")
            continue
        plt.plot(hist["generation"], hist[metric], label=label)

    plt.xlabel("Generation")
    plt.ylabel(metric.replace("_", " ").capitalize())
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    if save_path is not None:
        plt.savefig(save_path, dpi=300)
        print(f"Plot saved to '{save_path}'")

    if show:
        plt.show()
    else:
        plt.close()


def save_current_plot(filename: str, dpi: int = 300) -> None:
    """
    Saves the current matplotlib plot to a file.

    Args:
        filename (str): Path to save the image (e.g., 'plot.png' or 'results/plot.pdf').
        dpi (int): Image resolution.
    """
    plt.savefig(filename, dpi=dpi)
    print(f"Plot saved to '{filename}'")
