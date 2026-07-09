import os
import logging
from dotenv import load_dotenv
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import OneHotEncoder, StandardScaler
import random
import joblib
from utils.logger import setup_logger, log_error

# Load environment variables
load_dotenv()

# Configure logger
logger = setup_logger(__name__, level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")))

# Load configuration
MODEL_PATH = os.getenv("MODEL_PATH", "models/best_xgb_model_updated.joblib")
TEST_MODE = os.getenv("TEST_MODE", "False").lower() == "true"
REQUIRED_FEATURES = os.getenv(
    "REQUIRED_FEATURES", "year,mileage,engine_capacity,transmission,location"
).split(",")
NUMERIC_FEATURES = os.getenv("NUMERIC_FEATURES", "year,mileage,engine_capacity").split(
    ","
)
CATEGORICAL_FEATURES = os.getenv("CATEGORICAL_FEATURES", "transmission,location").split(
    ","
)
DEFAULT_NUM_RECOMMENDATIONS = int(os.getenv("DEFAULT_NUM_RECOMMENDATIONS", "5"))


def load_model(model_path=None, test_mode=None):
    """Load the trained model.

    Args:
        model_path: Optional path to model file. If not provided, uses MODEL_PATH from env.
        test_mode: If True, returns a simple test model. If None, uses TEST_MODE from env.

    Returns:
        Trained model (XGBoost or test model)
    """
    # Use environment variables if parameters not provided
    if model_path is None:
        model_path = MODEL_PATH
    if test_mode is None:
        test_mode = TEST_MODE

    if test_mode:
        from sklearn.base import BaseEstimator, RegressorMixin

        class TestModel(BaseEstimator, RegressorMixin):
            def predict(self, X):
                return np.array([2500000])  # Return fixed prediction for testing

            def get_booster(self):
                class MockBooster:
                    def feature_names(self):
                        return REQUIRED_FEATURES

                return MockBooster()

        logger.info("Using test model")
        return TestModel()

    try:
        model = joblib.load(model_path)
        logger.info(f"Model loaded successfully from {model_path}")
        try:
            feature_names = model.get_booster().feature_names
            logger.info(f"Model features: {feature_names}")
        except Exception as e:
            logger.warning(f"Could not get feature names: {str(e)}")
        return model
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise


def preprocess_input(data):
    """Preprocess input data for model prediction.

    Args:
        data: pandas DataFrame, dict, or list of dicts containing car features
            Must include either:
            - Raw features: defined by REQUIRED_FEATURES in env
            - Preprocessed features: including numeric and one-hot encoded categorical features

    Returns:
        pandas DataFrame with properly aligned features for model prediction

    Raises:
        ValueError: If required features are missing or invalid
    """
    try:
        # Convert input to DataFrame
        if isinstance(data, dict):
            data = pd.DataFrame([data])
        elif isinstance(data, list):
            data = pd.DataFrame(data)
        elif not isinstance(data, pd.DataFrame):
            raise ValueError(
                "Input must be a dictionary, list of dictionaries, or pandas DataFrame"
            )

        # Check if data is already preprocessed
        preprocessed_cols = {
            "numeric": NUMERIC_FEATURES,
            "transmission": [f"transmission_{cat}" for cat in ["Automatic", "Manual"]],
            "location": [
                f"location_{cat}" for cat in ["Islamabad", "Karachi", "Lahore"]
            ],
        }

        is_preprocessed = all(
            all(col in data.columns for col in cols)
            for cols in preprocessed_cols.values()
        )

        if is_preprocessed:
            # Data is already preprocessed, just validate and return
            for col in sum(
                preprocessed_cols.values(), []
            ):  # Flatten all expected columns
                if not pd.to_numeric(data[col], errors="coerce").notnull().all():
                    raise ValueError(
                        f"Column '{col}' must contain valid numerical values"
                    )
            return data[
                sum(preprocessed_cols.values(), [])
            ]  # Return with correct column order

        # If not preprocessed, check for raw features
        missing_cols = [col for col in REQUIRED_FEATURES if col not in data.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Validate numerical columns
        numeric_cols = NUMERIC_FEATURES
        for col in numeric_cols:
            if not pd.to_numeric(data[col], errors="coerce").notnull().all():
                raise ValueError(f"Column '{col}' must contain valid numerical values")

        # Create dummy variables for categorical features
        df_processed = pd.get_dummies(
            data, columns=CATEGORICAL_FEATURES, prefix=CATEGORICAL_FEATURES
        )

        # Add missing dummy columns and ensure correct order
        all_columns = []
        for prefix, values in preprocessed_cols.items():
            for col in values:
                if col not in df_processed.columns:
                    df_processed[col] = 0
                all_columns.append(col)

        return df_processed[all_columns]

    except Exception as e:
        logger.error(
            f"Error preprocessing input: {str(e)}",
            extra={
                "data_shape": data.shape if hasattr(data, "shape") else None,
                "data_columns": (
                    list(data.columns) if hasattr(data, "columns") else None
                ),
                "data_type": str(type(data)),
            },
        )
        raise


def predict_price(input_data, test_mode=None):
    """Predict car price based on input features.

    Args:
        input_data: DataFrame or dict with car features
        test_mode: If True, uses test model. If None, uses TEST_MODE from env.

    Returns:
        float: Predicted price
    """
    try:
        model = load_model(test_mode=test_mode)
        processed_input = preprocess_input(input_data)
        return model.predict(processed_input)
    except Exception as e:
        logger.error(f"Error predicting price - {type(e).__name__}: {str(e)}")
        raise


def preprocess_features(data):
    """Preprocess features for similarity calculation."""
    try:
        # Select numerical features
        numerical_features = ["year", "price", "mileage", "engine_capacity"]
        features = data[numerical_features].copy()

        # Encode categorical features
        categorical_features = ["transmission"]
        if all(col in data.columns for col in categorical_features):
            encoded = pd.get_dummies(
                data[categorical_features], prefix=categorical_features
            )
            features = pd.concat([features, encoded], axis=1)

        # Scale features
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features)

        # Create DataFrame with proper column names
        feature_names = (
            numerical_features
            + [f"transmission_{cat}" for cat in ["Automatic", "Manual"]]
            if "transmission" in data.columns
            else numerical_features
        )

        return pd.DataFrame(scaled_features, columns=feature_names, index=data.index)

    except Exception as e:
        log_error(logger, e)
        raise


def calculate_similarity(features):
    """Calculate cosine similarity between feature vectors.

    Args:
        features: numpy array or DataFrame of feature vectors

    Returns:
        numpy array of similarity scores between all pairs of vectors
    """
    if isinstance(features, pd.DataFrame):
        features = features.values

    # Normalize feature vectors
    norms = np.linalg.norm(features, axis=1, keepdims=True)
    normalized_features = np.divide(features, norms, where=norms != 0)

    # Calculate cosine similarity
    similarity = np.dot(normalized_features, normalized_features.T)

    # Ensure similarity values are in [-1, 1] range
    np.clip(similarity, -1, 1, out=similarity)

    return similarity


def get_similar_cars(reference_car, all_cars, n_recommendations=None):
    """Get similar cars based on features.

    Args:
        reference_car: The car to find similar ones to
        all_cars: DataFrame of all available cars
        n_recommendations: Number of recommendations to return. Uses DEFAULT_NUM_RECOMMENDATIONS from env if not specified.
    """
    if n_recommendations is None:
        n_recommendations = DEFAULT_NUM_RECOMMENDATIONS

    try:
        if len(all_cars) <= 1:
            raise ValueError("Need more than one car to make recommendations")
        if n_recommendations >= len(all_cars):
            raise ValueError("Requesting more recommendations than available cars")

        # Preprocess features
        features_df = preprocess_features(all_cars)

        # Calculate similarity
        similarity_matrix = calculate_similarity(features_df)

        # Get reference car index
        ref_idx = all_cars.index.get_loc(reference_car.name)

        # Get similar cars indices (excluding the reference car)
        similar_indices = np.argsort(similarity_matrix[ref_idx])[::-1][
            1 : n_recommendations + 1
        ]

        # Get similar cars with similarity scores
        similar_cars = all_cars.iloc[similar_indices].copy()
        similar_cars["similarity_score"] = similarity_matrix[ref_idx][similar_indices]

        return similar_cars

    except Exception as e:
        log_error(logger, e)
        raise


def enhanced_hybrid_recommendation(df, user_history=None, top_n=None, diversity=True):
    """Get enhanced hybrid recommendations.

    Args:
        df: DataFrame of all cars
        user_history: List of previously viewed/liked cars
        top_n: Number of recommendations. Uses DEFAULT_NUM_RECOMMENDATIONS from env if not specified.
        diversity: Whether to ensure diverse recommendations
    """
    if top_n is None:
        top_n = DEFAULT_NUM_RECOMMENDATIONS

    features = [
        "mileageFromOdometer",
        "engineDisplacement",
        "fuelType",
        "seller_location",
    ]
    available = [f for f in features if f in df.columns]
    df_rec = df.dropna(subset=available).copy()

    cat = [f for f in ["fuelType", "seller_location"] if f in df_rec.columns]
    enc = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
    cat_df = pd.DataFrame(
        enc.fit_transform(df_rec[cat]),
        columns=enc.get_feature_names_out(cat),
        index=df_rec.index,
    )

    num = [
        f for f in ["mileageFromOdometer", "engineDisplacement"] if f in df_rec.columns
    ]
    X = pd.concat([df_rec[num], cat_df], axis=1)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    sim = cosine_similarity(X_scaled)

    # Get popular items as fallback
    pop = (
        df["model"].value_counts().head(top_n * 2).index.tolist()
        if "model" in df.columns
        else []
    )

    hybrid = []
    # User profile: average features from user_history
    if user_history is not None and len(df_rec) > 0:
        if isinstance(user_history, list) and len(user_history) > 0:
            user_indices = (
                df_rec[df_rec["model"].isin(user_history)].index.tolist()
                if "model" in df_rec.columns
                else []
            )
            if user_indices:
                user_vec = X_scaled[user_indices].mean(axis=0, keepdims=True)
                sim_scores = cosine_similarity(user_vec, X_scaled).flatten()
                similar_idx = sim_scores.argsort()[::-1][: top_n * 2]
                hybrid = (
                    df_rec.iloc[similar_idx]["model"].tolist()
                    if "model" in df_rec.columns
                    else []
                )

    # Add popular items not already included
    hybrid += [m for m in pop if m not in hybrid]

    if diversity:
        seen = set()
        diverse = []
        for m in hybrid:
            if m not in seen:
                diverse.append(m)
                seen.add(m)
            if len(diverse) >= top_n:
                break
        random.shuffle(diverse)
        hybrid = diverse

    return hybrid[:top_n]
