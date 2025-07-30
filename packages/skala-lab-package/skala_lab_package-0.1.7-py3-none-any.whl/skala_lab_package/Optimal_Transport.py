import os
import numpy as np
import pandas as pd
import ot
import matplotlib.pyplot as plt
from sklearn.preprocessing import Normalizer
from sklearn.decomposition import PCA
import json

class Optimal_Transport:
    def __init__(self, path):
        self.path = path
        self.root = ""
        self.conditions = []
        self.decay_features = None
        self.nadh_decay = None
        self.fad_decay = None
        self.decay_multi_channel_features = None
        self.pca = None
        self.normalizer = None
        self.results = {}
    
    def load_decay_data(self):
        cytoplasm_decay_matrices = {}

        with open(self.path, "r") as f:
            config = json.load(f)
            self.root = config.get("root")
            self.conditions = config.get("conditions")

        for condition in self.conditions:
            condition_path = os.path.join(self.root, condition)
            if not os.path.isdir(condition_path):
                continue

            files = os.listdir(condition_path)
            for f in files:
                path = os.path.join(condition_path, f)
                if not os.path.isdir(path): 
                    continue

                # Skip specific dish-control combinations
                if path[-2] == "1" and "Dish1" in path and "Control" in path:
                    continue

                decay_file = [
                    name for name in os.listdir(path)
                    if '_decay_matrix.npy' in name and 'cytoplasm' not in name
                ]
                if not decay_file:
                    continue

                decay_path = os.path.join(path, decay_file[0])
                cytoplasm_decay_matrices[decay_path] = np.load(decay_path)

        decay_features = []
        for k, v in cytoplasm_decay_matrices.items():
            df = pd.DataFrame(v)
            info = os.path.basename(k).split("_")
            df.insert(0, 'fullName', k)
            df.insert(1, 'treatment', os.path.basename(os.path.dirname(os.path.dirname(k))))
            df.insert(2, 'dish', info[2])
            df.insert(3, 'site', info[3][0])
            df.insert(4, 'Channel', info[3][-1])
            df.insert(5, 'cell_id', np.arange(v.shape[0]))
            decay_features.append(df)

        self.decay_features = pd.concat(decay_features).reset_index()
        self.nadh_decay = self.decay_features[self.decay_features.Channel == "n"].copy()
        self.fad_decay = self.decay_features[self.decay_features.Channel == "f"].copy()

    def compute_global_pca(self, n_components=10):
        X_all_raw = self.nadh_decay.iloc[:, 7:]
        X_all = X_all_raw.astype(float).values
        self.normalizer = Normalizer(norm='l1')
        X_all_norm = self.normalizer.fit_transform(X_all)
        self.pca = PCA(n_components=n_components)
        self.pca.fit(X_all_norm)
        nadh_cols = X_all_raw.columns
        self.nadh_decay[nadh_cols] = X_all

    
    def get_ot_distance(self, treat_control, treat_experiment):
        """
        Returns a dictionary like:
        {
          "dist": float,
          "M": between-group distance matrix,
          "M1": within-group distance matrix for control,
          "M2": within-group distance matrix for experiment
        }
        or None if no data.
        """
        df_group1 = self.nadh_decay[self.nadh_decay['treatment'] == treat_control]
        df_group2 = self.nadh_decay[self.nadh_decay['treatment'] == treat_experiment]
        
        if df_group1.empty or df_group2.empty:
            print(f"Warning: No cells found for {treat_control} or {treat_experiment}. Skipping.")
            return None
        
        # Normalize, then PCA transform
        X_group1 = self.normalizer.transform(df_group1.iloc[:, 7:].values)
        X_group2 = self.normalizer.transform(df_group2.iloc[:, 7:].values)
        X_group1_pca = self.pca.transform(X_group1)
        X_group2_pca = self.pca.transform(X_group2)
        
        # Compute pairwise distances
        M = ot.dist(X_group1_pca, X_group2_pca, metric='euclidean')  # between-group
        M /= M.max()  # scale to [0,1]
        
        M1 = ot.dist(X_group1_pca, X_group1_pca, metric='euclidean') # within-group1
        M1 /= M1.max()
        
        M2 = ot.dist(X_group2_pca, X_group2_pca, metric='euclidean') # within-group2
        M2 /= M2.max()
        
        # Optimal Transport
        G_matrix = ot.emd(
            np.ones(X_group1_pca.shape[0]) / X_group1_pca.shape[0],
            np.ones(X_group2_pca.shape[0]) / X_group2_pca.shape[0],
            M,
            numItermax=1e7
        )
        dist = np.sum(G_matrix * M)
        
        result = {
            "dist": dist,
            "M": M,
            "M1": M1,
            "M2": M2
        }
        self.results[(treat_control, treat_experiment)] = result
        return result

    def compute_cohens_d(self, M, M1):
        
        """
        M: between-group distance matrix, shape (n1, n2)
        M1: within-group distance matrix, shape (n1, n1)
        Returns: float (Cohen's d)
        """
        
        vals_M = M.flatten()
        vals_M1 = M1[np.triu_indices(M1.shape[0], k=1)]
        
        mu_M, sigma_M = np.mean(vals_M), np.std(vals_M, ddof=1)
        mu_M1, sigma_M1 = np.mean(vals_M1), np.std(vals_M1, ddof=1)

        N_M, N_M1 = len(vals_M), len(vals_M1)
        
        s_pooled = np.sqrt(
            ((N_M - 1) * sigma_M**2 + (N_M1 - 1) * sigma_M1**2) / (N_M + N_M1 - 2)
        )
        cohens_d = (mu_M - mu_M1) / s_pooled
        return cohens_d

    def plot_cohens_d(self, pairs):
        """
        For each (control, treatment) in pairs, compute M, M1,
        then compute Cohen's d and store in a DataFrame. Plot the results.
        """
        cohen_d_results = []


        for (control, treatment) in pairs:
            print(f"\nProcessing: {control} vs {treatment}")
            result = self.get_ot_distance(control, treatment)
            if result is None:
                print(f"Skipping {control} vs {treatment} due to missing data.")
                continue
            
            M, M1 = result['M'], result['M1']
   
            c_d = self.compute_cohens_d(M, M1)
            print(f"Cohen's d: {c_d:.4f}")
            cohen_d_results.append((control, treatment, c_d))

        df_cohen_d = pd.DataFrame(cohen_d_results, columns=["Control", "Treatment", "Cohen's d"])
        print("\nCohen's d Results:")
        print(df_cohen_d)

        plt.figure(figsize=(10, 6))
        plt.bar(df_cohen_d["Treatment"], df_cohen_d["Cohen's d"], alpha=0.6, label="Cohen's d")

        plt.axhline(0.2, color='green', linestyle='dashed', label="Small (0.2)")
        plt.axhline(0.5, color='blue', linestyle='dashed', label="Medium (0.5)")
        plt.axhline(0.8, color='red', linestyle='dashed', label="Large (0.8)")
        
        plt.xticks(rotation=45, ha="right")
        plt.ylabel("Effect Size (Cohen's d)")
        plt.title("Cohen's d for M (between-group) vs M1 (within-group)")
        plt.legend()
        plt.tight_layout()
        plt.show()

    def plot_ot_distances(self, pairs):
        distances = []
        labels = []
        
        for (control_name, treat_name) in pairs:
            result = self.get_ot_distance(control_name, treat_name)
            if result is not None:
                distances.append(result["dist"])
                labels.append(f"{control_name}\nvs\n{treat_name}")
                print(f"OT distance: {control_name} vs {treat_name} = {result['dist']:.4f}")
        
        plt.figure(figsize=(10, 6))
        plt.bar(labels, distances, color='skyblue')
        plt.ylabel("OT Distance")
        plt.title("Pairwise OT Distances (Control vs Treatment) with L1 Normalization + PCA")
        plt.xticks(rotation=30, ha='right')
        plt.tight_layout()
        plt.show()
    
    def compare_distance_histograms_fair(self, M1, M):
        vals_M1 = M1[np.triu_indices(M1.shape[0], k=1)]
        vals_M = M.flatten()
        
        min_samples = min(len(vals_M1), len(vals_M))
        vals_M1_sampled = np.random.choice(vals_M1, size=min_samples, replace=False)
        vals_M_sampled = np.random.choice(vals_M, size=min_samples, replace=False)
        
        plt.figure(figsize=(8, 6))
        plt.hist(vals_M1_sampled, bins=50, alpha=0.5, label="M1 (within-group)", density=True)
        plt.hist(vals_M_sampled, bins=50, alpha=0.5, label="M (between-group)", density=True)
        plt.xlabel("Pairwise Distance")
        plt.ylabel("Density")
        plt.title("Comparison of Distance Distributions (Matched Samples)")
        plt.legend()
        plt.show()