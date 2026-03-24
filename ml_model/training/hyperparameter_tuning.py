"""Hyperparameter tuning using GridSearchCV"""
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from xgboost import XGBClassifier
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def tune_xgboost(X, y):
    """Tune XGBoost hyperparameters"""
    logger.info("Starting XGBoost hyperparameter tuning...")

    param_grid = {
        'n_estimators': [100, 200],
        'max_depth': [5, 7, 9],
        'learning_rate': [0.05, 0.1],
        'subsample': [0.7, 0.8],
    }

    xgb = XGBClassifier(random_state=42, n_jobs=-1)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    grid_search = GridSearchCV(
        xgb, param_grid, cv=cv, scoring='f1', n_jobs=-1, verbose=1
    )
    grid_search.fit(X, y)

    logger.info(f"Best parameters: {grid_search.best_params_}")
    logger.info(f"Best F1-Score: {grid_search.best_score_:.4f}")

    return grid_search.best_estimator_