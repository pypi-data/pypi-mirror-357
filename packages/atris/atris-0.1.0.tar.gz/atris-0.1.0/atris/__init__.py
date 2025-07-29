# atris/__init__.py
"""
atris: A library for seamless model ensembling and evaluation.
"""
from .ensemble import ensemble, monitor_performance
from .eval import evalModel
from . import models
from .process import processData
from .features import InteractionFeatures, PolynomialFeaturesWrapper, IdentityTransformer
# from .anomaly_models import *  # Removed to avoid exposing missing wrappers
from .classification_models import *
from .regression_models import *