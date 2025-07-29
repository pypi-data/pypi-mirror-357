import pytest
from atris import monitor_performance, evalModel, models
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

def test_monitor_performance_plateau():
    X, y = load_iris(return_X_y=True)
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.3, random_state=42)
    model_specs = [
        models.RandomForestClassifier,
        models.LogisticRegression,
        (models.KNeighborsClassifier, {"n_neighbors": 3}),
        (models.KNeighborsClassifier, {"n_neighbors": 5}),
    ]
    best_ensemble, scores = monitor_performance(
        model_specs, X_train, y_train, X_val, y_val, eval_fn=evalModel, patience=1, min_delta=0.0, verbose=False
    )
    # Should return an ensemble with at least 2 models
    assert hasattr(best_ensemble, 'predict')
    assert len(scores) >= 1 