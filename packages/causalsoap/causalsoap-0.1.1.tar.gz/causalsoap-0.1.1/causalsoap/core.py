import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.linear_model import LinearRegression

class CausalDRIFT:
    def __init__(self):
        self.ate_results = []

    def _get_confounders(self, X, treatment, model_type='regressor', threshold=0.8):
        X_ = X.drop(columns=[treatment])
        y = X[treatment]

        model = RandomForestClassifier(n_estimators=100, random_state=42) if model_type == 'classifier' else RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_, y)

        importances = model.feature_importances_
        sorted_idx = np.argsort(importances)[::-1]
        cumulative_importance = np.cumsum(importances[sorted_idx])
        selected_idx = sorted_idx[cumulative_importance <= threshold]

        if len(selected_idx) == 0:
            selected_idx = sorted_idx[:1]

        return X_.columns[selected_idx]

    def fit(self, X, y, outcome_type='continuous', categorical_features=None):
        categorical_features = categorical_features or []
        self.ate_results = []

        if outcome_type == 'categorical':
            clf = RandomForestClassifier(n_estimators=100, random_state=42)
            clf.fit(X, y)
            y_cont = clf.predict_proba(X)[:, 1]
        else:
            y_cont = y

        for treatment in X.columns:
            is_categorical = treatment in categorical_features
            model_type = 'classifier' if is_categorical else 'regressor'

            confounders = self._get_confounders(X, treatment, model_type)
            if len(confounders) == 0:
                continue

            X_confounders = X[confounders]
            T = X[treatment]

            y_model = RandomForestRegressor(n_estimators=100, random_state=42)
            y_model.fit(X_confounders, y_cont)
            Ro = y_cont - y_model.predict(X_confounders)

            t_model = RandomForestClassifier(n_estimators=100, random_state=42) if is_categorical else RandomForestRegressor(n_estimators=100, random_state=42)
            t_model.fit(X_confounders, T)
            T_hat = t_model.predict_proba(X_confounders)[:, 1] if is_categorical else t_model.predict(X_confounders)
            Rt = T - T_hat

            reg = LinearRegression()
            reg.fit(Rt.values.reshape(-1, 1), Ro)
            ate = reg.coef_[0]

            self.ate_results.append((treatment, ate))

        self.ate_results.sort(key=lambda x: abs(x[1]), reverse=True)

    def get_feature_ate(self):
        return self.ate_results
