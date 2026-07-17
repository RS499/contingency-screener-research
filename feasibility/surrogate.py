import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.ensemble import HistGradientBoostingRegressor

RIDGE_ALPHA = 10.0
HISTGB_MAX_ITER = 300
HISTGB_LEARNING_RATE = 0.08
HISTGB_MAX_DEPTH = 8


def train_ridge(X_train, y_train, alpha=RIDGE_ALPHA):
    scaler = StandardScaler().fit(X_train)
    model = Ridge(alpha=alpha).fit(scaler.transform(X_train), y_train)
    return dict(kind="ridge", scaler=scaler, model=model)


def train_histgb(X_train, y_train, seed=0):
    model = HistGradientBoostingRegressor(
        max_iter=HISTGB_MAX_ITER, learning_rate=HISTGB_LEARNING_RATE,
        max_depth=HISTGB_MAX_DEPTH, random_state=seed).fit(X_train, y_train)
    return dict(kind="histgb", model=model)


def predict(fitted, X):
    if fitted["kind"] == "ridge":
        return fitted["model"].predict(fitted["scaler"].transform(X))
    return fitted["model"].predict(X)



def predict_persistence(n0_min_vm):
    return np.asarray(n0_min_vm, dtype=np.float64)


def predict_mean(y_train, n):
    return np.full(n, float(np.mean(y_train)), dtype=np.float64)
