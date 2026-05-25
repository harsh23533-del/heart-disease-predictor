# train.py
import optuna, joblib
import numpy as np
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, classification_report
from data_loader import load_data, preprocess

def objective(trial, X_train, y_train, X_test, y_test):
    params = {
        'n_estimators':     trial.suggest_int('n_estimators', 100, 500),
        'max_depth':        trial.suggest_int('max_depth', 3, 8),
        'learning_rate':    trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
        'subsample':        trial.suggest_float('subsample', 0.6, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
        'use_label_encoder': False, 'eval_metric': 'logloss'
    }
    model = XGBClassifier(**params, random_state=42)
    model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)
    return roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])

if __name__ == '__main__':
    df = load_data()
    X_train, X_test, y_train, y_test, scaler, feature_names = preprocess(df)

    # Tune XGBoost
    study = optuna.create_study(direction='maximize')
    study.optimize(lambda t: objective(t, X_train, y_train, X_test, y_test), n_trials=50)

    best_model = XGBClassifier(**study.best_params, random_state=42,
                               use_label_encoder=False, eval_metric='logloss')
    best_model.fit(X_train, y_train)

    y_pred = best_model.predict(X_test)
    print(classification_report(y_test, y_pred))
    print(f"AUC-ROC: {roc_auc_score(y_test, best_model.predict_proba(X_test)[:,1]):.4f}")

    joblib.dump(best_model, 'model.pkl')
    joblib.dump(scaler, 'scaler.pkl')
    joblib.dump(feature_names, 'features.pkl')