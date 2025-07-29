from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
import numpy as np
import pandas as pd

def processData(X, y=None, scale_numeric=True, encode_categorical=True, return_pipeline=False):
    """
    Consistently preprocess data for use in ensembles.
    Args:
        X: Input features (pd.DataFrame or np.ndarray)
        y: Target (optional)
        scale_numeric: Whether to scale numeric features
        encode_categorical: Whether to encode categorical features
        return_pipeline: Whether to return the fitted pipeline
    Returns:
        X_processed, y (and pipeline if return_pipeline=True)
    """
    if isinstance(X, np.ndarray):
        X = pd.DataFrame(X)
    numeric_features = X.select_dtypes(include=[np.number]).columns.tolist()
    categorical_features = X.select_dtypes(include=["object", "category"]).columns.tolist()
    transformers = []
    if scale_numeric and numeric_features:
        transformers.append(("num", StandardScaler(), numeric_features))
    if encode_categorical and categorical_features:
        transformers.append(("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features))
    if transformers:
        preprocessor = ColumnTransformer(transformers)
        X_processed = preprocessor.fit_transform(X)
    else:
        X_processed = X.values if hasattr(X, 'values') else X
    if return_pipeline and transformers:
        pipe = Pipeline([("preprocessor", preprocessor)])
        return X_processed, y, pipe
    return X_processed, y 