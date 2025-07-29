from typing import List, Any, Callable, Tuple, Dict, Union
import numpy as np
import warnings
from concurrent.futures import ThreadPoolExecutor
from sklearn.base import BaseEstimator, TransformerMixin

class Ensemble:
    def __init__(self, models: List[Union[Any, Tuple[Any, Dict], Tuple[Any, Any], Tuple[Any, Tuple[Any, Dict]]]] ):
        if not (2 <= len(models) <= 10):
            raise ValueError("Ensemble must have between 2 and 10 models.")
        self.model_specs = models
        self.models = []  # Will be instantiated in fit
        self.pipelines = []  # Store per-model pipelines
        self._is_fitted = False

    def fit(self, X, y=None, n_jobs: int = 1, sample_fraction: float = 1.0, fast_mode: bool = False):
        """
        Fit all models in the ensemble.
        Args:
            X: Features
            y: Labels
            n_jobs: Number of parallel jobs (default 1)
            sample_fraction: Fraction of data to use for each model (default 1.0)
            fast_mode: If True, use lighter/faster hyperparameters if possible
        """
        def fit_model(spec):
            # Subsample data if needed
            if sample_fraction < 1.0:
                idx = np.random.choice(len(X), int(len(X) * sample_fraction), replace=False)
                X_sub = X[idx]
                y_sub = y[idx] if y is not None else None
            else:
                X_sub, y_sub = X, y
            pipeline = None
            model = None
            # Handle (pipeline, model) or (pipeline, (model, params))
            if isinstance(spec, tuple) and (isinstance(spec[0], BaseEstimator) or isinstance(spec[0], TransformerMixin)):
                pipeline = spec[0]
                model_part = spec[1]
                if isinstance(model_part, tuple) and callable(model_part[0]):
                    params = dict(model_part[1])
                    if fast_mode:
                        for key in ['n_estimators', 'max_iter', 'max_depth']:
                            if key in params:
                                params[key] = min(params[key], 10)
                    model = model_part[0](**params)
                elif callable(model_part):
                    if fast_mode:
                        try:
                            model = model_part(n_estimators=10)
                        except TypeError:
                            model = model_part()
                    else:
                        model = model_part()
                else:
                    model = model_part
                # Fit pipeline and transform X
                pipeline.fit(X_sub, y_sub) if y_sub is not None else pipeline.fit(X_sub)
                X_sub = pipeline.transform(X_sub)
            # Handle (model, params)
            elif isinstance(spec, tuple) and callable(spec[0]):
                params = dict(spec[1])
                if fast_mode:
                    for key in ['n_estimators', 'max_iter', 'max_depth']:
                        if key in params:
                            params[key] = min(params[key], 10)
                model = spec[0](**params)
            # Handle model class
            elif callable(spec):
                if fast_mode:
                    try:
                        model = spec(n_estimators=10)
                    except TypeError:
                        model = spec()
                else:
                    model = spec()
            # Handle pre-instantiated model
            else:
                model = spec
            # Fit model
            if hasattr(model, 'fit'):
                if pipeline is not None:
                    if y_sub is not None:
                        model.fit(X_sub, y_sub)
                    else:
                        model.fit(X_sub)
                else:
                    if y_sub is not None:
                        model.fit(X_sub, y_sub)
                    else:
                        model.fit(X_sub)
            return (pipeline, model)
        if n_jobs == 1:
            results = [fit_model(spec) for spec in self.model_specs]
        else:
            with ThreadPoolExecutor(max_workers=n_jobs) as executor:
                results = list(executor.map(fit_model, self.model_specs))
        self.pipelines, self.models = zip(*results)
        self._is_fitted = True
        return self

    def predict(self, X, return_type='vector'):
        """
        Predict using the ensemble.
        Args:
            X: Input features.
            return_type: 'vector' (default) returns a 1D array of predictions; 'scalar' returns a single value if only one sample is provided.
        Returns:
            np.ndarray or scalar
        """
        if not self._is_fitted:
            raise RuntimeError("Ensemble must be fitted before calling predict.")
        preds = []
        for pipeline, model in zip(self.pipelines, self.models):
            X_input = pipeline.transform(X) if pipeline is not None else X
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore",
                    message="X does not have valid feature names",
                    category=UserWarning,
                )
                preds.append(model.predict(X_input))
        if hasattr(self.models[0], 'predict_proba'):
            # Classification: majority vote
            preds = np.array(preds)
            from scipy.stats import mode
            result = mode(preds, axis=0).mode
            result = np.squeeze(result)
        else:
            # Regression: mean
            result = np.mean(preds, axis=0)
        if return_type == 'scalar':
            if isinstance(result, np.ndarray) and result.size == 1:
                return result.item()
            elif isinstance(result, np.ndarray) and result.shape == ():
                return result.item()
            else:
                raise ValueError("Result is not a scalar. Use return_type='vector' for multiple samples.")
        return result

    def predict_raw(self, X):
        """
        Always return the raw result (may be vector or scalar depending on input).
        """
        return self.predict(X, return_type='vector')

class _EnsembleCall:
    def call(self, *models):
        return Ensemble(list(models))

ensemble = _EnsembleCall()

def monitor_performance(model_specs, X_train, y_train, X_val, y_val, eval_fn, patience=2, min_delta=0.001, verbose=True, **fit_kwargs):
    """
    Incrementally add models to the ensemble, track validation score, and stop when improvement plateaus.
    Args:
        model_specs: List of model specs (same as for ensemble.call)
        X_train, y_train: Training data
        X_val, y_val: Validation data
        eval_fn: Function to evaluate the ensemble (e.g., evalModel)
        patience: Number of rounds to wait for improvement before stopping
        min_delta: Minimum improvement to reset patience
        verbose: Print progress
        fit_kwargs: Additional kwargs for fit
    Returns:
        best_ensemble: The ensemble with the best validation score
        scores: List of validation scores as models are added
    """
    from copy import deepcopy
    scores = []
    best_score = -np.inf
    best_ensemble = None
    no_improve = 0
    for i in range(2, len(model_specs)+1):
        ens = ensemble.call(*model_specs[:i])
        ens.fit(X_train, y_train, **fit_kwargs)
        score = eval_fn(ens, X_val, y_val)
        scores.append(score)
        if verbose:
            print(f"Ensemble size: {i}, Validation score: {score:.4f}")
        if score > best_score + min_delta:
            best_score = score
            best_ensemble = deepcopy(ens)
            no_improve = 0
        else:
            no_improve += 1
        if no_improve >= patience:
            if verbose:
                print("No significant improvement, stopping.")
            break
    return best_ensemble, scores 