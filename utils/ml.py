import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.preprocessing import StandardScaler
import io

class ModelStudio:
    """The engine behind Predictive Studio Pro."""
    
    MODELS = {
        "Linear Regression": LinearRegression,
        "Ridge Regression": Ridge,
        "Random Forest": RandomForestRegressor,
        "Gradient Boosting": GradientBoostingRegressor
    }

    def __init__(self, df, target, features, test_size=0.2, random_state=42):
        self.df = df.dropna(subset=[target] + features)
        self.target = target
        self.features = features
        self.test_size = test_size
        self.random_state = random_state
        self.results = {}
        self.trained_models = {}
        self.scaler = StandardScaler()

    def train_all(self, params=None):
        """Trains all models and stores metrics."""
        X = self.df[self.features]
        y = self.df[self.target]
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_size, random_state=self.random_state
        )

        # Scale numerical data for linear models
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        for name, model_cls in self.MODELS.items():
            model_params = params.get(name, {}) if params else {}
            
            # Default params for tree models if not provided
            if "Forest" in name or "Boosting" in name:
                model_params.setdefault("n_estimators", 100)
                model_params.setdefault("random_state", self.random_state)

            model = model_cls(**model_params)
            
            # Use scaled data for linear models, raw for trees (though scaled is fine too)
            is_linear = "Regression" in name
            X_tr = X_train_scaled if is_linear else X_train
            X_ts = X_test_scaled if is_linear else X_test
            
            model.fit(X_tr, y_train)
            y_pred = model.predict(X_ts)

            self.results[name] = {
                "R2": r2_score(y_test, y_pred),
                "MAE": mean_absolute_error(y_test, y_pred),
                "RMSE": np.sqrt(mean_squared_error(y_test, y_pred))
            }
            self.trained_models[name] = model

        return self.results

    def generate_python_code(self, model_name):
        """Returns a string of Python code to reproduce the model."""
        features_str = str(self.features)
        target_str = f"'{self.target}'"
        
        code = f"""import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error

# 1. Load your data
# df = pd.read_csv('your_data.csv')

# 2. Prepare features and target
features = {features_str}
target = {target_str}
X = df[features]
y = df[target]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size={self.test_size}, random_state={self.random_state})

"""
        if "Regression" in model_name:
            code += """
# 3. Scaling (Mandatory for Linear/Ridge)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)
"""

        if model_name == "Linear Regression":
            code += "from sklearn.linear_model import LinearRegression\nmodel = LinearRegression()"
        elif model_name == "Ridge Regression":
            code += "from sklearn.linear_model import Ridge\nmodel = Ridge()"
        elif model_name == "Random Forest":
            code += "from sklearn.ensemble import RandomForestRegressor\nmodel = RandomForestRegressor(n_estimators=100)"
        elif model_name == "Gradient Boosting":
            code += "from sklearn.ensemble import GradientBoostingRegressor\nmodel = GradientBoostingRegressor(n_estimators=100)"

        code += """
# 4. Train
model.fit(X_train, y_train)

# 5. Predict & Evaluate
y_pred = model.predict(X_test)
print(f"R2 Score: {r2_score(y_test, y_pred):.4f}")
"""
        return code
