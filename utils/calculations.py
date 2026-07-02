"""에너지 지표 계산 유틸리티."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


REGIONS = [
    "서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종",
    "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주",
]


@dataclass
class HouseholdInput:
    monthly_income: float
    household_size: int
    region: str
    monthly_electric: float
    monthly_fuel: float
    monthly_water: float = 0.0
    monthly_energy_consumption: Optional[float] = None

    @property
    def total_energy_cost(self) -> float:
        return self.monthly_electric + self.monthly_fuel + self.monthly_water

    @property
    def energy_ratio(self) -> float:
        if self.monthly_income <= 0:
            return 0.0
        return self.total_energy_cost / self.monthly_income

    @property
    def is_energy_poor(self) -> bool:
        return self.energy_ratio >= 0.10

    def to_feature_vector(self) -> list[float]:
        region_idx = REGIONS.index(self.region) if self.region in REGIONS else 0
        consumption = (
            self.monthly_energy_consumption
            if self.monthly_energy_consumption is not None
            else self.total_energy_cost / 150
        )
        return [
            self.monthly_income / 1_000_000,
            self.household_size / 10,
            region_idx / len(REGIONS),
            self.monthly_electric / 100_000,
            self.monthly_fuel / 100_000,
            consumption / 500,
            self.energy_ratio,
        ]


def check_policy_eligibility(
    policy: dict,
    household: HouseholdInput,
) -> tuple[bool, str]:
    """정책 지원 대상 여부를 규칙 기반으로 판단."""
    income = household.monthly_income
    min_income = policy.get("min_income", 0)
    max_income = policy.get("max_income", float("inf"))
    max_size = policy.get("max_household_size", 99)
    min_ratio = policy.get("min_energy_ratio", 0.0)
    regions = str(policy.get("regions", "전국"))

    reasons = []
    eligible = True

    if income < min_income or income > max_income:
        eligible = False
        reasons.append(
            f"소득 조건 미충족 (기준: {min_income:,.0f}~{max_income:,.0f}원)"
        )

    if household.household_size > max_size:
        eligible = False
        reasons.append(f"가구원 수 조건 미충족 (최대 {max_size}명)")

    if household.energy_ratio < min_ratio:
        eligible = False
        reasons.append(
            f"에너지지출비율 미충족 (최소 {min_ratio*100:.0f}% 이상 필요)"
        )

    if regions != "전국" and household.region not in regions.split("|"):
        eligible = False
        reasons.append(f"지역 조건 미충족 (대상: {regions.replace('|', ', ')})")

    if eligible:
        return True, "지원 대상에 해당합니다."
    return False, " / ".join(reasons)


def predict_savings(
    household: HouseholdInput,
    policy: dict,
) -> dict:
    """정책 적용 후 예상 절감 효과 계산."""
    electric_rate = float(policy.get("electric_discount_rate", 0))
    fuel_rate = float(policy.get("fuel_discount_rate", 0))
    monthly_support = float(policy.get("monthly_support_amount", 0))

    new_electric = household.monthly_electric * (1 - electric_rate)
    new_fuel = household.monthly_fuel * (1 - fuel_rate)
    new_total = new_electric + new_fuel + household.monthly_water - monthly_support
    new_total = max(new_total, 0)

    original = household.total_energy_cost
    savings = original - new_total
    savings_rate = (savings / original * 100) if original > 0 else 0

    return {
        "original_electric": household.monthly_electric,
        "original_fuel": household.monthly_fuel,
        "original_total": original,
        "predicted_electric": new_electric,
        "predicted_fuel": new_fuel,
        "predicted_total": new_total,
        "savings_amount": savings,
        "savings_rate": savings_rate,
        "monthly_support": monthly_support,
    }
