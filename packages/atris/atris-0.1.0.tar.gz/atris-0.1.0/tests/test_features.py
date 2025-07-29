import pytest
import numpy as np
from atris.features import InteractionFeatures, PolynomialFeaturesWrapper, IdentityTransformer

def test_interaction_features():
    X = np.array([[1, 2, 3], [4, 5, 6]])
    transformer = InteractionFeatures()
    X_new = transformer.fit_transform(X)
    # Should add 3 interaction features to 3 original features
    assert X_new.shape[1] == 6

def test_polynomial_features_wrapper():
    X = np.array([[1, 2], [3, 4]])
    transformer = PolynomialFeaturesWrapper(degree=2, include_bias=False)
    X_new = transformer.fit_transform(X)
    # For 2 features, degree 2, should add interaction and squared terms
    assert X_new.shape[1] == 5

def test_identity_transformer():
    X = np.array([[1, 2], [3, 4]])
    transformer = IdentityTransformer()
    X_new = transformer.fit_transform(X)
    assert np.allclose(X, X_new) 