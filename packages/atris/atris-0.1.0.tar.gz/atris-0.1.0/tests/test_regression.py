import pytest
from atris import ensemble, evalModel
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split

@pytest.fixture(scope="module")
def housing_data():
    X, y = fetch_california_housing(return_X_y=True)
    return train_test_split(X, y, test_size=0.2, random_state=42)

def test_rf_linreg_ensemble(housing_data):
    X_train, X_test, y_train, y_test = housing_data
    model = ensemble.call(RandomForestRegressor, LinearRegression)
    model.fit(X_train, y_train)
    score = evalModel(model, X_test, y_test, task='regression')
    assert score < 1.0  # RMSE should be reasonable

def test_rf_rf_ensemble(housing_data):
    X_train, X_test, y_train, y_test = housing_data
    model = ensemble.call(RandomForestRegressor, RandomForestRegressor)
    model.fit(X_train, y_train)
    score = evalModel(model, X_test, y_test, task='regression')
    assert score < 1.0 