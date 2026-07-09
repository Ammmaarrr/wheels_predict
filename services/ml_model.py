"""
ML model loader and predictors using the saved sklearn Pipeline.
Finds latest model under models/ and predicts from structured dict or free text via parser.
"""
from __future__ import annotations

import os
import glob
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

from .text_parser import parse_text_record

MODEL_GLOB = os.path.join('models', 'pakwheels_price_*_*.joblib')

class PriceModel:
    _pipe = None
    _path = None

    @classmethod
    def load_latest(cls) -> Optional[str]:
        if cls._pipe is not None:
            return cls._path
        files = sorted(glob.glob(MODEL_GLOB), key=lambda p: os.path.getmtime(p), reverse=True)
        if not files:
            return None
        cls._path = files[0]
        cls._pipe = joblib.load(cls._path)
        return cls._path

    @classmethod
    def is_ready(cls) -> bool:
        return cls._pipe is not None or cls.load_latest() is not None

    @classmethod
    def predict_structured(cls, features: Dict[str, Any]) -> Dict[str, Any]:
        if not cls.is_ready():
            raise RuntimeError('No trained model found under models/. Run the training notebook to produce a joblib file.')
        cols = ['brand','model','fuelType','vehicleTransmission','seller_location','bodyType','engineDisplacement','mileageFromOdometer','modelDate']
        row = {k: features.get(k) for k in cols}
        X = pd.DataFrame([row])
        # Sanitize dtypes aligning with notebook
        cat = [c for c in X.columns if c not in ['engineDisplacement','mileageFromOdometer','modelDate']]
        for c in cat:
            X[c] = X[c].astype('object')
            X[c] = X[c].where(pd.notna(X[c]), np.nan)
        for c in ['engineDisplacement','mileageFromOdometer','modelDate']:
            if c in X:
                X[c] = pd.to_numeric(X[c], errors='coerce')
        pred = float(cls._pipe.predict(X)[0])
        return {
            'predicted_price': pred,
        }

    @classmethod
    def predict_from_text(cls, text: str) -> Dict[str, Any]:
        parsed = parse_text_record(text)
        features = {
            'brand': (parsed.get('make') or '') if parsed.get('make') else None,
            'model': parsed.get('model'),
            'fuelType': parsed.get('fuel_type'),
            'vehicleTransmission': parsed.get('transmission'),
            'seller_location': parsed.get('location'),
            'bodyType': parsed.get('body_type'),
            'engineDisplacement': parsed.get('engine_cc'),
            'mileageFromOdometer': parsed.get('mileage_km'),
            'modelDate': parsed.get('year'),
        }
        pred = cls.predict_structured(features)
        return {
            'parsed': parsed,
            **pred,
        }
