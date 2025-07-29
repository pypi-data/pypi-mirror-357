from typing import Any
from sklearn.metrics import accuracy_score, mean_squared_error, f1_score, roc_auc_score
import numpy as np


def evalModel(model: Any, X_test, y_test, task: str = 'classification'):
    y_pred = model.predict(X_test)
    if task == 'classification':
        try:
            score = accuracy_score(y_test, y_pred)
        except Exception:
            score = f1_score(y_test, y_pred, average='weighted')
    elif task == 'regression':
        # RMSE, compatible with all sklearn versions
        score = np.sqrt(mean_squared_error(y_test, y_pred))
    elif task == 'anomaly':
        # For anomaly detection, use ROC AUC if possible
        try:
            score = roc_auc_score(y_test, y_pred)
        except Exception:
            score = f1_score(y_test, y_pred, average='binary')
    else:
        raise ValueError(f"Unknown task type: {task}")
    return score 