"""공통 UI 스타일 및 세션 상태 관리."""

import streamlit as st

from utils.calculations import HouseholdInput


def apply_custom_css():
    st.markdown(
        """
        <style>
        .main-header {
            font-size: 2rem;
            font-weight: 700;
            color: #1a5276;
            margin-bottom: 0.5rem;
        }
        .sub-header {
            font-size: 1rem;
            color: #566573;
            margin-bottom: 1.5rem;
        }
        .metric-card {
            background: linear-gradient(135deg, #eaf2f8 0%, #d4e6f1 100%);
            border-radius: 12px;
            padding: 1.2rem;
            border-left: 4px solid #2e86c1;
            margin-bottom: 1rem;
        }
        .policy-card {
            background: #ffffff;
            border: 1px solid #d5dbdb;
            border-radius: 12px;
            padding: 1.2rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .eligible-badge {
            background-color: #27ae60;
            color: white;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.85rem;
        }
        .ineligible-badge {
            background-color: #e74c3c;
            color: white;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.85rem;
        }
        .info-box {
            background-color: #fef9e7;
            border-left: 4px solid #f39c12;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_session_state():
    defaults = {
        "household": None,
        "household_dict": None,
        "recommendations": None,
        "savings": None,
        "forecast": None,
        "selected_policy": None,
        "input_complete": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def household_to_dict(household: HouseholdInput) -> dict:
    return {
        "monthly_income": household.monthly_income,
        "household_size": household.household_size,
        "region": household.region,
        "monthly_electric": household.monthly_electric,
        "monthly_fuel": household.monthly_fuel,
        "monthly_water": household.monthly_water,
        "monthly_energy_consumption": household.monthly_energy_consumption,
        "total_energy_cost": household.total_energy_cost,
        "energy_ratio": household.energy_ratio,
        "is_energy_poor": household.is_energy_poor,
    }
