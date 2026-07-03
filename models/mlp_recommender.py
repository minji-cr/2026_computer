"""MLP 기반 국가 복지 정책 추천 모델 (scikit-learn)."""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.neural_network import MLPRegressor

from utils.calculations import HouseholdInput, check_policy_eligibility
from utils.data_loader import load_policies

MODEL_DIR = Path(__file__).resolve().parent
MLP_PATH = MODEL_DIR / "mlp_recommender.joblib"

FEATURE_DIM = 7


def build_mlp_model() -> MLPRegressor:
    return MLPRegressor(
        hidden_layer_sizes=(64, 32, 16),
        activation="relu",
        solver="adam",
        alpha=1e-4,
        batch_size=64,
        max_iter=300,
        random_state=42,
    )


def generate_training_data(
    policies_df: pd.DataFrame,
    n_samples: int = 5000,
) -> tuple[np.ndarray, np.ndarray]:
    """정책 자격 조건 기반 합성 학습 데이터 생성."""
    rng = np.random.default_rng(42)
    n_policies = len(policies_df)
    X = np.zeros((n_samples, FEATURE_DIM), dtype=np.float32)
    y = np.zeros((n_samples, n_policies), dtype=np.float32)

    regions = [
        "서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종",
        "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주",
    ]

    for i in range(n_samples):
        income = rng.uniform(300_000, 5_000_000)
        size = int(rng.integers(1, 7))
        region = regions[int(rng.integers(0, len(regions)))]
        electric = rng.uniform(30_000, 200_000)
        fuel = rng.uniform(20_000, 250_000)
        water = rng.uniform(0, 30_000)
        consumption = rng.uniform(100, 600)

        household = HouseholdInput(
            monthly_income=income,
            household_size=size,
            region=region,
            monthly_electric=electric,
            monthly_fuel=fuel,
            monthly_water=water,
            monthly_energy_consumption=consumption,
        )
        X[i] = household.to_feature_vector()

        for j, (_, policy) in enumerate(policies_df.iterrows()):
            eligible, _ = check_policy_eligibility(policy.to_dict(), household)
            fitness = 0.0
            if eligible:
                income_score = 1 - (income / policy["max_income"])
                ratio_score = min(household.energy_ratio / 0.15, 1.0)
                fitness = 0.5 * income_score + 0.5 * ratio_score
                fitness = np.clip(fitness + rng.normal(0, 0.05), 0.3, 1.0)
            y[i, j] = fitness if eligible else rng.uniform(0, 0.2)

    return X, y


def train_and_save_mlp() -> MLPRegressor:
    policies_df = load_policies()
    X, y = generate_training_data(policies_df)
    model = build_mlp_model()
    model.fit(X, y)
    joblib.dump(model, MLP_PATH)
    return model


def load_mlp_model() -> MLPRegressor:
    if not MLP_PATH.exists():
        return train_and_save_mlp()
    return joblib.load(MLP_PATH)


def get_recommendation_reason(
    policy: dict,
    household: HouseholdInput,
    fitness: float,
    eligible: bool,
) -> str:
    if not eligible:
        return "소득·지역·에너지지출 조건 중 일부가 정책 기준에 미달합니다."

    reasons = []
    if household.is_energy_poor:
        reasons.append("에너지지출비율이 10% 이상으로 에너지빈곤 위험에 해당")
    if household.monthly_income <= policy["max_income"] * 0.7:
        reasons.append("소득 수준이 정책 지원 대상 범위에 적합")
    if fitness >= 70:
        reasons.append("AI 모델이 높은 적합도로 판단")
    elif fitness >= 50:
        reasons.append("가구 특성과 정책 조건이 부분적으로 일치")
    else:
        reasons.append("일부 조건은 충족하나 추가 검토가 필요")

    category = policy.get("category", "")
    if category:
        reasons.append(f"{category} 분야 지원으로 에너지비 부담 완화 기대")

    return " / ".join(reasons)


def recommend_policies(
    household: HouseholdInput,
    top_k: int = 5,
) -> list[dict]:
    policies_df = load_policies()
    model = load_mlp_model()
    features = np.array([household.to_feature_vector()], dtype=np.float32)
    predictions = np.clip(model.predict(features)[0], 0.0, 1.0)

    results = []
    for idx, (_, policy) in enumerate(policies_df.iterrows()):
        policy_dict = policy.to_dict()
        eligible, elig_msg = check_policy_eligibility(policy_dict, household)
        ai_score = float(predictions[idx]) * 100

        if eligible:
            fitness = min(ai_score * 0.6 + 40, 99.0)
        else:
            fitness = ai_score * 0.4

        reason = get_recommendation_reason(policy_dict, household, fitness, eligible)
        if not eligible:
            reason = elig_msg

        results.append(
            {
                "policy_id": policy_dict["policy_id"],
                "policy_name": policy_dict["policy_name"],
                "category": policy_dict["category"],
                "fitness": round(fitness, 1),
                "eligible": eligible,
                "eligibility_desc": policy_dict["eligibility_desc"],
                "support_content": policy_dict["support_content"],
                "application_method": policy_dict["application_method"],
                "reason": reason,
                "policy": policy_dict,
            }
        )

    results.sort(key=lambda x: (x["eligible"], x["fitness"]), reverse=True)
    return results[:top_k]
