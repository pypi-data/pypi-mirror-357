import pytest
from atris import ensemble, evalModel
from atris.classification_models import RandomForestClassifier, LogisticRegression, KNeighborsClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

@pytest.fixture(scope="module")
def iris_data():
    X, y = load_iris(return_X_y=True)
    return train_test_split(X, y, test_size=0.2, random_state=42)

def test_rf_logreg_ensemble(iris_data):
    X_train, X_test, y_train, y_test = iris_data
    model = ensemble.call(RandomForestClassifier, LogisticRegression)
    model.fit(X_train, y_train)
    score = evalModel(model, X_test, y_test, task='classification')
    assert score > 0.8

def test_rf_knn_ensemble(iris_data):
    X_train, X_test, y_train, y_test = iris_data
    model = ensemble.call(RandomForestClassifier, KNeighborsClassifier)
    model.fit(X_train, y_train)
    score = evalModel(model, X_test, y_test, task='classification')
    assert score > 0.8 