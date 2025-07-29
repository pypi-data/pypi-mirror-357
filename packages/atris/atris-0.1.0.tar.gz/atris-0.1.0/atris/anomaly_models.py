# Anomaly detection models for atris
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.neighbors import LocalOutlierFactor
from sklearn.covariance import EllipticEnvelope

# Wrappers for statistical and deep learning methods (to be implemented in wrappers/)
from .wrappers.zscore import ZScoreAnomaly
from .wrappers.iqr import IQRAnomaly
from .wrappers.knn_outlier import KNNOutlierAnomaly
# from .wrappers.hbos import HBOSAnomaly  # Removed: file no longer exists
# from .wrappers.pca_anomaly import PCAAnomaly  # Removed: file no longer exists
# from .wrappers.autoencoder import AutoencoderAnomaly  # Uncomment if keras is available 