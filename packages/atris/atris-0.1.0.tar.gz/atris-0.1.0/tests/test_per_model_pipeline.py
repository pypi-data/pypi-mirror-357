import pytest
from atris import ensemble, models
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.decomposition import PCA
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

def test_per_model_pipeline():
    X, y = load_iris(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    pipe1 = make_pipeline(StandardScaler(), PolynomialFeatures(2))
    pipe2 = make_pipeline(PCA(n_components=3))
    model = ensemble.call(
        (pipe1, models.RandomForestClassifier),
        (pipe2, (models.LogisticRegression, {"max_iter": 200}))
    )
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    assert len(preds) == len(y_test) 