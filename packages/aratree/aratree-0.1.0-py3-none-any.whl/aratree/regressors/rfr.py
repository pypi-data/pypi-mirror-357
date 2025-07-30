import numpy as np
from collections import Counter
from .dtr import DecisionTreeRegressor

class RandomForestRegressor:
    def __init__(self, n_estimators=10, max_depth=None, min_samples_split=2, max_features='sqrt'):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.max_features = max_features
        self.trees = []
        self.feature_subsets = []

    def _get_feature_indices(self, n_features):
        if self.max_features == 'sqrt':
            return np.random.choice(n_features, int(np.sqrt(n_features)), replace=False)
        elif isinstance(self.max_features, int):
            return np.random.choice(n_features, self.max_features, replace=False)
        else:
            return np.arange(n_features)

    def fit(self, X, y):
        self.trees = []
        self.feature_subsets = []

        for _ in range(self.n_estimators):
            # Bootstrap sample
            indices = np.random.choice(len(X), len(X), replace=True)
            X_sample, y_sample = X[indices], y[indices]

            # Feature subset
            feature_idx = self._get_feature_indices(X.shape[1])
            self.feature_subsets.append(feature_idx)

            # Train tree
            tree = DecisionTreeRegressor(
                max_depth=self.max_depth,
                min_sample_split=self.min_samples_split
            )
            tree.fit(X_sample[:, feature_idx], y_sample)
            self.trees.append(tree)

    def predict(self, X):
        preds = np.array([
            tree.predict(X[:, feat_idx]) for tree, feat_idx in zip(self.trees, self.feature_subsets)
        ])
        return np.mean(preds, axis=0)

    def feature_importances_(self, feature_names):
        # Count how often features were used across trees
        importances = Counter()
        total_splits = 0

        for tree, feat_idx in zip(self.trees, self.feature_subsets):
            stack = [tree.tree]
            while stack:
                node = stack.pop()
                if isinstance(node, dict):
                    importances[feature_names[feat_idx[node['feature']]]] += 1
                    total_splits += 1
                    stack.extend([node['left'], node['right']])

        # Normalize
        return {feat: count / total_splits for feat, count in importances.items()}