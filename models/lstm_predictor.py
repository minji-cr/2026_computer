"""LSTM 기반 정책 적용 후 에너지 비용 예측 모델."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import tensorflow as tf
from tensorflow import keras

from utils.calculations import HouseholdInput, predict_savings

MODEL_DIR = Path(__file__).resolve().parent
LSTM_PATH = MODEL_DIR / "lstm_predictor.keras"

SEQ_LEN = 6
FEATURES_PER_STEP = 3  # electric, fuel, total


def build_lstm_model() -> keras.Model:
    model = keras.Sequential(
        [
            keras.layers.Input(shape=(SEQ_LEN, FEATURES_PER_STEP)),
            keras.layers.LSTM(32, return_sequences=True),
            keras.layers.Dropout(0.2),
            keras.layers.LSTM(16),
            keras.layers.Dense(8, activation="relu"),
            keras.layers.Dense(3, activation="linear"),
        ],
        name="cost_lstm",
    )
    model.compile(optimizer="adam", loss="mse", metrics=["mae"])
    return model


def generate_lstm_training_data(n_samples: int = 3000) -> tuple[np.ndarray, np.ndarray]:
    """과거 6개월 에너지 비용 시계열 → 다음 달 비용 예측 학습 데이터."""
    rng = np.random.default_rng(42)
    X = np.zeros((n_samples, SEQ_LEN, FEATURES_PER_STEP), dtype=np.float32)
    y = np.zeros((n_samples, FEATURES_PER_STEP), dtype=np.float32)

    for i in range(n_samples):
        base_electric = rng.uniform(40_000, 150_000)
        base_fuel = rng.uniform(30_000, 180_000)
        trend = rng.uniform(-0.05, 0.05)
        seasonal = rng.uniform(0.8, 1.2)

        history = []
        for month in range(SEQ_LEN + 1):
            factor = (1 + trend * month) * seasonal
            if month in (11, 0, 1, 2):
                factor *= rng.uniform(1.1, 1.4)
            electric = base_electric * factor * rng.uniform(0.9, 1.1)
            fuel = base_fuel * factor * rng.uniform(0.9, 1.1)
            total = electric + fuel
            history.append([electric / 100_000, fuel / 100_000, total / 100_000])

        X[i] = history[:SEQ_LEN]
        y[i] = history[SEQ_LEN]

    return X, y


def train_and_save_lstm() -> keras.Model:
    X, y = generate_lstm_training_data()
    model = build_lstm_model()
    model.fit(X, y, epochs=40, batch_size=64, validation_split=0.2, verbose=1)
    model.save(LSTM_PATH)
    return model


def load_lstm_model() -> keras.Model:
    if not LSTM_PATH.exists():
        return train_and_save_lstm()
    return keras.models.load_model(LSTM_PATH)


def _build_sequence(household: HouseholdInput) -> np.ndarray:
    """가구 정보로 6개월 시계열 시퀀스 생성."""
    rng = np.random.default_rng(int(household.monthly_income) % 10000)
    seq = np.zeros((SEQ_LEN, FEATURES_PER_STEP), dtype=np.float32)

    for i in range(SEQ_LEN):
        variation = rng.uniform(0.85, 1.15)
        winter_boost = 1.2 if i in (0, 1, 5) else 1.0
        electric = household.monthly_electric * variation * winter_boost
        fuel = household.monthly_fuel * variation * winter_boost
        total = electric + household.monthly_water
        seq[i] = [electric / 100_000, fuel / 100_000, total / 100_000]

    return seq.reshape(1, SEQ_LEN, FEATURES_PER_STEP)


def predict_cost_with_lstm(
    household: HouseholdInput,
    policy: dict | None = None,
) -> dict:
    """LSTM으로 정책 적용 전·후 비용 예측."""
    model = load_lstm_model()
    sequence = _build_sequence(household)
    raw_pred = model.predict(sequence, verbose=0)[0]

    baseline = predict_savings(household, {
        "electric_discount_rate": 0,
        "fuel_discount_rate": 0,
        "monthly_support_amount": 0,
    })

    if policy:
        rule_based = predict_savings(household, policy)
        lstm_electric = float(raw_pred[0]) * 100_000
        lstm_fuel = float(raw_pred[1]) * 100_000

        discount_e = float(policy.get("electric_discount_rate", 0))
        discount_f = float(policy.get("fuel_discount_rate", 0))
        support = float(policy.get("monthly_support_amount", 0))

        predicted_electric = lstm_electric * (1 - discount_e)
        predicted_fuel = lstm_fuel * (1 - discount_f)
        predicted_total = max(
            predicted_electric + predicted_fuel + household.monthly_water - support, 0
        )

        original = baseline["original_total"]
        savings = original - predicted_total
        savings_rate = (savings / original * 100) if original > 0 else 0

        return {
            "original_electric": baseline["original_electric"],
            "original_fuel": baseline["original_fuel"],
            "original_total": original,
            "predicted_electric": predicted_electric,
            "predicted_fuel": predicted_fuel,
            "predicted_total": predicted_total,
            "savings_amount": savings,
            "savings_rate": savings_rate,
            "monthly_support": support,
            "lstm_baseline_electric": lstm_electric,
            "lstm_baseline_fuel": lstm_fuel,
        }

    lstm_electric = float(raw_pred[0]) * 100_000
    lstm_fuel = float(raw_pred[1]) * 100_000
    lstm_total = float(raw_pred[2]) * 100_000

    return {
        "original_electric": baseline["original_electric"],
        "original_fuel": baseline["original_fuel"],
        "original_total": baseline["original_total"],
        "predicted_electric": lstm_electric,
        "predicted_fuel": lstm_fuel,
        "predicted_total": lstm_total,
        "savings_amount": 0,
        "savings_rate": 0,
        "monthly_support": 0,
    }


def get_monthly_forecast(
    household: HouseholdInput,
    policy: dict,
    months: int = 6,
) -> list[dict]:
    """향후 N개월 비용 예측 (정책 적용 전·후)."""
    savings = predict_cost_with_lstm(household, policy)
    rng = np.random.default_rng(123)

    forecast = []
    for m in range(months):
        seasonal = 1.3 if m in (0, 1, 5) else 1.0
        variation = rng.uniform(0.95, 1.05) * seasonal

        before_e = household.monthly_electric * variation
        before_f = household.monthly_fuel * variation
        before_t = before_e + before_f + household.monthly_water

        after_e = savings["predicted_electric"] * variation
        after_f = savings["predicted_fuel"] * variation
        after_t = after_e + after_f + household.monthly_water - savings["monthly_support"]
        after_t = max(after_t, 0)

        forecast.append({
            "month": f"{m + 1}개월 후",
            "before_electric": before_e,
            "before_fuel": before_f,
            "before_total": before_t,
            "after_electric": after_e,
            "after_fuel": after_f,
            "after_total": after_t,
            "savings": before_t - after_t,
        })

    return forecast
