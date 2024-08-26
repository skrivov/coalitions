import numpy as np
import matplotlib.pyplot as plt
from relations_matrix import RelationsMatrix
import os

def load_matrix_from_json(config_path):
    relations_matrix = RelationsMatrix(config_path)
    return relations_matrix.to_matrix(relations_matrix.relations.keys())

def measure_mse(matrix1, matrix2):
    matrix1 = np.array(matrix1)
    matrix2 = np.array(matrix2)
    return np.mean((matrix1 - matrix2) ** 2)

def measure_cosine_similarity(matrix1, matrix2):
    matrix1 = np.array(matrix1).flatten()
    matrix2 = np.array(matrix2).flatten()
    return np.dot(matrix1, matrix2) / (np.linalg.norm(matrix1) * np.linalg.norm(matrix2))

def measure_jaccard_similarity(matrix1, matrix2):
    matrix1 = np.array(matrix1).flatten()
    matrix2 = np.array(matrix2).flatten()
    intersection = np.sum(np.minimum(matrix1, matrix2))
    union = np.sum(np.maximum(matrix1, matrix2))
    return intersection / union

def measure_pearson_correlation(matrix1, matrix2):
    matrix1 = np.array(matrix1).flatten()
    matrix2 = np.array(matrix2).flatten()
    return np.corrcoef(matrix1, matrix2)[0, 1]

class Analytics:
    def __init__(self, start_path, end_path, measures, output_dir):
        self.start_matrix = load_matrix_from_json(start_path)
        self.end_matrix = load_matrix_from_json(end_path)
        self.measures = measures
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def compare_current_to_end(self, current_matrix):
        results = {}
        for measure_name, measure_func in self.measures.items():
            results[measure_name] = measure_func(current_matrix, self.end_matrix)
        return results

    def visualize_matrices(self, current_matrix, step):
        fig, axes = plt.subplots(1, 2, figsize=(12, 6))
        
        self.plot_matrix(current_matrix, axes[0], "Current Matrix at Step {}".format(step))
        self.plot_matrix(self.end_matrix, axes[1], "End Matrix")

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, f"matrix_comparison_step_{step}.png"))
        plt.close()

    def plot_matrix(self, matrix, ax, title):
        cmap = plt.cm.RdBu_r
        norm = plt.Normalize(vmin=-1, vmax=1)
        cax = ax.matshow(matrix, cmap=cmap, norm=norm)
        ax.set_title(title)
        plt.colorbar(cax, ax=ax)
