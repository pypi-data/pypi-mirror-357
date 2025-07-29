import pytest
from atris import ensemble
from atris.anomaly_models import ZScoreAnomaly, IQRAnomaly
from sklearn.ensemble import IsolationForest
from sklearn.datasets import make_blobs
import numpy as np

@pytest.fixture(scope="module")
def anomaly_data():
    X, _ = make_blobs(n_samples=200, centers=1, cluster_std=1.0, random_state=42)
    # Add some outliers
    outliers = np.random.uniform(low=-10, high=10, size=(20, X.shape[1]))
    X = np.vstack([X, outliers])
    y = np.array([0]*200 + [1]*20)  # 0: normal, 1: anomaly
    return X, y

def test_zscore_iqr_ensemble(anomaly_data):
    X, y = anomaly_data
    model = ensemble.call(ZScoreAnomaly, IQRAnomaly)
    model.fit(X)
    preds = model.predict(X)
    # At least some anomalies should be detected
    assert preds.sum() > 0

def test_isolation_zscore_ensemble(anomaly_data):
    X, y = anomaly_data
    model = ensemble.call(IsolationForest, ZScoreAnomaly)
    model.fit(X)
    preds = model.predict(X)
    assert preds.sum() > 0 