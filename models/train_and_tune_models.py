import pandas as pd
import numpy as np
import os
from datetime import datetime
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, StackingRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib

CLEANED_DIR = "data/cleaned"
MODELS_DIR = "models"

# Find the latest cleaned CSV file
def get_latest_cleaned_csv():
    files = [f for f in os.listdir(CLEANED_DIR) if f.endswith('.csv')]
    if not files:
        raise FileNotFoundError("No cleaned CSV files found.")
    files.sort(reverse=True)
    return os.path.join(CLEANED_DIR, files[0])

def prepare_data(df):
    # Example: select features and target, encode categoricals, drop rows with missing price
    df = df.copy()
    df = df[df['price'].apply(lambda x: str(x).isdigit())]
    df['price'] = df['price'].astype(float)
    features = ['engineDisplacement', 'mileageFromOdometer', 'color', 'seller_location', 'name']
    for col in features:
        if col not in df.columns:
            df[col] = ''
    X = df[features].fillna("")
    # Simple encoding for demonstration
    X = pd.get_dummies(X, columns=['color', 'seller_location', 'name'], drop_first=True)
    y = df['price']
    return X, y

def train_and_tune_models(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    results = {}

    # Linear Regression
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    y_pred_lr = lr.predict(X_test)
    results['LinearRegression'] = {
        'model': lr,
        'rmse': mean_squared_error(y_test, y_pred_lr, squared=False),
        'r2': r2_score(y_test, y_pred_lr)
    }

    # Random Forest with GridSearch
    rf = RandomForestRegressor(random_state=42)
    rf_params = {'n_estimators': [50, 100], 'max_depth': [5, 10, None]}
    rf_grid = GridSearchCV(rf, rf_params, cv=3, n_jobs=-1)
    rf_grid.fit(X_train, y_train)
    y_pred_rf = rf_grid.predict(X_test)
    results['RandomForest'] = {
        'model': rf_grid.best_estimator_,
        'rmse': mean_squared_error(y_test, y_pred_rf, squared=False),
        'r2': r2_score(y_test, y_pred_rf)
    }

    # XGBoost with GridSearch
    xgb = XGBRegressor(random_state=42, verbosity=0)
    xgb_params = {'n_estimators': [50, 100], 'max_depth': [3, 6], 'learning_rate': [0.05, 0.1]}
    xgb_grid = GridSearchCV(xgb, xgb_params, cv=3, n_jobs=-1)
    xgb_grid.fit(X_train, y_train)
    y_pred_xgb = xgb_grid.predict(X_test)
    results['XGBoost'] = {
        'model': xgb_grid.best_estimator_,
        'rmse': mean_squared_error(y_test, y_pred_xgb, squared=False),
        'r2': r2_score(y_test, y_pred_xgb)
    }

    # Stacking (Ensemble)
    stack = StackingRegressor(
        estimators=[
            ('rf', rf_grid.best_estimator_),
            ('xgb', xgb_grid.best_estimator_)
        ],
        final_estimator=LinearRegression()
    )
    stack.fit(X_train, y_train)
    y_pred_stack = stack.predict(X_test)
    results['Stacking'] = {
        'model': stack,
        'rmse': mean_squared_error(y_test, y_pred_stack, squared=False),
        'r2': r2_score(y_test, y_pred_stack)
    }

    return results

def save_models(results):
    os.makedirs(MODELS_DIR, exist_ok=True)
    for name, res in results.items():
        joblib.dump(res['model'], os.path.join(MODELS_DIR, f"{name}.joblib"))

def main():
    latest_cleaned = get_latest_cleaned_csv()
    df = pd.read_csv(latest_cleaned)
    X, y = prepare_data(df)
    results = train_and_tune_models(X, y)
    save_models(results)
    for name, res in results.items():
        print(f"{name}: RMSE={res['rmse']:.2f}, R2={res['r2']:.3f}")

if __name__ == "__main__":
    main()
