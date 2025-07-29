import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.linear_model import LinearRegression

class DeepCausal:
    def __init__(self, confounder_threshold=0.8, random_state=42):
        self.confounder_threshold = confounder_threshold
        self.random_state = random_state
        self.feature_ate_scores = []

    def _get_confounders(self, X, treatment):
        X_ = X.drop(columns=[treatment])
        y = X[treatment]

        is_class = not np.issubdtype(y.dtype, np.number)
        model = RandomForestClassifier if is_class else RandomForestRegressor
        model = model(n_estimators=100, random_state=self.random_state)

        model.fit(X_, y)
        importances = model.feature_importances_
        sorted_idx = np.argsort(importances)[::-1]
        cum_imp = np.cumsum(importances[sorted_idx])
        selected_idx = sorted_idx[cum_imp <= self.confounder_threshold]
        if len(selected_idx) == 0:
            selected_idx = sorted_idx[:1]

        return X_.columns[selected_idx]

    def fit(self, X, y, outcome_type='continuous'):
        self.feature_ate_scores = []
        Y_cont = y

        if outcome_type == 'categorical':
            clf = RandomForestClassifier(n_estimators=100, random_state=self.random_state)
            clf.fit(X, y)
            Y_cont = clf.predict_proba(X)[:, 1] * 100  # Convert to continuous

        for treatment in X.columns:
            confs = self._get_confounders(X, treatment)
            if len(confs) == 0:
                continue

            Xc = X[confs]
            T = X[treatment]

            # Residualize outcome
            y_model = RandomForestRegressor(n_estimators=100, random_state=self.random_state)
            y_model.fit(Xc, Y_cont)
            Ro = Y_cont - y_model.predict(Xc)

            # Residualize treatment
            is_class = not np.issubdtype(T.dtype, np.number)
            t_model = RandomForestClassifier if is_class else RandomForestRegressor
            t_model = t_model(n_estimators=100, random_state=self.random_state)
            t_model.fit(Xc, T)

            T_hat = t_model.predict_proba(Xc)[:, 1] * 100 if is_class else t_model.predict(Xc)
            Rt = T - T_hat

            # Estimate ATE
            reg = LinearRegression()
            reg.fit(Rt.values.reshape(-1, 1), Ro)
            self.feature_ate_scores.append((treatment, reg.coef_[0]))

        self.feature_ate_scores.sort(key=lambda x: abs(x[1]), reverse=True)

    def get_feature_ate(self, top_n=None):
        if top_n:
            return self.feature_ate_scores[:top_n]
        return self.feature_ate_scores
