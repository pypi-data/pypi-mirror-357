from sklearn.base import BaseEstimator, TransformerMixin
import numpy as np
import itertools

class InteractionFeatures(BaseEstimator, TransformerMixin):
    """
    Adds pairwise interaction features (x_i * x_j) for all features.
    """
    def fit(self, X, y=None):
        self.n_features_in_ = X.shape[1]
        return self
    def transform(self, X):
        X = np.asarray(X)
        n = X.shape[1]
        interactions = [X[:, i] * X[:, j] for i, j in itertools.combinations(range(n), 2)]
        if interactions:
            X_new = np.column_stack([X] + interactions)
        else:
            X_new = X
        return X_new

class PolynomialFeaturesWrapper(BaseEstimator, TransformerMixin):
    """
    Wrapper for sklearn's PolynomialFeatures with sensible defaults.
    """
    def __init__(self, degree=2, include_bias=False):
        from sklearn.preprocessing import PolynomialFeatures
        self.degree = degree
        self.include_bias = include_bias
        self._poly = PolynomialFeatures(degree=degree, include_bias=include_bias)
    def fit(self, X, y=None):
        self._poly.fit(X, y)
        return self
    def transform(self, X):
        return self._poly.transform(X)

class IdentityTransformer(BaseEstimator, TransformerMixin):
    """
    Pass-through transformer (does nothing).
    """
    def fit(self, X, y=None):
        return self
    def transform(self, X):
        return X 