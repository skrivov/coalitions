"""
analytics.py

Provides methods for comparing relationship matrices and visualizing them over simulation steps.
"""

from __future__ import annotations
import os
from typing import Callable, Any
import numpy as np
import matplotlib.pyplot as plt
from relations_matrix import RelationsMatrix


def load_matrix_from_json(config_path: str) -> list[list[int]]:
    """
    Loads a relations matrix from a JSON file.

    Args:
        config_path (str): Path to the relations JSON file.

    Returns:
        list[list[int]]: The relations matrix loaded from the file.
    """
    relations_matrix = RelationsMatrix(config_path)
    return relations_matrix.to_matrix(list(relations_matrix.relations.keys()))


def measure_mse(matrix1: list[list[float]], matrix2: list[list[float]]) -> float:
    """
    Measures the Mean Squared Error (MSE) between two matrices.

    Args:
        matrix1 (list[list[float]]): The first matrix.
        matrix2 (list[list[float]]): The second matrix.

    Returns:
        float: The MSE between the two matrices.
    """
    arr1 = np.array(matrix1)
    arr2 = np.array(matrix2)
    return float(np.mean((arr1 - arr2) ** 2))


def measure_cosine_similarity(matrix1: list[list[float]], matrix2: list[list[float]]) -> float:
    """
    Measures the cosine similarity between two matrices by flattening them into vectors.

    Args:
        matrix1 (list[list[float]]): The first matrix.
        matrix2 (list[list[float]]): The second matrix.

    Returns:
        float: The cosine similarity (ranging from -1 to 1).
    """
    arr1 = np.array(matrix1).flatten()
    arr2 = np.array(matrix2).flatten()
    denom = float(np.linalg.norm(arr1) * np.linalg.norm(arr2))
    if denom == 0.0:
        return 0.0
    return float(np.dot(arr1, arr2) / denom)


def measure_jaccard_similarity(matrix1: list[list[int]], matrix2: list[list[int]]) -> float:
    """
    Measures the Jaccard similarity between two integer matrices.

    Args:
        matrix1 (list[list[int]]): The first matrix.
        matrix2 (list[list[int]]): The second matrix.

    Returns:
        float: The Jaccard similarity (ranging from 0 to 1).
    """
    arr1 = np.array(matrix1).flatten()
    arr2 = np.array(matrix2).flatten()
    intersection = np.sum(np.minimum(arr1, arr2))
    union = np.sum(np.maximum(arr1, arr2))
    if union == 0:
        return 0.0
    return float(intersection / union)


def measure_pearson_correlation(matrix1: list[list[float]], matrix2: list[list[float]]) -> float:
    """
    Measures the Pearson correlation coefficient between two matrices by flattening them.

    Args:
        matrix1 (list[list[float]]): The first matrix.
        matrix2 (list[list[float]]): The second matrix.

    Returns:
        float: The Pearson correlation coefficient (ranging from -1 to 1).
    """
    arr1 = np.array(matrix1).flatten()
    arr2 = np.array(matrix2).flatten()
    if arr1.size < 2 or arr2.size < 2:
        return 0.0
    return float(np.corrcoef(arr1, arr2)[0, 1])


class Analytics:
    """
    Encapsulates analytics for measuring and visualizing how close the current relations matrix is to the end-state matrix.
    """

    def __init__(
        self,
        start_path: str,
        end_path: str,
        measures: dict[str, Callable[[list[list[float]], list[list[float]]], float]],
        output_dir: str
    ) -> None:
        """
        Args:
            start_path (str): Path to the initial relations JSON file.
            end_path (str): Path to the final relations JSON file for comparison.
            measures (dict[str, Callable[[list[list[float]], list[list[float]]], float]]): A dict of measure_name -> measure_function.
            output_dir (str): Directory where output files (e.g., images) should be saved.
        """
        self.start_matrix = load_matrix_from_json(start_path)
        self.end_matrix = load_matrix_from_json(end_path)
        self.measures = measures
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def compare_current_to_end(self, current_matrix: list[list[int]]) -> dict[str, float]:
        """
        Compares a given matrix to the end-state matrix using the provided measures.

        Args:
            current_matrix (list[list[int]]): The current matrix to compare.

        Returns:
            dict[str, float]: A dictionary of measure_name -> computed_value.
        """
        results: dict[str, float] = {}
        for measure_name, measure_func in self.measures.items():
            results[measure_name] = measure_func(current_matrix, self.end_matrix)
        return results

    def visualize_matrices(self, current_matrix: list[list[int]], step: int) -> None:
        """
        Saves a side-by-side comparison plot of the current matrix vs. the end-state matrix.

        Args:
            current_matrix (list[list[int]]): The current relations matrix to visualize.
            step (int): The simulation step number.
        """
        fig, axes = plt.subplots(1, 2, figsize=(12, 6))

        self.plot_matrix(current_matrix, axes[0], f"Current Matrix at Step {step}")
        self.plot_matrix(self.end_matrix, axes[1], "End Matrix")

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, f"matrix_comparison_step_{step}.png"))
        plt.close()

    def plot_matrix(self, matrix: list[list[int]], ax: Any, title: str) -> None:
        """
        Plots a matrix using a color map, showing negative vs. positive relations.

        Args:
            matrix (list[list[int]]): The relations matrix to plot.
            ax (Any): The axis object to draw the plot on.
            title (str): The title for the plot.
        """
        cmap = plt.cm.RdBu_r
        norm = plt.Normalize(vmin=-1, vmax=1)
        cax = ax.matshow(matrix, cmap=cmap, norm=norm)
        ax.set_title(title)
        plt.colorbar(cax, ax=ax)
