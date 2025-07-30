import numpy as np



class DecisionTreeRegressor:
    """
    A simple Decision Tree Regressor class that can be
    """
    def __init__(self, max_depth=None, min_sample_split=2):
        self.max_depath = max_depth
        self.min_sample_split = min_sample_split
        self.tree = None

    def fit(self, X, y):
        self.tree = self._build_tree(X, y)

    def predict(self, X):
        result = np.array([self._predict_sample(x, self.tree) for x in X])
        return result
    
    def _build_tree(self, X, y, depth=0):
        num_samples, num_features = X.shape
        if (self.max_depth is not None and depth >= self.max_depth) or num_samples < self.min_sample_split:
            return np.mean(y)
        
        best_feat, best_thresh = self._best_split(X, y)
        if best_feat is None:
            return np.mean(y)
        
        left_mask = X[:, best_feat] <= best_thresh
        right_mask = X[:, best_feat] > best_thresh

        left = self._build_tree(X[left_mask], y[left_mask], depth + 1)
        right = self._build_tree(X[right_mask], y[right_mask], depth + 1)

        return {'feature': best_feat, 'threshold': best_thresh, 'left': left, 'right': right}    

    def _best_split(self, X, y):
        best_mse = float('inf')
        best_feat, best_thresh = None, None

        for feat in range(X.shape[1]):
            thresholds = np.unique(X[:, feat])
            for t in thresholds:
                left_mask = X[:, feat] <= t
                right_mask = X[:, feat] > t

                if len(y[left_mask]) == 0 or len(y[right_mask]) == 0:
                    continue

                mse = self._calculate_mse(y[left_mask], y[right_mask])
                if mse < best_mse:
                    best_mse = mse
                    best_feat = feat
                    best_thresh = t

        return best_feat, best_thresh      

    def _calculate_mse(self, left_y, right_y):
        left_mse = np.var(left_y) * len(left_y)
        right_mse = np.var(right_y) * len(right_y)
        return (left_mse + right_mse) / (len(left_y) + len(right_y))
    
    def _predict_sample(self, x, node):
        if not isinstance(node, dict):
            return node
        if x[node['feature']] <= node['threshold']:
            return self._predict_sample(x, node['left'])
        else:
            return self._predict_sample(x, node['right'])      